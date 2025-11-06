# 🔐 SECRETS FILE UPDATE GUIDE

**File to Update:** `k8s/02-secrets.yaml`

---

## 📋 Required Credentials

### 1. DATABASE_PASSWORD ✅ (YOU NEED TO CREATE)

**What:** PostgreSQL database password  
**Format:** Any secure string (32+ characters recommended)  
**How to create:**

**Option A - PowerShell:**
```powershell
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})
```

**Option B - Online:** https://www.random.org/strings/

**Example:**
```
aBc1DeF2gHi3JkL4mNo5PqR6sTu7VwX8yZ9
```

---

### 2. STRIPE_SECRET_KEY ✅ (FROM STRIPE DASHBOARD)

**What:** Stripe API secret key  
**Format:** `sk_live_...` (starts with sk_live)  
**Where to get:**
1. Go to: https://dashboard.stripe.com/apikeys
2. Copy the "Secret key" (the one starting with `sk_live_`)
3. Keep it secret!

---

### 3. STRIPE_WEBHOOK_SECRET ✅ (FROM STRIPE WEBHOOKS)

**What:** Stripe webhook signing secret  
**Format:** `whsec_live_...`  
**Where to get:**
1. Go to: https://dashboard.stripe.com/webhooks
2. Click on your webhook (or create one: https://dashboard.stripe.com/webhooks/create)
3. Endpoint URL should be: `https://api.Top Dog.com/stripe/webhook`
4. Click "Reveal" next to "Signing secret"
5. Copy the secret (starts with `whsec_live_`)

---

### 4. STRIPE_PUBLISHABLE_KEY ✅ (FROM STRIPE DASHBOARD)

**What:** Stripe public key (safe to share)  
**Format:** `pk_live_...`  
**Where to get:**
1. Go to: https://dashboard.stripe.com/apikeys
2. Copy the "Publishable key" (the one starting with `pk_live_`)

**Example:**
```
pk_live_51PqR6sTu7VwX8yZ9aBc1DeF2gHi3JkL4mNo5PqR6sTu7VwX8yZ9aBc1DeF2gHi3JkL4mNo5PqR6sTu7VwX8yZ9aBc1DeF2gHi3JkL4mNo5
```

---

### 5. STRIPE_PRICE_ID_PRO ✅ (FROM STRIPE PRODUCTS)

**What:** Stripe price ID for Pro tier  
**Format:** `price_1...` (alphanumeric)  
**Where to get:**
1. Go to: https://dashboard.stripe.com/products
2. Click on your "Pro" product
3. Scroll to "Pricing" section
4. Copy the Price ID (looks like: `price_1P5YzF4x...`)

**If product doesn't exist yet:**
- Create a new Product called "Pro"
- Add a price
- Copy the Price ID

**Example:**
```
price_1P5YzF4xKqR6sTu7VwX8yZ9aBc1DeF2
```

---

### 6. STRIPE_PRICE_ID_TEAM ✅ (FROM STRIPE PRODUCTS)

**What:** Stripe price ID for Team tier  
**Format:** `price_1...`  
**Where to get:** Same as Pro, but for "Team" product

**Example:**
```
price_1P5ZaG5xKqR6sTu7VwX8yZ9aBc1DeF3
```

---

### 7. STRIPE_PRICE_ID_ENTERPRISE ✅ (FROM STRIPE PRODUCTS)

**What:** Stripe price ID for Enterprise tier  
**Format:** `price_1...`  
**Where to get:** Same as Pro, but for "Enterprise" product

**Example:**
```
price_1P5ZbH6xKqR6sTu7VwX8yZ9aBc1DeF4
```

---

### 8. JWT_SECRET ✅ (YOU NEED TO CREATE)

**What:** Secret key for JWT token signing  
**Format:** Any random secure string (32+ characters)  
**How to create:**

**Option A - PowerShell:**
```powershell
[Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | % {[char]$_}))))
```

**Option B - Online:** https://www.random.org/strings/

**Example:**
```
abc123def456ghi789jkl012mno345pqr678stu901vwx234yz567ABC890
```

---

### 9. OPENAI_API_KEY (Optional - only if using OpenAI)

**What:** OpenAI API key  
**Format:** `sk-...`  
**Where to get:** https://platform.openai.com/api-keys

**If not using:** Leave as `CHANGE_ME_IF_USING_OPENAI`

---

### 10. ANTHROPIC_API_KEY (Optional - only if using Anthropic)

**What:** Anthropic Claude API key  
**Format:** `sk-ant-...`  
**Where to get:** https://console.anthropic.com/account/keys

**If not using:** Leave as `CHANGE_ME_IF_USING_ANTHROPIC`

---

### 11. GOOGLE_API_KEY (Optional - only if using Google)

**What:** Google API key  
**Format:** `AIza...`  
**Where to get:** https://console.cloud.google.com/apis/credentials

**If not using:** Leave as `CHANGE_ME_IF_USING_GOOGLE`

---

## 🚀 QUICK REFERENCE

### Required (Must replace):
- [x] DATABASE_PASSWORD
- [x] STRIPE_SECRET_KEY
- [x] STRIPE_WEBHOOK_SECRET
- [x] STRIPE_PUBLISHABLE_KEY
- [x] STRIPE_PRICE_ID_PRO
- [x] STRIPE_PRICE_ID_TEAM
- [x] STRIPE_PRICE_ID_ENTERPRISE
- [x] JWT_SECRET

### Optional (Can leave as-is):
- [ ] OPENAI_API_KEY
- [ ] ANTHROPIC_API_KEY
- [ ] GOOGLE_API_KEY

---

## ✅ CHECKLIST

**Before updating:**
- [ ] I have my DATABASE_PASSWORD ready
- [ ] I have my Stripe API keys ready
- [ ] I have my Stripe webhook secret ready
- [ ] I have my Stripe price IDs ready
- [ ] I have my JWT_SECRET ready

**After updating:**
- [ ] I've replaced all 8 required CHANGE_ME values
- [ ] I've saved the file
- [ ] I'm ready to deploy!

---

## 📝 HOW TO UPDATE

**Option 1: Edit in VS Code**
```powershell
code k8s/02-secrets.yaml
# Edit the values
# Ctrl+S to save
# Ctrl+W to close
```

**Option 2: Copy your values**
Have all values ready, then I'll update the file for you.

---

## ⚠️ SECURITY NOTES

✅ **DO:**
- Use strong, random passwords
- Keep secrets in a safe place
- Never commit secrets to git (k8s/02-secrets.yaml should be in .gitignore)
- Rotate secrets periodically

❌ **DON'T:**
- Commit secrets to GitHub
- Share secrets in chat/email
- Use simple/guessable passwords
- Reuse secrets across environments

---

**Ready?** Gather your credentials and let me know when you're ready to update the file!

