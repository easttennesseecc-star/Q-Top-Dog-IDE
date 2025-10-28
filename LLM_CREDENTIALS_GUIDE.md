# 🔐 Q-IDE LLM Credentials Guide

## Overview

Q-IDE uses your LLM credentials to authenticate with AI services **on your behalf**. You provide your API keys or authentication tokens, and Q-IDE sends them with requests to the LLM services. Your credentials are **stored locally** and never sent to Q-IDE servers.

## How It Works

```
You → Enter API Key → Q-IDE Stores Locally → Q-IDE Sends to LLM Service → Get AI Response
                           ↓
                    ~/.q-ide/llm_credentials.json
                    (Encrypted, Local Only)
```

**Key Points:**
- ✅ Credentials stored on **your machine only**
- ✅ Q-IDE uses credentials to call LLM APIs
- ✅ You can revoke/update anytime
- ✅ No account creation needed for Q-IDE itself
- ❌ Your credentials never leave your computer

---

## Getting Started

### Step 1: Go to LLM Setup

In Q-IDE:
1. Click **LLM Setup** tab
2. Click **Auth** tab (🔐 LLM Provider Credentials)
3. You'll see all available LLM providers

### Step 2: Add Credentials

For each LLM you want to use:

1. **Click the provider card** (e.g., "OpenAI", "Google", "Anthropic")
2. **Click the link** to open the provider's console
3. **Get your API key** (instructions shown in blue box)
4. **Paste the key** into the input field
5. **Click "Save"**
6. ✅ You'll see "Authenticated" status

### Step 3: Assign to Role

Once authenticated:
1. Go to **Roles** tab
2. Click the dropdown for each role (e.g., Q Assistant, Code Generation)
3. Select your LLM
4. ✓ Changes apply instantly

---

## Provider-Specific Guides

### 🤖 OpenAI (ChatGPT, GPT-4)

**What You Get:** GPT-4, GPT-3.5-turbo, text-davinci-003

**Getting Your API Key:**

1. Go to: https://platform.openai.com/account/api-keys
2. **Login** with your OpenAI account (create one if needed)
3. Click **"Create new secret key"**
4. Copy the key (it starts with `sk-`)
5. Paste in Q-IDE

**Cost:** Pay-as-you-go ($0.03-0.20 per 1K tokens, varies by model)

**Best For:** Q Assistant (high quality), Code Generation (very reliable)

---

### ✨ Google Gemini (or Google AI)

**What You Get:** Gemini 1.5 Pro, Gemini 1.5 Flash, Gemini Pro

**Getting Your API Key:**

1. Go to: https://ai.google.dev/tutorials/setup
2. Click **"Get API Key"**
3. **Choose or create a project**
4. Click **"Create API key in new project"**
5. Copy the key (it starts with `AIzaSy`)
6. Paste in Q-IDE

**Cost:** Free tier (60 requests/minute), then pay-as-you-go

**Best For:** Q Assistant (voice synthesis + fast), Code Review (excellent)

**Bonus:** Gemini has built-in voice capabilities for natural conversations!

---

### 🧠 Anthropic Claude

**What You Get:** Claude 3 Opus, Sonnet, Haiku

**Getting Your API Key:**

1. Go to: https://console.anthropic.com/account/keys
2. **Login** with your Anthropic account (sign up if needed)
3. Click **"Create Key"**
4. Copy the key (it starts with `sk-ant-`)
5. Paste in Q-IDE

**Cost:** Pay-as-you-go ($0.80-3.00 per 1M tokens)

**Best For:** Code Generation (thoughtful), Testing (detailed test coverage)

---

### 🐙 GitHub Copilot

**What You Get:** GPT-4 via GitHub's infrastructure

**Getting Access:**

GitHub Copilot requires OAuth (different from API key):

1. In Q-IDE, click **Sign In** button for GitHub
2. You'll be redirected to GitHub
3. **Authorize Q-IDE** to access Copilot
4. You'll be sent back to Q-IDE
5. ✓ GitHub Copilot is now authenticated

**Cost:** $10/month or included in GitHub Pro ($4/month student)

**Best For:** Code Generation (integrated with GitHub), Testing (understands your repo)

---

### 🖥️ Local Models (Ollama)

**What You Get:** Llama 2, Mistral, Neural Chat, and 50+ models

**Setup:**

1. Download Ollama: https://ollama.ai
2. Run: `ollama pull llama2` (or your preferred model)
3. Start Ollama: `ollama serve`
4. In Q-IDE, go to **Providers** tab
5. Click **"Setup"** for Ollama
6. Ollama will auto-detect at localhost:11434

**Cost:** Free (runs on your machine)

**Best For:** Privacy-conscious users, testing locally, no internet needed

---

## Common Tasks

### ✨ Adding Multiple LLMs

You can set up **multiple providers** and switch between them:

1. Add Google Gemini ✨
2. Add OpenAI GPT-4 🤖
3. Add Anthropic Claude 🧠
4. Add local Ollama 🖥️

Then in **Roles** tab, assign:
- Q Assistant → Gemini (for voice)
- Code Generation → GPT-4 (best quality)
- Code Review → Claude (detailed analysis)

This gives you the **best of each service**!

### 🔄 Changing Your API Key

If your API key expires or you want to use a different one:

1. Go to **Auth** tab
2. Find the provider
3. Click **"Clear"** button
4. Enter your **new API key**
5. Click **"Save"**

Done! New requests will use the new key.

### ❌ Removing a Provider

1. Go to **Auth** tab
2. Find the provider
3. Click **"Clear"** button
4. ✓ Removed from Q-IDE (but still active at the provider)

### 🔒 Keeping Your Keys Safe

**DO:**
- ✅ Treat API keys like passwords
- ✅ Don't share them in messages or emails
- ✅ Rotate keys periodically
- ✅ Use provider's console to revoke suspicious keys
- ✅ Keep Q-IDE on your personal machine

**DON'T:**
- ❌ Paste your key in emails or Slack
- ❌ Commit API keys to GitHub
- ❌ Share keys with others
- ❌ Use production keys for testing

---

## Troubleshooting

### ❌ "Failed: Invalid API key format"

**Cause:** You pasted an incomplete or wrong key

**Fix:**
1. Go to the provider's console
2. Copy the key again (make sure you got the whole thing)
3. Clear Q-IDE and paste again

### ❌ "API key saved but still says 'Not authenticated'"

**Cause:** Your account might not have API access enabled

**Fix:**
- For OpenAI: Add payment method in your account settings
- For Google: Make sure Generative AI API is enabled
- For Anthropic: Request API access if on waitlist

### ❌ "Q Assistant says 'not configured'"

**Cause:** You added the key but didn't assign it to Q Assistant role

**Fix:**
1. Go to **Roles** tab
2. Click dropdown for "Q Assistant"
3. Select your LLM
4. ✓ Should respond now

### ❌ "Keeps asking for credentials"

**Cause:** Your API key expired or hit rate limits

**Fix:**
1. Check provider's dashboard for errors
2. Generate a new key
3. Update in Q-IDE's Auth tab

---

## Example Setups

### 🎯 Best Quality (All Cloud)
```
Provider    Model              Role
═════════════════════════════════════════════════════════
OpenAI      GPT-4              Code Generation
Google      Gemini 1.5 Pro     Q Assistant (voice)
Anthropic   Claude 3 Opus      Code Review
Groq        Mixtral            Testing
```

### 💰 Cost-Optimized (Free)
```
Provider    Model              Role
═════════════════════════════════════════════════════════
Google      Gemini 1.5 Flash   All (free tier 60/min)
Ollama      Llama 2            Local testing (free)
```

### ⚡ Balanced (Popular)
```
Provider    Model              Role
═════════════════════════════════════════════════════════
OpenAI      GPT-4 Turbo        Code Generation
Google      Gemini 1.5 Pro     Q Assistant
Anthropic   Claude 3 Sonnet    Code Review
```

### 🏠 Privacy-First (All Local)
```
Provider    Model              Role
═════════════════════════════════════════════════════════
Ollama      Llama 2            All roles (local only)
```

---

## Next Steps

1. **Pick Your LLM** - Choose one from the guide above (GPT-4 or Gemini recommended)
2. **Get Your API Key** - Follow the provider-specific steps
3. **Add to Q-IDE** - Go to Auth tab and paste your key
4. **Assign Role** - Go to Roles tab and pick which LLM for each task
5. **Start Building** - Tell Q Assistant about your app idea!

---

## FAQ

**Q: Do I need to pay for Q-IDE to use LLMs?**
A: No! Q-IDE is free. You only pay the LLM services directly (OpenAI, Google, etc.).

**Q: Can Q-IDE see my credentials?**
A: No. Q-IDE stores them locally on your machine. We never see or store your keys.

**Q: Can I use the same key on multiple machines?**
A: Yes, but you'd need to add it to each Q-IDE installation separately.

**Q: What if I lose my API key?**
A: Go to the provider's console and revoke the key. Generate a new one.

**Q: Can I use multiple keys from the same provider?**
A: Currently Q-IDE stores one key per provider, but you can rotate them anytime.

**Q: Does Q-IDE work without internet?**
A: Yes, if you use local Ollama. Cloud providers require internet.

---

## Support

Having trouble? Check:
1. **Auth status** - Go to Auth tab, verify "Authenticated" shows
2. **Assigned role** - Go to Roles tab, make sure LLM is assigned
3. **Try Q Assistant** - Ask a simple question to test it's working
4. **Check provider status** - Visit provider's status page (service might be down)

Still stuck? Check the provider's documentation or Q-IDE logs.
