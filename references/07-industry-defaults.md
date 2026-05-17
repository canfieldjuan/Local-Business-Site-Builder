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
beats "we're available 24/7" on credibility, and 24/7 still gets named
in the subhead. Trying to out-emergency Roto-Rooter in the headline is
a losing position for a local plumber; trying to out-trust them on
locality and tenure is winnable.

- Headline: `[CITY]'s Trusted Plumber Since [YEAR]`
- Subhead (24/7 yes): `[YEARS] years of plumbing repair, replacement, and installation across [SERVICE_AREA]. 24/7 emergency service available. Licensed, insured, family-owned.`
- Subhead (24/7 no): `[YEARS] years of plumbing repair, replacement, and installation across [SERVICE_AREA]. Licensed, insured, family-owned. Free estimates.`

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

### Image generation prompts

Default hero prompt template:
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
