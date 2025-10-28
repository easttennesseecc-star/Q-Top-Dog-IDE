# 🎯 Q-IDE LLM Credentials - Visual Guide

## The Problem We Solved

### Before (Confusing):
```
User: "I want to use Google Gemini"
Q-IDE: "Go to some OAuth page?"
User: "But I just want to enter my API key..."
Q-IDE: ❌ No clear way to do it
```

### Now (Crystal Clear):
```
User: "I want to use Google Gemini"
Q-IDE: "Go to LLM Setup → Auth tab"
User: "Shows me Google, I click 'How to get credentials'"
Q-IDE: "Opens Google AI Studio, you copy your API key"
User: "Paste key, click Save"
Q-IDE: ✓ "Google Gemini authenticated!"
```

---

## Where Everything Is

### 📍 Q-IDE UI Location

```
Q-IDE Main Window
│
├─ LLM Setup (tab)
│  │
│  ├─ Providers (shows status of each LLM)
│  │
│  ├─ Roles (assign which LLM to which task)
│  │
│  ├─ Setup (one-at-a-time setup wizard)
│  │
│  └─ Auth (🔐 LLM PROVIDER CREDENTIALS) ← YOU ARE HERE
│     │
│     ├─ Google ✨ [Input field] [Save]
│     ├─ OpenAI 🤖 [Input field] [Save]
│     ├─ Anthropic 🧠 [Input field] [Save]
│     ├─ GitHub 🐙 [Input field] [Save]
│     └─ Groq 🚀 [Input field] [Save]
│
└─ (Other Q-IDE features)
```

---

## Step-by-Step: Add Google Gemini

### Step 1: Open Q-IDE

```
┌─────────────────────┐
│   Q-IDE            │
│  ┌───────────────┐  │
│  │ LLM Setup  ✓  │  │ ← Click this
│  └───────────────┘  │
└─────────────────────┘
```

### Step 2: Click "Auth" Tab

```
┌──────────────────────────────────────┐
│ Providers │ Roles │ Setup │ Auth ← │
├──────────────────────────────────────┤
│                                      │
│  🔐 LLM Provider Credentials         │
│                                      │
│  Enter your credentials below...    │
│                                      │
└──────────────────────────────────────┘
```

### Step 3: Find Google/Gemini Card

```
┌────────────────────────────────────┐
│  ✨ Google                         │
├────────────────────────────────────┤
│                                    │
│  How to get credentials:           │
│  Get API key from Google AI Studio │
│                                    │
│  Open Google AI Studio →           │
│  [Link: ai.google.dev]             │
│                                    │
│  API Key / Secret Token:           │
│  [AIzaSy________________]  [Save]  │
│                                    │
└────────────────────────────────────┘
```

### Step 4: Click the Link

```
1. Click "Open Google AI Studio →"
2. Browser opens: ai.google.dev
3. You'll see "Get API Key" button
4. Click it
5. Choose or create project
6. Get your API key (starts with AIzaSy)
7. Copy it (Ctrl+C)
```

### Step 5: Paste in Q-IDE

```
┌────────────────────────────────────┐
│  ✨ Google                         │
├────────────────────────────────────┤
│  [AIzaSyX1Y2Z3A4B5C6D7E8F9G...]   │  ← Paste here
│                              [Save] │  ← Click this
└────────────────────────────────────┘
         ↓
    (Sending to Q-IDE backend)
         ↓
    ✓ Authenticated!
```

### Step 6: Assign to Role

```
Go to "Roles" tab:

┌──────────────────────────────────────┐
│ Q Assistant       [Dropdown: Google]  │
│                   ← Select Gemini    │
├──────────────────────────────────────┤
│ Code Generation   [Dropdown: ------] │
│ Code Review       [Dropdown: ------] │
│ Testing           [Dropdown: ------] │
│ Release           [Dropdown: ------] │
└──────────────────────────────────────┘
         ↓
    ✓ Now Q Assistant uses Gemini!
```

---

## What Happens Behind the Scenes

```
FRONTEND (Q-IDE UI)          BACKEND (Your Computer)      EXTERNAL
─────────────────────        ────────────────────        ────────

User pastes:                 
"AIzaSy..."  ──POST──→   Q-IDE validates      
                         Stores in:
                         ~/.q-ide/llm_credentials.json
                         (Encrypted, Local)
                         
                              ↓
                         When user asks Q Assistant:
                         Q Assistant text ─POST──→  Google API
                                          ← Response
                                          
                         Uses API key from storage
                         to authenticate request
                         
                              ↓
                         Streams response back to UI
```

**Key Point:** Your API key stays on your computer, Q-IDE just uses it when needed.

---

## Data Flow: Asking Q Assistant a Question

```
┌─────────────────────────────────────────────────────────────┐
│ YOU: "Build a fitness app"                                 │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ↓
        ┌────────────────────────┐
        │ Q-IDE Frontend         │
        │ Sends message          │
        └────────────┬───────────┘
                     │
                     ↓
        ┌────────────────────────────┐
        │ Q-IDE Backend              │
        │ Looks up Q Assistant role  │
        │ Finds: "Assigned to Google"│
        │ Retrieves API key from     │
        │ ~/.q-ide/llm_credentials.  │
        │ json                       │
        └────────────┬───────────────┘
                     │
                     ↓
        ┌───────────────────────────────────┐
        │ Sends to Google Gemini API:       │
        │ {                                 │
        │   "message": "Build fitness app" │
        │   "api_key": "AIzaSy..."         │
        │ }                                 │
        └────────────┬────────────────────────┘
                     │
                     ↓ (Over HTTPS)
        ┌───────────────────────────────────┐
        │ Google's Server                   │
        │ Validates API key                 │
        │ Runs AI model                     │
        │ Sends back response               │
        └────────────┬────────────────────────┘
                     │
                     ↓
        ┌─────────────────────────────────────────┐
        │ Q-IDE Backend receives response         │
        │ Streams it back to Frontend character   │
        │ by character                            │
        └────────────┬────────────────────────────┘
                     │
                     ↓
        ┌──────────────────────────────────────────┐
        │ Q-IDE Frontend                           │
        │ Shows Q Assistant's response:            │
        │ "To build a fitness app, consider:       │
        │  - User authentication                   │
        │  - Workout logging system...             │
        │  - Progress tracking..."                 │
        └──────────────────────────────────────────┘
                     │
                     ↓
        ┌──────────────────────────────────────┐
        │ YOU: Read the response, ask follow-up│
        │ question                            │
        └──────────────────────────────────────┘
```

---

## Security Model

### Your Credentials Are NEVER Shared

```
🔒 Secure:
   Your Computer
   └─ API Key stored in ~/.q-ide/llm_credentials.json
      └─ Only Q-IDE can access it
      └─ Never sent to anyone but the LLM service itself
      └─ Q-IDE developers never see it

❌ Insecure (we DON'T do this):
   Your API Key → Q-IDE Server → Hackers steal it
   Your API Key → Shared in cloud → Exposed
   Your API Key → Sent to multiple services → Risky
```

### What Happens With Your Data

```
1. You paste API key in Q-IDE
2. Q-IDE stores it locally (encrypted if possible)
3. When you use Q Assistant:
   - Q-IDE uses your key to call Google/OpenAI/etc
   - Your question is sent along with your API key
   - Google/OpenAI processes it
   - Response comes back
4. Response is shown in Q-IDE
5. Your key is NEVER shared with anyone else
```

---

## Comparison: Different Auth Methods

### Method 1: API Key (What We Support) ✅

```
Pros:
✓ Simple - just paste and go
✓ No account needed on Q-IDE
✓ Full control - revoke anytime
✓ Each service has its own key
✓ Works offline (once saved)

Cons:
✗ Need to manage multiple keys
✗ Must get from each provider
```

### Method 2: OAuth (What We're Moving Away From)

```
Pros:
✓ One login
✓ Automatic expiration
✓ Easier account management

Cons:
✗ Requires user account on Q-IDE
✗ Complex flow with redirects
✗ Confusing for users
✗ "Why do I need to create an account?"
```

### Method 3: Q-IDE Account (What We DON'T Do)

```
Pros:
✓ Central management

Cons:
✗ We'd need to store YOUR credentials
✗ Major security risk
✗ Hackers would want to break in
✗ Creates liability for Q-IDE
✗ "Your API keys were exposed in a breach"
```

---

## Checklist: Getting Your First LLM Working

```
☐ Step 1: Choose a provider
  ☐ Google Gemini (recommended, free tier)
  ☐ OpenAI GPT-4 (best quality, paid)
  ☐ Anthropic Claude (thoughtful, paid)
  ☐ Local Ollama (free, offline)

☐ Step 2: Get API key from provider
  ☐ Go to provider's website
  ☐ Login to your account
  ☐ Generate API key
  ☐ Copy the key

☐ Step 3: Add to Q-IDE
  ☐ Open Q-IDE
  ☐ Go to LLM Setup → Auth tab
  ☐ Find your provider card
  ☐ Paste API key
  ☐ Click "Save"
  ☐ See "✓ Authenticated" message

☐ Step 4: Assign to role
  ☐ Go to LLM Setup → Roles tab
  ☐ Click dropdown for "Q Assistant"
  ☐ Select your provider
  ☐ See green checkmark

☐ Step 5: Test it
  ☐ Ask Q Assistant: "Hello, what can you do?"
  ☐ Get a response
  ☐ 🎉 Success!
```

---

## Troubleshooting Visual Guide

```
Problem: No LLMs showing in Auth tab
├─ Check: Is "Auth" tab visible at top?
│  └─ If not: Click "LLM Setup" first
├─ Check: Are there cards for Google, OpenAI, etc?
│  └─ If not: Refresh browser (Ctrl+R)
└─ Solution: Restart Q-IDE backend

Problem: "Invalid API key" error
├─ Check: Did you copy the ENTIRE key?
│  └─ Should be long string (50+ characters)
├─ Check: Is this the right key format?
│  └─ Google: AIzaSy...
│  └─ OpenAI: sk-...
│  └─ Anthropic: sk-ant-...
└─ Solution: Go back to provider, copy again

Problem: Key saved but says "Not authenticated"
├─ Check: Did you click "Save" button?
└─ Check: Page refresh (Ctrl+R)

Problem: Q Assistant not responding
├─ Check: Go to Roles tab
├─ Check: Is Q Assistant assigned to a LLM?
│  └─ Dropdown should show a model name
├─ Check: Go back to Auth tab
│  └─ Does that LLM show "✓ Authenticated"?
└─ Solution: Assign a different LLM to Q Assistant
```

---

## Next Steps

### 🚀 You're Ready To:

1. **Add Your First LLM** (choose Google, OpenAI, or local Ollama)
2. **Assign It to Q Assistant** (so Q Assistant can respond)
3. **Describe Your App Idea** ("I want to build an iOS and Android app...")
4. **Let Q Assistant Guide You** (through requirements, questions, code generation)
5. **Build Your App** (Q-IDE generates the codebase)

### 💡 Pro Tips:

- Start with Google Gemini (free, fast to set up)
- Use GPT-4 for best code quality (costs money but worth it)
- Try multiple LLMs for different roles
- You can change anytime - no lock-in!
- Keep your API keys safe (like passwords)

### 🎯 Your First Question to Ask:

Once everything is set up, tell Q Assistant:

> "I want to build an app for iOS and Android that helps users track their daily fitness goals. It should have:
> - User authentication
> - Ability to log workouts
> - Progress tracking with charts
> - Sharing with friends
> 
> Help me plan this out and generate the code."

---

**Questions? Check LLM_CREDENTIALS_GUIDE.md for more details!**
