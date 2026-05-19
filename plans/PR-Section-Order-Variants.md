# PR-Section-Order-Variants

## Why this slice exists

Last queued variation slice (slice 3b of the three-slice
"per-prospect uniqueness" plan agreed on 2026-05-18). After
PRs #12 / #14 / #15 / #18 landed:

- Theme rotation (6 variants, hash `[:8]`).
- Within-trade palette range (4 variants per trade, hash `[8:16]`).
- Hero shape coupled to theme (3 variants).
- Unsplash hero photo skipped on gradient.

Two prospects within the same trade now differ on typography,
color, and above-the-fold hero layout. Below the fold every site
still uses the same 9-section sequence. Two same-trade prospects
look identical from the services grid down.

The user explicitly flagged this as the lower-impact variation
axis (most prospects skim above the fold), and chose to ship it
anyway after slice 3a confirmed visible variation produces good
pitch-asset results. This slice closes the variation triple.

A second motivation surfaced during verification: the LLM was
never reading `09-themes.md` or any catalog file that 06's prose
"look this up in references/X.md" pattern referenced. Theme
typography silently fell through to base-template defaults
(Althoff under the `civic` theme rendered with Inter + Lora, not
Fjalla One + Noto Sans + Merriweather). The same input-pipeline
gap would have broken section-order variation. This PR closes the
gap for `10-section-orders.md`; the parallel `09-themes.md` fix
is filed separately as a follow-up (see Deferred).

## Scope (this PR)

1. Add `references/10-section-orders.md` -- catalog of three
   named section orderings (`default`, `services-led`,
   `reviews-led`). Each entry lists the section sequence with
   one-line rationale.
2. Add `select_section_order(prospect)` in `build.py` --
   `md5(business_name)[16:24]` mod 3 picks one of the three.
   Hash slice is disjoint from theme `[:8]` and palette
   `[8:16]`. `main()` injects the choice as
   `prospect["_computed_section_order"]` before HTML generation
   and logs `[*] Section order: <name>`.
3. Add `SECTION_ORDERS_PATH = "references/10-section-orders.md"`
   constant in `build.py` and inline 10's contents in
   `generate_build_html()`'s static block (between INDUSTRY
   DEFAULTS and BASE TEMPLATE). Without this, 06's prose
   pointer to 10 is a dangling reference -- the LLM never sees
   the named orderings.
4. Update `06-build-prompt.md` SECTION ARCHITECTURE: explicit
   "render order comes from `_computed_section_order` only" rule;
   numbered per-section list reframed as "rule index, not render
   sequence." USER PROMPT FORMAT documents the new `SECTION
   ORDERS` block in the user message.
5. Delete the three per-trade numbered "Section order for
   single-page X site" lists in `07-industry-defaults.md`
   (plumber lines 249-291, HVAC lines 594-611, electrician lines
   909-926). The LLM was using these as competing render-order
   sources. Replaced with prose "Section render order" pointers
   that defer to `10-section-orders.md`. Plumber's embedded
   "default 6 services" list and "no standalone Service Area
   section" guidance are preserved as separate prose subsections
   so the per-trade content isn't lost.

### Files touched

- `references/10-section-orders.md` (new, ~115 LOC)
- `references/07-industry-defaults.md` (-~90 / +~30, net ~-60)
- `references/06-build-prompt.md` (+45 / -3 = ~+42)
- `build.py` (~+53 LOC: helper + injection + path constant +
  static_block update)
- `plans/PR-Section-Order-Variants.md` (this file, ~110 LOC)

## Mechanism

Three orderings ship in `10-section-orders.md`:

| Name | Sequence (below nav) | Suits |
|---|---|---|
| `default` | trust -> hero -> coverage -> services -> why -> reviews -> contact | Trust-heavy prospects. |
| `services-led` | hero -> coverage -> services -> trust -> why -> reviews -> contact | Prospects whose services list is itself the differentiator. |
| `reviews-led` | hero -> coverage -> reviews -> services -> trust -> why -> contact | Prospects with strong review data. |

Always-first nav and always-last footer wrap each ordering. All
three honor existing conditional render rules (reviews
three-branch, coverage-band-needs-phone, why-choose-us
fabrication-guard padding, etc.). Selection is **purely
ordering**, never a presence override.

The LLM picks the sequence by reading
`prospect._computed_section_order` and looking up the matching
named ordering in the inlined `SECTION ORDERS:` block of the user
message. Without that inlining (the original scope) the LLM
defaulted to whichever numbered list it saw -- which on the first
two build attempts was 07's per-trade "Section order for
single-page plumber site" 1-9 list. After deleting those 07
lists and inlining 10 into the user prompt, the next build
applied `services-led` correctly.

## Intentional

- Three orderings only, not six or twelve. The LBSB target
  audience doesn't have wildly different content shapes; three
  reasonable variants gives enough fingerprint differentiation
  without over-engineering.
- Universal across trades (no per-trade `allowed_section_orders`
  list). Per-trade tuning is deferred.
- 07's per-trade "Section order" numbered lists were **deleted**,
  not annotated as advisory. The original plan kept them as
  advisory documentation, but during verification the LLM
  consistently treated those numbered 1-9 lists as the
  authoritative render order, ignoring 06's "rule index, not
  sequence" reframing AND the inlined 10 catalog. Advisor
  recommended the firmer fix: remove the competing numbered
  sources so 10's catalog is the only numbered ordering source
  the LLM sees. The advisor also noted the same input-pipeline
  bug applies to 09-themes.md (theme typography silently broken);
  that's filed as a follow-up rather than fixed here so this
  slice stays focused.
- Plumber's "default 6 services" list and "no standalone Service
  Area section" guidance were unique content embedded in the
  deleted ordering list. They're preserved as separate `###
  Default service grid selection (plumber)` and `### Service area
  handling (plumber)` prose subsections so the per-trade content
  survives the ordering-list deletion.
- `_computed_section_order` is a name (`"services-led"`), not a
  concrete list (`["hero", "coverage_band", ...]`). The
  name-based form requires the LLM to read the catalog; the
  list-based form would let `build.py` resolve the ordering
  directly. Advisor flagged the list-based form as a cleaner
  v2 architecture but said the name-based form converges
  acceptably once competing sources are removed -- so the
  name-based form ships here and the list-based form is
  deferred.

## Deferred

- **Same input-pipeline fix for `09-themes.md`.** The LLM
  currently does not read 09; theme typography silently falls
  through to base-template defaults. Althoff's verification
  build under `civic` rendered with Inter + Lora instead of
  Fjalla One + Noto Sans + Merriweather. Filed as a separate
  follow-up issue rather than fixed here -- the scope of slice
  3b is section ordering, not theme repair. The fix is small
  (mirror this PR's change: add 09 to the static block in
  `generate_build_html()`).
- Per-trade `allowed_section_orders` list (analogous to
  `allowed_themes`). Universal-list approach is the minimum
  viable; per-trade tuning makes sense after observing
  prospect-pitch results.
- `_computed_section_sequence` (concrete list of section names)
  instead of `_computed_section_order` (name pointing at the
  catalog). The list-based form removes the catalog-lookup
  indirection entirely; advisor flagged it as the cleaner v2
  architecture if cross-reference patterns keep proving fragile.
- New section variants (testimonials-led, video-hero-led, etc.).
  The three current orderings reuse the existing 9-section
  catalog from 06; new section types are larger scope.

## Verification

- `bash scripts/local_pr_review.sh` -> passed (worktree-clean,
  `git diff --check $base..HEAD`, plan-doc presence).
- `python3 -c "import ast; ast.parse(open('build.py').read())"` -> passed.
- `select_section_order()` across 5 fixture prospects produces 3
  distinct orderings: Drees=default, Althoff=services-led,
  Niebrugge=reviews-led, Olney=default, Pruemer's=reviews-led.
  Determinism confirmed -- 5 sequential calls on the same
  prospect always return the same ordering.
- Empirical: Althoff build (`services-led`) post-fix logs:
  ```
  [*] Section order: services-led
  ```
  Rendered HTML section sequence:
  ```
  HERO -> COVERAGE BAND -> SERVICES GRID -> TRUST STRIP ->
  WHY CHOOSE US -> REVIEWS -> CONTACT FORM -> FOOTER
  ```
  Trust strip moved from default position 2 to services-led
  position 4 -- the move slice 3b is targeting.
- Regression: zero literal placeholder leaks, zero fabricated
  why-choose-us claims in the Althoff build.
- Two earlier build attempts (before the 07-deletion +
  10-inline fix) demonstrated the bug clearly: first attempt
  rendered default ordering ignoring `_computed_section_order`
  entirely; second attempt rendered hero first but kept trust
  strip in default position 2. The third attempt (this PR's
  final state) renders services-led cleanly.

## Estimated diff size

| Area | Estimated LOC |
|---|---:|
| `references/10-section-orders.md` (new) | ~115 |
| `references/07-industry-defaults.md` (net) | ~-60 |
| `references/06-build-prompt.md` (net) | ~+42 |
| `build.py` | ~+53 |
| `plans/PR-Section-Order-Variants.md` (this file) | ~110 |
| **Total (net)** | **~260** |

Well under the 400 LOC soft budget.
