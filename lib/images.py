"""Hero / background image generation via OpenRouter's chat-completions
endpoint with modalities=image. Output is either a remote URL or a data URI;
data URIs are decoded to disk so they don't pollute the LLM context window
on the next call."""
import os
import base64
import requests
from lib.clients import OPENROUTER_API_KEY, IMAGE_MODEL


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
