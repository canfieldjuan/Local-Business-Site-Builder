# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Two parallel implementations of the same pipeline — fetch a small business website, extract its brand and content, generate a modernized HTML mockup, optionally deploy to Vercel and email a pitch.

1. **`SKILL.md` + `references/*.md`** — a Claude skill (Anthropic's `claude-skills` format). The four reference files are LLM prompts; the skill instructs a model to read them step-by-step and produce HTML in `/mnt/user-data/outputs/`. No Python involved at runtime.
2. **`pipeline.py`** — a standalone CLI that automates the same flow via OpenRouter (`openai/gpt-4o`) and writes to `outputs/<site-slug>/`. Reads the same four reference files as prompts.

The reference files are the source of truth for prompt content. The skill and the script both consume them — keep changes prompt-shaped, not code-shaped.

## Running the Python pipeline

```bash
# One-time setup
pip install -r requirements.txt
playwright install chromium   # only if fetching JS-rendered sites (Squarespace/Wix/Webflow)

# .env must contain OPENROUTER_API_KEY and RESEND_API_KEY
python pipeline.py <url>                          # full flow with interactive prompts
python pipeline.py <url> --skip-deploy            # generate HTML only, no Vercel
python pipeline.py <url> --skip-deploy --skip-email
```

Deployment uses the `vercel` CLI directly (`npm i -g vercel && vercel login`). Email uses Resend; the default `onboarding@resend.dev` sender only delivers to your own Resend account address — verify a domain in Resend before sending to clients.

No tests, linter, or build step exist in this repo.

## Pipeline architecture (the parts that span files)

The flow in `pipeline.py main()` mirrors `SKILL.md` steps 1–5:

1. **Fetch** (`fetch_and_clean_html`) — `requests` first; if visible text < 8000 chars, auto-upgrade to Playwright headless Chromium. Strips `<script>/<svg>/<noscript>/<iframe>` but **keeps `<style>`** because the analysis prompt extracts brand colors from inline styles. Prepends an `<!-- EXTRACTED IMAGE URLS -->` comment harvesting `src`, `data-src`, `data-lazy-src`, `data-original`, and `url(...)` from styles — this is how the LLM reliably finds images on lazy-loaded sites.
2. **Analyze** (`analyze_site`) — sends the cleaned HTML to GPT-4o with `references/01-site-analysis-prompt.md` as the system prompt, `response_format=json_object`, temp 0.1. Output JSON shape (`site`, `images`, `pages_to_fetch`, `single_page_sections`, `conversion_profile`, `platform`, `image_generation_prompt`) is defined entirely inside that prompt file.
3. **Mirror images** (`mirror_images_locally`) — downloads CDN URLs into `outputs/<slug>/images/` and rewrites JSON paths to relative `images/...`, so the deployed Vercel bundle is self-contained and doesn't break when source CDNs expire.
4. **Hero image fallback** (`generate_image_openrouter`) — if analysis didn't find a hero image (common on JS-heavy sites), generate one via OpenRouter Flux. Returns either a URL or a base64 data URI; base64 is decoded to `outputs/<slug>/images/hero.<ext>` to avoid blowing up the LLM context on the next call.
5. **Generate HTML** — `generate_redesign` (homepage) and `generate_interior_page` both feed `references/02-redesign-gen-prompt.md` or `04-interior-page-prompt.md` plus the full `references/03-base-template.html` (CSS component library, 2000 lines) into the LLM. Strips ``` fences from output. Theme is auto-selected in `main()` via `theme_map` keyed on `site.type`.
6. **Deploy** (`deploy_to_vercel`) — runs `vercel whoami` first as a preflight, then `vercel --prod --yes --name <slug>` in the output dir, regex-extracts the `*.vercel.app` URL from stdout/stderr.
7. **Email** (`send_pitch_email`) — Resend, only if a contact email was extracted.

## What lives where

- `pipeline.py` — the entire automated pipeline. One module, no internal imports.
- `references/01-site-analysis-prompt.md` — extraction prompt. Edits here change the JSON schema produced in step 2.
- `references/02-redesign-gen-prompt.md` — homepage generation prompt with theme specs (broadcast/warm/editorial/civic/minimal/brand-forward), typography, conversion rules, deployment comment block.
- `references/03-base-template.html` — CSS component library. Both generation prompts inline this as context for the LLM.
- `references/04-interior-page-prompt.md` — interior page generation (contact, about, services, FAQ, menu).
- `outputs/<site-slug>/` — generated artifacts. Each subdir contains `index.html`, optional `contact.html`, an `images/` mirror, and Vercel deployment metadata after deploy.

## Conventions worth knowing

- **Brand color preservation is a hard requirement.** `COLOR_MODE` defaults to `brand` (use extracted hex/rgb values), not theme defaults. Only override when the source site has no usable accent colors.
- **Never invent content.** Headlines, services, items must come verbatim from the analysis JSON. Sparse contact info (just phone + address) still ships as a clean contact page.
- **Theme is derived, not configured.** `theme_map` in `pipeline.py` and the table in `SKILL.md` Step 2 both map `site.type` → theme. Keep them in sync if you add a theme.
- **Reference files are read in full each step.** The skill workflow assumes the model has the whole reference in context for each call — don't refactor them into smaller fragments without updating both `SKILL.md` and `pipeline.py`.

## When working in this repo

- Changes to LLM behavior go in `references/*.md`, not in `pipeline.py`.
- Changes to fetching, image handling, deployment, or email go in `pipeline.py`.
- If you change the analysis JSON shape (`01-site-analysis-prompt.md`), audit every `site_json.get(...)` access in `pipeline.py` and every `{{ }}` placeholder in `02-` and `04-` for downstream breakage.
