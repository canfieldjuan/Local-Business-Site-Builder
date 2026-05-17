# Interior-Page Enrichment Pass

## Context

The current pipeline (`pipeline.py`) runs a single LLM analysis over the fetched **homepage HTML only**, producing `site_json`. The homepage generator (`generate_redesign()`) consumes that JSON to emit HTML. For multi-page sites whose homepage is a thin hero (the mocdlaw-com law firm is the canonical example), the analysis JSON has no practice areas, no attorney bios, no contact-form fields — and so the generated homepage is `nav -> trust-strip -> hero -> footer` and nothing else. The base template (`references/03-base-template.html`) already contains `.services-grid`, `.team-grid`, `.contact-form-wrap`, `.benefits-grid` components ready to receive content; the bottleneck is purely extraction.

Interior pages (`/areas-of-practice`, `/our-attorneys`, `/contact-us`) are already fetched **later** in `main()` to produce separate interior-page HTMLs (`generate_interior_page`). They never feed back into the homepage's analysis JSON.

**Goal of this change**: fetch the high-priority interior pages **before** homepage generation, run small per-page-type LLM extractions, and merge the results into `site_json`. The homepage generator then has real content to inject into its existing components.

**Out of scope this round** (named explicitly by the user, deferred to later passes):
- Hero copy quality (mission-statement-as-headline issue)
- Color discipline (`--accent` leaking everywhere from the logo color)
- Layout adjustments
- Local mirroring of enrichment-discovered images (e.g. attorney headshots)

---

## Approach

Three atomic changes. No existing function signature changes. No schema changes to `01-site-analysis-prompt.md`. Enrichment is best-effort: any single failure (fetch, LLM, schema) logs and continues; total failure leaves `site_json` exactly as analyzed and the existing homepage generation still works.

### Change 1 — New prompt file: `references/05-enrichment-prompt.md`

Single system prompt parameterized by `PAGE_TYPE`. Returns one JSON object whose shape depends on `PAGE_TYPE`. Reuses the existing `sections[]` item schema from `references/01-site-analysis-prompt.md:89-104` so the homepage generator already knows how to render the output. ASCII only.

Output shapes (caller is `enrich_site_json`; merge target on the right):

| PAGE_TYPE | Returned JSON | Merge target |
|---|---|---|
| `services` / `single-service` | `{type:"services", headline, items:[{title,url,image_url,tag,meta}], source_url}` | append to `site_json["sections"]` |
| `team` | `{type:"team", headline, items:[{title=name, url, image_url=photo, tag=role, meta=bio}], source_url}` | append to `site_json["sections"]` |
| `about` | `{type:"misc", headline, items:[{title, meta=paragraph}], source_url}` | append to `site_json["sections"]` |
| `faq` | `{type:"misc", headline:"FAQ", items:[{title=question, meta=answer}], source_url}` | append to `site_json["sections"]` |
| `contact` | `{form_fields:[str], contact_info:{phone,email,address,hours}, source_url}` | set as new top-level `site_json["contact_form"]` |

**Why `contact_form` is a new top-level key** (not a `sections[]` entry): existing schema carries `form_fields` only inside `single_page_sections[].content.form_fields` (`references/01-site-analysis-prompt.md:153`), which is empty by definition for multi-page sites. Reusing `sections[]` with `type:"contact"` would change the meaning of an existing slot. A dedicated key is the smallest non-disruptive landing spot. The redesign-prompt rule (Change 3) tells the generator how to read it.

Prompt rules: no invention, verbatim text, absolute URLs, return `{}` for empty/unusable pages.

### Change 2 — `pipeline.py`: new constants, new function, one new call line

**(a) Module-level constants**, inserted after the API-key block (after line 28, before `_fetch_with_playwright`):

```
ENRICHMENT_MODEL = "openai/gpt-4o"
ENRICHMENT_TEMPERATURE = 0.1
ENRICHMENT_HTML_TRUNCATE = 120000
ENRICHMENT_PRIORITY_THRESHOLD = 2
ENRICHABLE_PAGE_TYPES = {"services", "single-service", "team", "about", "faq", "contact"}
ENRICHMENT_PROMPT_PATH = "references/05-enrichment-prompt.md"
```

Values mirror existing literals already present in the file (model string, 120000 truncate, temp 0.1). The user's "no hard-coded values" rule applies to **new** values — these are introduced once at module top so the new code path is configurable; existing literals are not retroactively replaced (out of scope).

**(b) New function** `enrich_site_json(site_json)`, inserted after `analyze_site()` ends at `pipeline.py:165`, before `generate_redesign()` starts at `pipeline.py:167`. Contract:

- **Input**: `site_json` dict from `analyze_site()`.
- **Output**: same dict, mutated. May gain entries in `sections[]` and/or a top-level `contact_form`.
- **Pattern match**: mutates-and-returns, same as `mirror_images_locally` (`pipeline.py:148`). LLM call mirrors `analyze_site` (`pipeline.py:155-163`): `model=ENRICHMENT_MODEL`, `response_format={"type":"json_object"}`, `temperature=ENRICHMENT_TEMPERATURE`.

Algorithm:
1. Read `site_json.get("pages_to_fetch", [])`. Filter to entries where `fetchable is True`, `isinstance(priority, int)` and `priority <= ENRICHMENT_PRIORITY_THRESHOLD`, `page_type in ENRICHABLE_PAGE_TYPES`, `url` is a non-empty string.
2. De-duplicate by `page_type`: keep at most one page per type, lowest priority number wins. Caps LLM calls at `len(ENRICHABLE_PAGE_TYPES)` = 5.
3. Load the enrichment system prompt once from `ENRICHMENT_PROMPT_PATH`.
4. For each kept page, wrapped in try/except (fail-soft; log and continue):
   - `html = fetch_and_clean_html(url)` — reuses existing function at `pipeline.py:74-121`, which already handles Playwright fallback for JS-rendered sites and image extraction.
   - Build user prompt: `PAGE_TYPE: <type>\nSOURCE_URL: <url>\n\nHTML:\n<html[:ENRICHMENT_HTML_TRUNCATE]>`.
   - Call OpenRouter chat completion with the parameters above.
   - `json.loads(result)`. If `{}` -> skip.
   - **Schema guard**: for non-contact types, require `result.get("type")` is a string and `isinstance(result.get("items"), list)` and `len(items) > 0`. For contact, require non-empty `form_fields` list **or** any non-null value in `contact_info`. Otherwise skip with a log.
   - Inject `result["source_url"] = url` if not present.
   - Merge: non-contact -> `site_json.setdefault("sections", []).append(result)`. Contact -> `site_json["contact_form"] = result` only if the key is not already present (idempotent on re-run).
   - Log: `[*] Enriched {page_type} from {url}: {N} items`.
5. If nothing matches the filter, log `[*] No enrichable pages found; skipping enrichment.` and return unchanged.
6. Return `site_json`.

**(c) Call site in `main()`**: insert ONE line between `pipeline.py:400` (`site_json = analyze_site(html_content)`) and `pipeline.py:402` (the `site_name = ...` read):

```
site_json = enrich_site_json(site_json)
```

**Placement rationale**: must precede `mirror_images_locally` (`pipeline.py:413`), the hero-image generation block (`pipeline.py:418-433`), theme selection (`pipeline.py:437`), and `generate_redesign` (`pipeline.py:453`). No existing code moves; the contact-page block at `pipeline.py:457-466` is **unchanged** and still works — it reads `pages_to_fetch` and calls `generate_interior_page`, which fetches its own HTML.

### Change 3 — `references/02-redesign-gen-prompt.md`: append two rules

**Insertion point**: after line 256 (end of `MULTI-LOCATION RULE`), before the `---` separator on line 257.

```
ENRICHED INTERIOR-PAGE RULE: If sections[] contains an entry with type
"services" or "team" AND it carries a source_url field, render it on
the homepage as a preview grid and link to source_url with a "See all"
button. Limits: services -> top 6 items, team -> top 4 items,
FAQ-type misc sections -> top 4 items, about-type misc sections ->
render as a narrative block (no grid). Use .services-grid /
.team-grid / .benefits-grid classes from the base template -- do NOT
invent new layouts. If a section has no source_url, render it inline
without a "See all" link.

CONTACT FORM RULE: If site_json contains a top-level contact_form
object, populate .contact-form-wrap with one input per form_fields
entry and display contact_info values in the adjacent block. Link the
section heading to contact_form.source_url if present.
```

The `source_url` field is the discriminator that distinguishes enrichment-injected sections from any sections that `analyze_site` produces from the homepage itself (which never carry `source_url`). Existing/single-page behavior is therefore unchanged.

---

## Critical files

- `/home/juan-canfield/Desktop/website-redesign-skill/pipeline.py` — add constants, add `enrich_site_json()`, add one call line in `main()`. Reuses existing `fetch_and_clean_html()` (lines 74-121) and the OpenAI client (line 30).
- `/home/juan-canfield/Desktop/website-redesign-skill/references/05-enrichment-prompt.md` — new file.
- `/home/juan-canfield/Desktop/website-redesign-skill/references/02-redesign-gen-prompt.md` — append two rules after line 256.

**Read-only references** (consulted during implementation, not edited):
- `references/01-site-analysis-prompt.md` — `sections[]` schema at lines 89-104; `pages_to_fetch[]` schema at lines 124-132.
- `references/03-base-template.html` — confirms `.services-grid` (~line 1231), `.service-card` (~1237), `.team-grid` (~1157), `.team-card` (~1163), `.contact-form-wrap` (~951) exist.
- `CLAUDE.md:63` — "If you change the analysis JSON shape (`01-site-analysis-prompt.md`), audit every `site_json.get(...)` access in `pipeline.py`." This change does NOT modify `01`'s schema; new keys (`source_url` inside section entries, top-level `contact_form`) are additions the analyzer never produces, so no existing access pattern breaks.

---

## Verification

No tests exist in the repo. Verification is end-to-end + grep:

1. **Static checks on `pipeline.py` post-edit**:
   - `grep -P '[^\x00-\x7f]' pipeline.py` returns empty (no Unicode).
   - `grep -c 'def enrich_site_json' pipeline.py` returns `1`.
   - `grep -c 'site_json = enrich_site_json(site_json)' pipeline.py` returns `1`.
   - `python -c "import ast; ast.parse(open('pipeline.py').read())"` exits 0 (parses).

2. **End-to-end run**: `python pipeline.py https://mocdlaw.com --skip-deploy --skip-email`

   Expect new console lines:
   - `[*] Enriched services from <url>: <N> items`
   - `[*] Enriched team from <url>: <N> items`
   - Possibly `[*] Enriched contact from <url>: <N> items`

3. **Grep the resulting `outputs/mocdlaw-com/index.html`**:
   - `grep -c 'class="service-card"' outputs/mocdlaw-com/index.html` -> expect `>= 3` (was 0 in the previous run).
   - `grep -c 'class="team-card"' outputs/mocdlaw-com/index.html` -> expect `>= 2`.
   - `grep -o 'See all[^<]*' outputs/mocdlaw-com/index.html` -> at least one match.
   - Pick one practice-area name visible at `https://mocdlaw.com/areas-of-practice` and grep for it in `index.html` -> confirms enrichment reached the homepage, not just template fill.
   - `grep 'contact-form-wrap' outputs/mocdlaw-com/index.html` -> form inputs present whose labels match `form_fields` from `/contact-us`.

4. **Sanity on existing behavior**:
   - The contact-page block at `pipeline.py:457-466` still produces `outputs/mocdlaw-com/contact.html` unchanged in structure (it doesn't read `contact_form`; it generates from the fetched page HTML directly).

---

## Risks (acknowledged, accepted this round)

- **Token cost**: up to 5 extra GPT-4o calls per site. Capped by the priority<=2 filter and per-type dedup.
- **Wall-clock**: Playwright fallback inside `fetch_and_clean_html` can add ~30s per JS-rendered interior page. Acceptable.
- **Headshot images**: enrichment writes URLs into `sections[].items[].image_url` but `mirror_images_locally` only reads `site_json["images"]`. CDN URLs will remain — they load on Vercel but may break if the source CDN expires. Local mirroring of enriched images is deferred.
- **Duplicate sections**: if `analyze_site` happens to produce a `type:"services"` section from the homepage AND enrichment adds another from `/areas-of-practice`, both render. The `source_url` discriminator means only the enriched one gets "See all"; the original renders inline. Dedup is a later concern.
- **Single-page sites**: filtered out automatically (`fetchable: false` for all anchor links). Behavior is exactly the current behavior. No regression.
