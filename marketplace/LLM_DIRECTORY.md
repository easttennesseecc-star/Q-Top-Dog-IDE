# LLM Provider Directory (BYOK)

This marketplace is a directory: you bring your own provider keys (BYOK). Use the links below to create API keys, then paste them into Q‑IDE to enable each provider.

| Provider | Sign‑up / Keys | Docs | Env Var | Example Models |
|---|---|---|---|---|
| OpenAI | https://platform.openai.com/ | https://platform.openai.com/docs/overview | OPENAI_API_KEY | gpt-4o, gpt-4.1-mini |
| Anthropic | https://console.anthropic.com/ | https://docs.anthropic.com/ | ANTHROPIC_API_KEY | claude-3-opus, claude-3-sonnet |
| Google (Gemini) | https://aistudio.google.com/ | https://ai.google.dev/ | GOOGLE_API_KEY | gemini-1.5-pro, gemini-1.5-flash |
| Mistral | https://console.mistral.ai/ | https://docs.mistral.ai/ | MISTRAL_API_KEY | mistral-large, mistral-small |
| Cohere | https://dashboard.cohere.com/ | https://docs.cohere.com/ | COHERE_API_KEY | command, command-r |
| OpenRouter | https://openrouter.ai/ | https://openrouter.ai/docs | OPENROUTER_API_KEY | anthropic/claude-3-sonnet, mistralai/mixtral-8x7b |
| Together AI | https://www.together.ai/ | https://docs.together.ai/ | TOGETHER_API_KEY | meta-llama/Llama-3-70b, mistralai/Mixtral-8x7B |
| Hugging Face Inference API | https://huggingface.co/settings/tokens | https://huggingface.co/docs/api-inference/index | HUGGINGFACE_API_KEY | bart-large-cnn, all‑MiniLM‑L6‑v2 |
| Azure OpenAI | https://portal.azure.com/ | https://learn.microsoft.com/azure/ai-services/openai/ | AZURE_OPENAI_API_KEY | gpt‑4o, gpt‑35‑turbo (requires deployment name) |
| AWS Bedrock | https://aws.amazon.com/bedrock/ | https://docs.aws.amazon.com/bedrock/ | AWS SDK creds | anthropic.claude‑3‑sonnet, meta.llama3‑70b |
| Groq | https://console.groq.com/ | https://console.groq.com/docs | GROQ_API_KEY | llama3‑70b‑8192, mixtral‑8x7b‑32768 |

Notes
- Azure OpenAI and AWS Bedrock use cloud credentials and resource names rather than only a single API key.
- Referral links may be used where available; they don’t change your pricing or access.
- For local/offline: use Ollama (no keys required) → https://ollama.com/
