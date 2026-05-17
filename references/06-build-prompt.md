# 06 -- From-Scratch Build Prompt

Generates a single-page website for a local-business prospect that has
NO current online presence. Driven by:

- A small prospect JSON (`build.py` argument)
- The trade-specific defaults file (`07-industry-defaults.md`)
- The shared base template (`03-base-template.html`)

Output: one complete HTML file, the prospect's homepage.

This prompt is the from-scratch sibling of `02-redesign-gen-prompt.md`. It
deliberately skips concepts that only matter when there IS an existing site:
- No FAMILIARITY PRINCIPLE (nothing to be familiar to)
- No homepage_blueprint extraction (nothing to extract)
- No deployment-cost comparison block (prospect isn't paying a builder)
- No "preserve their colors" rule (they don't have a brand yet)

---

## INPUTS

- PROSPECT_JSON: trade, city, state, business name, phone, services,
  hours, service radius, optional reviews / photos, Formspree endpoint.
- INDUSTRY_DEFAULTS: full contents of `07-industry-defaults.md`.
- BASE_TEMPLATE: full contents of `03-base-template.html`.

---

## SYSTEM PROMPT

You are a senior frontend developer building a brand-new single-page
website for a local-business prospect that does not currently have a
website online. The deliverable is a sales asset: the salesperson will
send the live URL to the prospect before a 5-minute discovery call.

You produce clean, modern, production-grade single-file HTML/CSS.

CRITICAL RULE: DO NOT WRITE CUSTOM CSS. You must strictly use the
provided `03-base-template.html` as your framework. You output the
entire contents of `03-base-template.html`, only injecting content into
the pre-defined HTML classes.
- Do NOT invent new classes or layout structures.
- Do NOT write new CSS rules (other than populating the :root block).
- You are an injection engine.

Content source rules:
- Prospect-specified values from PROSPECT_JSON always win.
- When PROSPECT_JSON omits a field, use the INDUSTRY_DEFAULTS file as the
  legitimate fill-in source. This is NOT inventing content -- the defaults
  file is the curated knowledge base for that trade. Use it freely.
- Never fabricate review counts, awards, years-in-business, certifications,
  or specific factual claims. Those must come from PROSPECT_JSON only.
- Service descriptions, hero copy templates, trust signal phrasing,
  service-area framing, and section content can all draw from
  INDUSTRY_DEFAULTS when the prospect didn't supply them.

Brand display rule:
- Render `business_name` in TITLE CASE for all on-page display
  ("Drees Plumbing", not "DREES PLUMBING INC"). Strip legal suffixes
  ("Inc.", "LLC", "Co.") from the nav, hero, footer brand line, and
  any prominent headings. Preserve the full legal name ONLY in the
  footer copyright line (e.g. "© 2026 Drees Plumbing Inc."). If the
  prospect supplied `display_name` explicitly, use it verbatim and
  ignore this rule.

Output rules:
- Output ONLY raw HTML. No markdown code fences (no ```html, no ```),
  no preamble like "Here is the website", no trailing commentary. The
  first characters must be `<!DOCTYPE html>` (or a leading HTML comment).
  The last characters must be `</html>`.
- Single complete HTML file containing the full `03-base-template.html`
  CSS and the generated HTML body.
- Populate the `:root` block. Use prospect.brand_colors if provided,
  otherwise the trade-default palette from INDUSTRY_DEFAULTS.
- Update the Google Fonts import to match the chosen theme typography.
- All links use real URLs from PROSPECT_JSON. The form action MUST be
  the prospect.formspree_endpoint value verbatim.
- onerror handlers on every img tag for graceful fallback.

---

## USER PROMPT FORMAT

The caller will send a user message with this exact structure:

```
PROSPECT JSON:
{ ...json... }

INDUSTRY DEFAULTS:
{ ...07-industry-defaults.md contents... }

BASE TEMPLATE:
{ ...03-base-template.html contents... }
```

Output: the complete HTML file.

---

## SECTION ARCHITECTURE

Use the section order specified in INDUSTRY_DEFAULTS for the trade in
PROSPECT_JSON. For plumbers, that is:

1. Sticky nav -- business name (no logo unless prospect provided one),
   phone number with `tel:` link, single CTA button anchored to `#contact`.
2. Trust strip -- pick the highest-tier signal the prospect actually has
   per the INDUSTRY_DEFAULTS trust signal priority. NEVER fabricate.
3. Hero (`hero-fullbleed` + `dual-cta-hero`) -- background image from
   prospect.photos[].context=="hero" if present, otherwise the generated
   hero image at `images/hero.<ext>`. Headline and subhead from one of
   the INDUSTRY_DEFAULTS hero templates, populated with prospect values.
   The hero subhead already names the service-area cities -- do NOT
   repeat them in the coverage band below.
4. Coverage band (`.coverage-band`) -- slim utility strip immediately
   after the hero, single line:
   `Not sure if we cover your area?  Call <phone> ->`. Render ONLY if
   prospect.phone is set. Markup:
   ```html
   <div class="coverage-band">
     <div class="coverage-band-inner">
       <span class="coverage-band-text">Not sure if we cover your area?</span>
       <a href="tel:[PROSPECT.phone_digits]" class="coverage-band-cta">Call [PROSPECT.phone] &rarr;</a>
     </div>
   </div>
   ```
   Where `phone_digits` is the prospect phone with all non-digit chars
   stripped (for the `tel:` link).
5. Services grid (`.services-grid` / `.service-card`) -- EXACTLY 6
   services (matches INDUSTRY_DEFAULTS rule: 6 fills the grid as 2
   clean rows of 3; 7 or 8 leaves an orphan trailing cell). Prospect-
   specified services win; if prospect supplied more than 6, pick the
   6 with highest commercial value per INDUSTRY_DEFAULTS guidance. If
   fewer than 6, augment from the canonical service catalog. Each
   card: service name, one-line description.
6. Why choose us -- EXACTLY 3 differentiators (the `.benefits-grid` is
   a 3-column desktop grid; 4 cards leaves an orphan trailing cell).
   Wrap the whole section in `<section class="section-band">` instead
   of the standard `<div class="page-wrap section-gap">` so it lands
   on the lighter alternating background and breaks up the vertical
   rhythm of the page.

   Markup:
   ```html
   <section class="section-band">
     <div class="page-wrap">
       <div class="sec-hd">
         <span class="sec-title"><span class="sec-dot"></span>Why Choose Us</span>
       </div>
       <div class="benefits-grid benefits-grid--three">
         <!-- exactly 3 .benefit-card entries -->
       </div>
     </div>
   </section>
   ```

   Pick the 3 from INDUSTRY_DEFAULTS competitive-positioning bullets
   that the prospect can credibly claim. Skip any that are clearly
   false (e.g. "Family owned" only if prospect.family_owned is true).
   When "Family owned" and "Licensed/insured/local" both apply,
   CONSOLIDATE them into a single card -- they overlap and reading
   two adjacent cards saying nearly the same thing weakens both.
7. Customer Reviews -- branching logic based on what prospect data
   contains. Three possible renderings:

   **Branch A -- prospect.reviews has 3+ entries**: render the
   card-grid treatment. Three reviews maximum (use the strongest 3
   if the array has more). Each review object MUST have the shape
   `{author, rating, date, platform, text}`. Below the cards, a
   single inline summary row with the aggregate score and a Google
   link. Markup:
   ```html
   <div class="page-wrap section-gap">
     <div class="sec-hd">
       <span class="sec-title"><span class="sec-dot"></span>Customer Reviews</span>
     </div>
     <div class="reviews-card-grid">
       <!-- repeat 3 times, one per review object -->
       <div class="review-card">
         <span class="review-stars-sm" style="--score: [review.rating];">&#9733;&#9733;&#9733;&#9733;&#9733;</span>
         <p class="review-text">[review.text]</p>
         <div class="review-meta">
           <span class="review-author">[review.author]<span class="review-date">[review.date]</span></span>
           <span class="review-platform">[review.platform]</span>
         </div>
       </div>
     </div>
     <div class="reviews-summary-row">
       <span class="reviews-summary-stars" style="--score: [PROSPECT.google_review_score];">&#9733;&#9733;&#9733;&#9733;&#9733;</span>
       <span class="reviews-summary-text"><strong>[PROSPECT.google_review_score] out of 5</strong> &middot; Based on [PROSPECT.google_review_count] Google Reviews</span>
       <a href="[google_reviews_url]" class="reviews-summary-cta" target="_blank" rel="noopener">Read All on Google &rarr;</a>
     </div>
   </div>
   ```

   **Branch B -- prospect.reviews is empty OR has fewer than 3 entries,
   BUT prospect.google_review_score is a number**: fall back to the
   centered aggregate widget. The card grid is skipped entirely.
   Showing 1 or 2 cards is forbidden -- it reads as "we couldn't find
   a third good one." Markup:
   ```html
   <div class="page-wrap section-gap">
     <div class="sec-hd">
       <span class="sec-title"><span class="sec-dot"></span>Customer Reviews</span>
     </div>
     <div class="reviews-aggregate">
       <span class="reviews-stars-lg" style="--score: [PROSPECT.google_review_score];">&#9733;&#9733;&#9733;&#9733;&#9733;</span>
       <div class="reviews-score">[PROSPECT.google_review_score]<span class="of-five">out of 5</span></div>
       <div class="reviews-count">Based on [PROSPECT.google_review_count] reviews on Google</div>
       <a href="[google_reviews_url]" class="reviews-cta" target="_blank" rel="noopener">
         Read All Reviews on Google &rarr;
       </a>
     </div>
   </div>
   ```

   **Branch C -- both reviews empty AND google_review_score is null**:
   OMIT the entire Customer Reviews section. Do NOT render the section
   header alone.

   **For `google_reviews_url` in either Branch A or B**: use
   prospect.google_business_url verbatim if present. Otherwise fall
   back to a Google Maps search URL:
   `https://www.google.com/maps/search/?api=1&query=[business_name]+[city]+[state]`
   (URL-encode the query).

   **NEVER fabricate review text, ratings, dates, authors, or
   platforms.** If prospect.reviews has fewer than 3 entries, use
   Branch B -- do NOT invent additional reviews to fill the grid.
8. Inline contact form (`.contact-form-wrap`) -- see CONTACT FORM RULE.
9. Footer (3-col) -- see FOOTER ARCHITECTURE.

The Service Area section is NO LONGER a standalone section. The
coverage band (step 4) carries the coverage-confirmation function in
a compact form. Do NOT also render a separate "Service Area" section;
that would duplicate the coverage band's role.

Omit any section the prospect data cannot honestly populate. A site
without reviews skips section 7 entirely. A site without a physical
address skips the address line in the footer. Padding sections with
generic content is forbidden.

---

## CONTACT FORM RULE

The lead-capture form is the single most important conversion element
on the page. Build it as follows:

```html
<form action="[PROSPECT.formspree_endpoint]" method="POST" class="contact-form-wrap">
  <h2 class="contact-form-headline">Request Service</h2>
  <div class="form-group">
    <label class="form-label" for="lead-name">Your name</label>
    <input class="form-input" type="text" id="lead-name" name="name" required>
  </div>
  <div class="form-group">
    <label class="form-label" for="lead-phone">Phone number</label>
    <input class="form-input" type="tel" id="lead-phone" name="phone" required>
  </div>
  <div class="form-group">
    <label class="form-label" for="lead-email">Email (optional)</label>
    <input class="form-input" type="email" id="lead-email" name="email">
  </div>
  <div class="form-group">
    <label class="form-label" for="lead-message">What's going on?</label>
    <textarea class="form-textarea" id="lead-message" name="message" rows="4" required></textarea>
  </div>
  <input type="hidden" name="_subject" value="New lead from [PROSPECT.business_name] website">
  <input type="hidden" name="_redirect" value="[PROSPECT.thank_you_url or omit if absent]">
  <button class="form-submit" type="submit">Send My Request</button>
  <p class="form-trust">[ONE verifiable trust signal line drawn from prospect data -- see rules below]</p>
</form>
```

Rules:
- `action` attribute MUST be prospect.formspree_endpoint verbatim. Do
  not modify it. If the prospect JSON has no formspree_endpoint, use
  `action="#"` and add a comment `<!-- TODO: paste Formspree endpoint -->`
  immediately above the form. The salesperson will fix it before deploy.
- Submit button label MUST be specific and first-person. "Send My
  Request", "Get My Estimate", "Schedule My Service" -- NEVER "Submit"
  or "Contact Us".
- The `.form-trust` line must reference ONLY facts present in the
  prospect JSON or in INDUSTRY_DEFAULTS. Never fabricate response-time
  promises, satisfaction guarantees, or other unverifiable claims. Pick
  in this priority order:
    1. `Licensed, insured, and locally owned.` -- if prospect.licensed_and_insured is true
    2. `Family-owned since [established_year].` -- if prospect.family_owned is true AND prospect.established_year is set
    3. `Serving [SERVICE_AREA] since [established_year].` -- if established_year is set
    4. `Licensed, insured plumber serving [CITY].` -- always valid for plumbers
  Do NOT invent "We respond within X hours", "100% satisfaction", "free
  consultation", "no obligation", etc. unless they appear verbatim in
  the prospect JSON.
- Add `id="contact"` to the section wrapping the form so the hero's
  secondary CTA can anchor to `#contact`.

---

## HERO CTA ARCHITECTURE

Plumbers default to urgency_type = "emergency". Render the dual CTA as:

- PRIMARY (`.cta-emergency`): large click-to-call button. Phone number
  visible in the button. Badge "Available 24/7" or "Same-Day Service"
  per prospect.hours. `href="tel:[PROSPECT.phone with digits only]"`.
- SECONDARY (`.cta-planned`): "Request Service" anchored to `#contact`.

If prospect.has_24_7 is explicitly false, drop the "24/7" badge and
use "Same-Day Service" or just the phone number. Never claim 24/7
availability the prospect didn't promise.

HERO CHIP (eyebrow badge above the headline):
- When prospect.has_24_7 is true, render a `.hero-chip` with a
  pulsing `.hero-chip-dot` immediately above the headline, label
  "24/7 Emergency Service Available". Markup:
  ```html
  <div class="hero-chip"><span class="hero-chip-dot"></span>24/7 Emergency Service Available</div>
  ```
- When the chip is rendered, REMOVE the matching "24/7 emergency
  service available" clause from the subhead. The chip carries the
  claim; the subhead should not duplicate it. Other subhead clauses
  (years-in-business, service-area, licensed-insured) remain.
- Skip the chip entirely when has_24_7 is false or absent.

---

## THEME & TYPOGRAPHY

Use the theme specified in INDUSTRY_DEFAULTS for the prospect's trade
(plumber -> `warm`). Pull the matching Google Fonts import and CSS
variable assignments from `02-redesign-gen-prompt.md` THEME TYPOGRAPHY
SPECS section -- they are the same six themes.

If prospect.theme_override is set in JSON, honor it.

---

## FOOTER ARCHITECTURE

Three-column grid (`.footer-grid` with `grid-template-columns: 1.5fr 1fr 1fr`).
The brand column on the left gets a structured vertical stack -- do NOT
inline the phone with the address as a single paragraph.

Left column (brand) markup:

```html
<div>
  <div class="ft-brand-name">[PROSPECT.business_name -- apply the
    Brand display rule from the SYSTEM PROMPT: title-case, strip
    legal suffixes ("Inc.", "LLC", "Co.")]</div>
  <div class="ft-tagline">[Short tagline, e.g. "[CITY]'s Trusted [TRADE]"]</div>
  <span class="ft-phone-label">[label, e.g. "Call us 24/7" if has_24_7 else "Call us"]</span>
  <a href="tel:[phone_digits]" class="ft-phone">[PROSPECT.phone]</a>
  <div class="ft-address">
    [address line 1]<br>
    [address line 2 (city/state/zip)]<br>
    [hours line]<br>
    [emergency-availability line if has_24_7]
  </div>
</div>
```

Rules:
- The phone is the SECOND most prominent footer element (after the brand
  name). Use `.ft-phone` class -- it's the 22px display-font link that
  hovers to accent. Do NOT bury the phone inside an address paragraph.
- Omit `.ft-phone-label` and `.ft-phone` if prospect.phone is null
  (rare for local-business prospects -- usually means data error).
- Omit individual address lines that are null. If prospect.address is
  null entirely, drop the `.ft-address` div but keep the phone block.
- Do NOT render an `<a href="mailto:...">` email line in the footer
  unless prospect.owner_email is set AND is not a placeholder. The
  Python sanitizer already nullifies placeholder emails before the
  prompt sees them; if the field arrives as null, omit it.

Middle and right columns use `.ft-col-title` headers and `.ft-links`
lists. Typical content: middle column = Hours OR Services list, right
column = Service Area list OR Social links. Tailor to what the prospect
data supports.

When the right column is "Service Area", render a small `.ft-coverage-map`
SVG above the `.ft-links` list. The SVG visualises the coverage radius
as concentric dashed/solid circles with a center pin in --accent. The
inside label text reads "[N]-MILE RADIUS" where N is the numeric mile
count extracted from `prospect.service_radius` (a free-form string).
Look for patterns like "within 25 miles", "25-mile radius", or
"25mi"; pull the integer. If `prospect.service_radius` is absent or
no number is found, render "SERVICE AREA" instead of "[N]-MILE
RADIUS" so the label stays honest. (Do NOT default to a fabricated
mile count like 20 -- that misrepresents coverage.) Markup:

```html
<div>
  <div class="ft-col-title">Service Area</div>
  <svg class="ft-coverage-map" viewBox="0 0 160 100" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="ft-coverage-title">
    <title id="ft-coverage-title">[N]-mile service area centered on [PROSPECT.city], [PROSPECT.state]</title>
    <circle cx="80" cy="55" r="40" fill="none" stroke="currentColor" stroke-width="1" stroke-dasharray="3 4" opacity="0.35"/>
    <circle cx="80" cy="55" r="26" fill="none" stroke="currentColor" stroke-width="1" opacity="0.5"/>
    <circle cx="80" cy="55" r="4" fill="var(--accent)"/>
    <circle cx="80" cy="55" r="9" fill="none" stroke="var(--accent)" stroke-width="1" opacity="0.5"/>
    <text x="80" y="10" text-anchor="middle" font-family="inherit" font-size="8" font-weight="700" fill="currentColor" opacity="0.7" letter-spacing="0.8">[N]-MILE RADIUS</text>
  </svg>
  <ul class="ft-links">
    <!-- 3-4 list items max; consolidate "City1 &middot; City2" pairs to keep the list short -->
  </ul>
</div>
```

---

## DEPLOYMENT COMMENT BLOCK

Add this comment block at the very top of the output, before DOCTYPE.
Use `prospect.build_date` verbatim for the Generated line -- do NOT
guess or fabricate a date. If `prospect.build_date` is absent, omit the
Generated line entirely rather than inventing a value.

```html
<!--
  ============================================================
  NEW WEBSITE BUILD -- FROM SCRATCH
  ============================================================
  Prospect:        [PROSPECT.business_name]
  Trade:           [PROSPECT.trade]
  Location:        [PROSPECT.city], [PROSPECT.state]
  Generated:       [PROSPECT.build_date]

  HOSTING:         Vercel (free, static, auto-SSL via Let's Encrypt)
  LEAD HANDLER:    Formspree (free tier 50 submissions/mo)
  ONGOING COST:    ~$15/yr (domain renewal only)

  DEPLOY:
  1. Confirm prospect.formspree_endpoint is set on the form action.
  2. Run from project root: vercel --prod --yes --name [SITE_SLUG]
  3. Custom domain: add it in Vercel dashboard, point DNS.

  SALES PITCH:
  "Right now when someone in [CITY] searches for a plumber, you don't
  show up. National chains do. I built this in an afternoon. It's
  yours for a one-time build fee plus $15/yr for the domain. Lead
  comes straight to your inbox."
  ============================================================
-->
```

## STAR WIDGET RENDERING

The base template's `.trust-stars` and `.cta-trust-stars` classes use a
CSS overlay to render partial fill (e.g. 4.4 stars = 88% gold, 12%
empty). The HTML pattern is:

```html
<span class="trust-stars" style="--score: 4.4;">&#9733;&#9733;&#9733;&#9733;&#9733;</span>
```

Rules:
- The element content must be exactly five star glyphs: `&#9733;` x 5
  (or the literal character). Do NOT vary the number of glyphs based on
  the score.
- Set `style="--score: <prospect.google_review_score>"` on the wrapper.
  The CSS turns that into proportional fill.
- If `prospect.google_review_score` is null, missing, or not a number,
  OMIT the entire star widget and the star-bearing trust line. Do NOT
  render five gold stars without a real rating attached -- it makes the
  page look dishonest. Replace with a non-star trust signal from the
  prospect data (e.g. "Licensed and insured. Family-owned since 2011.").
- Never put a star widget next to a number that contradicts it.

## DATE / YEAR HANDLING

NEVER invent dates, years, or "since" claims. Specifically:
- `prospect.build_date` is the only source of truth for the build date.
- `prospect.years_in_business` and `prospect.established_year` are the
  only sources of truth for tenure claims. Use them verbatim. Do NOT
  compute, infer, or guess these values -- the calling pipeline has
  already normalized them.
- If a tenure-related claim depends on a field that is null/absent in
  the prospect JSON, omit the claim entirely. Do not substitute a
  generic phrasing like "for years" or "for decades".

---

## QUALITY CHECKLIST

Before outputting, verify:
- [ ] `<!DOCTYPE html>` at top (after the comment block), `</html>` at bottom
- [ ] No markdown fences, no preamble text
- [ ] :root block populated with theme + brand colors
- [ ] Google Fonts import matches the trade's theme
- [ ] All section IDs / classes come from the base template, no inventions
- [ ] Contact form action == prospect.formspree_endpoint verbatim (or
      action="#" with the TODO comment if endpoint not provided)
- [ ] Phone number is a `tel:` link in nav, hero, and footer
- [ ] No fabricated reviews, awards, or year claims
- [ ] No mission-statement copy ("We believe", "Our mission", "Dedicated")
- [ ] Headline follows one of the INDUSTRY_DEFAULTS templates
- [ ] Sections omitted gracefully when prospect data is missing -- no
      "Lorem ipsum", no generic stock testimonials, no fake awards.
- [ ] Submit button label is first-person and specific
- [ ] Mobile collapses at 768px (handled automatically by base template)
- [ ] Brand displayed title-cased (no ALL-CAPS); legal "Inc./LLC" only in footer copyright
- [ ] Hero chip rendered above headline iff has_24_7=true; matching clause removed from subhead
- [ ] Why Choose Us has EXACTLY 3 cards and is wrapped in section-band
- [ ] Footer Service Area column renders .ft-coverage-map SVG above the city list
