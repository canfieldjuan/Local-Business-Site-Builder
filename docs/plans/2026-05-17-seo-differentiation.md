# SEO Differentiation Across Per-Prospect Builds

**Status**: TABLED — not started, pick up when prioritized.
**Logged**: 2026-05-17.
**Primary differentiation goal**: SEO-facing (Google near-duplicate detection
in local pack, structured-data rich results).

## Context

The current `build.py` / build skill produces visually and textually similar
sites across plumber prospects because every build pulls from the same:

- `references/03-base-template.html` (CSS + components)
- Single hero copy template per tier in `references/07-industry-defaults.md`
- Fixed service descriptions in the canonical service catalog
- Fixed section headings ("Our Services", "Why Choose Us", "Customer Reviews")
- Default theme (`warm`) and accent (`#D9534F`)

Content that varies naturally is per-prospect data only: business name,
phone, city, years, services list, reviews. Two Tier-1 plumbers (established
>= 8 years, has_24_7) get nearly identical surface text.

Each prospect site lives on its own domain (Vercel subdomain or custom),
which softens Google's near-duplicate penalty substantially. But for an
agency shipping multiple plumber sites in the same metro, surface-text
deduplication + missing structured data is still a measurable SEO drag.

## Decision

When picked up, this work should optimize for **SEO** specifically, not
visual portfolio diversity. That ranks the work as follows:

| Add | SEO weight | Effort |
|---|---|---|
| JSON-LD schema with prospect data (`@type: "Plumber"` -- a LocalBusiness subtype) | Highest | ~30 min |
| Unique `<meta name="description">` per build | High | ~15 min |
| 2-3 hero copy variants per tier in `07` | Medium-high | ~30 min |
| 2-3 variants for each canonical service description | Medium-high | ~30 min |
| Section heading variants ("Our Services" -> "Plumbing Services" / "What We Fix") | Medium | ~15 min |
| Coverage band / trust strip phrasing variants | Low-medium | ~20 min |
| Color palettes, brand color pass-through | ~zero SEO | — |

Color palette / brand color work is **excluded from this scope** —
visual differentiation is a separate concern, separate PR if ever
warranted.

## Scope when picked up

**Files to touch**:

1. `references/06-build-prompt.md`
   - New `## STRUCTURED DATA (JSON-LD)` section with full LocalBusiness
     schema template. Plumber `@type`. Conditional rendering of
     `aggregateRating`, `review`, `address`, `openingHours`, `areaServed`
     based on which prospect fields are populated. Never fabricate.
   - New `## META TAGS` section: rule for `<meta name="description">`
     content (business name + trade + city verbatim, ~150 char).
   - New `## COPY VARIANT SELECTION` section: deterministic hash
     mechanism for picking variants from each variant set.

2. `references/07-industry-defaults.md`
   - Expand to 2-3 variants for:
     - Hero headline + subhead per tier
     - Each canonical service description (8 services x 2-3 variants)
     - Section headings (services, why-choose, customer-reviews)
     - Coverage band text
     - Trust strip phrasing
   - Add a `## COPY VARIANT GROUPS` section that lists each variant set
     by ID for reference.

3. `examples/prospect-plumber-template.json`
   - No schema changes needed; existing fields cover JSON-LD inputs.
   - Optional: document the variant selection mechanism in
     `_reviews_comment` style if a `palette_override` or similar field
     is ever added (currently out of scope).

4. `.claude/skills/local-business-build/SKILL.md`
   - Short note pointing to the new variant selection rule + JSON-LD
     section in 06.

## Variant selection mechanism (when implemented)

Deterministic hash of stable prospect identity:

```
seed = stable_hash(prospect.business_name + prospect.city)
variant_index = seed % len(variants_for_this_field)
chosen = variants_for_this_field[variant_index]
```

Properties:
- Same prospect always picks the same variant -> rebuilds are stable
- Different prospects (different business_name) pick different variants
- Mechanism is auditable: given a business_name + city + variant set, you
  can predict which variant was chosen

Each variant set is selected independently, so two prospects might share
the same hero copy variant but differ on service descriptions and section
headings -- additive variation across many small dimensions.

## JSON-LD template (reference)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Plumber",
  "name": "[business_name]",
  "telephone": "[phone]",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "[address line 1]",
    "addressLocality": "[city]",
    "addressRegion": "[state]",
    "postalCode": "[zip if present]"
  },
  "openingHours": "[hours formatted per schema.org spec]",
  "areaServed": ["[city 1]", "[city 2]", ...],
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "[google_review_score]",
    "reviewCount": "[google_review_count]"
  },
  "review": [
    {
      "@type": "Review",
      "author": {"@type": "Person", "name": "[review.author]"},
      "datePublished": "[parsed from review.date if possible]",
      "reviewRating": {"@type": "Rating", "ratingValue": "[review.rating]"},
      "reviewBody": "[review.text]"
    }
  ]
}
</script>
```

Only render fields the prospect actually provides. Skip any block that
would require null/placeholder values.

**Hours formatting**: by default use the simpler `openingHours` string
format (e.g. `"Mo-Fr 07:00-18:00 Sa 08:00-14:00"`) as shown in the
template above. The template uses this approach because most prospect
hours data is loose / human-readable. If a prospect provides
structured day-by-day hours in the JSON, optionally upgrade to the
fuller `openingHoursSpecification` array with one
`OpeningHoursSpecification` entry per day-range. Both forms are valid
schema.org; pick based on the precision of the source data.

## What's intentionally NOT in scope

- Color palette families per prospect
- Brand color extraction / pass-through
- Hero treatment variation (full-bleed vs split vs typographic)
- Theme switching (warm vs editorial vs civic)
- Layout reorderings (services-before-benefits flip etc.)
- FAQ section with `FAQPage` schema (would be a separate add)

Those belong to a separate "visual diversity" effort if ever pursued.
They have low SEO impact and high architectural cost.

## Triggers to pick this up

- Shipping 3+ plumbers in the same metro within a 30-day window (real
  duplicate-content risk surfaces)
- Agency portfolio gains visibility (current sales motion is per-prospect
  cold, so portfolio doesn't matter yet)
- Google Search Console signals on shipped sites show low rich-result
  coverage or duplicate-content warnings
- Anthropic releases a structured-data-aware update to Claude Design
  that affects how schema gets embedded

## Reference

Full discussion thread of this scoping decision is in the Claude Code
session log from 2026-05-17. See the question/answer exchange around
the prompt "want to test the new skill.md on a different plumber. So
that brings up an edge case..."
