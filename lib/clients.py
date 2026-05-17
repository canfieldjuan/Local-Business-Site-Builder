"""API keys, third-party client setup, and shared model constants.

Importing this module loads .env, initializes the OpenAI-compatible client
against OpenRouter, and configures the resend module. Both pipeline.py and
build.py import from here so the wiring stays single-sourced."""
import os
import json
import requests
import resend
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
RESEND_API_KEY = os.environ.get("RESEND_API_KEY")

if not OPENROUTER_API_KEY:
    print("Warning: OPENROUTER_API_KEY is not set. Please add it to your .env file.")
if not RESEND_API_KEY:
    print("Warning: RESEND_API_KEY is not set. Please add it to your .env file.")

# OpenAI-compatible client pointed at OpenRouter. None if no key was provided
# so import-time doesn't crash; callers that need the client will fail loudly
# at call time instead.
openai_client = None
if OPENROUTER_API_KEY:
    openai_client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY
    # Validate that at least one sending domain is verified in Resend.
    # Using onboarding@resend.dev only works for sending to your own account email.
    try:
        _domain_resp = requests.get(
            "https://api.resend.com/domains",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
            timeout=5
        )
        if _domain_resp.status_code == 200:
            _verified = [d for d in _domain_resp.json().get("data", []) if d.get("status") == "verified"]
            if not _verified:
                print("Warning: No verified sending domains found in Resend.")
                print("         Emails will only send to your Resend account address.")
                print("         Verify a domain at https://resend.com/domains to send to clients.")
        else:
            print(f"Warning: Could not verify Resend domain status (HTTP {_domain_resp.status_code}).")
    except Exception:
        pass  # Non-fatal -- domain check is informational only

# Model split: Haiku for structured extraction (analysis + enrichment),
# Sonnet for creative HTML generation (redesign + from-scratch builds).
# Both run via OpenRouter using the OpenAI-compatible client.
EXTRACTION_MODEL = "anthropic/claude-haiku-4.5"
GENERATION_MODEL = "anthropic/claude-sonnet-4.5"
# Hero / background image generation. OpenRouter's image model catalog
# shifts over time; update this constant when the provider deprecates an
# entry. Bypass at runtime with --skip-image-gen.
IMAGE_MODEL = "black-forest-labs/flux.2-max"

def extract_json_object(text):
    """Pull a single JSON object out of an LLM response, tolerating the
    markdown fences or leading preamble Claude sometimes emits even when
    asked for raw JSON. Raises json.JSONDecodeError if no valid object is
    recoverable."""
    if not isinstance(text, str):
        raise ValueError("LLM response was not a string")
    stripped = text.strip()
    # Strip an opening ```json or ``` fence if the whole payload is fenced.
    if stripped.startswith("```"):
        newline_idx = stripped.find("\n")
        if newline_idx != -1:
            stripped = stripped[newline_idx + 1:]
        if stripped.rstrip().endswith("```"):
            stripped = stripped.rstrip()[:-3].rstrip()
    # If there's preamble before the first '{' or trailing chatter after
    # the last '}', slice the JSON object out by brace position.
    first_brace = stripped.find("{")
    last_brace = stripped.rfind("}")
    if first_brace != -1 and last_brace > first_brace:
        candidate = stripped[first_brace:last_brace + 1]
        return json.loads(candidate)
    return json.loads(stripped)
