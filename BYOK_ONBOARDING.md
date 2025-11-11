## BYOK Onboarding & Local-First Default

Q‑IDE runs in BYOK (Bring Your Own Keys) mode: you supply provider API keys; the platform never resells or marks up tokens.

### Goals
- Immediate usability on first launch (even with zero keys)
- Privacy: no default shared credentials
- Guided setup via Q Assistant

### Local-First Auto Selection
On first run, if no LLM is assigned to the `q_assistant` role, Q‑IDE tries to auto-select a local model:
1. Detects Ollama CLI (preferred) or any local CLI from PATH
2. Assigns it to `q_assistant` automatically
3. Q Assistant announces: “Local model auto-selected (BYOK).”

If none found, Q Assistant prompts you to install Ollama:

```text
1. Download: https://ollama.ai
2. Install and run: ollama serve
3. Pull a model: ollama pull mistral
4. Reopen Q Assistant or refresh the page
```

### Adding Cloud Provider Keys
Use the LLM Setup panel:
1. Open LLM Setup → Providers
2. Choose a provider (OpenAI, Anthropic, Gemini, etc.)
3. Click “Add API key” and paste the key
4. Assign to `coding` or `q_assistant` role (Roles tab)
5. Q Assistant will reflect the new model

### Recommended Order
| Step | Action | Why |
|------|--------|-----|
| 1 | Local (Ollama) | Instant, private, no external calls |
| 2 | Gemini (free tier) | Quick cloud trial without cost |
| 3 | OpenAI / Anthropic | Higher quality / reasoning |

### Troubleshooting
| Symptom | Fix |
|---------|-----|
| “LLM not configured” toast | Install Ollama or add a provider key |
| Auto-assignment didn’t happen | Ensure no model already assigned; restart Q Assistant panel |
| Local CLI detected but slow | Pull a smaller model (`ollama pull mistral`) |
| Cloud model needs credentials | Add API key in LLM Setup → Providers |

### Security Notes
- Keys stored locally under user home (`~/.q-ide/llm_keys.json`) with restrictive file permissions.
- No keys sent to other users or shared tenant storage.
- Switching models only updates role assignment config (`~/.q-ide/llm_roles.json`).

### Advanced
- To force local-only mode, assign `ollama` to both `coding` and `q_assistant` roles.
- To reset assignments, delete `~/.q-ide/llm_roles.json` and reopen Q Assistant.

### Verification
Run: `tasklist | findstr /i ollama` (Windows) or `ps -ef | grep ollama` (Unix) to confirm the local service.

---
Q Assistant will continue to guide you through adding or rotating provider keys. Enjoy a fully BYOK, local-first workflow.

## Browser-only SaaS: Local Companion Proxy (concept)

When Q‑IDE runs in a pure browser SaaS (no desktop app), the page cannot call `http://localhost:*` directly in many enterprise networks or strict browsers. To enable local models (Ollama, llama.cpp) in that scenario, use a small “Local Companion” running on the user’s machine:

- Companion responsibilities:
	- Expose a secure local WebSocket (e.g., `wss://127.0.0.1:11435`) and proxy requests to the local model (Ollama default `11434`).
	- Establish an outbound tunnel to `companion.topdog-ide.com` so the browser can connect over a first‑party domain (same‑site cookies/CORS under control).
	- Perform origin checks and short‑lived token validation (issued by Q‑IDE after user login) before relaying.
	- Never store provider keys; only forwards local traffic.

- Browser wiring:
	- Frontend detects “companion available” via a preflight `wss://companion.topdog-ide.com/ping` and falls back to cloud/BYOK setup if unavailable.
	- All LLM calls use `wss://companion.topdog-ide.com/ollama/*` instead of `http://localhost:11434/*`.

- Security considerations:
	- Mutual auth: short‑lived JWT bound to device, signed by Q‑IDE; companion validates before proxying.
	- CORS: Limit to your SaaS app origins (staging and prod).
	- Rate limiting: Basic per‑session guard in the companion to avoid abuse from other local pages.
	- Privacy: No keys leave the device; the proxy only forwards localhost requests.

- Implementation sketch:
	- Companion: Go or Node service with `websocket <-> http` bridge, health endpoint `/healthz`, and `/ping`.
	- Domain: `companion.topdog-ide.com` fronted by reverse proxy that holds the TLS cert; the tunnel connects the local companion to this domain.
	- Deployment: optional signed installer for Windows/macOS; auto‑start on login.

This lets BYOK remain local‑first for browser SaaS users without requiring them to weaken browser protections.