import pytest

from backend.services.stripe_service import StripeService

# Webhook event fixture examples (only keys used by handler)

@pytest.mark.parametrize(
    "event, expected_type, required_keys",
    [
        (
            {"type": "customer.subscription.created", "data": {"object": {"id": "sub_1", "customer": "cus_1", "status": "active", "trial_end": 123456}}},
            "subscription_created",
            {"subscription_id", "customer_id", "status", "trial_end"},
        ),
        (
            {"type": "customer.subscription.updated", "data": {"object": {"id": "sub_2", "customer": "cus_2", "status": "past_due", "cancel_at": None}}},
            "subscription_updated",
            {"subscription_id", "customer_id", "status", "cancel_at"},
        ),
        (
            {"type": "customer.subscription.deleted", "data": {"object": {"id": "sub_3", "customer": "cus_3", "canceled_at": 999}}},
            "subscription_deleted",
            {"subscription_id", "customer_id", "canceled_at"},
        ),
        (
            {"type": "invoice.payment_succeeded", "data": {"object": {"id": "inv_1", "customer": "cus_4", "subscription": "sub_4", "amount_paid": 5000, "hosted_invoice_url": "https://example"}}},
            "payment_succeeded",
            {"invoice_id", "customer_id", "subscription_id", "amount_paid", "hosted_invoice_url"},
        ),
        (
            {"type": "invoice.payment_failed", "data": {"object": {"id": "inv_2", "customer": "cus_5", "subscription": "sub_5", "amount_due": 5000, "attempt_count": 2}}},
            "payment_failed",
            {"invoice_id", "customer_id", "subscription_id", "amount_due", "attempt_count"},
        ),
        (
            {"type": "charge.dispute.created", "data": {"object": {"id": "ch_1", "customer": "cus_6", "amount": 1000, "currency": "usd"}}},
            "charge_disputed",
            {"charge_id", "customer_id", "amount", "currency"},
        ),
        (
            {"type": "some.other.event", "data": {"object": {}}},
            "event_received",
            {"event_type"},
        ),
    ],
)
def test_handle_webhook(event, expected_type, required_keys):
    typ, payload = StripeService.handle_webhook(event)
    assert typ == expected_type
    assert required_keys.issubset(payload.keys())


def test_handle_webhook_error_branch():
    # Force an exception by passing malformed structure (missing data key)
    bad_event = {"type": "invoice.payment_succeeded"}  # Missing data
    typ, payload = StripeService.handle_webhook(bad_event)
    assert typ == "webhook_error"
    assert "error" in payload
