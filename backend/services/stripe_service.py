"""
Stripe Payment Processing Service
Handles customer creation, subscriptions, billing portal, and webhook events
"""

import stripe
import os
import logging
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from enum import Enum

logger = logging.getLogger("q-ide-topdog")

# Initialize Stripe with API key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


class SubscriptionTier(str, Enum):
    """Available subscription tiers"""
    FREE = "free"
    PRO = "pro"
    TEAMS = "teams"
    ENTERPRISE = "enterprise"


class StripeService:
    """Handle all Stripe operations"""

    # Pricing tier IDs (from Stripe Product Dashboard)
    PRICE_IDS = {
        "pro": os.getenv("STRIPE_PRICE_ID_PRO", "price_pro_placeholder"),
        "teams": os.getenv("STRIPE_PRICE_ID_TEAMS", "price_teams_placeholder"),
    }

    @staticmethod
    def create_customer(user_id: str, email: str, name: str) -> str:
        """
        Create a Stripe customer from a Q-IDE user
        
        Args:
            user_id: Q-IDE internal user ID
            email: User email
            name: User display name
            
        Returns:
            Stripe customer ID (cus_...)
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={
                    "user_id": user_id,
                    "created_at": datetime.utcnow().isoformat(),
                    "source": "q-ide"
                }
            )
            logger.info(f"Created Stripe customer {customer.id} for user {user_id}")
            return customer.id
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            raise

    @staticmethod
    def create_subscription(
        customer_id: str,
        price_id: str,
        trial_days: int = 14,
        metadata: Dict = None
    ) -> Dict:
        """
        Create a subscription for a customer
        
        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID
            trial_days: Days of free trial (default 14)
            metadata: Additional metadata to store
            
        Returns:
            Subscription object dict
        """
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                trial_period_days=trial_days,
                payment_behavior="default_incomplete",
                expand=["latest_invoice.payment_intent"],
                metadata=metadata or {}
            )
            logger.info(f"Created subscription {subscription.id} for customer {customer_id}")
            return {
                "id": subscription.id,
                "status": subscription.status,
                "customer_id": subscription.customer,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "trial_end": subscription.trial_end,
                "cancel_at": subscription.cancel_at
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create subscription: {e}")
            raise

    @staticmethod
    def cancel_subscription(subscription_id: str, at_period_end: bool = False) -> Dict:
        """
        Cancel a subscription
        
        Args:
            subscription_id: Stripe subscription ID
            at_period_end: If True, cancel at end of billing period; if False, cancel immediately
            
        Returns:
            Canceled subscription object dict
        """
        try:
            if at_period_end:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                subscription = stripe.Subscription.delete(subscription_id)
            
            logger.info(f"Canceled subscription {subscription_id}")
            return {
                "id": subscription.id,
                "status": subscription.status,
                "canceled_at": subscription.canceled_at,
                "cancel_at": subscription.cancel_at
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription: {e}")
            raise

    @staticmethod
    def get_subscription(subscription_id: str) -> Dict:
        """
        Get subscription details
        
        Args:
            subscription_id: Stripe subscription ID
            
        Returns:
            Subscription object dict
        """
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return {
                "id": subscription.id,
                "status": subscription.status,
                "customer_id": subscription.customer,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "trial_end": subscription.trial_end,
                "cancel_at": subscription.cancel_at,
                "canceled_at": subscription.canceled_at,
                "items": [
                    {
                        "price_id": item.price.id,
                        "price_amount": item.price.unit_amount,
                        "price_currency": item.price.currency
                    }
                    for item in subscription.items.data
                ]
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get subscription: {e}")
            raise

    @staticmethod
    def get_customer(customer_id: str) -> Dict:
        """
        Get customer details
        
        Args:
            customer_id: Stripe customer ID
            
        Returns:
            Customer object dict
        """
        try:
            customer = stripe.Customer.retrieve(customer_id)
            return {
                "id": customer.id,
                "email": customer.email,
                "name": customer.name,
                "metadata": customer.metadata or {}
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get customer: {e}")
            raise

    @staticmethod
    def create_portal_session(customer_id: str, return_url: str) -> str:
        """
        Create a link to Stripe billing portal
        
        Args:
            customer_id: Stripe customer ID
            return_url: URL to return to after portal session
            
        Returns:
            Billing portal URL
        """
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            logger.info(f"Created billing portal session for customer {customer_id}")
            return session.url
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create billing portal session: {e}")
            raise

    @staticmethod
    def create_checkout_session(
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        trial_days: int = 14
    ) -> str:
        """
        Create a checkout session for upgrading plan
        
        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID
            success_url: URL to redirect on success (include {CHECKOUT_SESSION_ID})
            cancel_url: URL to redirect on cancel
            trial_days: Days of free trial
            
        Returns:
            Checkout session ID
        """
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    },
                ],
                mode="subscription",
                subscription_data={
                    "trial_period_days": trial_days
                },
                success_url=success_url,
                cancel_url=cancel_url,
            )
            logger.info(f"Created checkout session {session.id}")
            return session.id
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create checkout session: {e}")
            raise

    @staticmethod
    def get_invoice(invoice_id: str) -> Dict:
        """
        Get invoice details
        
        Args:
            invoice_id: Stripe invoice ID
            
        Returns:
            Invoice object dict
        """
        try:
            invoice = stripe.Invoice.retrieve(invoice_id)
            return {
                "id": invoice.id,
                "number": invoice.number,
                "customer_id": invoice.customer,
                "subscription_id": invoice.subscription,
                "amount_paid": invoice.amount_paid,
                "amount_due": invoice.amount_due,
                "amount_remaining": invoice.amount_remaining,
                "status": invoice.status,
                "paid": invoice.paid,
                "created": invoice.created,
                "due_date": invoice.due_date,
                "period_start": invoice.period_start,
                "period_end": invoice.period_end,
                "hosted_invoice_url": invoice.hosted_invoice_url,
                "invoice_pdf": invoice.invoice_pdf,
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get invoice: {e}")
            raise

    @staticmethod
    def list_invoices(customer_id: str, limit: int = 10) -> List[Dict]:
        """
        List invoices for a customer
        
        Args:
            customer_id: Stripe customer ID
            limit: Maximum number of invoices to return
            
        Returns:
            List of invoice objects
        """
        try:
            invoices = stripe.Invoice.list(
                customer=customer_id,
                limit=limit
            )
            return [
                {
                    "id": inv.id,
                    "number": inv.number,
                    "amount_paid": inv.amount_paid,
                    "status": inv.status,
                    "created": inv.created,
                    "period_start": inv.period_start,
                    "period_end": inv.period_end,
                }
                for inv in invoices.data
            ]
        except stripe.error.StripeError as e:
            logger.error(f"Failed to list invoices: {e}")
            raise

    @staticmethod
    def handle_webhook(event: Dict) -> Tuple[str, Dict]:
        """
        Handle Stripe webhook events
        
        Args:
            event: Webhook event from Stripe
            
        Returns:
            Tuple of (event_type, data_dict)
        """
        event_type = event.get("type", "unknown")
        
        try:
            if event_type == "customer.subscription.created":
                subscription = event["data"]["object"]
                logger.info(f"Subscription created: {subscription['id']}")
                return ("subscription_created", {
                    "subscription_id": subscription["id"],
                    "customer_id": subscription["customer"],
                    "status": subscription["status"],
                    "trial_end": subscription["trial_end"]
                })

            elif event_type == "customer.subscription.updated":
                subscription = event["data"]["object"]
                logger.info(f"Subscription updated: {subscription['id']}")
                return ("subscription_updated", {
                    "subscription_id": subscription["id"],
                    "customer_id": subscription["customer"],
                    "status": subscription["status"],
                    "cancel_at": subscription["cancel_at"]
                })

            elif event_type == "customer.subscription.deleted":
                subscription = event["data"]["object"]
                logger.info(f"Subscription deleted: {subscription['id']}")
                return ("subscription_deleted", {
                    "subscription_id": subscription["id"],
                    "customer_id": subscription["customer"],
                    "canceled_at": subscription["canceled_at"]
                })

            elif event_type == "invoice.payment_succeeded":
                invoice = event["data"]["object"]
                logger.info(f"Invoice paid: {invoice['id']}")
                return ("payment_succeeded", {
                    "invoice_id": invoice["id"],
                    "customer_id": invoice["customer"],
                    "subscription_id": invoice["subscription"],
                    "amount_paid": invoice["amount_paid"],
                    "hosted_invoice_url": invoice["hosted_invoice_url"]
                })

            elif event_type == "invoice.payment_failed":
                invoice = event["data"]["object"]
                logger.warning(f"Invoice payment failed: {invoice['id']}")
                return ("payment_failed", {
                    "invoice_id": invoice["id"],
                    "customer_id": invoice["customer"],
                    "subscription_id": invoice["subscription"],
                    "amount_due": invoice["amount_due"],
                    "attempt_count": invoice["attempt_count"]
                })

            elif event_type == "charge.dispute.created":
                charge = event["data"]["object"]
                logger.warning(f"Charge disputed: {charge['id']}")
                return ("charge_disputed", {
                    "charge_id": charge["id"],
                    "customer_id": charge["customer"],
                    "amount": charge["amount"],
                    "currency": charge["currency"]
                })

            else:
                logger.debug(f"Unhandled webhook event: {event_type}")
                return ("event_received", {"event_type": event_type})

        except Exception as e:
            logger.error(f"Failed to handle webhook: {e}")
            return ("webhook_error", {"error": str(e)})

    @staticmethod
    def construct_event(payload: bytes, sig_header: str, webhook_secret: str) -> Dict:
        """
        Construct and verify webhook event from Stripe
        
        Args:
            payload: Raw webhook payload
            sig_header: Stripe signature header
            webhook_secret: Webhook signing secret
            
        Returns:
            Verified webhook event dict
            
        Raises:
            ValueError: If payload is invalid
            stripe.error.SignatureVerificationError: If signature doesn't match
        """
        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                webhook_secret
            )
            return event
        except ValueError as e:
            logger.error(f"Invalid webhook payload: {e}")
            raise
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {e}")
            raise


# Helper function to get tier from price ID
def get_tier_from_price_id(price_id: str) -> Optional[SubscriptionTier]:
    """Map Stripe price ID to subscription tier"""
    for tier, pid in StripeService.PRICE_IDS.items():
        if price_id == pid:
            return SubscriptionTier(tier)
    return None
