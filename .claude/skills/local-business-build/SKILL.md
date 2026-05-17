---
name: local-business-build
description: Generate a single-page website mockup for a local-business prospect that has zero online presence. Use when the user pastes or points to a prospect JSON (business name, trade, city, phone, services, optional reviews), or asks to "build a site for [business]", "make a mockup for [trade] in [city]", or similar. Plumbers are the only supported trade in v1; for any other trade, complete the build with plumber defaults and emit a "Trade mismatch" warning in the results report (defined in the Report Results section) so the user knows to manually review the copy. Claude does the generation itself -- this skill does NOT call OpenRouter, Flux, or any external LLM/image API. Requires computer use / Bash access for file writes; without it, offer to print HTML inline. For redesigning an existing live website (URL-driven), use the `website-redesign` skill instead.
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

Read all four in order before generating any HTML:

1. **`references/03-base-template.html`** — the complete CSS framework
   and component library. The output embeds this CSS verbatim. Inject
   content into existing classes; do NOT invent new classes or write
   new CSS rules outside the `:root` token block.
2. **`references/06-build-prompt.md`** — section architecture, contact
   form rule, hero CTA architecture, star widget rendering, footer
   architecture, deployment comment block template, quality checklist.
   This is the most important file — read it carefully.
3. **`references/07-industry-defaults.md`** — trade-specific knowledge.
   For plumbers: hero copy template selection (three-tier rule),
   canonical service catalog, trust signal priority, theme (warm),
   accent color (`#D9534F`), section sequence.
4. **`examples/prospect-plumber-template.json`** — only consult if you
   need to verify the shape of an optional field.

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

## Hero image handling (no auto-generation)

This skill does NOT call any image generation API. Three ways to handle
the hero:

1. **Prospect provided photos**: if `prospect.photos[]` contains an entry
   with `context: "hero"` or `context: "background"`, use that URL directly
   as the hero background-image.
2. **No prospect photos**: emit
   `style="background-image: url('images/hero.jpg')"` as the hero background,
   and tell the user explicitly:
   - The site references `outputs/builds/<slug>/images/hero.jpg` but that
     file doesn't exist yet
   - Suggest 2-3 Unsplash search URLs the user can pick from manually
     (e.g. `https://unsplash.com/s/photos/plumber-service-truck`,
     `https://unsplash.com/s/photos/copper-pipe-installation`)
   - The user drops their chosen image at the suggested path before deploy
3. **For headless / batch use**, refer the user to `build.py` which calls
   Flux 2 via OpenRouter. Trade-off: image gen costs ~$0.05-0.10 per build.

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

## Generate the pitch email draft (alongside the HTML)

After writing `index.html`, also write `outputs/builds/<slug>/email_draft.md`
containing the Day-1 pitch email the salesperson will manually send.

Read `references/08-pitch-email-prompt.md` for the voice rules, hooks,
and template. The email is peer-to-peer, plain-spoken, ~80 words, with
hooks driven by prospect data (longevity, review score, trade
competition, etc.).

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

### Natural-language triggers for skipping

In a Claude Code chat, the user won't type `--skip-email-draft`. Treat
any of the following as the skip signal and only write `index.html`:

- "skip the email"
- "no email draft"
- "just the HTML" / "just the site" / "website only"
- "no pitch email"
- "don't generate the email"

When you skip, also delete any pre-existing
`outputs/builds/<slug>/email_draft.md` from a prior build so a stale
draft doesn't sit next to the fresh `index.html`. Mirror the
`build.py` behavior exactly.

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
- Pitch email to the prospect — that's still in `build.py`.

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
