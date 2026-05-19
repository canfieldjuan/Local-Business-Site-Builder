# 09 -- Theme Catalog

Shared theme catalog the from-scratch build pipeline reads when populating
typography and layout personality. Themes control **typography and layout
feel only**; color values come from `prospect.brand_colors` if set, or
otherwise from the trade's `Color defaults` section in
`07-industry-defaults.md`.

The build harness (`build.py`) selects a theme deterministically per
prospect and injects the choice as `prospect._computed_theme` before the
LLM ever sees the prospect JSON. The LLM then reads this field verbatim
and applies the matching theme block below. **The LLM does not pick the
theme** -- the harness does, so two builds of the same prospect always
look the same. The selection rule lives in `06-build-prompt.md` under
"Theme selection."

For per-trade allowed themes, see each trade's `### Theme` section in
`07-industry-defaults.md`.

---

## broadcast -- dense, editorial, urgent

**When to use.** Emergency-oriented trades where speed is the visible
value prop: emergency plumber with `has_24_7: true`, no-heat HVAC,
fire-hazard electrician. Pairs naturally with `urgency_type =
"emergency"`. Ticker-and-grid news-station feel.

**Avoid when.** Heritage / tenured prospects (use `editorial`),
professional-services / commercial (use `minimal`).

**Google Fonts (insert in `<head>`):**

```html
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800;900&family=Barlow:wght@400;500;600&family=Playfair+Display:wght@700;900&display=swap" rel="stylesheet">
```

**`:root` overrides:**

```
--font-display:  'Barlow Condensed', sans-serif;
--font-body:     'Barlow', sans-serif;
--font-serif:    'Playfair Display', Georgia, serif;
--card-radius:   2px;
```

**Style notes.** Cards: flush grid -- minimal gap, no rounded corners.
Headlines: condensed sans, weight 800-900. Hero chip / badge style:
tight all-caps.

---

## editorial -- newspaper, column-based, refined

**When to use.** Established / tenured prospects: `established_year`
set AND `current_year - established_year >= 20`. Conveys longevity and
authority. Magazine-style layout, serif body, refined.

**Avoid when.** New businesses (the heritage signal is fabricated),
emergency-led trades (use `broadcast`).

**Google Fonts:**

```html
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=Playfair+Display:wght@700;900&display=swap" rel="stylesheet">
```

**`:root` overrides:**

```
--font-display:  'Oswald', sans-serif;
--font-body:     'Source Serif 4', Georgia, serif;
--font-serif:    'Playfair Display', Georgia, serif;
--card-radius:   0px;
```

**Style notes.** Cards: bordered, no rounded corners. Headlines: serif,
display weight. Badge style: category-underline (colored 2-3px underline
instead of pill).

---

## civic -- bold, structured, high-contrast

**When to use.** Utility / municipal / clinical feel. Best when the
trade is service-of-record and the prospect's brand reads cool and
professional rather than warm. Government-adjacent (city contractors,
school-district vendors) and commercial-leaning HVAC also work.

**Avoid when.** Family-owned, mom-and-pop, residential-only operations
(`warm` reads better).

**Google Fonts:**

```html
<link href="https://fonts.googleapis.com/css2?family=Fjalla+One&family=Noto+Sans:wght@400;500;600&family=Merriweather:ital,wght@0,700;1,400&display=swap" rel="stylesheet">
```

**`:root` overrides:**

```
--font-display:  'Fjalla One', sans-serif;
--font-body:     'Noto Sans', sans-serif;
--font-serif:    'Merriweather', Georgia, serif;
--card-radius:   4px;
```

**Style notes.** Cards: elevated -- subtle shadow OR strong border.
Headlines: bold geometric sans. Badge style: filled rectangles.

---

## warm -- friendly, slightly loose, inviting

**When to use.** Default for residential trades (plumber, HVAC,
electrician) when no stronger signal points elsewhere. Family-owned,
locally-owned, single-location prospects sit naturally here. Rounded
cards, friendly geometric sans, serif headlines for trust.

**Avoid when.** Emergency-led prospects with `has_24_7: true` and no
tenure story (use `broadcast`).

**Google Fonts:**

```html
<link href="https://fonts.googleapis.com/css2?family=Lexend:wght@500;600;700;800&family=Lato:wght@400;700&family=Lora:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
```

**`:root` overrides:**

```
--font-display:  'Lexend', sans-serif;
--font-body:     'Lato', sans-serif;
--font-serif:    'Lora', Georgia, serif;
--card-radius:   8px;
```

**Style notes.** Cards: rounded. Headlines: serif (Lora) for warmth +
trust on Tier 1 longevity prospects. Badge style: pill.

---

## minimal -- open, airy, lots of whitespace

**When to use.** Commercial / B2B-leaning trades, professional-services
feel. Commercial HVAC operations, electricians targeting business
clients. Single-column, no sidebar, generous whitespace -- the layout
itself is the trust signal.

**Avoid when.** Emergency-led residential trades (too quiet to convey
urgency).

**Google Fonts:**

```html
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Serif+Display:ital@0;1&display=swap" rel="stylesheet">
```

**`:root` overrides:**

```
--font-display:  'DM Sans', sans-serif;
--font-body:     'DM Sans', sans-serif;
--font-serif:    'DM Serif Display', Georgia, serif;
--card-radius:   8px;
```

**Style notes.** Cards: ghost -- minimal borders, whitespace does the
work. Headlines: serif display, but only on the hero. Badge style:
dot-plus-label (colored dot + text, no pill background).

---

## brand-forward -- hero-driven, large imagery

**When to use.** Forced selection when `prospect.brand_colors` is set
(see selection rule in `06-build-prompt.md`). The prospect already has
explicit brand identity -- the site should let those colors lead, with
display-weight typography and large hero imagery that frames them. Also
appropriate when explicitly opted into via `theme_override:
"brand-forward"`.

**Avoid when.** No brand colors and no opt-in -- the layout assumes a
distinctive accent and falls flat with the trade-default palette.

**Google Fonts:**

```html
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Manrope:wght@400;500;600&display=swap" rel="stylesheet">
```

**`:root` overrides:**

```
--font-display:  'Syne', sans-serif;
--font-body:     'Manrope', sans-serif;
--font-serif:    'Syne', sans-serif;
--card-radius:   6px;
```

**Style notes.** Cards: image-forward -- hero photos dominate, text
overlays. Headlines: display weight (Syne 800). Badge style: filled.

---

## Hero shape coupling

Each theme implies one hero layout shape. The `build.py` harness
reads `_computed_theme` and sets `prospect._computed_hero_shape`
accordingly -- no separate hash slice, so the coupling stays
deterministic and the theme/hero pairings always match.

| Theme | Hero shape | Why this pair |
|---|---|---|
| `broadcast` | `fullbleed` | Urgent, photo-driven -- the news-station register works best with a full-bleed image and dark overlay |
| `editorial` | `split` | Newspaper / column-based feel -- text-and-photo split mirrors the magazine layout the typography evokes |
| `civic` | `fullbleed` | Structured / high-contrast -- a full-bleed photo grounds the strong geometric typography |
| `warm` | `fullbleed` | Default residential warmth -- the historical hero behavior |
| `minimal` | `gradient` | Airy / whitespace-driven -- a photo would clutter the ghost-card aesthetic, so the gradient hero (accent + accent-dark, no image) carries the section instead |
| `brand-forward` | `fullbleed` | Image-forward by design -- this theme's spec already calls for hero photos to dominate |

For markup, see step 3 of `06-build-prompt.md`'s `SECTION ARCHITECTURE`
section. The `.hero-fullbleed`, `.hero-split`, and `.hero-gradient`
CSS classes live in `03-base-template.html` -- modifier classes on
top of `.dual-cta-hero`.

---

## Fallback rule

If `prospect._computed_theme` is missing or names a theme not listed
above, fall back to `warm` and emit a build-log warning. The harness
should always populate `_computed_theme`; encountering an unknown value
indicates a desync between `build.py` and this file -- fix and rerun.
