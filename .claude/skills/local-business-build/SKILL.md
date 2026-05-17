---
name: local-business-build
description: Generate a single-page website mockup for a local-business prospect that has zero online presence. Use when the user pastes or points to a prospect JSON (business name, trade, city, phone, services, optional reviews), or asks to "build a site for [business]", "make a mockup for [trade] in [city]", or similar. Plumbers are the only supported trade in v1; for any other trade, complete the build with plumber defaults and emit a "Trade mismatch" warning in the results report (defined in the Report Results section) so the user knows to manually review the copy. Claude does the HTML generation itself -- this skill does NOT call OpenRouter, Flux, or any LLM/image-generation API. It MAY call the Unsplash photo-library API for hero images when `UNSPLASH_ACCESS_KEY` is set (free, 50 req/hr); falls back to a placeholder with manual-fetch suggestions when absent. Requires computer use / Bash access for file writes; without it, offer to print HTML inline. For redesigning an existing live website (URL-driven), use the `website-redesign` skill instead.
---

# Local Business Site Builder

This skill produces a complete single-page sales mockup for a local-business
prospect using the curated build pipeline in this repo. It replaces the
OpenRouter-based `build.py` for individual builds — Claude generates the HTML
directly, no external API calls, no per-build dollar cost.

The reference files (03, 06, 07, 08) are the single source of truth and are
shared with the `build.py` Python pipeline and the Claude Design project.
Edit those files to change behavior; this SKILL.md only describes the
workflow, not the rules themselves.

---

## Runtime requirements

This skill writes files to disk (`outputs/builds/<slug>/index.html`,
optional `email_draft.md`) and may shell out to the Vercel CLI for
deployment. It requires:

- **Computer use / Bash access** (not a pure-chat context). Without it,
  the skill can still produce the HTML in the conversation but cannot
  persist anything or deploy. If the calling context has no file-write
  capability, tell the user upfront and offer to print the HTML inline
  instead of writing to disk.
- **`vercel` CLI** if and only if the user asks to deploy. See the
  Optional: Deploy to Vercel section for the preflight check.
- **`UNSPLASH_ACCESS_KEY` env var** (optional, recommended). When set,
  the skill fetches a trade-appropriate hero photo from Unsplash and
  injects the remote URL into the HTML's `background-image`. The key
  is read in this priority order, first match wins: (a) the shell
  environment that launched Claude Code; (b) a `UNSPLASH_ACCESS_KEY=...`
  line in `.env` at the project root (the skill loads this itself via
  Bash before the preflight -- `.env` does NOT auto-load into a fresh
  shell). The variable name must be exactly `UNSPLASH_ACCESS_KEY` --
  generic names like `ACCESS_KEY` are unsafe and unsupported. When
  neither source has the key, the hero falls back to a
  `images/hero.jpg` placeholder and the report tells the user to drop
  one in manually. See the Hero image handling section for the full
  priority order and the API workflow.

---

## Inputs

Acquire a prospect JSON. Three ways:

1. The user passes a path (e.g. `examples/effingham-mikes-plumbing.json`).
2. The user pastes JSON inline in the conversation.
3. The user says "use the template" — read `examples/prospect-plumber-template.json`
   verbatim, but then warn that placeholder values will trip the sanitizer
   and the build will fall back to safe defaults.

**Required fields**: `business_name`, `trade`, `city`, `state`, `phone`.
If any are missing, refuse to proceed and ask the user to fill them.

Optional but high-value: `owner_email`, `established_year`,
`years_in_business`, `family_owned`, `licensed_and_insured`, `has_24_7`,
`service_radius`, `hours`, `services` (array), `google_review_score`,
`google_review_count`, `google_business_url`, `reviews` (array of objects),
`formspree_endpoint`, `photos` (array).

---

## Validation steps (run BEFORE generation)

These replicate what `build.py` does in code — do them in your head or
write them out as you go.

### Placeholder detection

Define markers (case-insensitive substring match):
`example.com`, `REPLACE`, `YOUR_FORM_ID`, `(REPLACE)`, `TODO`.

- **Critical fields** (`business_name`, `formspree_endpoint`): if a value
  contains any marker, print a loud warning
  `[!] PLACEHOLDER VALUE in prospect.<field>: <value>`
  `    The site will render this verbatim. Update before sharing the live URL.`
  Continue with the build — don't fail-fast — the user may be testing.
- **Optional fields** (`owner_email`, `owner_first_name`, `phone`,
  `address`): if a value is a placeholder, set the field to `null` in your
  working copy and log
  `[*] Nullifying placeholder prospect.<field>: <value>`
  The site will omit those fields entirely.

### Year normalization

If `established_year` is a sensible integer (`1900 <= n < current_year`),
recompute `years_in_business = current_year - established_year` and log
the override:
`[*] years_in_business recomputed: <old> -> <new> (from established_year=<X>)`

This corrects stale JSON where `years_in_business` was set in a previous
year and hasn't been updated.

### Review sanitization

Walk `prospect.reviews`. For each entry, check `author`, `text`, `date`,
`platform` for placeholder markers. If any field contains a marker,
**drop the entire review entry** from the array and log
`[*] Dropping placeholder review entry: author=<...>, text=<first-60-chars>...`

After sanitization the array may be shorter or empty; this is fine and
intentional — the Customer Reviews section branches based on
post-sanitization length.

### Build date injection

Set `prospect.build_date = <today's ISO date>` (e.g. `"2026-05-17"`).
The deployment comment block uses this verbatim. Never make up dates.

---

## Read the reference files

Read all four source-of-truth reference files in order before
generating any HTML or email. (These match the "(03, 06, 07, 08)"
list at the top of this skill.) Plus consult the prospect JSON
schema as a supplementary reference when needed.

1. **`references/03-base-template.html`** — the complete CSS framework
   and component library. The output embeds this CSS verbatim. Inject
   content into existing classes; do NOT invent new classes or write
   new CSS rules outside the `:root` token block.
2. **`references/06-build-prompt.md`** — section architecture, contact
   form rule, hero CTA architecture, star widget rendering, footer
   architecture, deployment comment block template, quality checklist.
   This is the most important file for HTML generation — read it
   carefully.
3. **`references/07-industry-defaults.md`** — trade-specific knowledge.
   For plumbers: hero copy template selection (three-tier rule),
   canonical service catalog, trust signal priority, theme (warm),
   accent color (`#D9534F`), section sequence, `hero_search_query`
   for the Unsplash photo fetch.
4. **`references/08-pitch-email-prompt.md`** — voice rules, hook table
   (Longevity / Review score / 24/7 / Family-owned / Discoverability
   fallback), subject-line algorithm, fabrication guards. Drives the
   email_draft.md output. Read this before generating the pitch email.

Supplementary (consult on demand, not always required):
- **`examples/prospect-plumber-template.json`** — schema reference;
  consult to verify the shape of an optional field if the prospect
  JSON looks unfamiliar.

---

## Generate the HTML

Follow the SYSTEM PROMPT section of `06-build-prompt.md` exactly. Key
constraints:

- **Single complete HTML file** containing the base-template CSS + injected
  body markup + deployment comment block at the top.
- **Output is HTML only.** No markdown fences, no preamble, no commentary.
  First chars: `<!--` deployment comment. Last chars: `</html>`.
- **Populate `:root` brand colors** from prospect.brand_colors if provided,
  otherwise the trade-default palette from 07.
- **Update Google Fonts import** to match the trade's theme (plumbers default
  to `warm` -> Lexend + Lato + Lora).
- **Never fabricate** reviews, ratings, dates, authors, response-time
  promises, year claims, awards, or certifications. Omit anything the
  prospect data doesn't provide. Verbatim only.
- **Headline selection**: apply the three-tier rule in 07 — Tier 1
  (`years_in_business >= 8`) wins over Tier 2 emergency even when
  `has_24_7` is true; 24/7 moves to the subhead.
- **Contact form action**: MUST be `prospect.formspree_endpoint` verbatim.
  If null or placeholder, use `action="#"` with a visible TODO comment.
- **Customer Reviews section branches** by sanitized review count:
  - 3+ entries → card grid + summary row below
  - 1-2 entries OR 0 with google_review_score set → aggregate widget only
  - 0 reviews AND no google_review_score → omit section entirely
- **Coverage band** sits between hero and services as a slim utility strip
  ("Not sure if we cover your area? Call <phone>"). Omit if phone is null.
- **Footer brand column** uses `.ft-brand-name`, `.ft-tagline`,
  `.ft-phone-label`, `.ft-phone`, `.ft-address` per the FOOTER ARCHITECTURE
  in 06. The phone is the second-most prominent element after the brand —
  do not bury it inside an address paragraph.

---

## Hero image handling

Fetch a trade-appropriate hero photo from Unsplash and inject the URL
directly into the HTML. No file download needed -- the URL is used as
the CSS background-image value. Works for both local preview and Vercel
deployment as long as the page has internet access.

---

### Priority order

1. **Prospect-provided photo** -- if `prospect.photos[]` contains an entry
   with `context: "hero"` or `context: "background"`, use that URL verbatim.
   Skip all steps below.

2. **Unsplash API** -- if `UNSPLASH_ACCESS_KEY` env var is set, fetch a
   photo using the trade query from `07-industry-defaults.md`.

3. **Manual fallback** -- if neither is available, emit a placeholder
   and report to the user (see Manual Fallback below).

---

### Step A -- Preflight

The Unsplash key may live in either the shell environment OR in a
local `.env` file at the project root. `.env` does NOT auto-load into
a fresh Bash shell -- only `python-dotenv` reads it, and only when
build.py / pipeline.py / anything that imports `lib.clients` runs.
The skill executes via Bash directly, so we have to load `.env` here
ourselves before the preflight check.

```bash
# 1. If the var isn't in the shell environment yet, try to read it
#    from .env. Strip surrounding quotes; preserve embedded '=' in
#    the value by splitting only on the first '='.
if [ -z "$UNSPLASH_ACCESS_KEY" ] && [ -f .env ]; then
    export UNSPLASH_ACCESS_KEY="$(grep -E '^UNSPLASH_ACCESS_KEY=' .env | head -1 | cut -d= -f2- | sed -e 's/^["'"'"']//' -e 's/["'"'"']$//')"
fi

# 2. Final check. If still empty, skip to Manual Fallback below.
if [ -z "$UNSPLASH_ACCESS_KEY" ]; then
    echo "[*] UNSPLASH_ACCESS_KEY not set in shell or .env; using manual fallback"
    # ... jump to Manual Fallback section below ...
fi

echo "[*] UNSPLASH_ACCESS_KEY loaded; proceeding with Unsplash API fetch"
```

**Key naming**: the variable MUST be named exactly `UNSPLASH_ACCESS_KEY`
in `.env`. Generic names like `ACCESS_KEY` are unsafe (collide with
AWS credentials and other SDKs that auto-read `ACCESS_KEY`) and the
preflight grep above won't match them. If the user has `ACCESS_KEY=...`
in their `.env`, tell them to rename it to `UNSPLASH_ACCESS_KEY` before
the skill can use it.

Only the Unsplash **Access Key** is needed (the public key used in the
`Client-ID` header). `APPLICATION_ID` and `SECRET_KEY` from the Unsplash
dashboard are NOT used by this skill -- they're only relevant for OAuth
flows which are out of scope.

Do NOT proceed with the API call if the preflight is empty.

---

### Step B -- Build the search query

Read `prospect.trade`, look up `hero_search_query` in
`references/07-industry-defaults.md` for that trade.

Example entry in 07 (plumber):
```
hero_search_query: "plumber service truck residential work"
```

If the trade is not in 07, construct a safe fallback:
`"{trade} professional service work"`

Never include the business name, phone number, or any text that
would appear in the image. Unsplash is a photo library -- these
fields don't affect results and can break the query.

---

### Step C -- Fetch from Unsplash

```python
import os, requests

query      = "<hero_search_query from 07>"
access_key = os.environ["UNSPLASH_ACCESS_KEY"]

r = requests.get(
    "https://api.unsplash.com/search/photos",
    headers={"Authorization": f"Client-ID {access_key}"},
    params={
        "query":       query,
        "per_page":    1,
        "orientation": "landscape",
        "content_filter": "high"
    }
)

results = r.json().get("results", [])

if not results:
    # fall through to Manual Fallback
    raise ValueError(f"No Unsplash results for query: {query}")

photo      = results[0]
hero_url   = photo["urls"]["regular"]
photo_id   = photo["id"]
credit     = photo["user"]["name"]
credit_url = photo["user"]["links"]["html"]

# Trigger required download event (Unsplash API terms)
requests.get(
    photo["links"]["download_location"],
    headers={"Authorization": f"Client-ID {access_key}"}
)

print(f"[+] Hero photo: {hero_url}")
print(f"[+] Credit: {credit} ({credit_url})")
```

---

### Step D -- Inject into HTML

Use `hero_url` as the hero section background:

```html
style="background-image: url('{{ hero_url }}')"
```

Add attribution to the deployment comment block at the top of the HTML:

```html
<!--
  ...existing deployment fields...
  Hero photo: {{ credit }} via Unsplash ({{ credit_url }})
  Photo ID:   {{ photo_id }}
-->
```

Attribution goes in the comment block only -- do NOT render it
visibly on the page. The prospect's brand is the focus.

---

### Manual fallback (no API key or zero results)

Emit the placeholder URL and report:

```html
style="background-image: url('images/hero.jpg')"
```

Report to user:
```
[!] Hero image not fetched -- UNSPLASH_ACCESS_KEY not set or query returned
    no results.
    Query attempted: "<query string>"
    The site references images/hero.jpg which does not exist yet.
    Suggested Unsplash search URLs to find one manually:
      https://unsplash.com/s/photos/<trade>-service-truck
      https://unsplash.com/s/photos/<trade>-professional-work
    Drop your chosen image at: outputs/builds/<slug>/images/hero.jpg
    before deploying.
```

---

### Rate limits and cost

- Free Unsplash developer account: 50 requests/hour
- Cost per image fetch: $0.00
- For batch runs (5+ prospects in one session), use `build.py` which
  manages rate limiting. The skill does not throttle -- back-to-back
  runs against the free tier will exhaust the hourly limit fast.
- Production / agency volume: apply for Unsplash Production status
  (free, requires approval) to raise limits.

---

### Adding hero_search_query to 07-industry-defaults.md

Each trade entry in 07 needs a `hero_search_query` field. Current coverage:

| Trade    | Query                                      | Status  |
|----------|--------------------------------------------|---------|
| plumber  | "plumber service truck residential work"   | defined |

Add a row to this table and the corresponding field in 07 whenever a
new trade is onboarded. The skill reads from 07 -- no changes needed
here.

---

## Write the output

`outputs/builds/<slug>/index.html`

Where `<slug>` is `prospect.slug` if set, otherwise derived from
`prospect.business_name` (lowercase, non-alphanumeric runs collapsed to
hyphens, leading/trailing hyphens stripped, fallback to `"prospect"` if empty).

Create the `outputs/builds/<slug>/` directory if it doesn't exist. The
`outputs/` tree is gitignored — these are per-prospect artifacts, not
source.

---

## Generate the pitch email draft (sibling to the HTML, NOT inside the deploy root)

After writing `index.html`, also write the Day-1 pitch email draft to:

```
outputs/email_drafts/<slug>.md
```

This is a SIBLING directory to `outputs/builds/<slug>/`, NOT a file
inside it. The deploy step uploads `outputs/builds/<slug>/` to Vercel
verbatim; anything inside that directory becomes publicly reachable
(e.g. at `/email_draft.md`). The pitch email is an internal
salesperson handoff — it contains recipient hints and a pre-send
checklist and must never be exposed at a deployed URL. The sibling
location is the architectural guarantee.

Read `references/08-pitch-email-prompt.md` for the voice rules, hook
table, subject-line algorithm, and fabrication guards. The email is
peer-to-peer, plain-spoken, ~80 words. The hook table defines five
data-driven hooks: Longevity, Review score, 24/7 availability,
Family-owned, and Discoverability (the last-resort fallback that
talks ONLY about the prospect's own missing site/form — never about
Google, competitors, or SERP positions).

The body must contain a literal `[VERCEL_URL_PLACEHOLDER]` token where
the live URL will go — the salesperson swaps it in after deployment.

Use `prospect.salesperson_first_name` for the sign-off; fall back to
`"Juan"` if absent.

Hard rules from `08`:
- 4-6 short sentences, under 100 words
- No agency-speak ("elevate your brand", "value proposition", "love to chat")
- Subject line under 10 words, no "Re:" prefix, no emojis
- Explicit "no follow-up unless you say so" exit clause
- Never fabricate metrics, review quotes, or outcome promises
- Never name specific national chains, never claim what Google shows,
  never promise the new site will rank above anyone

### Natural-language triggers for skipping

In a Claude Code chat, the user won't type `--skip-email-draft`. Treat
any of the following as the skip signal and only write `index.html`:

- "skip the email"
- "no email draft"
- "just the HTML" / "just the site" / "website only"
- "no pitch email"
- "don't generate the email"

When you skip, also delete any pre-existing
`outputs/email_drafts/<slug>.md` from a prior build so a stale draft
doesn't sit in the sibling directory while the freshly built site has
no matching pitch copy. Mirror the `build.py` behavior exactly.

---

## Report results

After writing the file, print a short summary to the user:

- `[+] Build complete: outputs/builds/<slug>/index.html`
- Section count rendered (typically 8: nav, trust strip, hero, coverage band,
  services, why-choose, reviews, contact form, footer)
- Placeholder warnings that fired during validation, in priority order
- Hero image status: "using prospect-provided URL" / "needs hero.jpg at
  outputs/builds/<slug>/images/hero.jpg"
- Formspree endpoint status: "real endpoint set" / "placeholder — update
  before sharing"
- **If `prospect.trade != "plumber"`**, ALSO print verbatim:
  `[!] Trade mismatch: industry-defaults.md covers plumbing only. Section`
  `    order, canonical service catalog, hero copy templates, trust signal`
  `    priority, theme, and default palette were all derived from plumber`
  `    defaults. Review the output for trade-appropriate copy before sharing.`
  This is the trade-mismatch warning referenced in the skill description.
  Do NOT silently render a non-plumber site using plumber defaults — the
  warning is the user's signal to manually review and adjust.
- Reminder: open the file in a browser to preview before sharing

---

## Optional: deploy to Vercel

If the user explicitly asks to deploy, run via Bash. First, preflight
the Vercel CLI — bailing here is much friendlier than a cryptic
"command not found" mid-deploy:

```
which vercel >/dev/null 2>&1 || { echo "[!] vercel CLI not found -- install with: npm i -g vercel"; exit 1; }
vercel whoami >/dev/null 2>&1 || { echo "[!] vercel CLI not authenticated -- run: vercel login"; exit 1; }
```

If either preflight fails, report the message to the user and STOP.
Do not attempt the deploy. The user runs the install / login command,
then asks you to retry.

Once preflight passes, deploy:

```
cd outputs/builds/<slug>
vercel --prod --yes --name <slug>
```

Do NOT run any of this automatically — always confirm with the user
first because:
- Deployment is publicly visible on a `.vercel.app` subdomain
- The Formspree endpoint and phone number become live (real customers
  could submit the form)
- A placeholder hero image would deploy as a broken image
- The `--name <slug>` creates / reuses a Vercel project of that name
  on the user's account

---

## What this skill does NOT do

- URL fetching / analyzing an existing site — that's the `website-redesign`
  skill.
- Flux / OpenRouter image generation — use `build.py` for headless mode.
- Automatic Vercel deployment — confirm first.
- Formspree account creation — user does that, pastes endpoint into JSON.
- Auto-send pitch emails — the skill generates `email_draft.md` containing
  the pitch body and pre-send checklist, but the user manually sends from
  their own email client (Gmail, Outlook, etc.). No Resend, no SMTP, no
  automated send path. See the "Generate the pitch email draft" section
  above for what the skill *does* produce.

---

## Files this skill reads (single source of truth)

| File | Purpose |
|------|---------|
| `references/03-base-template.html` | CSS framework + component library |
| `references/06-build-prompt.md` | Section rules + generation contract |
| `references/07-industry-defaults.md` | Trade-specific knowledge |
| `references/08-pitch-email-prompt.md` | Day-1 pitch email voice + template (used to produce `email_draft.md` alongside the site) |
| `examples/prospect-plumber-template.json` | Schema / optional-field reference |

These same files are consumed by `build.py` (programmatic) and the
Claude Design project (visual canvas). Edit them, not this SKILL.md,
to change behavior.
