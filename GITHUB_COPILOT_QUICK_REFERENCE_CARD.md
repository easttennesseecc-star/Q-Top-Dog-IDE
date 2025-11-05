# 🎴 GitHub Copilot Setup - Quick Reference Card

## Print This Or Bookmark!

---

## ⚡ 3-MINUTE SETUP

### STEP 1 → CREATE TOKEN (2 min)
```
1. Go: https://github.com/settings/tokens/new
2. Name: "Top Dog Copilot API"
3. Scope: ✓ user:read, ✓ write:packages, ✓ read:packages
4. Click: "Generate token"
5. COPY the token (you only see it ONCE!)
```

### STEP 2 → ADD TO Top Dog (1 min)
```
1. Top Dog → LLM Setup tab
2. Click: Auth subtab
3. Find: GitHub Copilot card
4. Paste: Your token
5. Click: Save
6. See: Green ✓ checkmark
```

### STEP 3 → DONE!
```
1. Restart Top Dog
2. No modal = Copilot ready ✓
3. Start using!
```

---

## ❓ COMMON PROBLEMS

| Problem | Solution |
|---------|----------|
| "Invalid token" | Copy ENTIRE token (no spaces), try again |
| Red X mark | Token might be fake, create new one |
| "Subscription required" | Need Copilot ($20/mo) OR use Gemini (free) |
| Token expires | Go to github.com/settings/tokens, extend date |
| Copilot not responding | Check github.com/account/billing/summary |

---

## 🔑 API KEY vs OAUTH

| Factor | OAuth (VS Code) | API Key (Top Dog) |
|--------|-----------------|-----------------|
| What | Browser login | Copy-paste token |
| Time | 2 min | 3 min |
| Security | High | Higher (revocable) |
| Why needed | Official software | Local app |
| Revoke | Complex | 1 click delete |

---

## 🆓 FREE ALTERNATIVE

### If No Copilot Subscription:
```
Use: Google Gemini (completely FREE)

Go: https://makersuite.google.com/app/apikeys
Setup: 2 minutes
Cost: $0
Same features for coding
```

---

## 🔐 SECURITY CHECKLIST

```
☑ Token only in Top Dog (not email/chat)
☑ Never commit to Git
☑ Don't share on Discord/forums
☑ Can revoke anytime (github.com/settings/tokens)
☑ Each machine gets own token
☑ Expires automatically (configure in GitHub)
```

---

## 📱 REMEMBER

**You're not creating a Top Dog account.**
You're giving Top Dog permission to use your Copilot.

**API Key is like a:** 
- Netflix access card (you control)
- Temporary permission slip (you can revoke)
- App-specific password (different for each app)

---

## 🔗 QUICK LINKS

| What | Link |
|------|------|
| Create Token | https://github.com/settings/tokens/new |
| Manage Tokens | https://github.com/settings/tokens |
| Check Subscription | https://github.com/account/billing/summary |
| Get Gemini Key | https://makersuite.google.com/app/apikeys |

---

## ✅ VERIFICATION

After setup, you should see:

```
Backend Console:
  ✓ "GitHub Copilot: Authenticated"

Top Dog Frontend:
  ✓ Auth tab shows green checkmark
  
When asking Q Assistant:
  ✓ Gets Copilot responses
```

---

## 📞 STILL STUCK?

**Read:** `GITHUB_COPILOT_SETUP_GUIDE.md` (full version)
**Or:** `GITHUB_COPILOT_API_KEY_EXPLAINED.md` (why it works)
**Or:** Check `LLM_CREDENTIALS_QUICK_REF.md` (all options)

---

## 📋 CREDENTIALS STORAGE

```
Location: ~/.Top Dog/llm_credentials.json
Permissions: Read/write only (encrypted if possible)
Scope: Local only (never sent to Quellum)
Backup: Manual backup recommended
```

---

## ⏰ TOKEN LIFECYCLE

```
You create token
  ↓
Token valid for N days (you choose)
  ↓
Top Dog uses it every startup
  ↓
Token expires → Top Dog prompts you
  ↓
You extend date OR create new token
```

---

## 🎯 DECISION TREE

```
Do I have Copilot subscription?
├─ YES
│  └─ Create API token
│     └─ Follow 3-step setup
│     └─ Use Copilot!
│
└─ NO
   ├─ Get subscription ($20/mo)
   │  └─ Create API token
   │  └─ Use Copilot
   │
   └─ Use free Gemini instead
      └─ Get Gemini key
      └─ Same 3-step setup
      └─ Use Gemini!
```

---

## 📊 COSTS COMPARISON

| Service | Cost | Subscription | Setup |
|---------|------|--------------|-------|
| Copilot | Included | $20/mo | 3 min |
| Gemini | FREE | None | 2 min |
| GPT-4 | Pay/use | None | 3 min |
| Claude | Pay/use | None | 3 min |
| Ollama | FREE | None | 5 min |

---

## 🔄 ROTATING TOKEN

If you think token leaked:

```
1. Go: github.com/settings/tokens
2. Find: "Top Dog Copilot API"
3. Click: "Delete"
4. Confirm: Delete
5. Create: New token
6. Update: Top Dog with new token
7. Done: Takes 1 minute
```

---

## ✨ PRO TIPS

```
✓ Store token in secure password manager
✓ Create separate tokens per machine
✓ Set expiration to 90 days (automatic rotation)
✓ Comment tokens (which machine/date)
✓ Review tokens monthly
✓ Use different LLMs for different tasks
✓ Keep Gemini as backup (free alternative)
```

---

## 🚨 WHAT NOT TO DO

```
✗ Don't share token with others
✗ Don't post token online
✗ Don't email token
✗ Don't use same token across multiple apps
✗ Don't commit to Git
✗ Don't use permanent expiration (rotate regularly)
✗ Don't ignore expiration warnings
```

---

## 🎓 UNDERSTAND THE FLOW

```
GitHub Copilot
  │
  ├─ Option 1: VS Code Extension (Browser OAuth)
  │  └─ Use: Click button → browser login
  │  └─ Better for: Using directly in VS Code
  │
  └─ Option 2: API Key (Programmatic)
     └─ Use: Copy/paste token into app
     └─ Better for: Using in Top Dog or other apps
     └─ Same: All features available
     └─ Why Top Dog: Local app needs explicit permission
```

---

## 📝 TROUBLESHOOTING CHECKLIST

```
□ Token is complete (no truncation)
□ Token is fresh (just created)
□ Copilot subscription is active
□ Top Dog auth tab shows token
□ Browser shows green checkmark
□ Restart Top Dog
□ Check console for errors
□ Verify internet connection
□ Try creating new token
```

---

## 🎉 SUCCESS INDICATORS

You've succeeded when:

```
✅ Top Dog shows green checkmark
✅ No "missing credentials" modal
✅ Q Assistant responds with Copilot
✅ Code generation uses Copilot
✅ Backend logs show "Authenticated"
✅ No errors in console
```

---

## 🔍 VERIFY INSTALLATION

Run these checks:

```
1. Check LLM Setup → Auth tab
   → Green ✓ next to GitHub Copilot

2. Check Backend Console
   → Should see: "✓ GitHub Copilot: Authenticated"

3. Ask Q Assistant a question
   → Should get Copilot response

4. Go to https://github.com/settings/tokens
   → Should see "Top Dog Copilot API" token listed
```

---

## 📖 FULL DOCUMENTATION

**Quick Setup:** `GITHUB_COPILOT_SETUP_GUIDE.md`
**Why API Key:** `GITHUB_COPILOT_API_KEY_EXPLAINED.md`
**Visual Guide:** `GITHUB_OAUTH_VS_API_KEY_VISUAL.md`
**Index:** `GITHUB_COPILOT_DOCUMENTATION_INDEX.md`

---

## ✏️ NOTES

```
Created: October 28, 2025
Project: Top Dog
LLM: GitHub Copilot API
Status: Ready to Use
Support: See full documentation
```

---

**SAVE THIS CARD FOR QUICK REFERENCE!**

Bookmark or print for easy access during setup.
