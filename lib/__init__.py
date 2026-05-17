# Shared helpers used by both the redesign pipeline (pipeline.py) and the
# from-scratch build pipeline (build.py). Submodules:
#   - clients: API key loading, OpenAI client init, resend init, model constants
#   - images:  hero/background image generation via OpenRouter
#   - deploy:  Vercel CLI deployment helpers
#   - email:   Resend pitch / delivery email helpers
