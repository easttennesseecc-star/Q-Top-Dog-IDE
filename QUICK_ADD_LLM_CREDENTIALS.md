# 🚀 Quick Start: Add Your First LLM Credentials

## The Simple Workflow

### In Q-IDE UI:

```
1. Open Q-IDE
   ↓
2. Go to "LLM Setup" tab
   ↓
3. Click "Auth" tab (🔐 icon)
   ↓
4. You'll see all LLM providers
   ↓
5. For each one you want:
   - See blue box with "How to get credentials"
   - Click the link to open provider's console
   - Get your API key
   - Paste in the text field
   - Click "Save"
   ↓
6. Go to "Roles" tab
   ↓
7. Click dropdown for "Q Assistant"
   ↓
8. Pick your LLM
   ↓
✓ DONE! Try asking Q Assistant a question
```

---

## Choose Your First LLM (Recommended Order)

### 1️⃣ START HERE: Google Gemini ✨ (Easiest)

**Why First?**
- ✅ Completely free API tier (60 requests/minute)
- ✅ Gets you going immediately, no payment needed
- ✅ Great for voice + conversation
- ✅ Takes 2 minutes to set up

**Steps:**
1. Go to: https://ai.google.dev/tutorials/setup
2. Click "Get API Key"
3. Click "Create API key in new Google AI Studio"
4. **Copy the key** (starts with `AIzaSy`)
5. In Q-IDE → Auth tab → Find "Google" or "Gemini"
6. Paste the key, click Save
7. Go to Roles tab, assign to "Q Assistant"
8. ✓ Done!

---

### 2️⃣ ADVANCED: OpenAI GPT-4 🤖 (Best Quality)

**Why?**
- 🏆 Best code generation capability
- 🏆 Best understanding of complex requests
- 💰 Costs money (but very small amounts)
- ⏱️ Takes ~5 minutes (need to add payment method)

**Steps:**
1. Go to: https://platform.openai.com/account/api-keys
2. Login/create account
3. Add payment method (required by OpenAI)
4. Click "Create new secret key"
5. **Copy it** (starts with `sk-`)
6. In Q-IDE → Auth tab → Find "OpenAI"
7. Paste the key, click Save
8. Go to Roles tab, assign to "Code Generation"
9. ✓ Now you have GPT-4 for coding!

---

### 3️⃣ OPTIONAL: Anthropic Claude 🧠 (Most Thoughtful)

**Why?**
- Excellent code review and documentation
- Great for explaining complex topics
- Costs money but competitive pricing

**Steps:**
1. Go to: https://console.anthropic.com/account/keys
2. Login/create account
3. Add payment method
4. Click "Create Key"
5. **Copy it** (starts with `sk-ant-`)
6. In Q-IDE → Auth tab → Find "Anthropic" or "Claude"
7. Paste the key, click Save
8. Go to Roles tab, assign to "Code Review"
9. ✓ Now you have Claude for analysis!

---

### 🏠 LOCAL OPTION: Use Ollama 🦙 (Free, No Account)

**Why?**
- ✅ Completely free
- ✅ Runs on your computer
- ✅ No internet required
- ✅ No API key needed
- ⚠️ Slower than cloud, needs good GPU

**Steps:**
1. Download: https://ollama.ai
2. Run: `ollama pull mistral` (or `llama2`)
3. Start Ollama: `ollama serve`
4. In Q-IDE → Providers tab → Find Ollama
5. Click "Setup"
6. Q-IDE auto-detects it
7. Go to Roles tab, assign to "Q Assistant"
8. ✓ Works locally, no payment needed!

---

## What Each Role Does

| Role | What It Does | Best LLM |
|------|-------------|----------|
| **Q Assistant** | Answers your questions, guides you | Gemini (voice-enabled) |
| **Code Generation** | Writes code for your app | GPT-4 (best quality) |
| **Code Review** | Reviews and improves code | Claude (detailed analysis) |
| **Testing** | Writes tests and test cases | GPT-4 or Claude |
| **Release** | Generates release notes | Any LLM works |

---

## Your First 5 Minutes

**⏱️ Timeline:**

1. **Minute 0-1:** Go to Google AI Studio, click "Get API Key"
2. **Minute 1-2:** Copy your key from Google
3. **Minute 2-3:** Paste in Q-IDE Auth tab, click Save
4. **Minute 3-4:** Go to Roles tab, assign Gemini to Q Assistant
5. **Minute 4-5:** Ask Q Assistant: "I want to build a mobile app"

**✓ You're done!** You now have an AI assistant helping you build apps.

---

## Common API Key Formats

**Verify you have the right format:**

```
OpenAI:      sk-proj-... or sk-...
Google:      AIzaSy...
Anthropic:   sk-ant-...
Groq:        gsk_...
Perplexity:  pplx-...
Ollama:      (no key needed - local)
```

If your key doesn't match, go back to the provider and get the right one.

---

## Troubleshooting Your First Setup

**❌ "Invalid API key format"**
- You copied the wrong thing. Go back to provider and copy again.
- Make sure you got the WHOLE key.

**❌ "Authentication failed"**
- For OpenAI: Did you add a payment method?
- For Google: Did you enable the API?
- Copy the exact key again from provider.

**❌ "Q Assistant won't respond"**
- Go to Roles tab
- Make sure your LLM is assigned to "Q Assistant"
- Try asking a simple question: "Hello"

**❌ "Can't find the Auth tab"**
- Click "LLM Setup" tab first
- Then look for "Auth" tab at the top

---

## Next: Describe Your App

Once everything is working, tell Q Assistant what you want to build:

**Example:**
> "I want to build a fitness tracking app for iOS and Android. It should have:
> - User accounts with email login
> - Ability to log workouts (running, gym, yoga)
> - Show stats and progress charts
> - Cloud sync between devices"

Q Assistant will:
1. Ask clarifying questions
2. Help you refine requirements
3. Generate code for your app
4. Create a cross-platform codebase

---

**Ready? Let's go! 🚀**

1. Pick one LLM above (Google Gemini recommended)
2. Get your API key (2-5 minutes)
3. Add to Q-IDE (1 minute)
4. Assign to Q Assistant (30 seconds)
5. Start building your app! 🎯
