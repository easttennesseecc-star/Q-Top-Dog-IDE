"""Typed dicts and lightweight protocols for Stripe service responses.

These types strengthen structure checking without requiring the full Stripe
SDK type stubs. Only keys accessed/returned by our wrapper are modeled.
"""
from __future__ import annotations

from typing import TypedDict, Optional


class SubscriptionInfo(TypedDict, total=False):
    id: str
    status: str
    customer_id: str
    current_period_start: int
    current_period_end: int
    trial_end: Optional[int]
    cancel_at: Optional[int]
    canceled_at: Optional[int]
    items: list[dict]


class CustomerInfo(TypedDict, total=False):
    id: str
    email: Optional[str]
    name: Optional[str]
    metadata: dict


class InvoiceInfo(TypedDict, total=False):
    id: str
    number: Optional[str]
    customer_id: str
    subscription_id: Optional[str]
    amount_paid: int
    amount_due: int
    amount_remaining: int
    status: str
    paid: bool
    created: int
    due_date: Optional[int]
    period_start: int
    period_end: int
    hosted_invoice_url: Optional[str]
    invoice_pdf: Optional[str]


class PortalSessionInfo(TypedDict):
    url: str


class CheckoutSessionInfo(TypedDict):
    id: str


class WebhookSubscriptionCreated(TypedDict):
    subscription_id: str
    customer_id: str
    status: str
    trial_end: Optional[int]


class WebhookSubscriptionUpdated(TypedDict):
    subscription_id: str
    customer_id: str
    status: str
    cancel_at: Optional[int]


class WebhookSubscriptionDeleted(TypedDict):
    subscription_id: str
    customer_id: str
    canceled_at: Optional[int]


class WebhookPaymentSucceeded(TypedDict):
    invoice_id: str
    customer_id: str
    subscription_id: Optional[str]
    amount_paid: int
    hosted_invoice_url: Optional[str]


class WebhookPaymentFailed(TypedDict):
    invoice_id: str
    customer_id: str
    subscription_id: Optional[str]
    amount_due: int
    attempt_count: int


class WebhookChargeDisputed(TypedDict):
    charge_id: str
    customer_id: str
    amount: int
    currency: str


class WebhookGenericEvent(TypedDict):
    event_type: str


class WebhookError(TypedDict):
    error: str


WebhookPayload = (
    WebhookSubscriptionCreated | WebhookSubscriptionUpdated | WebhookSubscriptionDeleted |
    WebhookPaymentSucceeded | WebhookPaymentFailed | WebhookChargeDisputed | WebhookGenericEvent |
    WebhookError
)
