"""Vercel CLI deployment helper. Writes the provided page dict to
outputs/<site_slug>/ and runs `vercel --prod --yes --name <slug>` against
that directory. Returns the live URL or None on failure."""
import os
import re
import subprocess


def deploy_to_vercel(site_slug, pages_dict, output_root="outputs"):
    """Deploy the generated pages to Vercel.

    site_slug: directory + Vercel project name.
    pages_dict: {filename: html_content}.
    output_root: base output directory ('outputs' for redesigns,
                 'outputs/builds' for from-scratch sites).
    """
    print(f"[*] Deploying {site_slug} to Vercel...")

    output_dir = os.path.join(output_root, site_slug)
    os.makedirs(output_dir, exist_ok=True)

    for filename, html_content in pages_dict.items():
        with open(os.path.join(output_dir, filename), "w") as f:
            f.write(html_content)

    try:
        # Pre-flight: confirm vercel CLI is installed and authenticated
        auth_check = subprocess.run(
            ["vercel", "whoami"],
            capture_output=True, text=True, timeout=10
        )
        if auth_check.returncode != 0:
            print("[!] Vercel CLI is not authenticated. Please run: vercel login")
            print(f"    Detail: {auth_check.stderr.strip()}")
            return None
        print(f"[*] Vercel authenticated as: {auth_check.stdout.strip()}")
    except FileNotFoundError:
        print("[!] Vercel CLI not found. Please run: npm install -g vercel && vercel login")
        return None
    except subprocess.TimeoutExpired:
        print("[!] Vercel CLI auth check timed out. Check your network connection.")
        return None

    try:
        result = subprocess.run(
            ["vercel", "--prod", "--yes", "--name", site_slug],
            cwd=output_dir,
            capture_output=True,
            text=True,
            check=True
        )

        url_match = re.search(r"https://[a-zA-Z0-9-]+\.vercel\.app", result.stdout + result.stderr)
        if url_match:
            vercel_url = url_match.group(0)
            print(f"[*] Successfully deployed to: {vercel_url}")
            return vercel_url
        fallback_url = f"https://{site_slug}.vercel.app"
        print(f"[*] Could not parse URL from output, trying fallback: {fallback_url}")
        return fallback_url

    except subprocess.CalledProcessError as e:
        print("[!] Vercel deployment failed:")
        print(e.stderr)
        return None
    except FileNotFoundError:
        print("[!] Error: Vercel CLI not found. Please run 'npm i -g vercel' and 'vercel login'.")
        return None
