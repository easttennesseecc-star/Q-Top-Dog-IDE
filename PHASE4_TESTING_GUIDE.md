# 🧪 PHASE 4 VERIFICATION & TESTING GUIDE

**Purpose**: Complete end-to-end testing of Stripe payment integration
**Time**: 1-2 hours (depending on any issues found)
**Success Criteria**: All 13 test scenarios pass

---

## ✅ PRE-TESTING CHECKLIST

Before starting tests, verify:

- [ ] Backend running: `uvicorn main:app --reload`
- [ ] Frontend running: `npm run dev`
- [ ] Stripe test keys in `.env`:
  - `STRIPE_PUBLIC_KEY=pk_test_...`
  - `STRIPE_SECRET_KEY=sk_test_...`
  - `STRIPE_WEBHOOK_SECRET=whsec_...`
- [ ] Stripe products created in dashboard with price IDs
- [ ] Webhook endpoint configured in Stripe
- [ ] Database reset (optional): `rm backend/topdog_ide.db`

---

## 🧪 TEST SCENARIO 1: User Signup & Free Tier

**Goal**: Verify free tier assignment on signup

```
1. Go to http://localhost:3000
2. Sign up with email: test-user-1@example.com
3. Verify:
   - User created in database ✅
   - FREE tier assigned by default ✅
   - /api/tier/info shows FREE tier ✅
   - Can access dashboard ✅
```

**Expected Result**: ✅ PASS
**Failure Recovery**: Check backend logs for tier assignment

---

## 🧪 TEST SCENARIO 2: Tier Info API

**Goal**: Verify tier information is returned correctly

```bash
# In terminal (or use Postman)
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/tier/info

# Should return:
{
  "current_tier": "free",
  "tiers": [
    {"tier_name": "free", "price": 0, "features": 5},
    {"tier_name": "starter", "price": 12, "features": 15},
    ...
  ]
}
```

**Expected Result**: ✅ PASS - All 10 tiers returned

---

## 🧪 TEST SCENARIO 3: Navigate to Pricing Page

**Goal**: Verify pricing page loads and displays tiers

```
1. Frontend: Click "Pricing" in navigation
2. Verify:
   - All 10 tiers display ✅
   - Grid view shows tiers with prices ✅
   - Features list for each tier ✅
   - CTA buttons visible ✅
   - FAQ section loads ✅
```

**Expected Result**: ✅ PASS
**Failure Recovery**: Check browser console for errors

---

## 🧪 TEST SCENARIO 4: Click Upgrade Button

**Goal**: Verify navigation to checkout page

```
1. From pricing page, click "Upgrade to PRO"
2. Verify:
   - Navigates to /checkout?tier=pro ✅
   - Checkout page loads ✅
   - Back button works ✅
   - Form fields visible ✅
   - Stripe card element loads ✅
```

**Expected Result**: ✅ PASS
**Failure Recovery**: Check browser console for Stripe errors

---

## 🧪 TEST SCENARIO 5: Fill Checkout Form

**Goal**: Verify form validation

```
1. On checkout page, fill form:
   - Email: test-user-1@example.com ✅
   - Name: Test User ✅
   - Card: 4242 4242 4242 4242 (test card) ✅
   - Expiry: 12/25 ✅
   - CVC: 123 ✅

2. Verify:
   - Submit button enables ✅
   - No validation errors ✅
```

**Expected Result**: ✅ PASS
**Failure Recovery**: Check form validation logic

---

## 🧪 TEST SCENARIO 6: Submit Payment (Test Card - Success)

**Goal**: Process payment with test card

```
1. Click "Upgrade to PRO" button
2. Verify:
   - Loading spinner appears ✅
   - Redirects to Stripe checkout (hosted form) ✅
   - Can enter payment details securely ✅
```

**Expected Result**: ✅ PASS (redirects to Stripe)
**Failure Recovery**: Check Stripe API key configuration

---

## 🧪 TEST SCENARIO 7: Payment Success Handler

**Goal**: Verify success redirect and database update

```
1. After payment completes, should redirect to /billing/success
2. Verify:
   - URL shows success page ✅
   - Message displays "Welcome to PRO!" ✅
   - Can click "Go to Dashboard" ✅
```

**Expected Result**: ✅ PASS
**Failure Recovery**: Check backend webhook processing

---

## 🧪 TEST SCENARIO 8: Subscription Updated in Database

**Goal**: Verify tier changed after payment

```bash
# Check database
sqlite3 backend/topdog_ide.db

SELECT user_id, tier, status, stripe_subscription_id 
FROM user_subscriptions 
WHERE user_id = 'test-user-1';

# Should show:
# | test-user-1 | pro | active | sub_xxxxx |
```

**Expected Result**: ✅ PASS - Tier is now "pro"
**Failure Recovery**: Check webhook handler in billing.py

---

## 🧪 TEST SCENARIO 9: Dashboard Shows New Tier

**Goal**: Verify subscription status displays

```
1. Go to /dashboard/billing
2. Verify:
   - Shows "Current Subscription: PRO" ✅
   - Shows status "Active" ✅
   - Shows billing period end date ✅
   - Shows API call limits ✅
   - Show features included ✅
```

**Expected Result**: ✅ PASS
**Failure Recovery**: Check SubscriptionStatus component API calls

---

## 🧪 TEST SCENARIO 10: Manage Payments Button

**Goal**: Verify Stripe billing portal opens

```
1. On dashboard, click "Manage Payments"
2. Verify:
   - Opens Stripe billing portal ✅
   - Shows current subscription ✅
   - Can update payment method ✅
   - Can view invoices ✅
   - Can download PDFs ✅
```

**Expected Result**: ✅ PASS (opens in new tab)
**Failure Recovery**: Check /api/billing/portal endpoint

---

## 🧪 TEST SCENARIO 11: Invoice History

**Goal**: Verify invoice appears after payment

```
1. On dashboard, scroll to "Invoice History"
2. Verify:
   - Shows recent invoice ✅
   - Amount matches payment ✅
   - Status shows "paid" ✅
   - Download button present ✅
```

**Expected Result**: ✅ PASS - Invoice appears after webhook processes
**Failure Recovery**: Wait 5-10 seconds for webhook, then refresh

---

## 🧪 TEST SCENARIO 12: Tier Upgrade API Protection

**Goal**: Verify tier-protected endpoints work

```bash
# Test with upgraded tier
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/tier/usage

# Should return:
# {
#   "tier": "pro",
#   "api_calls_today": 0,
#   "api_calls_limit": 5000,
#   "usage_percent": 0
# }
```

**Expected Result**: ✅ PASS - Returns PRO tier limits
**Failure Recovery**: Check rate limiter service

---

## 🧪 TEST SCENARIO 13: Owner Account Protection

**Goal**: Verify owner cannot be charged

```bash
# Test with owner account
curl -X POST http://localhost:8000/api/billing/create-checkout-session \
  -H "Authorization: Bearer <owner-token>" \
  -H "Content-Type: application/json" \
  -d '{"price_id": "price_pro", "trial_days": 14}'

# Should return 403 error:
# {
#   "detail": "Cannot charge owner account"
# }
```

**Expected Result**: ✅ PASS - 403 error returned
**Failure Recovery**: Verify OWNER_ACCOUNT_IDS in billing.py

---

## 🧪 BONUS TEST SCENARIO: Failed Payment

**Goal**: Verify failed payment handling

```
1. Go back to pricing, click upgrade again
2. On checkout, enter test card: 4000 0000 0000 0002 (decline)
3. Verify:
   - Payment is declined ✅
   - Error message displays ✅
   - Subscription NOT updated ✅
   - Tier still FREE ✅
```

**Expected Result**: ✅ PASS - Payment declined, tier unchanged
**Failure Recovery**: Check error handling in CheckoutPage

---

## 📊 TEST RESULTS SUMMARY

| # | Test | Result | Notes |
|----|------|--------|-------|
| 1 | Signup & Free Tier | ✅/❌ | Check database |
| 2 | Tier Info API | ✅/❌ | Check backend logs |
| 3 | Pricing Page | ✅/❌ | Check browser console |
| 4 | Checkout Navigation | ✅/❌ | Check routing |
| 5 | Form Validation | ✅/❌ | Check form logic |
| 6 | Payment Submission | ✅/❌ | Check Stripe keys |
| 7 | Success Handler | ✅/❌ | Check redirect logic |
| 8 | Database Update | ✅/❌ | Check webhook |
| 9 | Dashboard Display | ✅/❌ | Check API calls |
| 10 | Billing Portal | ✅/❌ | Check portal endpoint |
| 11 | Invoice History | ✅/❌ | Wait for webhook |
| 12 | API Protection | ✅/❌ | Check tier validation |
| 13 | Owner Protection | ✅/❌ | Check exemption |

**Overall Status**: _____ / 13 PASS

---

## 🐛 TROUBLESHOOTING GUIDE

### Problem: Checkout redirects to Stripe but nothing happens

**Solution**:
1. Check Stripe public key is correct
2. Verify price ID matches Stripe dashboard
3. Check browser console for errors
4. Ensure CORS is configured correctly

### Problem: Payment succeeds but subscription not updated

**Solution**:
1. Check webhook endpoint configured in Stripe dashboard
2. Verify webhook secret in `.env`
3. Check backend logs for webhook errors
4. Manually trigger webhook:
   ```bash
   # In Stripe dashboard: Webhooks → Test event
   ```

### Problem: Redirect after payment not working

**Solution**:
1. Verify success URL in create_checkout_session
2. Check FRONTEND_URL in `.env`
3. Verify /billing/success page exists

### Problem: Invoices not showing

**Solution**:
1. Wait 10 seconds for webhook to process
2. Check database: `SELECT * FROM invoices;`
3. Verify webhook signature in logs
4. Manually create invoice (for testing only):
   ```bash
   # In Stripe dashboard: Create test invoice
   ```

---

## 🔍 DEBUGGING COMMANDS

### Check Database State
```bash
sqlite3 backend/topdog_ide.db

# View users
SELECT * FROM users;

# View subscriptions
SELECT user_id, tier, status, stripe_subscription_id FROM user_subscriptions;

# View invoices
SELECT * FROM invoices;

# View usage tracking
SELECT user_id, calls_used, quota FROM daily_usage_tracking;
```

### Check Backend Logs
```bash
# If running with logging
tail -f backend/logs/Top Dog-topdog.log

# Or check for specific errors:
grep -i error backend/logs/Top Dog-topdog.log
grep -i stripe backend/logs/Top Dog-topdog.log
grep -i webhook backend/logs/Top Dog-topdog.log
```

### Test Stripe API Directly
```bash
# List customers
curl -u sk_test_xxx: \
  https://api.stripe.com/v1/customers

# List subscriptions
curl -u sk_test_xxx: \
  https://api.stripe.com/v1/subscriptions

# List invoices
curl -u sk_test_xxx: \
  https://api.stripe.com/v1/invoices
```

---

## 📋 SIGN-OFF

When all tests pass, complete this sign-off:

```
Test Date: _______________
Tester: ___________________
Environment: DEVELOPMENT / STAGING / PRODUCTION

Passed: _____ / 13 tests
Failed: _____ / 13 tests

Critical Issues: ☐ None ☐ Fixed ☐ Pending
Minor Issues: ☐ None ☐ Fixed ☐ Pending

Sign-off: __________________ Date: _______

Ready for Production: ☐ YES ☐ NO (needs fixes)
```

---

## 🚀 NEXT STEPS (After All Tests Pass)

1. **Set up production Stripe account** (separate from test)
2. **Update .env with production keys**
3. **Deploy to staging first**
4. **Run all tests again in staging**
5. **Deploy to production**
6. **Monitor webhook delivery in Stripe dashboard**
7. **Announce payment feature to users**

---

## 📚 REFERENCE DOCUMENTATION

- Stripe API: https://stripe.com/docs/api
- Stripe Testing: https://stripe.com/docs/testing
- Webhook Events: https://stripe.com/docs/webhooks/events
- Payment Processing: https://stripe.com/docs/payments
- Billing Portal: https://stripe.com/docs/billing/portal

---

*Phase 4 is complete when all 13 scenarios pass consistently.*
