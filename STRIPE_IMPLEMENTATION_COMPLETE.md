# 💳 Stripe Integration - Complete Setup Guide

**Status**: Implementation Complete ✅  
**Timeline**: ~1-2 hours to configure  
**Complexity**: Medium  
**Revenue Impact**: 🚀 Turns Q-IDE into revenue-generating SaaS

---

## 📋 What Was Just Implemented

✅ **Backend Services** (`backend/services/stripe_service.py`)
- Customer creation and management
- Subscription creation and cancellation
- Billing portal management
- Webhook event handling
- Invoice retrieval
- Full error handling

✅ **Database Models** (`backend/models/subscription.py`)
- Subscription table (user plans, status, trial info)
- Invoice table (payment records)
- UsageEvent table (API call tracking)
- BillingAlert table (payment failures, warnings)
- All relationships configured

✅ **API Endpoints** (`backend/routes/billing.py`)
- `GET /api/billing/subscription` - Get current plan
- `POST /api/billing/create-checkout-session` - Start payment
- `POST /api/billing/checkout-success` - Handle successful checkout
- `GET /api/billing/portal` - Billing portal link
- `POST /api/billing/cancel-subscription` - Cancel plan
- `GET /api/billing/invoices` - Payment history
- `POST /api/billing/webhook` - Stripe webhook handler
- `GET /api/billing/admin/stats` - Revenue analytics

✅ **Main App Integration** (`backend/main.py`)
- Billing router registered
- All endpoints accessible at `/api/billing/*`

---

## 🚀 Step 1: Create Stripe Account (5 minutes)

### 1. Sign Up
```
Go to: https://dashboard.stripe.com/register
Sign up with email
Verify email
Add business info
```

### 2. Set Up Bank Account
```
Dashboard → Bank Accounts → Add Account
Add your business bank info
Verify account (2-3 business days)
```

### 3. Get API Keys
```
Go to: https://dashboard.stripe.com/test/apikeys
Copy both keys:
├─ Publishable Key: pk_test_...
└─ Secret Key: sk_test_...
```

**⚠️ IMPORTANT**: Never commit Secret Key to GitHub!

---

## 🔧 Step 2: Configure Environment Variables (5 minutes)

### 1. Set Local Variables
```bash
# In your terminal or .env.development file
export STRIPE_SECRET_KEY="sk_test_..."
export STRIPE_PUBLISHABLE_KEY="pk_test_..."
export STRIPE_WEBHOOK_SECRET="whsec_test_..."  # We'll get this next
export STRIPE_PRICE_ID_PRO="price_..."
export STRIPE_PRICE_ID_TEAMS="price_..."
```

### 2. Create Stripe Products
```
Go to: https://dashboard.stripe.com/products
Click "Add Product"

CREATE PRODUCT 1: "Q-IDE Pro"
├─ Name: Q-IDE Pro
├─ Type: Recurring
├─ Price: $12.00 per month
├─ Click "Save"
└─ Copy Price ID: price_1A2B3C...

CREATE PRODUCT 2: "Q-IDE Teams"
├─ Name: Q-IDE Teams
├─ Type: Recurring
├─ Price: $25.00 per month
├─ Click "Save"
└─ Copy Price ID: price_2D3E4F...
```

### 3. Set Price IDs
```bash
export STRIPE_PRICE_ID_PRO="price_1A2B3C..."
export STRIPE_PRICE_ID_TEAMS="price_2D3E4F..."
```

---

## 🔔 Step 3: Set Up Webhook (10 minutes)

### 1. Install Stripe CLI
```bash
# macOS
brew install stripe/stripe-cli/stripe

# Windows (PowerShell)
choco install stripe-cli
# OR download from: https://github.com/stripe/stripe-cli/releases

# Linux
curl -s https://s3-us-west-2.amazonaws.com/stripe-cli-releases/releases/linux/x86_64/latest/stripe_linux_x86_64.tar.gz -o stripe.tar.gz
tar -zxf stripe.tar.gz
```

### 2. Login to Stripe CLI
```bash
stripe login
# Paste code from dashboard
```

### 3. Get Webhook Secret
```bash
stripe listen --forward-to localhost:8000/api/billing/webhook
# Output: whsec_test_...
```

Copy the webhook secret and set:
```bash
export STRIPE_WEBHOOK_SECRET="whsec_test_..."
```

### 4. Create Webhook in Dashboard
```
Go to: https://dashboard.stripe.com/webhooks
Click "Add Endpoint"

Endpoint URL: https://yourdomain.com/api/billing/webhook
(For local development: use ngrok or Stripe CLI)

Select Events:
✅ customer.subscription.created
✅ customer.subscription.updated
✅ customer.subscription.deleted
✅ invoice.payment_succeeded
✅ invoice.payment_failed
✅ charge.dispute.created

Click "Create Endpoint"
Copy Signing Secret: whsec_live_...
```

---

## 📊 Step 4: Test Stripe Integration Locally (15 minutes)

### 1. Start Backend
```bash
cd backend
python main.py
# Server running on http://localhost:8000
```

### 2. Start Webhook Listener (in another terminal)
```bash
stripe listen --forward-to localhost:8000/api/billing/webhook
# Shows webhook events as they arrive
```

### 3. Test API Endpoints

#### Test 1: Get Free Subscription
```bash
curl -X GET http://localhost:8000/api/billing/subscription \
  -H "Authorization: Bearer YOUR_USER_TOKEN"
```

Expected response:
```json
{
  "tier": "free",
  "status": "active",
  "api_calls_used": 0,
  "api_calls_limit": 100,
  "current_period_end": null,
  "cancel_at": null
}
```

#### Test 2: Create Checkout Session
```bash
curl -X POST http://localhost:8000/api/billing/create-checkout-session \
  -H "Authorization: Bearer YOUR_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "price_id": "price_1A2B3C...",
    "trial_days": 14
  }'
```

Expected response:
```json
{
  "status": "ok",
  "sessionId": "cs_test_..."
}
```

### 4. Test with Stripe Test Cards

Go to checkout URL from sessionId:
```
https://checkout.stripe.com/pay/cs_test_...
```

Use test card:
```
Card Number: 4242 4242 4242 4242
Expiry: 12/25
CVC: 123
```

### 5. Test Webhook Events
```bash
# In terminal with stripe listen running
stripe trigger customer.subscription.created

# Watch webhook arrive in API logs
```

---

## 💻 Step 5: Create Frontend Billing Page (Next)

Will create `frontend/src/pages/BillingPage.tsx` with:
- Current subscription display
- Pricing tier cards
- Upgrade button → Stripe checkout
- Manage billing link
- Invoice history

---

## 🚀 Step 6: Deploy to Production (When Ready)

### 1. Switch to Live Keys
```bash
# Get from https://dashboard.stripe.com/apikeys (switch to Live)
export STRIPE_SECRET_KEY="sk_live_..."
export STRIPE_PUBLISHABLE_KEY="pk_live_..."
```

### 2. Update Webhook
```
Stripe Dashboard → Webhooks
Add New Endpoint:
├─ URL: https://yourdomain.com/api/billing/webhook
├─ Events: Same as before
└─ Save
```

### 3. Deploy to Heroku (or Digital Ocean)
```bash
heroku config:set \
  STRIPE_SECRET_KEY="sk_live_..." \
  STRIPE_PUBLISHABLE_KEY="pk_live_..." \
  STRIPE_WEBHOOK_SECRET="whsec_live_..." \
  STRIPE_PRICE_ID_PRO="price_..." \
  STRIPE_PRICE_ID_TEAMS="price_..." \
  --app q-ide-backend
```

---

## 📈 What This Enables

### Immediate (This Week)
✅ Accept payments from users  
✅ Create subscriptions with trials  
✅ Track billing status  
✅ Send invoices  
✅ Handle failed payments  

### Next Week
✅ Revenue dashboard  
✅ Email notifications  
✅ Usage tracking and limits  
✅ Automatic dunning (retry failed payments)  

### By Month End
✅ Multiple pricing tiers  
✅ Enterprise custom pricing  
✅ Team billing  
✅ Annual payment discounts  

---

## 🔐 Security Checklist

- [ ] Never commit Secret Key to git
- [ ] Use environment variables for all keys
- [ ] Verify webhook signatures (code already does this)
- [ ] Validate customer ownership before updating
- [ ] Test webhook with invalid signatures
- [ ] Monitor for suspicious activity
- [ ] Enable fraud detection in Stripe Dashboard

---

## ❓ Common Issues & Solutions

### Issue: Webhook Not Triggering
**Solution**: 
- Check endpoint is accessible from internet
- Verify webhook secret matches
- Look at webhook delivery logs in Stripe Dashboard

### Issue: Checkout Returns Wrong Status
**Solution**:
- Verify price_id is correct
- Check STRIPE_PRICE_ID_* env vars
- Test with hardcoded price ID first

### Issue: Subscription Not Created After Payment
**Solution**:
- Check webhook is receiving events
- Verify database connection
- Check logs for errors

### Issue: "Invalid API Key"
**Solution**:
- Confirm key is set in environment
- Make sure you're using SECRET key (not publishable)
- In dev, switch from sk_live_ to sk_test_

---

## 📞 Next Steps

1. **This Week**:
   - [ ] Create Stripe account
   - [ ] Configure environment variables
   - [ ] Set up webhook
   - [ ] Test locally with test cards

2. **Next Week**:
   - [ ] Build frontend Billing page
   - [ ] Test full checkout flow
   - [ ] Set up monitoring/alerts

3. **Production**:
   - [ ] Switch to live keys
   - [ ] Deploy to Digital Ocean
   - [ ] Enable payment method verification
   - [ ] Set up PCI compliance

---

**You now have a complete payment system. Ready to make money! 💰**

Questions? Check Stripe docs: https://stripe.com/docs
