# 🎯 Quick Reference: LLM Credentials in Q-IDE

## In 30 Seconds

```
Q-IDE → LLM Setup → Auth tab
        ↓
      Enter your API keys for Google, OpenAI, etc.
        ↓
      Q-IDE stores them locally
        ↓
      Q-IDE uses them to call LLM services
        ↓
      You get AI responses without creating accounts
```

---

## The Tab Layout

```
┌─────────────────────────────────────────────────┐
│ LLM Setup                                       │
├─────────────────────────────────────────────────┤
│ Providers    Roles    Setup    Auth ← YOU HERE  │
├─────────────────────────────────────────────────┤
│                                                 │
│ 🔐 LLM Provider Credentials                    │
│                                                 │
│ ✨ Google         [API Key]  [Save]            │
│ 🤖 OpenAI         [API Key]  [Save]            │
│ 🧠 Anthropic      [API Key]  [Save]            │
│ 🐙 GitHub         [Sign In]                    │
│ 🚀 Groq           [API Key]  [Save]            │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## API Key Locations (Cheat Sheet)

| Provider | Go To | Format | Time |
|----------|------|--------|------|
| **Google** | ai.google.dev | AIzaSy... | 2 min |
| **OpenAI** | platform.openai.com/api-keys | sk-proj-... | 5 min |
| **Anthropic** | console.anthropic.com/keys | sk-ant-... | 5 min |
| **GitHub** | github.com (OAuth) | N/A | 3 min |
| **Groq** | console.groq.com | gsk_... | 2 min |

---

## Keyboard Shortcuts in Auth Tab

```
[Paste API Key] → [Tab] → [Enter] → Auto-saves
```

---

## Status Messages

```
✅ Green text    = Authenticated successfully
⚠️ Yellow text   = Warning or needs attention
❌ Red text      = Error or not authenticated
⏳ Spinning icon = Loading/saving in progress
```

---

## The 3-Step Process

### Step 1: Get Key
```bash
Visit provider → Create API key → Copy (Ctrl+C)
```

### Step 2: Paste in Q-IDE
```
Auth tab → Paste key → Click Save
```

### Step 3: Assign to Role
```
Roles tab → Select your LLM → Done ✓
```

---

## Which LLM to Pick?

| Need | Pick | Why |
|------|------|-----|
| **Free** | Google Gemini | ✨ Free tier, no payment needed |
| **Best Quality** | OpenAI GPT-4 | 🤖 Most capable, best code |
| **Analysis** | Anthropic Claude | 🧠 Excellent at explaining |
| **Privacy** | Ollama Local | 🖥️ Runs on your computer |
| **GitHub Integration** | GitHub Copilot | 🐙 Knows your repo |

---

## Error Quick-Fix

```
❌ "Invalid API key"
   → Go back to provider, copy whole key again

❌ "Authentication failed"
   → Add payment method (for paid services)
   → Check API is enabled in provider settings

❌ "Q Assistant won't respond"
   → Go to Roles tab
   → Make sure LLM assigned to "Q Assistant"

❌ Can't find Auth tab
   → Click "LLM Setup" first
   → Then click "Auth" tab
```

---

## Remember

```
🔒 Your keys stay on your computer
   └─ Never sent to anyone but LLM service
   └─ Never visible to Q-IDE developers
   └─ Treat like passwords

⚡ Q-IDE uses them on your behalf
   └─ You don't sign into LLM websites
   └─ Q-IDE signs in using your key
   └─ You get AI responses

🎯 You control everything
   └─ Add anytime → Go to Auth tab
   └─ Remove anytime → Click "Clear"
   └─ Switch anytime → New key, old one deleted
```

---

## Files Reference

| File | What It Is | Read Time |
|------|-----------|-----------|
| **QUICK_ADD_LLM_CREDENTIALS.md** | 5-min setup guide | 5 min |
| **LLM_CREDENTIALS_GUIDE.md** | Complete reference | 15 min |
| **LLM_CREDENTIALS_VISUAL_GUIDE.md** | Diagrams & troubleshooting | 10 min |
| **LLM_CREDENTIALS_SETUP_COMPLETE.md** | Full solution summary | 10 min |

---

## One-Page Workflow

```
START
  ↓
Open Q-IDE
  ↓
Go to LLM Setup tab
  ↓
Click Auth tab
  ↓
Pick a provider (Google recommended)
  ↓
Click "How to get credentials" link
  ↓
Browser opens provider's website
  ↓
Follow steps to get API key
  ↓
Copy the key
  ↓
Return to Q-IDE
  ↓
Paste in the text field
  ↓
Click Save
  ↓
See "✓ Authenticated" message
  ↓
Go to Roles tab
  ↓
Assign LLM to "Q Assistant"
  ↓
Ask Q Assistant a question
  ↓
Get AI response
  ↓
🎉 SUCCESS!
```

---

## Pro Tips

✨ You can have multiple LLMs (Google + OpenAI + Anthropic)
⚡ Each role can use different LLM (Q Assistant → Gemini, Code → GPT-4)
🔄 Rotate API keys by clearing and adding new one
🎯 Start simple: one provider, build from there
💡 Use free tiers first, upgrade later if needed

---

**Ready? Open Q-IDE, go to LLM Setup → Auth tab. Let's go! 🚀**
