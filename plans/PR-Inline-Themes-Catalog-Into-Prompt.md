# PR-Inline-Themes-Catalog-Into-Prompt

## Why this slice exists

Closes issue #20. The parallel input-pipeline bug to the one PR
#19 just fixed for `references/10-section-orders.md`: the LLM
never reads `references/09-themes.md` because `build.py` only
inlines 06 (system prompt), 07 (INDUSTRY DEFAULTS), 10 (SECTION
ORDERS as of PR #19), and 03 (BASE TEMPLATE) into its prompt.
09's theme catalog has been a dangling reference since PR #12.

Symptom (observed during PR #19 verification, filed as issue #20
before this slice was opened):

```
./venv/bin/python build.py examples/althoff-plumbing-effingham.json
[*] Theme: civic
```

`civic` theme per 09 specifies Fjalla One + Noto Sans +
Merriweather. Actual rendered HTML loads Inter + Lora -- the
base-template defaults the LLM falls back to when it can't see
the theme block. The same fallthrough affects every theme: Drees
under `broadcast` does not actually load Barlow Condensed,
Niebrugge under `editorial` does not load Oswald + Source Serif
4, Olney under `minimal` does not load DM Sans, etc.

PR #12's verification claimed visible Barlow Condensed on Drees,
but that verification looked at the per-prospect theme name in
stdout (`[*] Theme: broadcast`), not at the rendered HTML's
`<link href=".../Barlow...">` import. The font import was always
the base-template default; the variation has been harness-level
only since slice 1 landed.

## Scope (this PR)

1. Add `THEMES_CATALOG_PATH = "references/09-themes.md"`
   constant in `build.py` alongside the existing
   `INDUSTRY_DEFAULTS_PATH` / `SECTION_ORDERS_PATH` /
   `BASE_TEMPLATE_PATH` set.
2. In `generate_build_html()`, read 09 alongside 07, 10, and 03,
   then inline it in the user prompt static block as a labeled
   `THEMES:` section. Block order in the static prompt:
   `INDUSTRY DEFAULTS` -> `THEMES` -> `SECTION ORDERS` ->
   `BASE TEMPLATE`. THEMES sits between INDUSTRY DEFAULTS and
   SECTION ORDERS because the LLM reads INDUSTRY DEFAULTS to
   resolve trade-specific guidance (which references theme
   selection rules), then THEMES to resolve typography for the
   chosen theme.
3. Update `06-build-prompt.md` USER PROMPT FORMAT to document
   the new `THEMES:` block. Update the THEME & TYPOGRAPHY rule
   to reflect that 09's catalog is now inlined (drop any
   wording that implied the LLM should "look up" 09 from a
   filesystem path it never sees).

### Files touched

- `build.py` (~5 LOC: constant + read + inline in static_block)
- `references/06-build-prompt.md` (~10 LOC: USER PROMPT FORMAT
  block + minor tightening in THEME & TYPOGRAPHY)
- `plans/PR-Inline-Themes-Catalog-Into-Prompt.md` (new, this
  file, ~95 LOC)

## Mechanism

Identical pattern to PR #19's 10-inlining fix. Sequential reads
in `generate_build_html()`:

```python
with open(INDUSTRY_DEFAULTS_PATH, "r") as f:
    industry_defaults = f.read()
with open(THEMES_CATALOG_PATH, "r") as f:
    themes_catalog = f.read()              # NEW
with open(SECTION_ORDERS_PATH, "r") as f:
    section_orders = f.read()
with open(BASE_TEMPLATE_PATH, "r") as f:
    base_template = f.read()
```

`static_block` grows by one labeled section:

```python
static_block = (
    f"INDUSTRY DEFAULTS:\n{industry_defaults}\n\n"
    f"THEMES:\n{themes_catalog}\n\n"                 # NEW
    f"SECTION ORDERS:\n{section_orders}\n\n"
    f"BASE TEMPLATE:\n{base_template}"
)
```

09 is ~210 LOC. The static block grows by ~210 lines; the cache
key changes once (one-time miss on the next build); subsequent
builds rehit cache normally.

## Intentional

- This does not change `select_theme()` or any other harness
  selection. The harness was already correctly picking a theme
  per prospect (verified at stdout level since PR #12); only the
  LLM-side application was broken. This PR closes the input-
  pipeline gap without touching selection logic.
- 09's catalog is inlined as-is, not flattened or restructured.
  The file's organization (one section per theme, each with
  Google Fonts import + :root vars + style notes) is already in
  a shape the LLM can consume directly. Restructuring would
  expand scope and risk breaking the catalog the harness reads
  for validation (`KNOWN_THEMES` in `build.py`).
- 06's THEME & TYPOGRAPHY rule is tightened to reflect that 09 is
  now inlined, but not rewritten. The existing rule already says
  "look up the matching theme block in 09" and "apply its Google
  Fonts <link> + :root overrides" -- those instructions become
  actionable now that 09 is actually in the prompt.

## Deferred

- A `_computed_theme_block` concrete-form alternative
  (analogous to the `_computed_section_sequence` alternative
  deferred from slice 3b). Could replace `_computed_theme: "broadcast"`
  with `_computed_theme: {font_import: "https://...", font_display:
  "...", ...}` -- the harness resolves the theme block before
  injection, the LLM never needs to look up the catalog. Cleaner
  architecture if cross-reference patterns keep failing, but
  09's name-based form already works (proven by PR #19's
  equivalent fix for 10). Defer until a real failure surfaces.
- A fixture test asserting rendered HTML's `<link href="...">`
  matches the expected fonts per theme. Useful regression
  protection; deferred to a separate "tests/" slice rather than
  bundled here.
- Restructuring 09 to consolidate the per-theme blocks or change
  the catalog's layout. The current organization is fine for the
  LLM; no change needed.

## Verification

- `bash scripts/local_pr_review.sh` -> passed (worktree-clean,
  `git diff --check $base..HEAD`, plan-doc presence).
- `python3 -c "import ast; ast.parse(open('build.py').read())"` -> passed.
- Empirical (3 builds covering 3 different themes):
  - Drees Plumbing (theme=broadcast): rendered HTML loads
    `Barlow+Condensed`, `Barlow`, and `Playfair+Display` from
    Google Fonts and sets `--font-display: 'Barlow Condensed'`,
    `--font-body: 'Barlow'`, `--font-serif: 'Playfair Display'`
    in `:root` per 09's broadcast block.
  - Olney Heating (theme=minimal): rendered HTML loads
    `DM+Sans` and `DM+Serif+Display`, and sets `--font-display:
    'DM Sans'`, `--font-body: 'DM Sans'`, `--font-serif: 'DM
    Serif Display'` in `:root` per 09's minimal block.
  - Althoff Plumbing (theme=civic, section-order=services-led):
    rendered HTML loads `Fjalla+One`, `Noto+Sans`,
    `Merriweather` (not the base-template Inter + Lora it had
    been loading pre-fix); section ordering still matches
    services-led per PR #19's already-shipped fix.
- Regression: zero placeholder leaks, zero fabricated benefit
  cards across all three builds.

## Estimated diff size

| Area | Estimated LOC |
|---|---:|
| `build.py` | ~5 |
| `references/06-build-prompt.md` | ~10 |
| `plans/PR-Inline-Themes-Catalog-Into-Prompt.md` (this file) | ~95 |
| **Total** | **~110** |

Well under the 400 LOC soft budget.
