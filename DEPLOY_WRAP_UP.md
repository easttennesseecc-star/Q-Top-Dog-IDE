# Deployment Wrap-Up: Top Dog IDE

## Completed Engineering Work
- Blue/green + canary strategy with SLO burn-rate gates and auto promotion/rollback
- SPA served at root with canonical redirects and SEO endpoints (robots + sitemap + verification)
- Multi-LLM pool with safe fallback, org pooled API buckets, and BYOK per-seat/org enforcement
- Stripe integration endpoints (checkout, portal, webhook) with price ID mapping including Pro Plus + annual normalization
- Personal BYOK slot enforcement (Free/Pro/Pro Plus) and org BYOK pool enforcement (Teams/Enterprise)
- Pricing page updated: Dev lineup notes, annual discount copy, BYOK capacity + Org API bucket rows
- Org model: organizations, members, org daily usage, org BYOK credentials tracking
- Rate limiter: personal limit then org fallback, exposes source and BYOK pool status
- CI workflow: non-blocking Stripe secret presence check + existing lint/type/test gates
- Billing smoke script added (`scripts/billing_smoke.py`)

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
- Health: `/health`
- Metrics: `/metrics` (Prometheus scrape)
- Consistency: `/consistency/sli`
- Billing admin stats: `/api/billing/admin/stats` (requires admin session)

## Manual Follow-Ups (Optional)
- Add regulated tier BYOK/org pool enforcement if policy evolves.
- Expand front-end tests for pricing table rows.
- Introduce per-user credential revocation endpoint with audit trail.
- Add subscription downgrade UI path and annual toggle display.

## Rollback Procedure
1. `kubectl rollout undo deployment <backend-deploy>` (if canary misbehaves).
2. Remove Stripe secret to disable billing (endpoints 503 gracefully).
3. Re-run smoke tests on previous version.

## Quick Reference
- Org BYOK (Teams): 12 + 2/seat
- Org API bucket (Teams): +400/seat/day
- Org BYOK (Enterprise): 24 + 3/seat
- Org API bucket (Enterprise): +1,750/seat/day
- Personal BYOK: Free=2, Pro=3, Pro Plus=5
- Annual discount: Dev tiers only (10%)

Deployment is production-ready pending Stripe secrets provisioning.
