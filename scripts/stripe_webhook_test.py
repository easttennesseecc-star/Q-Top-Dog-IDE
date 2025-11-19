"""Stripe Webhook Automated Test

Simulates signed Stripe webhook events against the running backend to validate
signature verification and event handling logic.

Usage (PowerShell):
  python scripts/stripe_webhook_test.py --base-url https://api.topdog-ide.com \
    --secret $Env:STRIPE_WEBHOOK_SECRET --customer cus_test123 \
    --subscription sub_test123 --invoice in_test123

Test Flow:
  1. customer.subscription.created
  2. invoice.payment_succeeded
  3. customer.subscription.updated (cancel_at future timestamp)
  4. invoice.payment_failed
  5. customer.subscription.deleted

Exits non-zero on first failure.
Requires: STRIPE_WEBHOOK_SECRET (or --secret), endpoint /api/billing/webhook.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sys
import time
from typing import Any, Dict

import httpx

EVENTS = []

def build_events(customer_id: str, subscription_id: str, invoice_id: str) -> list[Dict[str, Any]]:
    now = int(time.time())
    return [
        {
            "id": f"evt_{subscription_id}_created",
            "object": "event",
            "type": "customer.subscription.created",
            "created": now,
            "data": {"object": {
                "id": subscription_id,
                "object": "subscription",
                "customer": customer_id,
                "status": "active",
                "trial_end": None,
                "cancel_at": None,
            }}
        },
        {
            "id": f"evt_{invoice_id}_paid",
            "object": "event",
            "type": "invoice.payment_succeeded",
            "created": now + 1,
            "data": {"object": {
                "id": invoice_id,
                "object": "invoice",
                "customer": customer_id,
                "subscription": subscription_id,
                "amount_paid": 2900,
                "hosted_invoice_url": "https://example.test/invoice/paid"
            }}
        },
        {
            "id": f"evt_{subscription_id}_updated",
            "object": "event",
            "type": "customer.subscription.updated",
            "created": now + 2,
            "data": {"object": {
                "id": subscription_id,
                "object": "subscription",
                "customer": customer_id,
                "status": "active",
                "cancel_at": now + 86400,
            }}
        },
        {
            "id": f"evt_{invoice_id}_failed",
            "object": "event",
            "type": "invoice.payment_failed",
            "created": now + 3,
            "data": {"object": {
                "id": invoice_id,
                "object": "invoice",
                "customer": customer_id,
                "subscription": subscription_id,
                "amount_due": 2900,
                "attempt_count": 1
            }}
        },
        {
            "id": f"evt_{subscription_id}_deleted",
            "object": "event",
            "type": "customer.subscription.deleted",
            "created": now + 4,
            "data": {"object": {
                "id": subscription_id,
                "object": "subscription",
                "customer": customer_id,
                "status": "canceled",
                "canceled_at": now + 4
            }}
        },
    ]

def sign_payload(secret: str, payload: bytes) -> str:
    ts = str(int(time.time()))
    sig = hmac.new(secret.encode("utf-8"), msg=f"{ts}.".encode("utf-8") + payload, digestmod=hashlib.sha256).hexdigest()
    return f"t={ts},v1={sig}"

def post_event(client: httpx.Client, base_url: str, secret: str, event: Dict[str, Any]) -> None:
    payload = json.dumps(event).encode("utf-8")
    sig_header = sign_payload(secret, payload)
    resp = client.post(f"{base_url}/api/billing/webhook", content=payload, headers={"stripe-signature": sig_header})
    if resp.status_code != 200:
        print(f"[FAIL] Event {event['type']} -> {resp.status_code} {resp.text}")
        sys.exit(1)
    data = resp.json()
    print(f"[OK] {event['type']} handled as: {data.get('event')} status={data.get('status')}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base-url', default='http://127.0.0.1:8000')
    ap.add_argument('--secret', default=os.getenv('STRIPE_WEBHOOK_SECRET', ''))
    ap.add_argument('--customer', required=True)
    ap.add_argument('--subscription', required=True)
    ap.add_argument('--invoice', required=True)
    ap.add_argument('--timeout', type=float, default=8.0)
    args = ap.parse_args()

    if not args.secret:
        print('[FAIL] Provide webhook secret via --secret or STRIPE_WEBHOOK_SECRET env')
        sys.exit(1)

    events = build_events(args.customer, args.subscription, args.invoice)
    with httpx.Client(timeout=args.timeout) as client:
        for ev in events:
            post_event(client, args.base_url, args.secret, ev)
    print('[SUCCESS] All webhook events processed successfully.')

if __name__ == '__main__':
    main()
