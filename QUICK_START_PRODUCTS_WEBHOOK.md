# ⚡ QUICK START: CREATE PRODUCTS & CONFIGURE WEBHOOK
**Time to completion**: 30 minutes
**Status**: Follow these 5 steps in order

---

## 🎯 YOUR PUBLIC KEY (Already Have This)
```
pk_test_51SOUvGE9Wrj4s4WewXow3R9iPCitRlegTKqexYp5KAF6gipPy6tJMWQofmCav6sWSHVIqErqLxRdFS1E5O2SgwvW00EreHPqgz
```

---

## ✅ STEP 1: RUN SETUP ASSISTANT (5 mins)

```powershell
cd c:\Quellum-topdog-ide
python stripe_setup_assistant.py
```

This will guide you through:
1. ✓ Creating 9 Stripe products
2. ✓ Collecting Price IDs
3. ✓ Entering API keys
4. ✓ Updating .env file

**What you'll need from Stripe:**
- [ ] Secret Key (sk_test_...)
- [ ] 9 Product Price IDs (price_xxxxx)
- [ ] Webhook Secret (whsec_...)

---

## ✅ STEP 2: CREATE 9 PRODUCTS IN STRIPE (20 mins)

### Quick Reference Table
```
Product 1: PRO          →  $20/month
Product 2: PRO-PLUS     →  $45/month
Product 3: PRO-TEAM     →  $75/month
Product 4: TEAMS-SMALL  →  $75/month
Product 5: TEAMS-MEDIUM →  $300/month
Product 6: TEAMS-LARGE  →  $800/month
Product 7: ENTERPRISE-STANDARD   →  $5,000/month
Product 8: ENTERPRISE-PREMIUM    →  $15,000/month
Product 9: ENTERPRISE-ULTIMATE   →  $50,000/month
```

### For Each Product:
1. Go to: https://dashboard.stripe.com/products
2. Click "Create Product"
3. Enter name (e.g., "PRO")
4. Click "Add Pricing"
5. Enter price (e.g., $20.00)
6. Select "Monthly"
7. Click "Create Product"
8. Copy the **Price ID** (looks like: `price_1SOUvGE9Wrj4s4We`)
9. Save in a text file

---

## ✅ STEP 3: GET YOUR SECRET KEY (2 mins)

1. Go to: https://dashboard.stripe.com/settings/apikeys
2. Under "Secret key"
3. Click "Reveal test key" (if hidden)
4. Copy the entire key (starts with `sk_test_`)
5. Save it - you'll need it in the setup assistant

---

## ✅ STEP 4: RUN SETUP ASSISTANT (5 mins)

```powershell
python stripe_setup_assistant.py
```

**When prompted:**
- Paste your Secret Key: `sk_test_xxxxx`
- Paste each Price ID when asked
- Setup assistant will update your `.env` file automatically

---

## ✅ STEP 5: CREATE WEBHOOK (5 mins)

### 5A: Start ngrok (in new terminal)
```powershell
ngrok http 8000
```

You'll see:
```
Forwarding https://a1b2c3d4e5f6.ngrok.io -> http://localhost:8000
```

### 5B: Create Webhook in Stripe
1. Go to: https://dashboard.stripe.com/webhooks
2. Click "Add Endpoint"
3. Endpoint URL:
   ```
   https://a1b2c3d4e5f6.ngrok.io/api/billing/webhook
   ```
   (Replace with YOUR ngrok URL from 5A)

4. Click "Select events"
5. Enable:
   - ✓ customer.subscription.created
   - ✓ customer.subscription.updated
   - ✓ customer.subscription.deleted
   - ✓ invoice.payment_succeeded
   - ✓ invoice.payment_failed

6. Click "Create endpoint"
7. Copy the "Signing secret" (starts with `whsec_`)

### 5C: Update .env with Webhook Secret
```powershell
# Open in VS Code
code backend\.env
```

Find and update:
```env
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
```

Save the file (Ctrl+S)

---

## ✅ VERIFY EVERYTHING

### Run verification script
```powershell
python PHASE4_VERIFICATION.py
```

This checks:
- ✓ .env file has all keys
- ✓ Stripe API keys are valid
- ✓ Database is ready
- ✓ Backend routes exist
- ✓ Webhook endpoint responds

**Expected output:**
```
✅ Environment variables loaded
✅ Stripe API key valid
✅ Products exist in Stripe
✅ Database schema initialized
✅ Webhook endpoint listening
```

---

## 🚀 TEST PAYMENT

### Terminal 1: Start Backend
```powershell
cd backend
python main.py
```

Should show:
```
Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2: Start Frontend
```powershell
cd frontend
npm run dev
```

Should show:
```
Local: http://localhost:5173
```

### Terminal 3: Keep ngrok Running
```powershell
ngrok http 8000
```

### Browser: Test Payment
1. Go to: http://localhost:5173/pricing
2. Click "Upgrade" on any tier
3. Fill out checkout form
4. Use test card: **4242 4242 4242 4242**
5. Expiry: 12/25
6. CVC: 123
7. Click "Pay"

### Expected Result:
- ✅ Payment processes
- ✅ Success page appears
- ✅ Database updated with tier
- ✅ Webhook received in Stripe Dashboard

---

## 📋 CHECKLIST

- [ ] Created 9 Stripe products
- [ ] Collected all 9 Price IDs
- [ ] Got Secret Key from Stripe
- [ ] Ran setup assistant
- [ ] Updated .env file
- [ ] Started ngrok tunnel
- [ ] Created webhook endpoint
- [ ] Enabled webhook events
- [ ] Copied webhook secret
- [ ] Ran verification script (all passed ✅)
- [ ] Started backend server
- [ ] Started frontend server
- [ ] Tested payment with test card
- [ ] Verified success page
- [ ] Checked database for subscription
- [ ] Checked Stripe Dashboard for webhook event

---

## 🆘 IF SOMETHING FAILS

### ❌ "Invalid Price ID"
- [ ] Copy exact Price ID from Stripe product page
- [ ] Make sure it starts with `price_`
- [ ] Re-run setup assistant

### ❌ "Webhook not received"
- [ ] Is ngrok running? (`ngrok http 8000`)
- [ ] Is ngrok URL correct? (should end with `/api/billing/webhook`)
- [ ] Restart backend after .env update
- [ ] Check webhook logs in Stripe Dashboard

### ❌ "Invalid signature"
- [ ] Copy exact webhook secret from Stripe
- [ ] Make sure it starts with `whsec_`
- [ ] Restart backend after .env update

### ❌ "Payment failed"
- [ ] Use test card: 4242 4242 4242 4242
- [ ] Check backend logs for errors
- [ ] Verify Price ID is correct in product

---

## 📞 NEXT STEPS

After verification passes ✅:

1. Run all 13 test scenarios: `PHASE4_TESTING_GUIDE.md`
2. Review security checklist: `SECURITY_INFRASTRUCTURE_HARDENING.md`
3. Deploy to production (update LIVE keys)

---

## 💰 REVENUE UNLOCKED

| Monthly Users | Tier Mix | Monthly Revenue |
|---------------|----------|-----------------|
| 10 | 5x PRO ($20), 3x PRO-PLUS ($45) | $335 |
| 50 | 20x PRO, 20x PRO-PLUS, 10x PRO-TEAM | $2,200 |
| 100 | 40x PRO, 40x PRO-PLUS, 15x PRO-TEAM, 5x TEAMS | $4,650 |
| 500 | Diversified mix | $25,000+ |
| 1000+ | Full tier adoption | $300,000+ |

**Timeline to revenue:**
- Today: Setup complete
- +4-6 hours: All tests passing
- +1 week: First paying customers
- +1 month: $1K+ MRR
- +3 months: $10K+ MRR
- +1 year: $100K+ MRR

---

**Ready to go?** 🚀

Start with:
```powershell
python stripe_setup_assistant.py
```

