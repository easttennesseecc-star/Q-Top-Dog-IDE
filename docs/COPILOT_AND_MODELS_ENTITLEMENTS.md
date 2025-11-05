# GitHub Copilot vs. LLM API Entitlements

Short version: a personal or org Copilot subscription gives you IDE/chat features. It does not grant general-purpose, production API access to use Copilot models inside your own service for multiple users.

## Recommended ways to populate your LLM pool

- Azure OpenAI Service (Microsoft) — commercial models with enterprise controls
- OpenAI / Anthropic / Google Gemini — direct API access
- Local models (Ollama) — on-node inference for prototyping/cost control
- Optional: GitHub Models — only if your org has access and terms allow server-side use; integrate behind a feature flag.

## Why not Copilot API?

Copilot is licensed for developer assistance in editors and GitHub products. Multiplexing a single Copilot subscription as a backend LLM for your app is typically not permitted and is technically unsupported.

When/if GitHub Models meets your use case and licensing, add a provider adapter and enable it for your org only.

## Adapter pattern (already in code)

`backend/llm_chat_service.py` routes by provider key (openai/google/anthropic/ollama). To add a new provider:

1. Map `_map_source(name)` to return a new key (e.g., `githubmodels`)
2. Implement `_stream_githubmodels(...)` with your org's endpoint/headers
3. Guard with a feature flag and org-level allowlist
