"""Hero image acquisition. Two paths:

1. `fetch_unsplash_hero(trade, output_dir)` -- preferred when
   UNSPLASH_ACCESS_KEY is set. Free, fast, real photography. Reads the
   trade-specific `hero_search_query` from
   `references/07-industry-defaults.md` so the query is single-sourced
   alongside the rest of the trade defaults.

2. `generate_image_openrouter(prompt, output_dir)` -- paid Flux
   generation. Fallback when Unsplash returns nothing (no key, no
   results, network error) or when the caller prefers a custom prompt.

Both paths save the image locally to `<output_dir>/images/hero.<ext>`
and return a relative URL suitable for HTML injection (or None on
failure). Local mirroring matters because the deployed Vercel bundle
needs to be self-contained -- CDN URLs from Unsplash or OpenRouter
can expire."""
import os
import re
import base64
import requests
from lib.clients import OPENROUTER_API_KEY, UNSPLASH_ACCESS_KEY, IMAGE_MODEL

INDUSTRY_DEFAULTS_PATH = "references/07-industry-defaults.md"
UNSPLASH_SEARCH_URL = "https://api.unsplash.com/search/photos"
UNSPLASH_REQUEST_TIMEOUT = 10
UNSPLASH_DOWNLOAD_TIMEOUT = 30


def _extract_trade_unsplash_query(trade):
    # Read 07's `## TRADE: <trade>` section and pull the value of
    # `hero_search_query: "..."`. Single source of truth -- the same
    # 07 file documents the query under each trade's Hero Image section.
    # Returns the unquoted string or None if the file, section, or
    # field can't be parsed.
    try:
        with open(INDUSTRY_DEFAULTS_PATH, "r") as f:
            content = f.read()
    except OSError:
        return None

    section_match = re.search(
        r"^## TRADE:\s*" + re.escape(trade) + r"\s*$(.*?)(?=^## TRADE:|\Z)",
        content,
        re.MULTILINE | re.DOTALL,
    )
    if not section_match:
        return None

    query_match = re.search(
        r'^\s*hero_search_query:\s*"([^"]+)"',
        section_match.group(1),
        re.MULTILINE,
    )
    if not query_match:
        return None
    return query_match.group(1).strip()


def fetch_unsplash_hero(trade, output_dir):
    # Search Unsplash for a trade-appropriate hero photo, mirror it
    # locally to <output_dir>/images/hero.<ext>, and return a dict with
    # the relative URL plus attribution metadata. Returns None on any
    # failure so the caller can fall through to the Flux path.
    if not UNSPLASH_ACCESS_KEY:
        return None
    if not trade:
        return None

    query = _extract_trade_unsplash_query(trade)
    if not query:
        # Conservative single-word fallback. Matches the SKILL.md
        # guidance to default to bare `{trade}` rather than padded
        # multi-word strings that narrow Unsplash results.
        query = trade

    print(f"[*] Searching Unsplash for hero: query='{query}'")
    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
    params = {
        "query": query,
        "per_page": 1,
        "orientation": "landscape",
        "content_filter": "high",
    }
    try:
        response = requests.get(
            UNSPLASH_SEARCH_URL,
            headers=headers,
            params=params,
            timeout=UNSPLASH_REQUEST_TIMEOUT,
        )
    except requests.RequestException as e:
        print(f"[!] Unsplash search request failed: {e}")
        return None

    if response.status_code != 200:
        # 401 likely means the key is invalid; 403 may indicate rate
        # limit or content_filter rejection. Either way we fail soft
        # so the build doesn't break -- Flux is the safety net.
        print(f"[!] Unsplash API returned HTTP {response.status_code}: {response.text[:200]}")
        return None

    try:
        results = response.json().get("results", [])
    except ValueError:
        print("[!] Unsplash response was not valid JSON.")
        return None

    if not results:
        print(f"[!] No Unsplash results for query: '{query}'")
        return None

    photo = results[0]
    hero_url = photo.get("urls", {}).get("regular")
    photo_id = photo.get("id")
    credit_name = photo.get("user", {}).get("name", "Unknown")
    credit_url = photo.get("user", {}).get("links", {}).get("html", "https://unsplash.com")
    download_loc = photo.get("links", {}).get("download_location")
    if not hero_url:
        print("[!] Unsplash result missing regular URL; cannot download.")
        return None

    # Required by Unsplash API ToS: hit download_location once per use.
    # Pure analytics ping; we ignore the response body and any error
    # (a failed ping shouldn't break the build).
    if download_loc:
        try:
            requests.get(download_loc, headers=headers, timeout=UNSPLASH_REQUEST_TIMEOUT)
        except requests.RequestException:
            pass

    img_dir = os.path.join(output_dir, "images")
    os.makedirs(img_dir, exist_ok=True)
    img_path = os.path.join(img_dir, "hero.jpg")
    try:
        img_response = requests.get(hero_url, timeout=UNSPLASH_DOWNLOAD_TIMEOUT)
        img_response.raise_for_status()
        with open(img_path, "wb") as f:
            f.write(img_response.content)
    except requests.RequestException as e:
        print(f"[!] Failed to download Unsplash hero from {hero_url}: {e}")
        return None

    print(f"[+] Saved Unsplash hero to: {img_path}")
    return {
        "url": "images/hero.jpg",
        "credit_name": credit_name,
        "credit_url": credit_url,
        "photo_id": photo_id,
    }


def generate_image_openrouter(prompt, output_dir=None):
    print(f"[*] Generating custom hero image via OpenRouter ({IMAGE_MODEL})...")
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": IMAGE_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "modalities": ["image"]
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"[!] OpenRouter Image API error: {response.text}")
        return None

    data = response.json()
    try:
        image_url = data["choices"][0]["message"]["images"][0]["image_url"]["url"]

        # If the response is a base64 data URI, save it to disk.
        # Returning raw base64 to the LLM would consume the entire context window.
        if image_url.startswith("data:image"):
            if not output_dir:
                print("[!] Cannot save base64 image: no output_dir provided.")
                return None
            header, b64data = image_url.split(",", 1)
            ext = header.split("/")[1].split(";")[0]  # e.g. "webp" or "jpeg"
            img_dir = os.path.join(output_dir, "images")
            os.makedirs(img_dir, exist_ok=True)
            img_path = os.path.join(img_dir, f"hero.{ext}")
            with open(img_path, "wb") as f:
                f.write(base64.b64decode(b64data))
            relative_url = f"images/hero.{ext}"
            print(f"[*] Saved generated hero image to: {img_path}")
            return relative_url

        print("[*] Generated image URL successfully!")
        return image_url
    except Exception as e:
        print(f"[!] Failed to parse generated image: {e}")
        return None
