"""Billing smoke test script

Validates presence and basic operation of billing endpoints when Stripe is configured.
Usage:
  python scripts/billing_smoke.py --base-url http://localhost:8000 --price-id $STRIPE_PRICE_ID_PRO --session-id <dev_session>

Notes:
- Requires STRIPE_* envs and backend running with billing router active.
- Does NOT create real subscriptions if using test Price IDs.
- Provides clear output and non-zero exit code on failure.
"""
from __future__ import annotations

import argparse
import os
import sys

import httpx

def fail(msg: str):
    print(f"[FAIL] {msg}")
    sys.exit(1)

def info(msg: str):
    print(f"[INFO] {msg}")

def check_env():
    required = [
        "STRIPE_SECRET_KEY", "STRIPE_PUBLIC_KEY", "STRIPE_WEBHOOK_SECRET"
    ]
    missing = [v for v in required if not os.getenv(v)]
    if missing:
        fail(f"Missing required Stripe env vars: {', '.join(missing)}")
    info("Stripe envs present")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base-url', default='http://127.0.0.1:8000')
    ap.add_argument('--price-id', required=True, help='Stripe Price ID to test checkout session creation')
    ap.add_argument('--session-id', required=False, help='Dev session identifier if backend uses session auth header')
    ap.add_argument('--timeout', type=float, default=10.0)
    args = ap.parse_args()

    check_env()

    headers = {'Content-Type': 'application/json'}
    if args.session_id:
        headers['X-Session-ID'] = args.session_id

    with httpx.Client(base_url=args.base_url, timeout=args.timeout) as client:
        # 1. Get subscription (auto-provision free tier)
        info('Querying current subscription...')
        r = client.get('/api/billing/subscription', headers=headers)
        if r.status_code not in (200,):
            fail(f"Subscription endpoint error {r.status_code}: {r.text}")
        sub = r.json()
        info(f"Subscription tier: {sub.get('tier')} status: {sub.get('status')}")

        # 2. Create checkout session
        info('Creating checkout session...')
        r = client.post('/api/billing/create-checkout-session', headers=headers, json={
            'price_id': args.price_id,
            'trial_days': 0
        })
        if r.status_code != 200:
            fail(f"Checkout session creation failed {r.status_code}: {r.text}")
        data = r.json()
        session_id = data.get('sessionId')
        if not session_id:
            fail('No sessionId returned from checkout creation')
        info(f"Checkout session created: {session_id}")

        # 3. Simulate success (only for smoke; in real flow Stripe redirects) - we skip webhook.
        info('Simulating checkout success...')
        r = client.post('/api/billing/checkout-success', headers=headers, json={'sessionId': session_id})
        if r.status_code != 200:
            fail(f"Checkout success simulation failed {r.status_code}: {r.text}")
        info('Checkout success path OK')

        # 4. Create portal link
        info('Requesting billing portal link...')
        r = client.get('/api/billing/portal', headers=headers)
        if r.status_code != 200:
            fail(f"Portal endpoint failed {r.status_code}: {r.text}")
        portal_url = r.json().get('url')
        info(f"Portal URL returned: {portal_url}")

    info('All billing smoke tests passed.')

if __name__ == '__main__':
    main()
