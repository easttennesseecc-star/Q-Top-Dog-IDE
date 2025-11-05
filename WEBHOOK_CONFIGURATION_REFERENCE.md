# 🔗 STRIPE WEBHOOK CONFIGURATION REFERENCE

## Your Public Key (Already Saved)
```
pk_test_51SOUvGE9Wrj4s4WewXow3R9iPCitRlegTKqexYp5KAF6gipPy6tJMWQofmCav6sWSHVIqErqLxRdFS1E5O2SgwvW00EreHPqgz
```

---

## Webhook Events Configuration

When creating your webhook endpoint in Stripe, enable these events:

### Required Events (Core Payment Processing)
```
✅ customer.subscription.created    → When user upgrades to paid tier
✅ customer.subscription.updated    → When user changes tier
✅ customer.subscription.deleted    → When user downgrades or cancels
✅ invoice.payment_succeeded        → When payment is successful
✅ invoice.payment_failed           → When payment fails
```

### Recommended Events (Additional Protection)
```
✅ charge.dispute.created           → Chargeback protection
✅ charge.refunded                  → Handle refunds
✅ customer.created                 → Track new Stripe customers
```

---

## Webhook Payload Handling

Your backend at `/api/billing/webhook` will receive JSON like:

### Example: Subscription Created
```json
{
  "id": "evt_1234567890",
  "object": "event",
  "type": "customer.subscription.created",
  "data": {
    "object": {
      "id": "sub_1234567890",
      "customer": "cus_1234567890",
      "status": "active",
      "items": {
        "data": [
          {
            "price": {
              "id": "price_1234567890",
              "unit_amount": 2000,
              "currency": "usd"
            }
          }
        ]
      },
      "current_period_start": 1698768000,
      "current_period_end": 1701446400,
      "trial_end": null
    }
  }
}
```

---

## Your Backend Webhook Handler

Location: `backend/routes/billing.py`

The webhook endpoint automatically:
1. ✅ Verifies Stripe signature (using STRIPE_WEBHOOK_SECRET)
2. ✅ Handles subscription creation → Updates user tier in database
3. ✅ Handles subscription updates → Updates tier if changed
4. ✅ Handles subscription deletion → Downgrades to FREE tier
5. ✅ Handles payment success → Updates subscription status
6. ✅ Handles payment failure → Alerts user to update payment method

---

## Testing Your Webhook Locally

### Option 1: Using Stripe CLI (Recommended)
```bash
# Install Stripe CLI
# https://stripe.com/docs/stripe-cli

# Login to Stripe
stripe login

# Forward webhooks to your local backend
stripe listen --forward-to localhost:8000/api/billing/webhook

# This gives you a webhook signing secret:
# whsec_test_...
```

### Option 2: Using ngrok (Quick & Easy)
```bash
# Start ngrok
ngrok http 8000

# Update webhook URL in Stripe to:
# https://YOUR_NGROK_URL.ngrok.io/api/billing/webhook
```

### Option 3: Using Stripe Dashboard Test Events
```
1. Stripe Dashboard → Webhooks → Select your endpoint
2. Click "Send test event"
3. Choose event type (e.g., customer.subscription.created)
4. Click "Send event"
5. Check logs in Stripe Dashboard
```

---

## Webhook Signature Verification

Your backend verifies webhook authenticity:

```python
# In backend/routes/billing.py

@router.post("/webhook")
async def handle_webhook(request):
    # 1. Get raw request body
    body = await request.body()
    
    # 2. Get signature header
    sig = request.headers.get("stripe-signature")
    
    # 3. Verify signature using webhook secret
    event = stripe.Webhook.construct_event(
        body,
        sig,
        STRIPE_WEBHOOK_SECRET
    )
    
    # 4. Process event
    if event["type"] == "customer.subscription.created":
        # Handle subscription creation
        pass
```

---

## Debugging Webhooks

### In Stripe Dashboard
```
1. Go to: Webhooks
2. Click on your endpoint
3. Scroll to "Events" section
4. Click on an event to see:
   - Request body (what Stripe sent)
   - Response status (200 = success)
   - Response body (what your server returned)
```

### Common Issues

#### ❌ Webhook not being received
- [ ] Is ngrok running? (`ngrok http 8000`)
- [ ] Is ngrok URL correct in Stripe? (should end with `/api/billing/webhook`)
- [ ] Is backend running? (`python main.py`)
- [ ] Is STRIPE_WEBHOOK_SECRET in .env?

#### ❌ "Invalid signature" error
- [ ] Copy EXACT webhook secret from Stripe Dashboard
- [ ] Make sure it starts with `whsec_`
- [ ] Restart backend after updating .env

#### ❌ Webhook "failing" (not 200)
- [ ] Check webhook response in Stripe Dashboard
- [ ] Check backend logs for errors
- [ ] Verify database connection
- [ ] Check subscription table exists

---

## Production Webhook Setup

When deploying to production:

### 1. Get Live Webhook Secret
```
Stripe Dashboard (Live mode) → Webhooks → Create endpoint

Use your production domain:
https://yourdomain.com/api/billing/webhook
```

### 2. Update .env with Live Secret
```
STRIPE_WEBHOOK_SECRET=whsec_live_1234567890
```

### 3. Enable HTTPS (Required by Stripe)
```
Your backend must be HTTPS in production
(HTTP only works in test mode)
```

### 4. Update DNS
```
Make sure DNS points to your backend server
yourdomain.com → Your backend IP
```

---

## Database Updates on Webhook

When a webhook is received, your system:

### On `customer.subscription.created`
```sql
INSERT INTO user_subscriptions (
    user_id,
    stripe_customer_id,
    stripe_subscription_id,
    tier,
    status,
    current_period_start,
    current_period_end,
    trial_end
)
VALUES (...)

UPDATE users SET tier = 'pro' WHERE user_id = ...
```

### On `customer.subscription.updated`
```sql
UPDATE user_subscriptions
SET tier = 'teams_medium', status = 'active'
WHERE stripe_subscription_id = ...

UPDATE users SET tier = 'teams_medium'
WHERE user_id = ...
```

### On `customer.subscription.deleted`
```sql
UPDATE user_subscriptions
SET status = 'canceled'
WHERE stripe_subscription_id = ...

UPDATE users SET tier = 'free'
WHERE user_id = ...
```

---

## Webhook Response Requirements

Your webhook handler must respond with:

### Success (Processing webhook)
```
Status: 200 OK
Body: {
  "success": true,
  "event_id": "evt_1234567890"
}
```

### Error (Don't process again)
```
Status: 400 Bad Request
Body: {
  "error": "Invalid signature"
}
```

### Retry Later
```
Status: 500 Internal Server Error
Body: {
  "error": "Database connection failed"
}

Stripe will retry up to 3 days later
```

---

## Webhook Retry Policy

Stripe retries failed webhooks:

- **1st attempt**: Immediately
- **2nd attempt**: 5 minutes later
- **3rd attempt**: 30 minutes later
- **4th attempt**: 2 hours later
- **5th attempt**: 5 hours later
- **6th attempt**: 10 hours later
- **7th attempt**: 24 hours later
- **8th attempt**: 48 hours later
- **9th attempt**: 72 hours later

After 72 hours, the webhook is marked as failed.

---

## Monitoring Webhooks

### Set up alerts for:
```
⚠️  Webhook failure rate > 5%
⚠️  Response time > 2 seconds
⚠️  Signature verification failures
⚠️  Subscription creation failures
```

### Check webhook logs:
```bash
# View all webhooks
curl -H "Authorization: Bearer sk_test_..." \
  https://api.stripe.com/v1/webhook_endpoints

# View webhook events
curl -H "Authorization: Bearer sk_test_..." \
  "https://api.stripe.com/v1/events?type=customer.subscription.created"
```

---

## Testing Webhook Events

### Using `stripe_setup_assistant.py` (Automated)
```powershell
python stripe_setup_assistant.py
# Walks you through entire setup
```

### Using `PHASE4_VERIFICATION.py` (Verification)
```powershell
python PHASE4_VERIFICATION.py
# Checks webhook configuration
```

### Manual Webhook Testing
```bash
# Using Stripe CLI
stripe trigger customer.subscription.created

# This sends a test event to your registered webhook endpoint
```

---

## Your Webhook Endpoint Details

| Setting | Value |
|---------|-------|
| **URL** | `https://yourdomain.com/api/billing/webhook` |
| **Protocol** | HTTPS (production) / HTTP (development with ngrok) |
| **Timeout** | 30 seconds |
| **Signature Method** | HMAC-SHA256 |
| **Events** | See "Webhook Events Configuration" above |
| **Secret** | `whsec_test_...` (save in `.env`) |

---

## ✅ Webhook Checklist

- [ ] Created webhook endpoint in Stripe Dashboard
- [ ] Copied webhook signing secret to `.env`
- [ ] Enabled required events (subscriptions + invoices)
- [ ] Set endpoint URL (local with ngrok or production domain)
- [ ] Started ngrok tunnel (`ngrok http 8000`)
- [ ] Restarted backend after .env changes
- [ ] Tested webhook with Stripe CLI or test event
- [ ] Verified webhook received in Stripe Dashboard logs
- [ ] Confirmed database updated with subscription
- [ ] Verified user tier changed in database

---

## 📞 NEXT: Test Payments

After webhook is configured, proceed to:
```
PHASE4_TESTING_GUIDE.md
→ Test Scenario 6: Complete Payment Process
```

This will fully verify:
- ✅ Checkout form appears
- ✅ Payment processes through Stripe
- ✅ Webhook received subscription event
- ✅ Database updated with tier
- ✅ User sees success page

---

**Ready?** Let's start testing! 🚀

