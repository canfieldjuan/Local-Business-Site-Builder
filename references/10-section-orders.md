# 10 -- Section Order Catalog

Catalog of section orderings the build harness picks among per
prospect. The build harness (`build.py select_section_order()`)
sets `prospect._computed_section_order` to one of the names below
before HTML generation. `06-build-prompt.md` SECTION ARCHITECTURE
reads that field and renders sections in the matching order.

Two prospects within the same trade get different orderings when
their `md5(business_name)[16:24]` hashes map to different
indices. The hash slice is disjoint from theme `[:8]` and palette
`[8:16]`, so all three variation axes are statistically
independent.

All three orderings honor the same per-section render rules from
`06-build-prompt.md` and `07-industry-defaults.md`:

- The reviews section's three-branch rendering (card grid /
  aggregate widget / omit) still applies.
- The coverage band still requires `prospect.phone`.
- The why-choose-us grid still gates each card per the
  fabrication guard (verified trust + service promise + safe
  generic padding to 3).
- The services grid still renders EXACTLY 6 cards.

Selection is **purely ordering** -- never a presence override.
A section that has no data to render still omits, regardless of
where the ordering places it.

For the per-trade narrative on why each ordering suits a given
prospect register, see the rationale lines in each catalog entry
below.

---

## default

Order below the nav:

1. Trust strip
2. Hero (full-bleed / split / gradient per `_computed_hero_shape`)
3. Coverage band
4. Services grid (6 cards)
5. Why-choose-us (3 cards, fabrication-guard-gated)
6. Reviews (three-branch rendering)
7. Contact form
8. Footer

**Rationale.** Today's historical ordering (pre-slice-3b).
Trust-heavy prospects (high review score AND tenure AND
licensed/insured) suit this register best because the trust strip
above the hero front-loads the credibility signal before the
visitor reaches anything else. The default name reflects "we
were here before slice 3b" rather than "the harness defaults
here" -- the harness picks evenly across all three.

---

## services-led

Order below the nav:

1. Hero (full-bleed / split / gradient per `_computed_hero_shape`)
2. Coverage band
3. Services grid (6 cards)
4. Trust strip
5. Why-choose-us (3 cards)
6. Reviews (three-branch rendering)
7. Contact form
8. Footer

**Rationale.** Hero straight into services. The trust strip moves
below the services grid so the visitor sees the *what* before the
*credibility*. Suits prospects whose services list is itself the
differentiator -- specialty trades, niche service mixes, prospects
who can name 6 things they actually do well rather than the
canonical-catalog padding.

---

## reviews-led

Order below the nav:

1. Hero (full-bleed / split / gradient per `_computed_hero_shape`)
2. Coverage band
3. Reviews (three-branch rendering)
4. Services grid (6 cards)
5. Trust strip
6. Why-choose-us (3 cards)
7. Contact form
8. Footer

**Rationale.** Reviews right after the hero. Suits prospects with
strong review data (4+ stars, multiple Google reviews) where the
social proof carries the page. When the prospect has no review
data, the reviews section omits per its three-branch rule and the
ordering effectively becomes `hero -> coverage -> services ->
trust -> why-choose -> contact -> footer` -- which is reasonable
fallback behavior, not a bug. Don't override the ordering based
on review presence; the harness picks ordering, the section's
own rule handles emptiness.

---

## Fallback rule

If `prospect._computed_section_order` is missing or names an
ordering not catalogued above, fall back to `default`. The harness
(`select_section_order()` in `build.py`) only ever picks from
`KNOWN_SECTION_ORDERS`, so encountering an unknown name in a
generated site indicates a desync between `KNOWN_SECTION_ORDERS`
and the names in this file -- the fallback keeps the build
buildable; the operator should reconcile the catalog and rerun.
