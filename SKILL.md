---
name: website-redesign
description: Complete pipeline for creating professional website redesign mockups for local businesses and organizations. Use this skill whenever someone wants to redesign a website, create a mockup for a client, modernize an existing site, or pitch a web design service. Triggers when a user shares a URL and wants a redesigned version, mentions website builder platforms (Wix, Squarespace, GoDaddy), asks how to show prospects what their new site could look like, or wants to generate a multi-page site mockup. Also use when the user asks to "redo", "freshen up", "modernize", or "rebuild" any website.
---

# Website Redesign Pipeline

Full pipeline for producing professional local business website redesigns:
fetch a site, extract its content and brand, generate a modern HTML mockup
preserving the owner's brand identity, deploy to Vercel as a live sales demo.

Outputs are self-contained HTML files -- free static hosting on Vercel,
free SSL via Let's Encrypt, client's only ongoing cost is their domain (~$15/yr).

---

## Quick Start (single URL, homepage only)

1. `web_fetch` the URL
2. Read `references/01-site-analysis-prompt.md`, run analysis, get JSON
3. Read `references/02-redesign-gen-prompt.md`, pick theme, generate HTML
4. Save to `/mnt/user-data/outputs/[site-slug]-homepage.html`
5. `present_files` the result

That covers the majority of requests. Continue below for interior pages,
multi-page deliverables, and platform-specific sales pitch generation.

---

## Full Pipeline

### Step 1 -- Fetch and Analyze

```
web_fetch(url)
```

Read `references/01-site-analysis-prompt.md` in full, then use it to analyze
the fetched content. Return structured JSON covering:
- Site identity, contact info, nav structure
- Brand colors (extracted from CSS/inline styles -- be aggressive here)
- All content sections with items verbatim
- `site_structure`: multi-page | single-page | mixed
- `pages_to_fetch` with `fetchable` boolean per page
- `conversion_profile` with urgency_type, primary_goal, trust_signals
- `platform.detected` for cost calculation

**Color extraction is critical.** The redesign must preserve brand colors.
Pull every hex/rgb value found anywhere in the HTML. Quantity over quality.

### Step 2 -- Select Theme

Read `references/02-redesign-gen-prompt.md` THEME REFERENCE table.
Match theme to site type:

| site.type              | default theme    |
|------------------------|-----------------|
| radio / news           | broadcast       |
| restaurant / cafe      | warm            |
| home-services / trades | broadcast       |
| legal / medical        | editorial       |
| civic / church         | civic           |
| retail / ecommerce     | warm            |
| portfolio / services   | minimal         |
| entertainment / events | brand-forward   |

COLOR_MODE should almost always be `brand` -- use extracted colors, not theme defaults.
Override only when the brand has no usable colors (e.g. site is pure white with no accent).

### Step 3 -- Generate Homepage

Read `references/02-redesign-gen-prompt.md` in full before generating.

Key rules:
- Paste :root token block built from brand colors -- no theme placeholder colors
- Above the fold: headline (service + location), dual CTAs, trust strip
- Dual CTA pattern from `conversion_profile.urgency_type`
- Section order from industry priority table matching `site.type`
- Trust signals near every CTA, not isolated on one page
- All headlines verbatim from analysis JSON
- All image src from analysis JSON with onerror handlers
- Include deployment comment block at top (see DEPLOYMENT BLOCK section in ref 02)

Save output to `/mnt/user-data/outputs/[site-slug]-homepage.html`

### Step 4 -- Interior Pages (optional, high value for sales)

Check `site_structure` from the JSON:

**multi-page**: fetch priority 1-2 pages from `pages_to_fetch` where `fetchable: true`
**single-page**: use `single_page_sections` -- no additional fetching needed
**mixed**: fetch where fetchable, use sections where not

Read `references/04-interior-page-prompt.md` for each page.
Recommended set for a full revamp demo: contact + about + one service page.

Save each to `/mnt/user-data/outputs/[site-slug]-[page-type].html`

### Step 5 -- Present and Pitch

`present_files` all generated HTML files together.

After presenting, give the client the deployment one-liner:
> "Drag any of these files to vercel.com/new -- live HTTPS URL in 30 seconds.
> Send that URL to the prospect before the sales call."

---

## Platform Cost Reference

Used to populate the deployment comment block in each HTML file.
The comment block auto-generates the annual cost comparison and sales pitch copy.

| Detected platform    | Typical annual cost | Key pain point                         |
|----------------------|--------------------|-----------------------------------------|
| wix (Core)           | ~$363/yr           | $29/mo + $15 domain, locked in template |
| wix (Business)       | ~$483/yr           | $39/mo + apps add $10-50/mo extra       |
| squarespace          | ~$207/yr           | $16/mo, design-locked, hard to migrate  |
| godaddy-builder      | ~$240/yr           | Renewal doubles after year 1            |
| traditional-hosting  | ~$350/yr           | Separate hosting + $200 SSL + domain    |
| wordpress-hosted     | ~$180/yr           | Plugins, maintenance, security overhead |

Vercel comparison: $0/yr hosting + $0 SSL + ~$15/yr domain = **~$15/yr total**

---

## Theme Typography Reference

Each theme requires a specific Google Fonts import and font stack.
Read `references/02-redesign-gen-prompt.md` THEME TYPOGRAPHY SPECS section
for the exact import URL and CSS variable values per theme.

---

## Site Structure Handling

### Single-page sites (Wix, Squarespace one-pagers, hand-coded)

Nav links use `#anchor` syntax or all resolve to the same base URL.
`site_structure` will be `single-page`.

Interior pages come from `single_page_sections` in the analysis JSON.
This is all the content available -- extract it thoroughly in step 1.
A sparse contact section (just phone + address) still makes a clean contact page.
Never invent content to fill gaps.

### Multi-page sites

`pages_to_fetch` contains real URLs with `fetchable: true`.
`web_fetch` each priority 1-2 page, run through `references/04-interior-page-prompt.md`.

---

## Deployment Instructions (give to client)

```
1. Go to vercel.com/new (free account)
2. Drag and drop the HTML file -- no config needed
3. Vercel gives you a .vercel.app subdomain instantly
4. HTTPS/SSL is automatic -- no setup, no annual fee
5. For a custom subdomain: add it in Vercel dashboard, point DNS
6. Only ongoing cost: domain renewal (~$15/yr at Namecheap or Porkbun)
```

For a preview subdomain during the sales process:
- Buy one domain like `preview.youragency.com` ($15 once)
- Each client mockup gets `clientname.preview.youragency.com`
- Share the live URL via text before the sales call:
  `"I redesigned [Business Name] -- take a look: [URL]"`

---

## Reference Files

| File | Purpose | When to read |
|------|---------|--------------|
| `references/01-site-analysis-prompt.md` | System + user prompt for extracting structured JSON from fetched HTML | Step 1, every time |
| `references/02-redesign-gen-prompt.md` | Full generation prompt with theme specs, conversion rules, deployment block | Step 3, every time |
| `references/03-base-template.html` | Complete CSS component library with all layout patterns | When building a page from scratch or debugging a component |
| `references/04-interior-page-prompt.md` | Interior page generation for contact, about, services, single-service, FAQ, menu | Step 4, for each interior page |

All four files must be read before their respective step -- do not skip.
The reference files contain the full prompt text, CSS patterns, and component specs
needed to produce production-quality output.
