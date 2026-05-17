"""From-scratch website build for local-business prospects with no
existing online presence. Sibling pipeline to pipeline.py (which redesigns
existing sites).

Usage:
  python build.py <prospect.json> [--skip-deploy] [--skip-image-gen] [--skip-email-draft]

Reads a small prospect JSON, optionally generates a hero image, generates
a single-page site via Sonnet, writes to outputs/builds/<slug>/, writes
a pitch email draft to outputs/email_drafts/<slug>.md (siblings -- the
draft is NOT in the Vercel deploy root and never published), and
optionally deploys the site to Vercel. The salesperson sends the pitch
email manually from their own email client AFTER replacing the
[VERCEL_URL_PLACEHOLDER] token in the draft. No automated send path.
"""
import os
import re
import sys
import json
from datetime import date

from lib.clients import openai_client as client, GENERATION_MODEL
from lib.images import generate_image_openrouter
from lib.deploy import deploy_to_vercel
# lib.email.send_pitch_email is intentionally NOT imported here. The
# from-scratch build flow uses the manual email_draft.md workflow
# instead -- the salesperson sends from their own client after
# replacing [VERCEL_URL_PLACEHOLDER]. The Resend-backed auto-send
# path is still used by pipeline.py (the redesign flow).

BUILD_PROMPT_PATH = "references/06-build-prompt.md"
INDUSTRY_DEFAULTS_PATH = "references/07-industry-defaults.md"
BASE_TEMPLATE_PATH = "references/03-base-template.html"
EMAIL_PROMPT_PATH = "references/08-pitch-email-prompt.md"
BUILD_OUTPUT_ROOT = os.path.join("outputs", "builds")
# Email drafts live in a SIBLING directory, never inside BUILD_OUTPUT_ROOT/<slug>/.
# The Vercel deploy uses outputs/builds/<slug>/ as its root; anything in there
# gets published. The pitch email is an internal salesperson handoff and must
# not be reachable at /email_draft.md on the deployed site.
EMAIL_DRAFT_ROOT = os.path.join("outputs", "email_drafts")
BUILD_TEMPERATURE = 0.4
BUILD_USER_TRUNCATE = 200000
# Email-draft generation is short, deterministic, and copy-focused.
# Lower temperature than the HTML build to keep the voice tight.
EMAIL_TEMPERATURE = 0.3
DEFAULT_SALESPERSON_FIRST_NAME = "Juan"

REQUIRED_FIELDS = ("business_name", "trade", "city", "state", "phone")

# Substring markers that indicate a prospect-JSON field was left at its
# template default. Case-insensitive substring match against the value.
PLACEHOLDER_MARKERS = (
    "example.com",
    "REPLACE",
    "YOUR_FORM_ID",
    "(REPLACE)",
    "TODO",
)
# Fields where a placeholder is a credibility / functionality problem --
# warn loudly, don't silently strip. The site will still build, but the
# salesperson needs to fix these before sending the link to a prospect.
PLACEHOLDER_CRITICAL_FIELDS = ("business_name", "formspree_endpoint")
# Fields where a placeholder should be silently nullified so the LLM
# doesn't render it. Safer to omit "owner@example.com" from the footer
# than to render it on a live site.
PLACEHOLDER_NULLIFY_FIELDS = ("owner_email", "owner_first_name", "phone", "address")


def _is_placeholder(value):
    if not isinstance(value, str):
        return False
    lowered = value.lower()
    return any(marker.lower() in lowered for marker in PLACEHOLDER_MARKERS)


def sanitize_placeholders(prospect):
    """Detect prospect-JSON values left at their template defaults. Critical
    fields produce a loud warning; nullifiable fields are silently set to
    None so the LLM omits them from the rendered output."""
    for field in PLACEHOLDER_CRITICAL_FIELDS:
        value = prospect.get(field)
        if _is_placeholder(value):
            print(f"[!] PLACEHOLDER VALUE in prospect.{field}: {value!r}")
            print(f"    The site will render this verbatim. Update before sharing the live URL.")
    for field in PLACEHOLDER_NULLIFY_FIELDS:
        value = prospect.get(field)
        if _is_placeholder(value):
            print(f"[*] Nullifying placeholder prospect.{field}: {value!r}")
            prospect[field] = None


def sanitize_reviews(prospect):
    """Drop entries from prospect.reviews that still contain template
    placeholder markers (EXAMPLE / REPLACE / etc.) in any of their
    visible string fields. The remaining list is what the build will
    actually render."""
    reviews = prospect.get("reviews")
    if not isinstance(reviews, list) or not reviews:
        return
    cleaned = []
    dropped = 0
    for r in reviews:
        if not isinstance(r, dict):
            dropped += 1
            continue
        suspect_fields = ("author", "text", "date", "platform")
        if any(_is_placeholder(r.get(f)) for f in suspect_fields):
            text_preview = (r.get("text") or "")[:60]
            print(f"[*] Dropping placeholder review entry: author={r.get('author')!r}, text={text_preview!r}...")
            dropped += 1
            continue
        cleaned.append(r)
    if dropped:
        prospect["reviews"] = cleaned
        print(f"[*] {dropped} placeholder review(s) removed; {len(cleaned)} real review(s) remain.")


def normalize_years(prospect, build_date):
    """If established_year is set, recompute years_in_business from
    current_year - established_year so a stale JSON doesn't report the
    wrong tenure. Established_year wins over years_in_business when both
    are present."""
    current_year = build_date.year
    established = prospect.get("established_year")
    if isinstance(established, int) and 1900 <= established < current_year:
        computed = current_year - established
        existing = prospect.get("years_in_business")
        if existing != computed:
            print(f"[*] years_in_business recomputed: {existing} -> {computed} (from established_year={established})")
        prospect["years_in_business"] = computed
    return prospect


def load_prospect(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Prospect JSON not found: {path}")
    with open(path, "r") as f:
        prospect = json.load(f)
    missing = [k for k in REQUIRED_FIELDS if not prospect.get(k)]
    if missing:
        raise ValueError(f"Prospect JSON missing required field(s): {', '.join(missing)}")
    sanitize_placeholders(prospect)
    sanitize_reviews(prospect)
    build_date = date.today()
    prospect["build_date"] = build_date.isoformat()
    normalize_years(prospect, build_date)
    return prospect


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "prospect"


def build_hero_prompt(prospect):
    trade = prospect.get("trade", "local business")
    city = prospect.get("city", "")
    state = prospect.get("state", "")
    return (
        f"Professional photorealistic hero image for a local {trade} business in "
        f"{city}, {state}. Wide cinematic crop, golden-hour natural light, depth "
        f"of field. Subject: a clean service van in a residential driveway OR a "
        f"close-up of professional tools in use. NO text, NO logos, NO faces "
        f"clearly visible, no branded apparel from any specific company. "
        f"Generic-but-professional. Avoid stock-photo cliches."
    )


def generate_build_html(prospect):
    print(f"[*] Generating site for {prospect['business_name']} using {GENERATION_MODEL}...")
    with open(BUILD_PROMPT_PATH, "r") as f:
        system_prompt = f.read()
    with open(INDUSTRY_DEFAULTS_PATH, "r") as f:
        industry_defaults = f.read()
    with open(BASE_TEMPLATE_PATH, "r") as f:
        base_template = f.read()

    user_prompt = (
        f"PROSPECT JSON:\n{json.dumps(prospect, indent=2)}\n\n"
        f"INDUSTRY DEFAULTS:\n{industry_defaults}\n\n"
        f"BASE TEMPLATE:\n{base_template}\n"
    )

    response = client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt[:BUILD_USER_TRUNCATE]}
        ],
        temperature=BUILD_TEMPERATURE
    )

    html = response.choices[0].message.content
    # Belt-and-suspenders in case the LLM leaks fences despite the prompt rule.
    html = re.sub(r"^```html\n?", "", html)
    html = re.sub(r"^```\n?", "", html)
    html = re.sub(r"```$", "", html)
    return html.strip()


def generate_email_draft(prospect):
    """Generate the Day-1 pitch email draft for this prospect. Returns the
    markdown content that gets written to email_draft.md alongside the
    site. The VERCEL_URL_PLACEHOLDER token is intentionally left in --
    the salesperson swaps it for the real URL after deployment."""
    salesperson = prospect.get("salesperson_first_name") or DEFAULT_SALESPERSON_FIRST_NAME
    print(f"[*] Generating pitch email draft for {prospect['business_name']}...")
    with open(EMAIL_PROMPT_PATH, "r") as f:
        system_prompt = f.read()

    user_prompt = (
        f"PROSPECT JSON:\n{json.dumps(prospect, indent=2)}\n\n"
        f"SALESPERSON FIRST NAME: {salesperson}\n\n"
        f"Generate the email_draft.md file content per the rules above. "
        f"Output the markdown directly -- no code fences, no preamble. "
        f"Leave the [VERCEL_URL_PLACEHOLDER] token in the body verbatim."
    )

    response = client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=EMAIL_TEMPERATURE
    )

    draft = response.choices[0].message.content
    # Strip any markdown fences the LLM might have leaked.
    draft = re.sub(r"^```markdown\n?", "", draft)
    draft = re.sub(r"^```\n?", "", draft)
    draft = re.sub(r"```$", "", draft)
    return draft.strip()


def main(prospect_json_path):
    prospect = load_prospect(prospect_json_path)
    slug = prospect.get("slug") or slugify(prospect["business_name"])
    output_dir = os.path.join(BUILD_OUTPUT_ROOT, slug)
    os.makedirs(output_dir, exist_ok=True)

    print(f"[*] Building {prospect['business_name']} ({prospect['trade']}, {prospect['city']}, {prospect['state']})")
    print(f"[*] Output: {output_dir}/")

    # Hero image generation (unless skipped or prospect already provided one).
    if "--skip-image-gen" in sys.argv:
        print("[*] Skipping hero image generation due to --skip-image-gen flag.")
    else:
        existing_hero = any(
            p.get("context") in ("hero", "background")
            for p in prospect.get("photos", []) if isinstance(p, dict)
        )
        if not existing_hero:
            img_prompt = build_hero_prompt(prospect)
            print(f"[*] Hero prompt: {img_prompt[:120]}...")
            generated_url = generate_image_openrouter(img_prompt, output_dir=output_dir)
            if generated_url:
                prospect.setdefault("photos", []).append({
                    "url": generated_url,
                    "alt": f"Modern hero image for {prospect['business_name']}",
                    "context": "hero"
                })

    html = generate_build_html(prospect)

    index_path = os.path.join(output_dir, "index.html")
    with open(index_path, "w") as f:
        f.write(html)

    print(f"\n[+] Build complete: {index_path}")
    print(f"[+] Review locally before deploying.")

    # Email draft -- written alongside the HTML so the salesperson sees
    # the pitch copy right when they review the site. Skippable; the
    # VERCEL_URL_PLACEHOLDER token gets manually replaced post-deploy.
    # Stale-draft protection: any prior email_draft.md in the reused
    # output_dir is removed whenever the draft is skipped or generation
    # fails. Otherwise a salesperson reviewing the new site could pick
    # up an outdated pitch from a previous build.
    # email_draft.md lives in a SIBLING directory, NOT inside output_dir.
    # output_dir is the Vercel deploy root; anything in there gets published.
    # The pitch draft is internal-only.
    os.makedirs(EMAIL_DRAFT_ROOT, exist_ok=True)
    email_path = os.path.join(EMAIL_DRAFT_ROOT, f"{slug}.md")
    if "--skip-email-draft" in sys.argv:
        print("[*] Skipping pitch email draft due to --skip-email-draft flag.")
        if os.path.isfile(email_path):
            os.remove(email_path)
            print(f"[*] Removed stale draft from prior build: {email_path}")
    else:
        try:
            email_md = generate_email_draft(prospect)
            # Verify the [VERCEL_URL_PLACEHOLDER] token survived in the BODY
            # (not just in the "Before sending" checklist, which always
            # contains it because the prompt template instructs the model
            # to include it there). Split on the "Before sending" marker
            # and check the body portion only -- if the body is missing
            # the token, the salesperson has no handoff point for the
            # deployed URL and the draft is unusable.
            body_portion = re.split(r"##\s*Before sending", email_md, maxsplit=1)[0]
            if "[VERCEL_URL_PLACEHOLDER]" not in body_portion:
                raise ValueError(
                    "Generated draft is missing the [VERCEL_URL_PLACEHOLDER] token "
                    "in the email body (the checklist alone does not count). "
                    "Salesperson would have no place to insert the deployed URL."
                )
            with open(email_path, "w") as f:
                f.write(email_md)
            print(f"[+] Pitch email draft: {email_path}")
            print(f"[*] Replace [VERCEL_URL_PLACEHOLDER] with the deployed URL before sending.")
        except Exception as e:
            print(f"[!] Email draft generation failed: {e}")
            if os.path.isfile(email_path):
                os.remove(email_path)
                print(f"[*] Removed stale draft from prior build: {email_path}")
            print(f"[*] Site build still complete; rerun with --skip-email-draft if this keeps failing.")

    if "--skip-deploy" in sys.argv:
        print("\n[*] Skipping Vercel deployment due to --skip-deploy flag.")
        return

    deploy_choice = input("\n[?] Deploy to Vercel now? (y/N): ")
    if deploy_choice.lower() != "y":
        print("[*] Deployment cancelled.")
        return

    vercel_url = deploy_to_vercel(slug, {"index.html": html}, output_root=BUILD_OUTPUT_ROOT)
    if not vercel_url:
        return

    print(f"\n[+] Live URL: {vercel_url}")
    email_draft_hint_path = os.path.join(EMAIL_DRAFT_ROOT, f"{slug}.md")
    if os.path.isfile(email_draft_hint_path):
        print(f"[*] Pitch email draft ready: {email_draft_hint_path}")
        print(f"[*] Replace [VERCEL_URL_PLACEHOLDER] with {vercel_url}")
        print(f"[*] Send from your own email client. Do NOT use any automated sender.")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1].startswith("--"):
        print("Usage: python build.py <prospect.json> [--skip-deploy] [--skip-image-gen] [--skip-email-draft]")
    else:
        main(sys.argv[1])
