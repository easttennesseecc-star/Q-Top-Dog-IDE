# LLM Bootstrap Options (No in-house model required)

You can run Q‑IDE today without building your own LLM. Pick one or combine them:

## 1) Local and Free: Ollama (zero external spend)

- What: Runs open-source models locally (e.g., Llama/Mistral) for demos and early users.
- Why: Zero API cost, keeps data local.
- How:
  - Use the included quick start: `QUICK_START_60_SECONDS.md`
  - Or run the automation: `INSTALL_OLLAMA_AUTO.bat` (Windows) / `INSTALL_OLLAMA_AUTO.ps1`
  - After install, Q‑IDE should list Ollama in the LLM Pool.

Notes:
- Best for development, offline, or cost-sensitive trials.
- Quality/latency will vary by model/hardware.

## 2) BYOK (Bring Provider Keys) — default for every tier

- What: Customers supply their own OpenAI/Anthropic/etc API keys.
- Why: You don’t pay model bills; tenants pay their providers directly.
- How:
  - Users add keys via the LLM config panels or OAuth linking (OpenAI/Anthropic).
  - Backend reads keys via your existing auth routes and/or environment/secret store.

Notes:
- Works across all tiers (Free→Enterprise).
- Use plan/segment labels to align SLAs and pricing.

## 3) Platform‑Managed Keys (bootstrap mode)

- What: You (the platform) supply provider keys temporarily to get to revenue before tenants bring their own.
- Why: Smooth out onboarding; sell value before tenants integrate their billing.
- How (env flags — set where you deploy the backend):

```
# Enable managed keys mode (temporary bootstrap)
PLATFORM_MANAGED_LLM_ENABLED=true

# Provider keys from your org (rotate regularly, store in secret manager)
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
# Optional additional providers
GOOGLE_API_KEY=...
COHERE_API_KEY=...

# Safety guardrails (strongly recommended)
SPEND_ALERT_TCU_WARN=200000    # warn per-tenant monthly at 200k TCU
SPEND_ALERT_TCU_HARD=300000    # hard stop for Starter at 300k (example)
```

- Billing & Safety:
  - Record metering events with `key_type: "platform"` vs `"byok"`.
  - Keep Prometheus alerts for TCU budget and margin guardrails enabled.
  - Consider per-plan request caps/rate limits until BYOK adoption increases.

Notes:
- Treat this as an interim strategy. Prefer BYOK for long-term margin stability.

## Recommended rollout

1) Start with Ollama + Platform‑Managed Keys (limited) to demo and onboard.
2) Guide paying tenants to BYOK within 1–2 weeks; keep Ollama for low‑risk flows.
3) Revisit margins monthly; use the Profit Guardrails from `MONETIZATION_V2_PRICING_AND_PACKAGING.md`.

## Troubleshooting

- "No models listed": Check Ollama service status or ensure provider keys are set.
- "Excess spend risk": Lower caps, increase alerts, or switch flows to Ollama.
- "Enterprise needs managed keys": Enable `PLATFORM_MANAGED_LLM_ENABLED` and scope usage by plan/segment.
