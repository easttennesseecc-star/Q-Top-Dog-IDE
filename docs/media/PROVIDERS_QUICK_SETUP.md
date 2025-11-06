# Media Providers — Quick Setup (Easy Mode)

This guide gives you direct links and a two-step setup for each provider. No code edits required.

How it works
1) Get your API key from the provider
2) Call our configure API once (stores key in env for this session)

Supported providers
- DALL·E 3 (OpenAI)
  - Get key: https://platform.openai.com/api-keys
  - Configure: POST /media/configure with provider="dalle3", api_key="sk-..."
- Runway
  - Get key: https://docs.runwayml.com/reference/authentication
  - Configure: POST /media/configure with provider="runway", api_key="rw-..."
- Stable Diffusion (Hugging Face Inference API)
  - Get key: https://huggingface.co/settings/tokens
  - Configure: POST /media/configure with provider="stable_diffusion", api_key="hf_..."
- Midjourney (via proxy)
  - Choose a provider that exposes a simple HTTP API for prompts (examples: search for "Midjourney API proxy")
  - You will need: API key + Base URL endpoint
  - Configure: POST /media/configure with provider="midjourney", api_key="mj-...", endpoint="https://api.your-mj-proxy.com"

API examples
- POST /media/configure
  {
    "provider": "dalle3",
    "api_key": "sk-...",
    "test": true
  }
- GET /media/status — shows which providers are configured
- POST /media/generate
  {
    "description": "A golden retriever as a senior software engineer, cinematic lighting",
    "media_type": "image",
    "tier": "premium"
  }

Tips
- If you prefer not to handle keys manually, ask us to wire a tiny UI for /media/configure that stores keys locally during dev.
- Midjourney: because there is no official public API, use a proxy provider you trust. We support any base URL that accepts POST /imagine { prompt }.
