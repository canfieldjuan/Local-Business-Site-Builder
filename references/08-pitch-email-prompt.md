# 08 -- Pitch Email Draft Prompt

Used by `build.py` (the from-scratch build pipeline) AND by the
`local-business-build` Claude Code skill to generate a Day-1 pitch
email draft alongside the generated site. The draft is written to
`outputs/builds/<slug>/email_draft.md` for the salesperson to review,
edit, and send manually from their own email client.

**No auto-send. No follow-up emails in this prompt.** The follow-up
"demo customer request" email is a future addition.

---

## AUDIENCE

Small-trade business owners (plumbers, electricians, HVAC, roofers,
landscapers, etc.) who have been in business 5-25 years without a
website. Survived on referrals, repeat customers, and a yellow-pages
Google Business Profile listing. They have a phone, they have work
booked out 2-4 weeks, they're skeptical of anyone selling them
"digital presence."

They will read the email on a phone, between jobs, in <30 seconds.
If the email reads like an agency cold-pitch, they delete and never
look at the URL. The voice is what makes the click happen, not the
URL itself.

---

## VOICE RULES (HARD)

**The voice is peer-to-peer, plain-spoken, economical.** Imagine a
neighbor who happens to build websites tapping you on the shoulder.
Not a sales rep. Not a consultant. Not a brand. A person.

**Do NOT use any of these phrases or anything close to them**:
- "elevate your brand"
- "modernize your online presence"
- "digital transformation"
- "value proposition"
- "synergies"
- "I noticed your business is amazing"
- "I'd love to chat" / "would love to connect"
- "we help businesses like yours"
- "let's hop on a call"
- "exciting opportunity"
- "next-level" / "10x your business" / "crushing it"
- Generic flattery of any kind ("great reputation", "stellar reviews")
- "transform" / "optimize" / "leverage"

**DO use**:
- The owner's first name if known. Otherwise no salutation -- start
  cold with the offer.
- Specific facts you know: city, trade, years in business, review
  score, name of one service they're known for. Verbatim from prospect.
- One verifiable observation about the prospect's own reachability --
  the fact that they have no website / no contact form / nowhere
  online for a customer to land outside this new build. Do NOT make
  observations about competitor rankings, national chains, SERP
  layouts, or anything you cannot verify without checking Google
  yourself for that exact query in that exact city.
- The live Vercel URL as the lead-in to action. The URL replaces 80%
  of the sales pitch -- they click, they see, they decide.
- An explicit "no follow-up unless you say so" exit clause. Lowers
  defenses, makes the click more likely.

**Length**: 4-6 short sentences total, including signature. Under
100 words. Anything longer gets skimmed and dismissed.

**Subject line**: 6-9 words (must be UNDER 10). The business name +
a hook. Not clickbait. Examples:
- "Built a website for Drees Plumbing"
- "A free draft for [Business Name]"
- "Quick look -- new site for [Business Name]"
NEVER use "Re:" prefix on a cold email (it's a manipulation
prospects recognize immediately).

---

## DATA-DRIVEN VARIANT LOGIC

The email pulls from prospect data when available, gracefully omits
when not. The hooks below are listed in priority order; use the
strongest available, do NOT stack more than two of them.

| Hook | Trigger | Example phrasing |
|---|---|---|
| Longevity | `years_in_business >= 10` | "You've been at this for [N] years without a website. The work speaks for itself." |
| Review score | `google_review_score >= 4.0` AND `google_review_count >= 5` | "Your [SCORE]/5 from [COUNT] Google reviews tells me people who find you are happy. I'd like more of them finding you." |
| Discoverability | Last-resort fallback ONLY if no other hook triggers. NEVER make claims about specific SERP positions, competitor rankings, the number of results, or what national chains are doing in any city. NEVER claim the prospect has "no phone to tap" -- the prospect JSON requires a phone number and the prospect may also have a Google Business Profile that already exposes their phone publicly. | "Right now, anyone who searches for [BUSINESS NAME] online has nowhere of yours to land -- no site to read, no form to fill out at 10pm. This gives them one." (Stick to verifiable absences only: no website, no contact form. Do NOT claim the prospect lacks a phone, a Google listing, or any other channel you have not confirmed is absent. Do NOT describe what Google shows or what competitors rank for -- those are unverifiable SERP claims and violate the fabrication guard below.) |
| 24/7 availability | `has_24_7: true` | "I noticed you're 24/7. People searching at 11pm need to find you fast -- the phone in the hero is one tap on mobile." |
| Family-owned | `family_owned: true` | "Made the family-owned thing obvious throughout -- not buried in fine print." |

**Fabrication guards**:
- NEVER claim specific review text or specific customer stories. The
  prospect's reviews are listed in the JSON; the email can reference
  the aggregate (score + count) but should not paraphrase any single
  review.
- NEVER invent competitive facts. Do NOT name specific national
  chains (Roto-Rooter, Mr. Rooter, Stanley Steemer, etc.), do NOT
  claim a specific number of search results, do NOT describe what
  Google shows for any query, and do NOT promise the new site will
  rank above any competitor. "Generally true" national-chain
  observations are still unverified for this specific prospect's
  city and query -- treat them as fabricated and reject them.
- NEVER claim metrics about their business you don't have ("your
  customers" can be reasonable; "the X customers you served last
  year" is fabricated).
- NEVER promise outcomes ("you'll get more leads", "this will rank
  on page 1") -- the email's job is to get them to click, not to
  close the sale.

---

## EMAIL TEMPLATE

The email_draft.md output should contain THREE distinct sections,
clearly delineated for the salesperson:

1. **Subject line** at the top, prefixed `Subject:`
2. **To/From hints** (optional, for the salesperson's reference)
3. **Body** -- plain text, no markdown formatting

### Subject line

Pick a template, then COUNT the words in the resulting subject. If
the total is 10 or more words, fall back to a shorter template. The
hard ceiling is 9 words.

Templates in order of preference:

1. `Built a [TRADE] website for [BUSINESS_NAME_TITLE_CASE]` -- default
   (works when the business name is 1-4 words after suffix-stripping)
2. `A free draft for [BUSINESS_NAME_TITLE_CASE]` -- 4 fixed words +
   business name; works for business names up to 5 words
3. `[BUSINESS_NAME_TITLE_CASE] -- new website` -- 2 fixed words +
   business name; works for business names up to 7 words
4. `Quick look: [BUSINESS_NAME_TITLE_CASE]` -- 2 fixed words +
   business name; works for business names up to 7 words

ALGORITHM:
- Start with template 1. Count words. If <= 9, use it.
- If > 9, try template 2, then 3, then 4 in that order.
- All four templates above will produce a <= 9-word subject for any
  business name up to 7 words. If the business name itself exceeds
  7 words (rare), use template 3 or 4 and truncate the business
  name at a natural word boundary (e.g. drop trailing words like
  "Services", "Solutions", "Company") rather than mid-word.

Apply the brand display rule from `06-build-prompt.md`: title-case
the business name, strip legal suffixes ("Inc.", "LLC", "Co.")
BEFORE counting words.

### Body structure

```
[Owner first name if known, otherwise no salutation] [single em-dash or comma]

[One opener sentence: what you did. Include business name + city.
Live URL on its own line.]

[VERCEL_URL_PLACEHOLDER]

[One or two sentences: the offer + one strongest hook from the
table above. Be specific. Don't oversell.]

[One sentence: explicit exit / no-follow-up clause.]

[Sign-off + first name]
```

### Worked example (Drees Plumbing, 15 years, 4.4 from 12 reviews, has_24_7, family-owned, Effingham IL)

```
Subject: Built a plumbing website for Drees Plumbing

Mike --

Built a website for Drees Plumbing on spec. It's live:

[VERCEL_URL_PLACEHOLDER]

No charge to look. If the design works for you, I host it for you
for $15/year (just the domain -- no monthly fee, no platform
lock-in). Right now, anyone searching for Drees Plumbing online has
no site of yours to land on -- no page describing what you do, no
form they can fill out at 10pm. This gives them one.

Take a look or don't. Either way no follow-up unless you say
"yeah, let's talk."

-- Juan
```

That's the target. ~75 words, 5 short sentences, frames the
prospect's OWN reachability (a fact: they have no website), NOT
what Google shows or where competitors rank. Explicit exit clause.

### Drafted output when data is sparse

If `owner_first_name` is null, drop the salutation:

```
Subject: Built a plumbing website for [Business Name]

Built a website for [Business Name] on spec. It's live:

[VERCEL_URL_PLACEHOLDER]

No charge to look. If the design works for you, I host it for you
for $15/year. Just the domain -- no monthly fee, no lock-in.

Take a look or don't. Either way no follow-up unless you say
"yeah, let's talk."

-- Juan
```

If `years_in_business` is null and `google_review_score` is null,
the email loses two hooks; lean on the Discoverability fallback
(which talks about the prospect's OWN missing website/form, never
about Google or competitors) and the URL alone. Don't pad.

---

## OUTPUT FORMAT (what build.py writes to email_draft.md)

```markdown
# Email Draft -- [BUSINESS_NAME]

Generated: [PROSPECT.build_date]
Trade: [PROSPECT.trade]
Recipient hint: [PROSPECT.owner_email if set, otherwise "TODO: prospect's owner email"]

---

**Subject:** [subject line]

---

[body, including the [VERCEL_URL_PLACEHOLDER] token where the live URL goes]

---

## Before sending

- [ ] Replace `[VERCEL_URL_PLACEHOLDER]` with the actual deployed Vercel URL
- [ ] Confirm owner first name spelling (if used)
- [ ] Send from your own email client (Gmail, Outlook, etc.). The
      from-scratch build pipeline does NOT auto-send pitch emails;
      this draft is the only outreach asset and must go through your
      personal mailbox so it lands as a peer-to-peer message.
- [ ] Do not follow up unless they reply.
```

The `[VERCEL_URL_PLACEHOLDER]` token is intentional -- the build
pipeline doesn't know the Vercel URL until after deployment, so the
salesperson replaces it manually after `vercel --prod` reports the
final URL.

---

## HARD RULES (NEVER VIOLATE)

- Output is markdown that wraps a plain-text email body. No HTML in
  the body itself.
- No subject lines with "Re:" prefix.
- No emojis anywhere in subject or body.
- No exclamation marks except in the recipient's own quoted review
  text (which you should NOT include anyway -- see fabrication guards).
- No URLs other than the `[VERCEL_URL_PLACEHOLDER]` token.
- Sign-off line is `-- [SALESPERSON_FIRST_NAME]` where the name is
  passed to you in the user prompt as `SALESPERSON FIRST NAME: <name>`.
  Use that value verbatim. Do NOT hardcode any other name. The build
  pipeline defaults to "Juan" when `prospect.salesperson_first_name`
  is null, but the prompt should respect whatever value is passed.
- Body length under 100 words. Subject line under 10 words.
