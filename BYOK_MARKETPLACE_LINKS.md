# BYOK Marketplace Links (Models & Provider Portals)

Purpose: Fast path to acquire API keys and review model pages so users can add providers to Top Dog quickly. Keep this list current.

Note: These are external links; ensure you follow each provider’s key security best practices.

---

## LLM Providers

- OpenAI
  - Keys/Account: https://platform.openai.com/account/api-keys
  - Models: https://platform.openai.com/docs/models
- Anthropic (Claude)
  - Keys/Account: https://console.anthropic.com/
  - Models: https://docs.anthropic.com/en/docs/about-claude/models
- Google (Gemini)
  - Keys/Account: https://aistudio.google.com/app/apikey
  - Models: https://ai.google.dev/gemini-api/docs/models
- Mistral AI
  - Keys/Account: https://console.mistral.ai/
  - Models: https://docs.mistral.ai/getting-started/models/
- Cohere
  - Keys/Account: https://dashboard.cohere.com/api-keys
  - Models: https://docs.cohere.com/docs/models
- Meta (Llama via third parties)
  - Overview: https://ai.meta.com/llama/
  - Providers: AWS Bedrock, Azure, together.ai (see each portal)
- Together AI
  - Keys/Account: https://api.together.ai/
  - Models: https://docs.together.ai/docs/inference-models
- Groq
  - Keys/Account: https://console.groq.com/keys
  - Models: https://console.groq.com/docs/models
- AWS Bedrock
  - Keys/Account: https://console.aws.amazon.com/bedrock/
  - Models: https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids-arns.html
- Azure OpenAI
  - Keys/Account: https://portal.azure.com/
  - Models: https://learn.microsoft.com/azure/ai-services/openai/concepts/models
- Ollama (Local Models)
  - Install: https://ollama.com/
  - Models: https://ollama.com/library

---

## Media Synthesis (Runway)

- Runway
  - Keys/Account: https://runwayml.com/ (account) | https://research.runwayml.com/ (R&D)
  - Docs & API: https://docs.runwayml.com/
  - Pricing: https://runwayml.com/pricing/

---

## Email/SMS (if used)

- Twilio (SMS)
  - Keys/Account: https://console.twilio.com/
  - Docs: https://www.twilio.com/docs/sms
- Vonage (SMS)
  - Keys/Account: https://dashboard.nexmo.com/
  - Docs: https://developer.vonage.com/en/messaging/sms/overview
- SendGrid (Email)
  - Keys/Account: https://app.sendgrid.com/settings/api_keys
  - Docs: https://docs.sendgrid.com/for-developers/sending-email/api-getting-started

---

## How to Add Keys in Top Dog (Draft)

- Open Settings → Integrations → Providers
- Paste API keys into the appropriate provider field
- For local LLMs (Ollama): ensure the local daemon is running and set the endpoint
- For Runway: paste API key, then enable asset generation in project settings

See also: `CONFIGURATION_REFERENCE.md` and `PRODUCT_AND_MARKET_ANALYSIS.md`.
