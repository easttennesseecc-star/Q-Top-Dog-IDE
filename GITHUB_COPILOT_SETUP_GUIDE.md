# 🚀 GitHub Copilot Quick Setup for Top Dog

## Before You Start

### Requirements:
- ✅ Active [GitHub Copilot subscription](https://github.com/copilot) ($20/month)
- ✅ GitHub account logged in
- ✅ Top Dog open with LLM Setup tab visible

**Don't have Copilot?** Use **Google Gemini (free)** instead - follow the Gemini guide.

---

## Step 1: Create API Token (2 minutes)

### Go to Token Creation Page
```
1. Visit: https://github.com/settings/tokens/new
   (Must be logged into GitHub)
```

### Generate Token
```
On the "New personal access token" page:

Token name: 
  "Top Dog Copilot API"

Expiration:
  Select "30 days" or "No expiration"

Select scopes:
  ✓ user:read
  ✓ write:packages  
  ✓ read:packages
```

### Copy the Token
```
1. Click "Generate token"
2. GitHub shows the token (long string of characters)
3. ⚠️ IMPORTANT: Copy it NOW - you only see it once
4. Keep it safe (like a password)
```

---

## Step 2: Add to Top Dog (1 minute)

### Open Auth Tab
```
In Top Dog:
1. Click "LLM Setup" tab
2. Click "Auth" subtab
3. Look for "GitHub Copilot" card
```

### Paste Your Token
```
1. Find the "API Key" input field under GitHub Copilot
2. Paste your token from Step 1
3. The field shows: "••••••••••••" (hidden for security)
4. Click "Save"
```

### Verify
```
After clicking Save:
✓ Green checkmark appears → Token is valid
✗ Red error → Token invalid or incorrect

If error:
  - Make sure you copied the ENTIRE token
  - No extra spaces at beginning/end
  - Create a new token at https://github.com/settings/tokens/new
```

---

## Step 3: Verify It Works

### Check Status
```
Option A: Close & Reopen Top Dog
  → Backend checks Copilot credentials on startup
  → If no modal appears, credentials are valid ✓

Option B: Check Console
  In Top Dog backend console, you should see:
  "✓ GitHub Copilot: Authenticated"
```

### Test Copilot
```
1. Ask Q Assistant a coding question
2. If Copilot is assigned to Q Assistant role:
   → You'll get Copilot responses
3. If Copilot is assigned to Code Generation:
   → You'll get Copilot code completion
```

---

## Common Issues & Fixes

### Problem: "Invalid Token"
```
Check:
□ Did you copy the ENTIRE token (no spaces)?
□ Is it a fresh token (just created)?
□ Expires in the future?

Fix:
1. Go to https://github.com/settings/tokens
2. Delete the old token
3. Create a NEW token
4. Paste in Top Dog
5. Try again
```

### Problem: "Subscription Required"
```
You see: "Not signed up for Copilot"

This means: You don't have active Copilot subscription

Options:
1. Subscribe to Copilot ($20/month)
   → https://github.com/copilot
   
2. Use free Google Gemini instead
   → No subscription needed
   → Same features
```

### Problem: "Token Expires Soon"
```
Top Dog will warn you: "Copilot token expiring in 7 days"

Fix:
1. Go to https://github.com/settings/tokens
2. Click on your Top Dog token
3. Edit expiration date
4. Save
```

### Problem: "Top Dog Not Recognizing Token"
```
Try:
1. Clear browser cache (Ctrl+Shift+Delete)
2. Close Top Dog completely
3. Restart Top Dog
4. Try again

Still not working?
1. Delete token from Top Dog
2. Clear saved credentials
3. Create completely new token
4. Re-add to Top Dog
```

---

## What Happens Next?

### Every Time You Start Top Dog:
```
Backend startup:
  ↓
Check: "Is Copilot token valid?"
  ↓
✓ Yes: Continue normally
✗ No: Show modal "Add Copilot credentials"
```

### You Can Now:
```
✓ Ask Q Assistant coding questions
✓ Get code completions
✓ Use Copilot for code review
✓ Generate code snippets
✓ Debug using Copilot
```

---

## Managing Your Token

### View All Your Tokens
```
Go to: https://github.com/settings/tokens
See all tokens you created
Shows expiration dates
Shows scopes (permissions)
```

### Revoke (Delete) a Token
```
If you want to stop Top Dog from using Copilot:
1. Go to https://github.com/settings/tokens
2. Find "Top Dog Copilot API"
3. Click "Delete"
4. Confirm
Result: Top Dog will no longer work with Copilot
```

### Rotate (Change) a Token
```
If you think your token leaked:
1. Go to https://github.com/settings/tokens
2. Click on token name
3. Edit expiration date to today
4. OR click Delete to remove it
5. Create a new token
6. Update Top Dog with new token
```

---

## Security Tips

### Protect Your Token:
```
✓ DO: Keep it in Top Dog only
✓ DO: Don't share it with others
✓ DO: Don't post it in forums/Discord
✓ DO: Regenerate if you think it's exposed

✗ DON'T: Commit it to Git
✗ DON'T: Put it in environment variables (globally)
✗ DON'T: Share your screen with the token visible
✗ DON'T: Use same token across multiple machines
```

### Top Dog Protects It:
```
✓ Stored in: ~/.Top Dog/llm_credentials.json
✓ Not sent to: Quellum servers
✓ Only sent to: GitHub servers (for API calls)
✓ Encrypted: When possible
✓ Revocable: Anytime at github.com/settings/tokens
```

---

## Costs

### GitHub Copilot:
```
Pricing:
  $20/month OR
  $200/year (save $40)
  
Free for:
  ✓ GitHub students
  ✓ Open source maintainers
  ✓ Teachers
```

### Top Dog:
```
Top Dog itself: FREE
LLM services: Based on usage
  - Copilot: Included with subscription
  - Gemini: Free tier generous
  - OpenAI: Pay-per-token (usually cheap)
```

---

## Alternatives

### If Copilot Isn't Working:

| LLM | Cost | Setup | Features |
|-----|------|-------|----------|
| **Google Gemini** | Free | 2 min | Code generation, Q&A |
| **OpenAI GPT-4** | Pay/use | 3 min | Advanced coding, reasoning |
| **Claude** | Pay/use | 3 min | Long context, analysis |
| **Ollama** | Free | 5 min | Local, offline, no API |

**Simplest:** Google Gemini (completely free, no subscription)
**Most Capable:** OpenAI GPT-4o (best for coding)

---

## Switching Between LLMs

### If You Want to Stop Using Copilot:

**Option 1: Remove Token**
```
1. Go to LLM Setup → Auth tab
2. Find Copilot card
3. Click "Remove"
4. Top Dog will suggest alternatives
```

**Option 2: Reassign Role**
```
1. Go to LLM Setup → Roles tab
2. Find the role using Copilot
3. Change to different LLM (Gemini, OpenAI, etc.)
4. Copilot token still saved but not used
```

---

## Troubleshooting Copilot Responses

### Problem: "Copilot not responding"

Check:
```
1. Token still valid?
   → https://github.com/settings/tokens
   
2. Subscription still active?
   → https://github.com/account/billing/summary
   
3. Role assigned to Copilot?
   → LLM Setup → Roles tab
   
4. Top Dog can reach GitHub?
   → Check internet connection
   → Try ping google.com
   
5. Backend running?
   → Check backend console for errors
```

---

## Next Steps

### You're All Set!
```
✅ Token created
✅ Added to Top Dog
✅ Credentials saved

Now:
1. Ask Q Assistant a question
2. Go to Code tab and test completions
3. Use Copilot for various tasks
4. Report any issues
```

### Want to Add More LLMs?
```
See: LLM_CREDENTIALS_QUICK_REF.md
Or: Go to LLM Setup → Auth tab
    (All providers listed with setup links)
```

---

## Reference

| What | Link |
|------|------|
| Get Copilot | https://github.com/copilot |
| Create Token | https://github.com/settings/tokens/new |
| Manage Tokens | https://github.com/settings/tokens |
| Check Subscription | https://github.com/account/billing/summary |
| Copilot Pricing | https://github.com/copilot/pricing |

---

**Still confused?** Read `GITHUB_COPILOT_API_KEY_EXPLAINED.md` for detailed explanation!
