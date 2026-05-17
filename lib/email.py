"""Resend-backed email helpers. The 'from' address must be on a domain
verified in Resend; the default 'onboarding@resend.dev' only sends to
the email tied to your Resend account."""
import resend
# Import for side effects: ensures resend.api_key is configured.
from lib import clients as _clients  # noqa: F401


def send_pitch_email(owner_email, site_name, vercel_url, subject_prefix="A modernized redesign for"):
    """Send a pitch email pointing the recipient at the live mockup URL.

    subject_prefix lets callers tune the subject for redesign vs from-scratch
    contexts ('A modernized redesign for X' vs 'A free website draft for X')."""
    print(f"[*] Sending pitch email to {owner_email} via Resend...")

    params = {
        "from": "Agency <onboarding@resend.dev>",
        "to": [owner_email],
        "subject": f"{subject_prefix} {site_name}",
        "html": f"""
        <p>Hi there,</p>
        <p>I took the liberty of creating a modernized, conversion-optimized website for <strong>{site_name}</strong>.</p>
        <p>You can view the live interactive demo here:<br>
        <a href="{vercel_url}">{vercel_url}</a></p>
        <p>This version is designed to load faster, look better on mobile devices, and turn more visitors into customers.</p>
        <p>Would you be open to a quick 5-minute chat about putting this live for you?</p>
        <p>Best regards,</p>
        """
    }

    try:
        email = resend.Emails.send(params)
        print("[*] Email successfully sent!", email)
    except Exception as e:
        print("[!] Failed to send email:", str(e))
