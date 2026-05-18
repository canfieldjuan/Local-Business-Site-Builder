# 07 -- Industry Defaults (Plumbing)

Knowledge base the from-scratch build pipeline (`build.py`) uses when the
prospect JSON doesn't specify a value. Used by `06-build-prompt.md` to
fill in industry-standard content for a local plumbing business that has
no current online presence.

This is NOT a content database -- it's a defaults book. Prospect-specified
values always win. Use these only to fill gaps.

---

## TRADE: plumber

### Buyer / urgency profile

A plumbing prospect's site visitor falls into two segments:

1. **Emergency** (~70% of inbound traffic for plumbers) -- pipe burst,
   water heater failed, sewage backup, no water, no hot water. Decision
   in minutes. They will call the first credible result. Phone CTA dominates.
2. **Planned** (~30%) -- water heater replacement, repipe quote,
   bathroom remodel rough-in, recurring drain maintenance. Decision in
   days. Form CTA acceptable.

A plumber site MUST serve emergency first. Phone visible in nav, sticky
on mobile, "Available 24/7" badge if applicable. Form is secondary.

### Canonical service catalog

Use these as the default service list when the prospect's JSON doesn't
specify, OR to augment a sparse list. Prospect-specified items win.

| Service                       | One-line description                                                |
|-------------------------------|---------------------------------------------------------------------|
| Emergency Leak Repair         | 24/7 response to burst pipes, slab leaks, and active water damage.  |
| Water Heater Repair & Install | Tank and tankless systems. Same-day replacement available.          |
| Drain Cleaning                | Hydro-jet and snake service for kitchen, bath, and main lines.      |
| Sewer Line Repair             | Camera inspection, spot repair, and trenchless replacement.         |
| Sump Pump Service             | Repair, replacement, and battery backup installation.               |
| Garbage Disposal              | Repair, replacement, and new installation.                          |
| Faucet & Fixture Replacement  | Kitchen, bath, and outdoor fixtures.                                |
| Toilet Repair & Install       | Running toilets, leaks, full replacement.                           |
| Repiping                      | Whole-home replacement for failing galvanized or polybutylene pipe. |
| Gas Line Repair               | Licensed gas line work for ranges, water heaters, and grills.       |

### Hero copy templates -- selection rule

Apply this decision tree in order. The first matching tier wins.
Substitute `[CITY]`, `[YEAR]`, `[YEARS]`, `[SERVICE_AREA]` from
prospect values. NEVER fabricate a tenure value -- if the field is
absent, fall through to the next tier.

**Tier 1 -- Established (years_in_business >= 8):**

This tier wins even when has_24_7 is true. An 8+ year track record
beats "we're available 24/7" on credibility. When has_24_7 is true,
the 24/7 claim is carried by the `.hero-chip` eyebrow badge above the
headline (see 06-build-prompt.md HERO CHIP rule) -- do NOT duplicate
it in the subhead. Trying to out-emergency Roto-Rooter in the headline
is a losing position for a local plumber; trying to out-trust them on
locality and tenure is winnable.

- Headline: `[CITY]'s Trusted Plumber Since [YEAR]`
- Subhead (any value of has_24_7): `[YEARS] years of plumbing repair, replacement, and installation across [SERVICE_AREA]. Licensed, insured, family-owned.`
  (If has_24_7 is false, append: ` Free estimates.`)

**Tier 2 -- Emergency (years_in_business < 8 AND has_24_7 true):**

Newer business that still differentiates on 24/7 availability. Lead
with it because there is no longer-tenure story to tell yet.

- Headline: `Emergency Plumber in [CITY] -- We Answer 24/7`
- Subhead: `Same-day service across [SERVICE_AREA]. Licensed, insured, locally owned.`

**Tier 3 -- Local (years_in_business < 8 AND has_24_7 false/absent):**

New business without 24/7 service. Lead on credentials, pricing
transparency, and the anti-franchise angle.

- Headline: `Licensed Plumber Serving [CITY]`
- Subhead: `Fast response, upfront pricing, no franchise fees padding your bill.`

NEVER use mission-statement language ("We believe in honest plumbing",
"Our mission is to..."). NEVER use "dedicated" or "committed to."
NEVER drop the headline tier rule -- a Tier-1 plumber with 24/7
service does NOT get the bare emergency headline; the 24/7 fact goes
into the subhead, not the headline.

### Trust signal priority

Use the highest-tier signal the prospect actually has. Skip lower tiers
if a higher one exists.

1. Third-party review score with platform name (`4.8 from 127 Google Reviews`)
2. Years in business + location (`Serving [CITY] since [YEAR]`)
3. Licensing + insurance + locally-owned line (`Licensed, insured, family-owned`)
4. Service-radius coverage (`Serving [CITY] and surrounding areas within 25 miles`)

NEVER fabricate review counts. If the prospect didn't provide a review
score, use tier 2 or 3.

### Competitive positioning vs national chains

Local plumbers compete against Roto-Rooter, Mr. Rooter, Benjamin Franklin,
and similar national/franchise brands that dominate paid local-pack ads.
The site should signal *local* without being explicit / defensive about it.

Positive signals to include (when true):
- "Family owned and operated"
- "Local technicians, not call-center dispatchers"
- "Upfront flat-rate pricing, no surprise fees"
- "Owner answers the phone after hours"
- Specific small geographic coverage area

Do NOT explicitly name competitors ("better than Roto-Rooter"). Looks
defensive and triggers brand-disparagement issues.

### Section order for single-page plumber site

This is the canonical section sequence. Render top to bottom in this order.
See 06-build-prompt.md SECTION ARCHITECTURE for exact markup patterns.

1. Sticky nav (business name + phone + CTA button)
2. Trust strip (review score / years-in-business / licensed-insured row,
   directly under nav, full-width band)
3. Hero (full-bleed photo, headline, subhead, dual CTAs: call + form anchor).
   Subhead names the service-area cities -- those cities are NOT repeated
   anywhere else on the page.
4. Coverage band (slim strip: "Not sure if we cover your area? Call <phone>")
5. Services grid (3 columns desktop, 1 column mobile, EXACTLY 6 services).
   6 fills the grid as 2 clean rows of 3 -- 7 or 8 leaves an orphan
   trailing cell that reads as a layout bug. Prospect-specified
   services win; if the prospect supplied more than 6, pick the 6
   with highest commercial value (emergency + replacement work over
   small-ticket fixture jobs). The default 6 for a plumber when the
   prospect list is sparse: Emergency Leak Repair, Water Heater
   Repair & Install, Drain Cleaning, Sewer Line Repair, Sump Pump
   Service, Toilet Repair & Install. (Faucet & Fixture Replacement
   and Garbage Disposal stay in the canonical catalog above for
   prospects who explicitly ask for them.)
6. Why choose us / differentiators (EXACTLY 3 cards, wrapped in
   <section class="section-band">. Consolidate overlapping claims --
   "family-owned" + "licensed/insured/local" become ONE card, not two.)
7. Customer Reviews -- three branches (see 06-build-prompt.md for full
   markup):
   - 3+ entries in prospect.reviews -> card grid with quote cards plus
     an inline summary row below (best treatment).
   - prospect.reviews empty (or <3 entries) AND google_review_score is
     set -> centered aggregate widget only (score + count + link).
     Never render 1 or 2 cards.
   - Both reviews empty AND google_review_score null -> OMIT the
     entire section. No section header alone.
8. Inline contact form (above footer, anchor target for the hero's form CTA)
9. Footer (3-col: brand+phone+address | hours | service-area)

NOTE: there is NO standalone "Service Area" section in this sequence.
The hero subhead names the cities; the coverage band (step 4) carries
the "not sure if we cover you" prompt. Rendering an additional service-
area section duplicates both. The Service Area's textual function is
absorbed into steps 3 and 4.

Omit any section the prospect data can't fill honestly. A plumber site
without a Google review score skips section 7 cleanly -- do not pad
with generic testimonials or fabricated review claims.

### Hours defaults

If prospect didn't specify, use:
- Office: `Monday-Friday 7:00 AM - 6:00 PM, Saturday 8:00 AM - 2:00 PM`
- Emergency: `24/7 emergency service available`

### Service radius defaults

If prospect didn't specify, use a 20-mile radius from the listed city.
Phrase as: `Serving [CITY] and surrounding communities within 20 miles`.

### Hero image source -- two paths

**Path 1 -- Unsplash photo library (skill default; build.py-compatible)**

The `local-business-build` Claude Code skill (and any future
Unsplash-aware build pipeline) fetches a hero from Unsplash using a
trade-specific search query. The skill reads this field per-trade:

```
hero_search_query: "plumbing"
```

**Empirically verified** against the Unsplash search API (May 2026):
this single-word query returns 2,314 results, and the top
landscape-oriented match is a plumber-in-action photo ("a man working
on a pipe in a wall"). Earlier multi-word phrases like "plumber
service truck residential work" returned only 2 results, with the
top match being a snow-covered crane truck -- not plumber-appropriate.

The "fewer words wins" rule for Unsplash search:

- Unsplash search is keyword-based, not phrase-based. Long multi-word
  queries narrow the pool to photos tagged with ALL words; few
  photographers tag with five words. A single specific trade word
  ("plumbing", "roofing", "electrical") usually returns 1000+ results.
- The first result for a single-word trade query is almost always the
  most-favorited photo for that tag, which tends to be a real working
  professional in context -- exactly what we want.
- Do NOT include the business name, city, or any text that would
  appear in the image. Unsplash is a photo library; those words don't
  improve results and can break the query.

When onboarding a new trade, start with the single-word trade name
(e.g. "roofing", "hvac", "landscaping") and only narrow if results
are off-target. Verify the top result is appropriate by inspecting
the API response before committing the query.

**Path 2 -- generated hero image (legacy build.py path via Flux 2)**

For `build.py` runs with `UNSPLASH_ACCESS_KEY` unset, the existing
Flux 2 image-generation prompt remains. Default hero prompt template:

```
Professional photorealistic hero image for a local plumbing business in
[CITY]. Wide cinematic crop, golden-hour natural light, depth of field.
Subject: a plumber's service van parked in a residential driveway, tools
visible but tidy, or a close-up of a clean copper pipe installation
under a sink. NO text, NO logos, NO faces clearly visible, no people
wearing branded apparel from any specific company.
```

Why no faces / branded apparel: the same image gets reused across multiple
prospects in this trade, and we don't want any prospect to feel the photo
is "of someone else's business." Generic-but-professional wins.

The Unsplash path (Path 1) is preferred when available -- it's free,
fast, and produces real photography. The Flux path (Path 2) is the
fallback when no Unsplash key is configured.

### Page set for MVP

Single page (`index.html`) containing all sections above. That's the
shippable product. Multi-page (services subpages, individual service
detail pages, blog) is v2 and lives in a different generation prompt.

### Theme

Plumber sites default to theme = `warm` (rounded cards, friendly Lexend
typography, Lora serif for headlines). Override to `civic` only if the
prospect's brand colors are explicitly cool/blue and they want a more
utility/clinical feel.

### Color defaults

If prospect provided brand colors, use them. If not:
- Accent: red-orange (`#D9534F`) -- emergency/urgency signal
- Secondary: navy (`#1F3A5F`) -- trust/professional
- Background: white (light theme)

Apply the COLOR DISCIPLINE rule from `02-redesign-gen-prompt.md`: accent
appears on AT MOST 3-4 elements (primary CTA, sticky phone, one badge).

---

## TRADE: hvac

### Buyer / urgency profile

An HVAC prospect's site visitor falls into two segments:

1. **Emergency** (~60% of inbound traffic) -- AC failure in summer,
   no heat in winter, furnace making concerning noises before it
   quits. Decision in hours rather than minutes (unlike a burst
   pipe). They will call the first credible result. Phone CTA
   dominates.
2. **Planned** (~40%) -- end-of-life system replacement (15-25 year
   cycle), new-construction install, ductwork upgrade, seasonal
   tune-up, indoor air quality improvements. Decision in days to
   weeks. Form CTA acceptable.

Compared to plumbing, HVAC emergencies have slightly more grace
period and a higher proportion of planned high-ticket work
(~$5-15K full system installs). The site should still serve
emergency first -- phone visible in nav, sticky on mobile, "24/7"
badge if applicable -- but the planned-work pitch carries more
weight here than for plumber.

### Canonical service catalog

Use these as the default service list when the prospect's JSON
doesn't specify, OR to augment a sparse list. Prospect-specified
items always win.

| Service                       | One-line description                                                |
|-------------------------------|---------------------------------------------------------------------|
| AC Repair & Installation      | Window units, central AC, mini-splits. Same-day repair, multi-day install. |
| Furnace Repair & Installation | Gas, electric, oil. Repair to full system replacement.              |
| Heat Pump Service             | Installation, repair, and refrigerant service for heat pumps.       |
| Duct Cleaning & Sealing       | Air duct cleaning, sealing leaks, improving system airflow.         |
| Thermostat Installation       | Smart thermostats, programmable thermostats, replacement.           |
| Seasonal Tune-Up              | Annual maintenance: AC in spring, furnace in fall.                  |
| Indoor Air Quality            | Whole-home humidifiers, dehumidifiers, air purifiers, HEPA filters. |
| Refrigerant Service           | EPA Section 608 certified refrigerant recharge and recovery.        |
| Emergency No-Heat / No-AC     | 24/7 response for system failures during extreme weather.           |
| New Construction HVAC         | Full HVAC rough-in and finish for new homes and additions.          |

The default 6 for an HVAC build when the prospect list is sparse:
AC Repair & Installation, Furnace Repair & Installation, Duct
Cleaning & Sealing, Thermostat Installation, Seasonal Tune-Up,
Indoor Air Quality. Heat Pump Service is regional (less common in
the rural Midwest, much more common in the Southeast) -- include
only when the prospect explicitly offers it.

### Hero copy templates -- selection rule

Apply this decision tree in order. The first matching tier wins.
Substitute `[CITY]`, `[YEAR]`, `[YEARS]`, `[SERVICE_AREA]` from
prospect values. NEVER fabricate a tenure value -- if the field is
absent, fall through to the next tier.

**Tier 1 -- Established (years_in_business >= 8):**

This tier wins even when has_24_7 is true. An 8+ year track record
beats "we're available 24/7" on credibility. When has_24_7 is true,
the 24/7 claim is carried by the `.hero-chip` eyebrow badge above
the headline (see 06-build-prompt.md HERO CHIP rule) -- do NOT
duplicate it in the subhead.

- Headline: `[CITY]'s Trusted HVAC Since [YEAR]`
- Subhead (any value of has_24_7): `[YEARS] years of heating, cooling, and indoor-air comfort across [SERVICE_AREA]. Licensed, insured, family-owned.`
  (If has_24_7 is false, append: ` Free estimates on system replacements.`)

**Tier 2 -- Emergency (years_in_business < 8 AND has_24_7 true):**

Newer business that still differentiates on 24/7 availability. Lead
with it because there is no longer-tenure story to tell yet.

- Headline: `Emergency HVAC in [CITY] -- 24/7 No-Heat & No-AC Service`
- Subhead: `Same-day repair for furnace, AC, and heat pump failures across [SERVICE_AREA]. Licensed, insured, locally owned.`

**Tier 3 -- Local (years_in_business < 8 AND has_24_7 false/absent):**

New business without 24/7. Lead on credentials, certifications,
and the anti-franchise angle.

- Headline: `Licensed HVAC Contractor Serving [CITY]`
- Subhead: `EPA-certified heating, cooling, and indoor-air work. Fast response, upfront pricing, no franchise dispatch fees padding your bill.`

NEVER use mission-statement language ("We believe in honest HVAC",
"Our mission is to..."). NEVER use "dedicated" or "committed to."
NEVER drop the tier rule -- a Tier-1 established HVAC with 24/7
service does NOT get the bare emergency headline; 24/7 moves to
the subhead or hero chip, not the headline.

### Trust signal priority

Use the highest-tier signal the prospect actually has. Skip lower
tiers if a higher one exists.

1. Third-party review score with platform name (`4.8 from 127 Google Reviews`)
2. Years in business + location (`Serving [CITY] since [YEAR]`)
3. **EPA Section 608 / NATE certification** (`EPA-certified, NATE-certified`) -- HVAC-specific, real, verifiable credential
4. Licensing + insurance + locally-owned line (`Licensed, insured, family-owned`)
5. Service-radius coverage (`Serving [CITY] and surrounding areas within 25 miles`)

EPA Section 608 certification is legally required in the US to
handle refrigerants -- if a prospect is operating, they almost
certainly have it. Worth surfacing as a trust signal because most
homeowners don't know it's mandatory and reading "EPA-certified"
adds credibility. NATE (North American Technician Excellence) is a
voluntary trade-association credential that signals higher
training; only mention if the prospect actually holds it.

NEVER fabricate certifications. If the prospect JSON doesn't
confirm NATE or specific licensing class, drop those claims and
fall back to the generic licensed/insured signal.

### Competitive positioning vs national chains

Local HVAC contractors compete against ARS / Service Experts,
American Home Shield (home-warranty dispatch), Trane Comfort
Specialists, Mr. Cool, Roto-Rooter Heating & Cooling, and similar
national/franchise brands that dominate paid local-pack ads. The
site should signal *local* without being explicit / defensive
about it.

Positive signals to include (when true):
- "Family owned and operated"
- "EPA-certified technicians, not seasonal contractors"
- "Upfront flat-rate pricing, no warranty-company runaround"
- "Same crew installs the system AND comes back for the service call"
- "Owner answers the phone after hours"
- Specific small geographic coverage area

Do NOT explicitly name competitors ("better than ARS"). Same
fabrication guards as plumber section -- looks defensive and
triggers brand-disparagement issues.

### Section order for single-page HVAC site

Same as plumber (HVAC sits under the `home-services` umbrella in
`02-redesign-gen-prompt.md`'s industry section priority table).
Render top to bottom in this order:

1. Sticky nav (business name + phone + CTA button)
2. Trust strip (review score / years / EPA-cert / licensed-insured row)
3. Hero (full-bleed photo, headline, subhead, dual CTAs: call + form anchor)
4. Coverage band (`Not sure if we cover your area? Call <phone>`)
5. Services grid (EXACTLY 6 services -- same orphan-cell logic as plumber)
6. Why choose us (EXACTLY 3 cards in `.section-band`, `benefits-grid--three`)
7. Customer Reviews (three-branch logic -- same as plumber's Branch A/B/C)
8. Inline contact form
9. Footer (3-col: brand+phone+address | hours | service-area)

No HVAC-specific section additions vs plumber. The framework
transfers as-is.

### Hours defaults

If prospect didn't specify, use:
- Office: `Monday-Friday 7:00 AM - 6:00 PM, Saturday 8:00 AM - 2:00 PM`
- Emergency: `24/7 emergency service available`
- Seasonal note: HVAC demand is bimodal -- if prospect data
  indicates extended summer/winter hours during peak season,
  surface that fact rather than using the standard week.

### Service radius defaults

If prospect didn't specify, use a 25-mile radius from the listed
city. Phrase as: `Serving [CITY] and surrounding communities
within 25 miles`. HVAC service areas tend to be slightly larger
than plumber because higher-ticket installs justify longer drive
time per call.

### Hero image source -- two paths

**Path 1 -- Unsplash photo library (skill default)**

```
hero_search_query: "hvac technician"
```

**Multi-word exception to the "fewer words wins" rule** (empirical,
verified 2026-05-18): for HVAC, the single-word `"hvac"` query
maps to commercial-system stock imagery (industrial pipes, exterior
AC units on walls) -- credible but cold, no human presence. The
single-word fallbacks `"furnace"`, `"heating"`, and `"air
conditioning"` produce the same equipment-only failure mode. Only
the multi-word `"hvac technician"` (605 results vs 8000+ for
"heating") returns the **tradesperson-at-work imagery** that
matches the warmth target. Lesson: "fewer words wins" is a
trade-specific heuristic, not universal. Plumber works at one word
because "plumbing" already maps to the human-at-work tag pool;
HVAC does not. When onboarding a new trade, **start with the
single-word trade name AND verify the top result has a human in
it**; if not, escalate to a two-word query that names the person
(`<trade> technician`, `<trade> contractor`, `<trade> worker`).

**Path 2 -- generated hero image (legacy build.py Flux path)**

```
Professional photorealistic hero image for a local HVAC contractor
in [CITY]. Wide cinematic crop, natural light, depth of field.
Subject: a technician in unbranded work uniform servicing an
outdoor AC condenser unit, OR a close-up of a clean high-efficiency
furnace installation. NO text, NO logos, NO faces clearly visible,
no people wearing branded apparel from any specific company.
```

Why no faces / branded apparel: same reasoning as plumber section
-- the same image gets reused across multiple prospects in this
trade, and we don't want any prospect to feel the photo is "of
someone else's business."

### Page set for MVP

Single page (`index.html`) containing all sections above. Same
constraint as plumber. Multi-page (services subpages, individual
service detail pages, blog) is v2.

### Theme

HVAC sites default to theme = `warm` (same as plumber and most
local trades). Override to `civic` only if the prospect's brand is
explicitly cool/clinical, OR to `minimal` for commercial HVAC
operations that want a professional-services feel (less common in
the rural residential profile we're targeting).

### Color defaults

If prospect provided brand colors, use them. If not:
- Accent: **HVAC industry blue** (`#1E5BB8`) -- cool, professional,
  associated with cooling/comfort
- Accent-dark: `#164B96` (darker variant for hover states)
- Secondary: red-orange (`#D9534F`) -- emergency/urgency signal,
  reserved for "no heat" / "no AC" emergency CTAs only
- Background: white (light theme)

The blue/red-orange split intentionally parallels the cool/hot
duality of HVAC services (cooling = blue, heating = red). This
differs from the plumber default (red-orange dominant) because
plumber visits are uniformly urgent while HVAC is split between
urgent comfort failures and planned high-ticket installs.

Apply the COLOR DISCIPLINE rule from `02-redesign-gen-prompt.md`:
accent appears on AT MOST 3-4 elements (primary CTA, sticky phone,
one badge). The secondary red-orange is reserved for emergency
CTAs only -- not used as a general accent.
