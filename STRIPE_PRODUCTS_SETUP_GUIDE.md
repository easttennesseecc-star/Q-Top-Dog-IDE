# 🎯 STRIPE PRODUCTS & WEBHOOK SETUP GUIDE

**Status**: Step-by-step walkthrough for creating 10 Stripe products
**Time**: 30 minutes
**Your API Key**: `pk_test_51SOUvGE9Wrj4s4WewXow3R9iPCitRlegTKqexYp5KAF6gipPy6tJMWQofmCav6sWSHVIqErqLxRdFS1E5O2SgwvW00EreHPqgz`

---

## 📋 THE 10 TIER PRICING STRUCTURE

Your system has 10 tiers that need Stripe products:

| Tier # | Tier Name | Monthly Price | Billing |
|--------|-----------|---------------|---------|
| 1 | FREE | $0 | (No product needed) |
| 2 | PRO | $20 | Monthly |
| 3 | PRO-PLUS | $45 | Monthly |
| 4 | PRO-TEAM | $75 | Monthly |
| 5 | TEAMS-SMALL | $75 | Monthly |
| 6 | TEAMS-MEDIUM | $300 | Monthly |
| 7 | TEAMS-LARGE | $800 | Monthly |
| 8 | ENTERPRISE-STANDARD | $5,000 | Monthly |
| 9 | ENTERPRISE-PREMIUM | $15,000 | Monthly |
| 10 | ENTERPRISE-ULTIMATE | $50,000 | Monthly |

**Total**: 9 paid products + 1 free tier = 10 tiers

---

## ✅ STEP 1: GET YOUR STRIPE KEYS

### 1.1 Log in to Stripe Dashboard
```
https://dashboard.stripe.com/login
```

### 1.2 Get API Keys
```
Go to: Settings (gear icon) → API Keys

You need these 4 keys:

📌 TEST MODE KEYS (for development):
- Publishable Key (pk_test_...): pk_test_51SOUvGE9Wrj4s4WewXow3R9iPCitRlegTKqexYp5KAF6gipPy6tJMWQofmCav6sWSHVIqErqLxRdFS1E5O2SgwvW00EreHPqgz
- Secret Key (sk_test_...): **SAVE IN .env FILE** ⚠️
- Webhook Signing Secret (whsec_...): **WILL CREATE BELOW**

📌 LIVE MODE KEYS (for production):
- Publishable Key (pk_live_...)
- Secret Key (sk_live_...)
- These will be different from test keys!
```

### 1.3 Copy Your Secret Key
```
In Stripe Dashboard:
Settings → API Keys → Reveal Live Key under "Secret key"

Click "Reveal test key" button
Copy the entire key (starts with sk_test_)
Save to backend/.env as: STRIPE_SECRET_KEY=sk_test_xxxx
```

---

## ✅ STEP 2: CREATE 9 STRIPE PRODUCTS

### 2.1 Navigate to Products
```
Stripe Dashboard → Products → Create Product
```

### 2.2 CREATE PRODUCT 1: PRO ($20/mo)

**Step 1**: Click "Create Product"

**Step 2**: Fill out:
```
Name: PRO
Description: Individual developer with API access
Type: Service (default)
```

**Step 3**: Under "Pricing", click "Add Pricing":
```
Price: $20.00
Billing period: Monthly
Tax behavior: Unspecified (or set as needed)
```

**Step 4**: Click "Create Product"

**Step 5**: Copy the Price ID
```
After creation, click on the product
Look for "Price ID" field (looks like: price_1SOUvGE9Wrj4s4WehxxxxxX)
⚠️ SAVE THIS! You'll need it.
```

---

### 2.3 CREATE PRODUCT 2: PRO-PLUS ($45/mo)

Repeat the same process for:

| Product Name | Price | Description |
|--------------|-------|-------------|
| PRO-PLUS | $45.00 | Custom LLMs + Advanced features |

---

### 2.4 CREATE PRODUCT 3: PRO-TEAM ($75/mo)

| Product Name | Price | Description |
|--------------|-------|-------------|
| PRO-TEAM | $75.00 | Team collaboration (3 members) |

---

### 2.5 CREATE PRODUCT 4: TEAMS-SMALL ($75/mo)

| Product Name | Price | Description |
|--------------|-------|-------------|
| TEAMS-SMALL | $75.00 | Teams plan (5 members) |

---

### 2.6 CREATE PRODUCT 5: TEAMS-MEDIUM ($300/mo)

| Product Name | Price | Description |
|--------------|-------|-------------|
| TEAMS-MEDIUM | $300.00 | Teams plan (15 members) |

---

### 2.7 CREATE PRODUCT 6: TEAMS-LARGE ($800/mo)

| Product Name | Price | Description |
|--------------|-------|-------------|
| TEAMS-LARGE | $800.00 | Teams plan (unlimited members) |

---

### 2.8 CREATE PRODUCT 7: ENTERPRISE-STANDARD ($5,000/mo)

| Product Name | Price | Description |
|--------------|-------|-------------|
| ENTERPRISE-STANDARD | $5,000.00 | Enterprise (HIPAA Ready, SOC2) |

---

### 2.9 CREATE PRODUCT 8: ENTERPRISE-PREMIUM ($15,000/mo)

| Product Name | Price | Description |
|--------------|-------|-------------|
| ENTERPRISE-PREMIUM | $15,000.00 | Enterprise (SSO/SAML + Compliance) |

---

### 2.10 CREATE PRODUCT 9: ENTERPRISE-ULTIMATE ($50,000/mo)

| Product Name | Price | Description |
|--------------|-------|-------------|
| ENTERPRISE-ULTIMATE | $50,000.00 | Enterprise (On-Premise + Data Residency) |

---

## 📝 STEP 3: COLLECT ALL PRICE IDs

After creating all 9 products, you'll have 9 Price IDs. Collect them in this format:

```
STRIPE_PRICE_ID_PRO=price_xxxxxxxxxxxx
STRIPE_PRICE_ID_PRO_PLUS=price_xxxxxxxxxxxx
STRIPE_PRICE_ID_PRO_TEAM=price_xxxxxxxxxxxx
STRIPE_PRICE_ID_TEAMS_SMALL=price_xxxxxxxxxxxx
STRIPE_PRICE_ID_TEAMS_MEDIUM=price_xxxxxxxxxxxx
STRIPE_PRICE_ID_TEAMS_LARGE=price_xxxxxxxxxxxx
STRIPE_PRICE_ID_ENTERPRISE_STANDARD=price_xxxxxxxxxxxx
STRIPE_PRICE_ID_ENTERPRISE_PREMIUM=price_xxxxxxxxxxxx
STRIPE_PRICE_ID_ENTERPRISE_ULTIMATE=price_xxxxxxxxxxxx
```

---

## 🔐 STEP 4: CREATE WEBHOOK ENDPOINT

### 4.1 Navigate to Webhooks
```
Stripe Dashboard → Developers (top right) → Webhooks
```

### 4.2 Click "Add Endpoint"

### 4.3 Fill in Webhook Details

**Endpoint URL**:
```
For development (local testing):
https://ngrok-tunnel-url/api/billing/webhook

For production:
https://yourdomain.com/api/billing/webhook
```

**Note**: If you don't have ngrok set up yet, use:
```
https://localhost:8000/api/billing/webhook
```
(You'll need to expose it via ngrok or similar tunnel for Stripe to reach it)

### 4.4 Select Events to Receive

Click "Select events" and enable:

```
✅ customer.subscription.created
✅ customer.subscription.updated
✅ customer.subscription.deleted
✅ invoice.payment_succeeded
✅ invoice.payment_failed
✅ charge.dispute.created
✅ charge.refunded
```

### 4.5 Create the Endpoint

Click "Create endpoint"

### 4.6 Get Your Webhook Secret

After creating:
```
Click on the webhook
Look for "Signing secret"
It looks like: whsec_1234567890abcdef

⚠️ SAVE THIS! Click "Reveal" if needed
```

---

## 🔧 STEP 5: UPDATE YOUR .env FILE

### 5.1 Open `backend/.env`

```bash
cd c:\Quellum-topdog-ide\backend
```

### 5.2 Add These Lines

```env
# ===== STRIPE CONFIGURATION =====

# Test Mode Keys (for development)
STRIPE_PUBLIC_KEY=pk_test_51SOUvGE9Wrj4s4WewXow3R9iPCitRlegTKqexYp5KAF6gipPy6tJMWQofmCav6sWSHVIqErqLxRdFS1E5O2SgwvW00EreHPqgz
STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET_HERE

# Price IDs - Map each tier to its Stripe price ID
STRIPE_PRICE_ID_PRO=price_xxxxxxxxxxxxx
STRIPE_PRICE_ID_PRO_PLUS=price_xxxxxxxxxxxxx
STRIPE_PRICE_ID_PRO_TEAM=price_xxxxxxxxxxxxx
STRIPE_PRICE_ID_TEAMS_SMALL=price_xxxxxxxxxxxxx
STRIPE_PRICE_ID_TEAMS_MEDIUM=price_xxxxxxxxxxxxx
STRIPE_PRICE_ID_TEAMS_LARGE=price_xxxxxxxxxxxxx
STRIPE_PRICE_ID_ENTERPRISE_STANDARD=price_xxxxxxxxxxxxx
STRIPE_PRICE_ID_ENTERPRISE_PREMIUM=price_xxxxxxxxxxxxx
STRIPE_PRICE_ID_ENTERPRISE_ULTIMATE=price_xxxxxxxxxxxxx

# Frontend URL (for Stripe redirect after payment)
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000

# Optional: Live mode keys (after testing)
# STRIPE_LIVE_PUBLIC_KEY=pk_live_xxxx
# STRIPE_LIVE_SECRET_KEY=sk_live_xxxx
# STRIPE_LIVE_WEBHOOK_SECRET=whsec_live_xxxx
```

### 5.3 Save the File

```bash
# Save: Ctrl+S (in VS Code)
```

---

## 🔗 STEP 6: EXPOSE WEBHOOK LOCALLY (ngrok Setup)

### 6.1 Install ngrok (if not already installed)

```powershell
# Using Chocolatey
choco install ngrok

# Or download: https://ngrok.com/download
```

### 6.2 Start ngrok Tunnel

```powershell
# In a new terminal, expose your backend on port 8000
ngrok http 8000
```

### 6.3 Update Webhook URL

```
ngrok will show you a tunnel URL like:
https://a1b2c3d4e5f6.ngrok.io

Update your webhook endpoint to:
https://a1b2c3d4e5f6.ngrok.io/api/billing/webhook

Go back to Stripe → Webhooks → Click your endpoint → Update Endpoint URL
```

---

## 📋 STEP 7: VERIFY EVERYTHING

### 7.1 Test Your Stripe Connection

```powershell
cd c:\Quellum-topdog-ide\backend

# Run verification
python PHASE4_VERIFICATION.py
```

This will check:
- ✅ Stripe API keys are valid
- ✅ All products exist in Stripe
- ✅ All price IDs are correct
- ✅ Webhook endpoint is reachable
- ✅ Database is ready

---

## 🎯 STEP 8: QUICK TEST PAYMENT

### 8.1 Start Your Backend

```powershell
cd c:\Quellum-topdog-ide\backend
python main.py
```

### 8.2 Start Your Frontend

```powershell
cd c:\Quellum-topdog-ide\frontend
npm run dev
```

### 8.3 Go to Pricing Page

```
http://localhost:5173/pricing
```

### 8.4 Click "Upgrade" Button

Select any tier (e.g., PRO for $20/mo)

### 8.5 Use Stripe Test Card

In the checkout form, use:
```
Card Number: 4242 4242 4242 4242
Expiry: 12/25
CVC: 123
```

### 8.6 Complete Payment

Click "Pay Now"

You should see:
- ✅ Payment processed
- ✅ Subscription created in database
- ✅ Redirect to success page
- ✅ User tier updated to PRO

---

## ✅ CHECKLIST

- [ ] Created Stripe account
- [ ] Copied public key
- [ ] Copied secret key to `.env`
- [ ] Created 9 Stripe products
- [ ] Collected all 9 Price IDs
- [ ] Added Price IDs to `.env`
- [ ] Created webhook endpoint
- [ ] Copied webhook secret to `.env`
- [ ] Started ngrok tunnel
- [ ] Updated webhook URL in Stripe
- [ ] Ran PHASE4_VERIFICATION.py (passed ✅)
- [ ] Started backend server
- [ ] Started frontend server
- [ ] Tested payment with card: 4242 4242 4242 4242
- [ ] Verified subscription created in database
- [ ] Checked webhook log in Stripe dashboard

---

## 🆘 TROUBLESHOOTING

### Problem: "Invalid Price ID"
**Solution**: Copy the exact Price ID from Stripe product page. Make sure you copied the `Price ID`, not the product ID.

### Problem: "Webhook not being received"
**Solution**: 
1. Make sure ngrok is running: `ngrok http 8000`
2. Update webhook URL to ngrok URL in Stripe
3. Check webhook logs in Stripe dashboard
4. Make sure backend is running

### Problem: "Card declined during test"
**Solution**: Use the test card `4242 4242 4242 4242` for successful payments.
Other test cards:
```
4000 0025 0000 3155  → Requires authentication (3D Secure)
4000 0000 0000 0002  → Card declined
5555 5555 5555 4444  → Mastercard test
```

### Problem: ".env file not being read"
**Solution**: 
1. Make sure backend is in `backend/` folder
2. Make sure file is named `.env` (with dot)
3. Restart backend after editing `.env`
4. Check file has no BOM (use UTF-8 encoding)

---

## 📞 NEXT STEPS

✅ After completing this guide:

1. Run all 13 test scenarios from `PHASE4_TESTING_GUIDE.md`
2. Configure production Stripe keys when ready
3. Set up real domain instead of localhost
4. Deploy to production

---

**Status**: Ready to create products! 🚀
**Time Spent**: ~5 minutes setup, 20 minutes product creation = 25 minutes total
**Next**: 13 test scenarios (1 hour)

