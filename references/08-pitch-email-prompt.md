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
- One concrete competitive observation (e.g., the Roto-Rooter
  saturation in local search) -- something they'd recognize as true.
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
| Trade competition | Always available, but phrase as observation NOT specific SERP claim or outcome promise | "When customers in [CITY] search '[TRADE] near me,' the national chains crowd the top of the page. Without a site, you're hard to find." (Do NOT claim a specific number of results, a specific competitor's rank, or that this site will rank above any competitor. State the visibility problem; do not promise a ranking outcome.) |
| 24/7 availability | `has_24_7: true` | "I noticed you're 24/7. People searching at 11pm need to find you fast -- the phone in the hero is one tap on mobile." |
| Family-owned | `family_owned: true` | "Made the family-owned thing obvious throughout -- not buried in fine print." |

**Fabrication guards**:
- NEVER claim specific review text or specific customer stories. The
  prospect's reviews are listed in the JSON; the email can reference
  the aggregate (score + count) but should not paraphrase any single
  review.
- NEVER invent competitive facts. The Roto-Rooter / Mr. Rooter
  saturation point is true for plumbers in most US metros, but only
  use trade-specific facts that hold up generally.
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

Use one of (pick based on what data you have):
- `Built a [TRADE] website for [BUSINESS_NAME_TITLE_CASE]` -- default
- `A free draft for [BUSINESS_NAME_TITLE_CASE]` -- if you want it
  softer/less assertive
- `[CITY] [TRADE] -- quick look at something I made` -- if leading
  with city is stronger

Apply the brand display rule from `06-build-prompt.md`: title-case
the business name, strip legal suffixes ("Inc.", "LLC", "Co.").

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
lock-in). When folks in Effingham search "plumber near me," the
national chains crowd the page. Without a site, you're hard to find.

Take a look or don't. Either way no follow-up unless you say
"yeah, let's talk."

-- Juan
```

That's the target. ~75 words, 5 short sentences, one observation
about visibility (NOT a specific SERP claim, NOT a ranking promise),
explicit exit clause.

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
the email loses two hooks; lean on the trade-competition hook and
the URL alone. Don't pad.

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
