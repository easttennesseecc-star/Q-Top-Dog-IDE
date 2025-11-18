# Top Dog API Key Responsibility Model

**TL;DR**: You bring your own API keys. Top Dog doesn't provide them, store them insecurely, or charge you for LLM usage. You pay the provider directly.

---

## Three Core Rules

### Rule 1: Free Tier = Free/Local Models Only
```
Free users get:
- Ollama (local Llama, Mistral, etc.) - 100% free
- LLaMA models - Open source, no keys needed
- GPT4All - Local, private, completely free
- No API keys required
- Works completely offline
```

### Rule 2: Pro/Teams/Enterprise = BYOK (Bring Your Own Key)
```
Paid users can add their own keys:
- OpenAI GPT-4 (you pay OpenAI directly)
- Google Gemini (you pay Google directly)
- Anthropic Claude (you pay Anthropic directly)
- Still can use free local models too
- You manage all keys in Top Dog Settings
```

### Rule 3: Top Dog Never Handles Your API Keys
```
What Top Dog does NOT do:
- Store your keys on our servers
- Charge you for API usage
- Log or monitor your API calls
- Share keys with anyone
- Process payments for LLM usage
```

---

## How It Works: Visual Flow

```
┌─────────────────────────────────────────────────────────┐
│ USER EXPERIENCE                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 1. User creates Top Dog account                          │
│ 2. Chooses Free/Pro/Teams/Enterprise                   │
│ 3. If Free: Start coding with Ollama (no key needed)   │
│ 4. If Paid:                                            │
│    a. Go to Settings → LLM Configuration               │
│    b. Add your OpenAI/Google/Claude API key            │
│    c. Key is encrypted and stored LOCALLY              │
│    d. Start using that LLM immediately                 │
│ 5. User pays provider directly on THEIR invoice        │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ BILLING RELATIONSHIPS                                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Top Dog Invoice: Top Dog Subscription ($0-25/seat/mo)     │
│     You pay us for Top Dog features                      │
│                                                         │
│ OpenAI Invoice: LLM Usage ($0.03-0.06/1K tokens)      │
│     You pay OpenAI for GPT-4 usage                     │
│     (completely separate from Top Dog)                   │
│                                                         │
│ Google Invoice: LLM Usage (free tier OR $0.00075/tok)  │
│     You pay Google for Gemini usage                    │
│     (completely separate from Top Dog)                   │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ DATA FLOW: HOW YOUR API KEY IS USED                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Your Top Dog App                                         │
│       ↓                                                │
│ Your API Key (encrypted in ~/.Top Dog/llm_keys.json)    │
│       ↓                                                │
│ When you use AI features, Top Dog calls:                │
│ POST https://api.openai.com/v1/chat/completions       │
│       ↓                                                │
│ Using YOUR key, on YOUR behalf                        │
│       ↓                                                │
│ OpenAI processes your request                         │
│       ↓                                                │
│ Result returned to Top Dog                              │
│       ↓                                                │
│ Displayed in your editor                              │
│                                                         │
│ NOTE: Top Dog never stores the response on our servers  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Tier-by-Tier API Key Model

### FREE TIER ($0)

**What you get:**
- Ollama (local LLMs, completely free)
- LLaMA models
- GPT4All
- 100% offline capability

**API keys required:** None

**Cost breakdown:**
- Top Dog: $0
- LLM: $0
- Total: $0

**Sample usage:**
```
# Free tier user
User: "Analyze this code"
Top Dog: Loads local Ollama model
Ollama: Analyzes code on user's machine
User: Gets results instantly, offline
Cost: $0
```

---

### PRO TIER ($12/month)

**What you get:**
- Add your own API keys to Top Dog settings
- Use any model you have a key for
- Still have access to free local models
- Your choice of OpenAI, Google, Anthropic, or local

**API keys required:** Bring your own (optional)

**Cost breakdown example:**
```
Top Dog Pro: $12/month
└─ Fixed cost for features

OpenAI GPT-4: $20/month (example)
├─ Based on YOUR usage
├─ Billed separately by OpenAI
└─ You manage API key in Top Dog

Total: $12 + $20 = $32/month
```

**Sample usage:**
```
# Pro tier user with OpenAI key
User: "Refactor this function"
Top Dog: Uses user's OpenAI API key
OpenAI: Generates refactored code
User: Accepts and commits
Cost: $0.02 added to OpenAI bill (not Top Dog bill)
```

---

### TEAMS TIER ($25/seat/month)

**What you get:**
- Add team's API keys
- Each team member can add their own key
- Manage keys per-team or per-person
- Recommended: Shared API key + spending limit on provider

**API keys required:** Bring your own (optional)

**Cost breakdown example:**
```
Top Dog Teams: $25 × 5 developers = $125/month
└─ Fixed cost for team features

Shared OpenAI Key: $200/month
├─ Team's total usage across all 5 developers
├─ Billed once to OpenAI
├─ Set spending limit on OpenAI dashboard
└─ Each team member uses same key

Total: $125 + $200 = $325/month
```

**Best practice:**
```
Option A (Shared Key):
- Team creates one OpenAI key
- All developers use that key in Top Dog
- Set spending limit on OpenAI to $X
- Everyone sees team's usage on OpenAI dashboard

Option B (Individual Keys):
- Each developer gets own OpenAI key
- Each adds their key to Top Dog
- Each developer pays separately
- Good for distributed teams or departments
```

---

### ENTERPRISE ($Custom)

**What you get:**
- BYOK: Add your own API keys (same as Teams)
- Self-hosted: Deploy your own LLM server
- Managed LLM: Use Top Dog's hosted LLM service (additional cost)

**API keys required:** Depends on model choice

**Cost breakdown example:**
```
OPTION 1: BYOK (Self-managed keys)
Top Dog Enterprise: $5,000/month
└─ For 100 developers

OpenAI API: $3,000-5,000/month
└─ Team's total GPT-4 usage
└─ Completely separate invoice from OpenAI

Total: $8,000-10,000/month

---

OPTION 2: Self-hosted LLM
Top Dog Enterprise: $5,000/month
└─ For 100 developers

Self-hosted LLM (on your infrastructure): $1,000-2,000/month
└─ EC2/GCP instances running Llama or Mistral
└─ Completely on your servers
└─ No per-token cost

Total: $6,000-7,000/month

---

OPTION 3: Top Dog Managed LLM
Top Dog Enterprise: $5,000/month + $2,000/month for managed LLM
└─ For 100 developers
└─ Uses OpenAI backend

Total: $7,000/month
```

---

## Security & Privacy: How We Protect Your Keys

### Key Storage (Encrypted)
```
Your API Key
     ↓
Encrypted using system keyring
     ↓
Stored in: ~/.Top Dog/llm_keys.json
     ↓
Only readable by your user on your machine
```

### Key Usage (Private)
```
Your encrypted key
     ↓
Top Dog decrypts only when you use AI feature
     ↓
Key sent directly to provider (OpenAI, Google, etc.)
     ↓
Top Dog NEVER logs, stores, or monitors the request
     ↓
Response returned to Top Dog
     ↓
Top Dog displays to you, then forgets
```

### Key Lifecycle (Safe)
```
┌─────────────┐
│ Add Key     │ You paste your API key in Top Dog settings
└──────┬──────┘
       ↓
┌─────────────┐
│ Encrypt     │ Top Dog encrypts with system keyring
└──────┬──────┘
       ↓
┌─────────────┐
│ Store Local │ Saved in ~/.Top Dog/llm_keys.json
└──────┬──────┘
       ↓
┌─────────────┐
│ Use         │ Each time you call an AI feature
└──────┬──────┘
       ↓
┌─────────────┐
│ Revoke      │ Delete from Top Dog settings anytime
└──────┬──────┘
       ↓
┌─────────────┐
│ Forgotten   │ Top Dog no longer has access to key
└─────────────┘
```

---

## Common Questions

### Q: What if Top Dog gets hacked?
**A:** Hackers can't access your API keys because:
- Keys stored in system keyring (encrypted)
- Keys never sent to Top Dog servers
- Top Dog doesn't know your keys on the backend
- Even if they hacked our servers, they'd find nothing

**Recommendation:** Rotate your API key on OpenAI's dashboard annually for safety.

---

### Q: Will my Top Dog bill include LLM costs?
**A:** No. Ever.
- Top Dog invoice: Top Dog features only ($0-$25/month)
- OpenAI invoice: Separate, direct from OpenAI
- No hidden LLM fees in your Top Dog bill

---

### Q: Can I use multiple LLM providers?
**A:** Yes! Assign different providers to different tasks:
```
Settings → LLM Configuration:
├─ Coding role: OpenAI GPT-4 ($)
├─ Documentation role: Google Gemini (free)
├─ Research role: Local Ollama ($0)
└─ Top Dog picks the best one automatically
```

---

### Q: What if OpenAI's API goes down?
**A:** Top Dog keeps working:
- GPT-4 feature becomes unavailable
- You can still use local Ollama
- Your code doesn't disappear
- Service resumes when OpenAI recovers

---

### Q: Can I use Top Dog without any API keys?
**A:** Yes! Use the free local models:
```
Free tier: Always works with Ollama
Pro/Teams/Enterprise: Use Pro tier WITHOUT adding any keys
└─ You'd just use local models
└─ No extra features, but completely free LLM usage
```

---

### Q: What if I lose my API key?
**A:**
1. Go to OpenAI/Google/Anthropic dashboard
2. Delete the old key
3. Generate a new one
4. Update it in Top Dog Settings
5. Done (takes 2 minutes)

---

### Q: Can I share my API key with coworkers?
**A:**

**NOT recommended** (security risk):
- Anyone with the key can use it
- Anyone can accidentally consume your budget
- Not accountable if something goes wrong

**Better approach** (Teams tier):
- Set up a shared key with spending limits
- Or give each person their own key
- Manager tracks usage on provider dashboard

---

### Q: How do I set a spending limit?
**A:** On the provider's side (not Top Dog):

**OpenAI:**
1. Go to https://platform.openai.com/account/billing/limits
2. Set "Hard limit" (max spend per month)
3. Set "Soft limit" (alert threshold)

**Google Gemini:**
1. Go to Google Cloud Console
2. Set quotas for APIs
3. Monitor usage

---

## Responsibility Matrix

| Question | Free Tier | Pro/Teams | Enterprise |
|----------|-----------|-----------|------------|
| Who provides API keys? | N/A | You | You |
| Who manages the keys? | N/A | You | You (or self-host) |
| Who pays for LLM usage? | N/A | You (direct) | You (direct) |
| Who manages spending limits? | N/A | You (on provider) | You (on provider) |
| Who is responsible for security? | N/A | You | You |
| Where are keys stored? | N/A | Your machine | Your machine (or self-hosted) |
| Does Top Dog bill for LLM? | N/A | NO | NO |
| Can Top Dog access your keys? | N/A | NO | NO |

---

## Summary

### What This Means For You

**Free tier:**
- 100% free
- 100% private
- 100% offline
- Use local Ollama

**Pro tier:**
- $12/month for Top Dog features
- Add your API keys (optional)
- Pay provider directly for LLM usage
- No Top Dog markup

**Teams tier:**
- $25/seat/month for Top Dog features
- Team members add their API keys
- Pay provider directly for LLM usage
- No Top Dog markup

**Enterprise:**
- Custom pricing for Top Dog
- BYOK, self-hosted, or managed LLM
- Full control over infrastructure
- Direct billing with providers

---

## Bottom Line

> Top Dog is a product company, not a payment processor.
> We focus on building great tools.
> You manage your API keys and pay providers directly.
> This keeps things simple, secure, and transparent.

**Questions?** See [PRICING_AND_MONETIZATION_STRATEGY.md](./PRICING_AND_MONETIZATION_STRATEGY.md#-llm-model-access--api-key-model-critical) for full details.
