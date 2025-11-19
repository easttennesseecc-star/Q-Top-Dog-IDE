# Deployment Wrap-Up: Top Dog IDE

## Completed Engineering Work

## Required Secrets / Config
Kubernetes secret `provider-api-keys` (existing). New secret `stripe-keys` containing:
```
STRIPE_SECRET_KEY
STRIPE_PUBLIC_KEY
STRIPE_WEBHOOK_SECRET
STRIPE_PRICE_ID_PRO
STRIPE_PRICE_ID_PRO_ANNUAL
STRIPE_PRICE_ID_PRO_PLUS
STRIPE_PRICE_ID_PRO_PLUS_ANNUAL
STRIPE_PRICE_ID_TEAMS
STRIPE_PRICE_ID_TEAMS_ANNUAL
STRIPE_PRICE_ID_ENTERPRISE
STRIPE_PRICE_ID_ENTERPRISE_ANNUAL
```
(Use test mode initially; switch to live when ready.)

## Post-Deployment Validation Steps
1. Apply Stripe secret to cluster namespace.
2. Trigger canary deploy; confirm CI warning absent for Stripe.
3. Run smoke script locally:
```
python scripts/billing_smoke.py --base-url https://api.topdog-ide.com --price-id $STRIPE_PRICE_ID_PRO --session-id <dev_session>
```
4. Complete real checkout in browser (Stripe test card) → verify webhook updates subscription row.
5. Inspect `/api/billing/invoices` for created invoice record.
6. Confirm BYOK capacity errors:
   - Add > allowed personal keys → expect 403.
   - Add org credentials until capacity reached → expect 403 + guidance.
7. Check pricing UI shows BYOK and Org API bucket rows.
8. Verify canonical redirect and no `q-ide` domains served.

## Operational Dashboards

## Manual Follow-Ups (Optional)

## Rollback Procedure
1. `kubectl rollout undo deployment <backend-deploy>` (if canary misbehaves).
2. Remove Stripe secret to disable billing (endpoints 503 gracefully).
3. Re-run smoke tests on previous version.

## Quick Reference

Deployment is production-ready pending Stripe secrets provisioning.
Re-trigger canary deployment at: 2025-11-19T18:41Z for billing subscription fix promotion.
