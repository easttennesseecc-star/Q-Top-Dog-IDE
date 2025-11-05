# LLM Auto-Assignment System - User Guide

## What's New

Top Dog now **automatically discovers and assigns the best LLM models to each role** based on what you have available. No more manual configuration!

---

## How It Works

### Step 1: Available LLM Providers

Top Dog supports these popular LLM providers (all have free trials):

| Provider | Best For | Free Tier | Sign Up |
|----------|----------|-----------|---------|
| **OpenAI** | Planning, Coding, Verification | $5 credits (3 mo) | https://platform.openai.com/account/api-keys |
| **Anthropic (Claude)** | Code Generation, Reasoning | $5 credits | https://console.anthropic.com/account/keys |
| **Google (Gemini)** | All-around capability | Free tier available | https://makersuite.google.com/app/apikey |
| **Mistral AI** | Fast, Cost-effective coding | $5 credits | https://console.mistral.ai/ |

### Step 2: Setup Wizard (First Time)

When you first launch Top Dog:

1. **Choose Providers** - Select which LLM services you want to use (you can use multiple!)
2. **Get API Keys** - Sign up and create free API keys
3. **Enter API Keys** - Save keys securely in Top Dog
4. **Auto-Assign** - Top Dog tests your APIs and assigns models optimally

### Step 3: Automatic Assignment

Top Dog analyzes your available models and assigns them like this:

```
Your Models                    ↓ Top Dog Smart Assignment ↓              Your Team

gpt-4 (OpenAI)            →  Q Assistant (Orchestrator)
gpt-3.5-turbo (OpenAI)    →  Code Writer (Implementation)
claude-3-sonnet (Claude)  →  Test Auditor (QA)
gemini-pro (Google)       →  Verification Overseer (Fact-check)
mistral-large (Mistral)   →  Release Manager (Documentation)
```

**Why this works:**
- Each model gets a role matching its strengths
- Cost-optimized (cheaper models for simpler tasks)
- Speed-optimized (faster models for time-critical roles)
- Verified to work with your actual API keys

---

## API Endpoints

### Setup Wizard

**Start Setup** (First Time)
```
GET /api/setup/wizard/start
```
Returns: Step-by-step wizard instructions

**Get Available Providers**
```
GET /api/setup/wizard/providers
```
Returns: List of all supported LLM providers with sign-up links

**Save API Keys**
```
POST /api/setup/wizard/save-api-keys
Body: {"openai": "sk-...", "anthropic": "sk-ant-..."}
```

**Complete Setup**
```
POST /api/setup/wizard/complete
```
Returns: Auto-assigned models + configuration summary

**Get Setup Status**
```
GET /api/setup/status
```
Returns: Current setup status and configured providers

---

### Auto-Assignment

**Auto-Assign Models**
```
GET /api/llm/auto-assign
```
Returns: Best model assignment for each role

**Get Available Models**
```
GET /api/llm/available-models
```
Returns: All known LLM models and their capabilities

**Get Assignment Summary**
```
GET /api/llm/assignment-summary
```
Returns: Cost estimates, speed profiles, etc.

---

## Example: Complete Setup Flow

```python
# 1. Start wizard
GET /api/setup/wizard/start
→ Shows: "Welcome to Top Dog LLM Setup!"

# 2. List providers
GET /api/setup/wizard/providers
→ Shows: OpenAI, Anthropic, Google, Mistral with sign-up links

# 3. User signs up and gets API keys

# 4. Save keys
POST /api/setup/wizard/save-api-keys
{
  "openai": "sk-proj-xxxxxx",
  "anthropic": "sk-ant-xxxxxx"
}
→ Keys saved securely

# 5. Complete setup
POST /api/setup/wizard/complete
→ Returns:
{
  "status": "setup_complete",
  "assignments": {
    "q_assistant": "gpt-4",
    "code_writer": "gpt-3.5-turbo",
    "test_auditor": "claude-3-sonnet",
    "verification_overseer": "claude-3-haiku",
    "release_manager": "gemini-pro"
  },
  "monthly_cost_estimate": "$12.50"
}

# 6. Start building!
```

---

## How Assignment Scoring Works

Top Dog scores each model for each role based on:

| Factor | Weight | How it works |
|--------|--------|-------------|
| **Capability Match** | 60% | Does the model have the skills needed? |
| **Cost** | 20% | Prefer cheaper models for equivalent quality |
| **Speed** | 15% | Fast models for time-critical roles |
| **Uniqueness** | 5% | Avoid duplicate models when possible |

### Example Scoring:

```
Q Assistant (Planning role) - What's the best fit?

GPT-4:           Score: 95/100  (excellent planning, but expensive)
Claude-3-Sonnet: Score: 85/100  (good planning, mid-price)
GPT-3.5-Turbo:   Score: 80/100  (good planning, cheap)
Gemini-Pro:      Score: 75/100  (ok planning, very cheap)

→ Assignment: GPT-4 (best all-around for orchestrator role)

Code Writer (Implementation role) - What's the best fit?

GPT-4:           Score: 92/100  (excellent code, but expensive)
Claude-3-Sonnet: Score: 90/100  (excellent code, mid-price) ← PICKED (save GPT-4 for Q-Assistant)
GPT-3.5-Turbo:   Score: 88/100  (good code, cheap)
Gemini-Pro:      Score: 70/100  (ok code, very cheap)

→ Assignment: Claude-3-Sonnet (excellent coder, freeing GPT-4 for planning)
```

---

## Recommended Setup for First-Time Users

### Budget-Conscious ($0-$5/month)
```
Use: GPT-3.5-Turbo (OpenAI) + Gemini-Pro (Google)
Cost: Free or $2-3/month
Best for: Learning Top Dog, small projects
```

### Balanced ($5-$20/month)
```
Use: GPT-4-Turbo (OpenAI) + Claude-3-Sonnet (Anthropic)
Cost: $5-10/month with free credits
Best for: Most projects, good quality
```

### High-Quality ($20-$50/month)
```
Use: GPT-4 (OpenAI) + Claude-3-Opus (Anthropic) + Gemini-Pro (Google)
Cost: $20-30/month
Best for: Complex projects, need best results
```

---

## Your App Building Journey

Once setup is complete:

```
1. Setup Wizard         ← You are here first time
   ↓ (Save API keys, auto-assign)

2. Top Dog Dashboard
   ↓ (Choose your app idea)

3. Q Assistant Chat
   ↓ (Describe your app requirements)

4. Auto Build Pipeline
   ↓ (Top Dog coordinates all 5 LLM roles)

5. Generated Codebase
   ↓ (Ready-to-run application)

6. Deploy
   ↓ (Your app is live!)
```

---

## Troubleshooting

### "No models available"
- **Issue:** No LLM providers authenticated
- **Fix:** Run `/api/setup/wizard/start` and complete setup

### "API key rejected"
- **Issue:** Invalid or expired API key
- **Fix:** Go back to provider website, regenerate API key, try again

### "Model assignment failed"
- **Issue:** Available model doesn't match role needs
- **Fix:** Add another LLM provider for better coverage

### "Setup wizard says no providers configured"
- **Issue:** Changes weren't saved
- **Fix:** Make sure you hit "Save" after entering API keys

---

## Advanced: Manual Model Assignment

If you don't want auto-assignment, manually configure:

```
POST /api/llm/config/assign
{
  "q_assistant": "gpt-4",
  "code_writer": "claude-3-opus",
  "test_auditor": "gpt-3.5-turbo",
  "verification_overseer": "gemini-pro",
  "release_manager": "mistral-large"
}
```

---

## Next Steps

1. **First Time?** → Go to `/api/setup/wizard/start`
2. **Already Set Up?** → Go to Dashboard to create your first project
3. **Need Help?** → All endpoints have `/docs` (Swagger UI) at `http://localhost:8000/docs`

**Ready to build? Let's go! 🚀**
