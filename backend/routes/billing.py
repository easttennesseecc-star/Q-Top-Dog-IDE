"""
Billing API endpoints - Stripe integration routes
Handles subscriptions, checkout, portal, and webhooks
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional, cast

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from pydantic import BaseModel
from backend.services.stripe_service import StripeService, SubscriptionTier
from backend.services.stripe_types import (
    WebhookSubscriptionCreated,
    WebhookSubscriptionUpdated,
    WebhookSubscriptionDeleted,
    WebhookPaymentSucceeded,
    WebhookPaymentFailed,
)
from backend.models.subscription import Subscription, Invoice, BillingAlert, SubscriptionStatus
# Fix note: switched to SQLAlchemy `get_db` dependency (backend.database) to avoid
# runtime failures when calling `.query` on the previous DatabaseService wrapper.
from backend.database import get_db
from backend.auth import get_current_user

# Stripe may be unavailable in some environments (tests/dev)
stripe: Any
_StripeError: type[Exception]
try:
    import stripe as _stripe_mod
    _StripeError = _stripe_mod.error.StripeError  # type: ignore[attr-defined]
    stripe = _stripe_mod
except Exception:  # stripe not installed in some envs (tests)
    stripe = None
    _StripeError = Exception

 

logger = logging.getLogger("q-ide-topdog")
router = APIRouter(prefix="/api/billing", tags=["billing"])
def _require_stripe():
    if stripe is None:
        raise HTTPException(status_code=503, detail="Billing is not configured on this environment")



class CreateCheckoutRequest(BaseModel):
    """Request to create checkout session"""
    price_id: str
    trial_days: int = 14


class UpdateSubscriptionRequest(BaseModel):
    """Request to update subscription"""
    plan: str  # pro or teams


class GetSubscriptionResponse(BaseModel):
    """Subscription status response"""
    tier: str
    status: str
    api_calls_used: int
    api_calls_limit: int
    current_period_end: Optional[int]
    cancel_at: Optional[int]
    stripe_subscription_id: Optional[str]


# ============================================================================
# Subscription Management Endpoints
# ============================================================================


@router.get("/subscription", response_model=GetSubscriptionResponse)
async def get_subscription(
    current_user: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get current subscription info for user"""
    try:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user
        ).first()
        
        if not subscription:
            # Create free tier subscription for new user
            subscription = Subscription(
                user_id=current_user,
                tier=SubscriptionTier.FREE,
                status=SubscriptionStatus.ACTIVE,
                api_calls_limit=100
            )
            db.add(subscription)
            db.commit()
            logger.info(f"Created free subscription for user {current_user}")
        
        return GetSubscriptionResponse(
            tier=subscription.tier.value,
            status=subscription.status.value,
            api_calls_used=subscription.api_calls_used,
            api_calls_limit=subscription.api_calls_limit,
            current_period_end=int(subscription.current_period_end.timestamp()) if subscription.current_period_end else None,
            cancel_at=int(subscription.cancel_at.timestamp()) if subscription.cancel_at else None,
            stripe_subscription_id=subscription.stripe_subscription_id
        )
    except Exception as e:
        logger.error(f"Failed to get subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve subscription")


@router.post("/create-checkout-session")
async def create_checkout_session(
    request_data: CreateCheckoutRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create Stripe checkout session for plan upgrade"""
    try:
        _require_stripe()
        # Get or create subscription
        subscription = db.query(Subscription).filter(Subscription.user_id == current_user).first()
        
        if not subscription:
            subscription = Subscription(
                user_id=current_user,
                tier=SubscriptionTier.FREE,
                status=SubscriptionStatus.ACTIVE
            )
            db.add(subscription)
            db.commit()
        
        # Get or create Stripe customer
        if not subscription.stripe_customer_id:
            customer_id = StripeService.create_customer(
                current_user,
                f"{current_user}@example.local",
                current_user
            )
            subscription.stripe_customer_id = customer_id
            db.commit()
        
        # Create checkout session
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        session_id = StripeService.create_checkout_session(
            customer_id=subscription.stripe_customer_id,
            price_id=request_data.price_id,
            trial_days=request_data.trial_days,
            success_url=f"{frontend_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{frontend_url}/billing/cancel"
        )
        logger.info(f"Created checkout session for user {current_user}: {session_id}")
        return {
            "status": "ok",
            "sessionId": session_id
        }
    
    except _StripeError as e:
        logger.error(f"Stripe error creating checkout: {e}")
        raise HTTPException(status_code=400, detail=f"Payment error: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create checkout session")


@router.post("/checkout-success")
async def checkout_success(
    request_data: Dict = Body(...),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Handle successful checkout"""
    try:
        _require_stripe()
        session_id = request_data.get("sessionId")
        if not session_id:
            raise HTTPException(status_code=400, detail="Missing session ID")
        
        # Retrieve checkout session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        
        subscription = db.query(Subscription).filter(Subscription.user_id == current_user).first()
        
        if subscription:
            subscription.stripe_subscription_id = session.subscription
            db.commit()
            logger.info(f"Checkout successful for user {current_user}")
        
        return {
            "status": "ok",
            "message": "Subscription activated",
            "subscription_id": session.subscription
        }
    except Exception as e:
        logger.error(f"Error processing checkout success: {e}")
        raise HTTPException(status_code=500, detail="Failed to process checkout")


@router.get("/portal")
async def create_billing_portal(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create link to Stripe billing portal"""
    try:
        _require_stripe()
        subscription = db.query(Subscription).filter(Subscription.user_id == current_user).first()
        
        if not subscription or not subscription.stripe_customer_id:
            raise HTTPException(status_code=404, detail="No billing account found")
        
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        portal_url = StripeService.create_portal_session(
            customer_id=subscription.stripe_customer_id,
            return_url=f"{frontend_url}/dashboard"
        )
        logger.info(f"Created billing portal for user {current_user}")
        return {
            "status": "ok",
            "url": portal_url
        }
    
    except _StripeError as e:
        logger.error(f"Stripe error creating portal: {e}")
        raise HTTPException(status_code=400, detail="Failed to create billing portal")
    except Exception as e:
        logger.error(f"Error creating billing portal: {e}")
        raise HTTPException(status_code=500, detail="Failed to create billing portal")


@router.post("/cancel-subscription")
async def cancel_subscription(
    request_data: Dict = Body(...),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Cancel subscription at end of billing period"""
    try:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user
        ).first()
        
        if not subscription or not subscription.stripe_subscription_id:
            raise HTTPException(status_code=404, detail="No subscription found")
        
        # Cancel at end of period (user keeps access until billing period ends)
        result = StripeService.cancel_subscription(
            subscription.stripe_subscription_id,
            at_period_end=True
        )
        
        cancel_at_val = result.get("cancel_at")
        subscription.cancel_at = (
            datetime.fromtimestamp(float(cancel_at_val))
            if isinstance(cancel_at_val, (int, float)) else None
        )
        subscription.status = SubscriptionStatus(result.get("status", "canceled"))
        db.commit()
        logger.info(f"Canceled subscription for user {current_user}")
        return {
            "status": "ok",
            "message": "Subscription will cancel at end of billing period",
            "cancel_at": result.get("cancel_at")
        }
    
    except _StripeError as e:
        logger.error(f"Stripe error canceling subscription: {e}")
        raise HTTPException(status_code=400, detail="Failed to cancel subscription")
    except Exception as e:
        logger.error(f"Error canceling subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")


# ============================================================================
# Invoices and History
# ============================================================================

@router.get("/invoices")
async def get_invoices(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get user's invoice history"""
    try:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user
        ).first()
        
        if not subscription:
            return {"status": "ok", "invoices": []}
        
        invoices = db.query(Invoice).filter(
            Invoice.subscription_id == subscription.id
        ).order_by(Invoice.created_at.desc()).all()
        
        return {
            "status": "ok",
            "invoices": [
                {
                    "id": inv.id,
                    "stripe_invoice_id": inv.stripe_invoice_id,
                    "number": inv.invoice_number,
                    "amount_paid": inv.amount_paid,
                    "status": inv.status,
                    "created": int(inv.created_at.timestamp()),
                    "period_start": int(inv.period_start.timestamp()) if inv.period_start else None,
                    "period_end": int(inv.period_end.timestamp()) if inv.period_end else None,
                    "hosted_url": inv.hosted_invoice_url
                }
                for inv in invoices
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching invoices: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve invoices")


# ============================================================================
# Webhook Handler - Critical for payment processing
# ============================================================================

@router.post("/webhook")
async def handle_webhook(request: Request, db = Depends(get_db)):
    """
    Handle Stripe webhook events
    Critical: This processes all payment events and updates subscriptions
    """
    try:
        _require_stripe()
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        
        if not webhook_secret:
            logger.error("STRIPE_WEBHOOK_SECRET not configured")
            raise HTTPException(status_code=500, detail="Webhook secret not configured")
        if not sig_header:
            logger.error("Missing Stripe signature header")
            raise HTTPException(status_code=400, detail="Missing signature header")
        
        # Verify webhook signature
        event = StripeService.construct_event(payload, sig_header, webhook_secret)
        
        # Handle event
        event_type, event_data = StripeService.handle_webhook(event)
        
        # Update database based on event
        if event_type == "subscription_created":
            sub_created = cast(WebhookSubscriptionCreated, event_data)
            subscription = db.query(Subscription).filter(
                Subscription.stripe_customer_id == sub_created["customer_id"]
            ).first()
            
            if subscription:
                subscription.stripe_subscription_id = sub_created["subscription_id"]
                subscription.status = SubscriptionStatus.TRIALING if sub_created.get("trial_end") else SubscriptionStatus.ACTIVE
                _te = sub_created.get("trial_end")
                subscription.trial_end = datetime.fromtimestamp(float(_te)) if isinstance(_te, (int, float)) else None
                db.commit()
                logger.info(f"Updated subscription {sub_created['subscription_id']} status to {subscription.status}")
        
        elif event_type == "subscription_updated":
            sub_updated = cast(WebhookSubscriptionUpdated, event_data)
            subscription = db.query(Subscription).filter(
                Subscription.stripe_customer_id == sub_updated["customer_id"]
            ).first()
            
            if subscription:
                subscription.status = SubscriptionStatus(sub_updated["status"])
                _ca = sub_updated.get("cancel_at")
                if isinstance(_ca, (int, float)):
                    subscription.cancel_at = datetime.fromtimestamp(float(_ca))
                db.commit()
                logger.info(f"Updated subscription status to {subscription.status}")
        
        elif event_type == "subscription_deleted":
            sub_deleted = cast(WebhookSubscriptionDeleted, event_data)
            subscription = db.query(Subscription).filter(
                Subscription.stripe_customer_id == sub_deleted["customer_id"]
            ).first()
            
            if subscription:
                subscription.status = SubscriptionStatus.CANCELED
                subscription.tier = SubscriptionTier.FREE
                _cd = sub_deleted.get("canceled_at")
                subscription.canceled_at = (
                    datetime.fromtimestamp(float(_cd)) if isinstance(_cd, (int, float)) else datetime.utcnow()
                )
                db.commit()
                logger.info("Downgraded subscription to free tier after cancellation")
        
        elif event_type == "payment_succeeded":
            pay_succeeded = cast(WebhookPaymentSucceeded, event_data)
            # Create invoice record
            subscription = db.query(Subscription).filter(
                Subscription.stripe_subscription_id == pay_succeeded.get("subscription_id")
            ).first()
            
            if subscription:
                invoice = Invoice(
                    subscription_id=subscription.id,
                    stripe_invoice_id=pay_succeeded["invoice_id"],
                    stripe_customer_id=pay_succeeded["customer_id"],
                    amount_paid=float(cast(int, pay_succeeded.get("amount_paid", 0))) / 100.0,  # Convert from cents
                    status="paid",
                    paid=True
                )
                db.add(invoice)
                subscription.status = SubscriptionStatus.ACTIVE
                db.commit()
                logger.info(f"Recorded payment for subscription {subscription.id}")
        
        elif event_type == "payment_failed":
            pay_failed = cast(WebhookPaymentFailed, event_data)
            # Create alert for user
            subscription = db.query(Subscription).filter(
                Subscription.stripe_subscription_id == pay_failed.get("subscription_id")
            ).first()
            
            if subscription:
                subscription.status = SubscriptionStatus.PAST_DUE
                alert = BillingAlert(
                    user_id=subscription.user_id,
                    subscription_id=subscription.id,
                    alert_type="payment_failed",
                    message=f"Payment failed for invoice {pay_failed.get('invoice_id')}. Please update your payment method.",
                    severity="critical"
                )
                db.add(alert)
                db.commit()
                logger.warning(f"Payment failed for subscription {subscription.id}")
        
        return {"status": "ok", "event": event_type}
    
    except ValueError as e:
        logger.error(f"Invalid webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except _StripeError as e:
        logger.error(f"Invalid webhook signature: {e}")
        raise HTTPException(status_code=401, detail="Invalid signature")
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        # Still return 200 to acknowledge receipt (Stripe will retry if we return error)
        return {"status": "error", "message": str(e)}


# ============================================================================
# Admin Endpoints - Revenue Analytics
# ============================================================================

@router.get("/admin/stats")
async def get_revenue_stats(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get revenue and subscription statistics (admin only)"""
    try:
        # Check if user is admin
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Count subscriptions by tier
        total_subs = db.query(Subscription).filter(
            Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING])
        ).count()
        
        pro_subs = db.query(Subscription).filter(
            Subscription.tier == SubscriptionTier.PRO,
            Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING])
        ).count()
        pro_plus_subs = db.query(Subscription).filter(
            Subscription.tier == SubscriptionTier.PRO_PLUS,
            Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING])
        ).count()
        
        teams_subs = db.query(Subscription).filter(
            Subscription.tier == SubscriptionTier.TEAMS,
            Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING])
        ).count()
        
        enterprise_subs = db.query(Subscription).filter(
            Subscription.tier == SubscriptionTier.ENTERPRISE,
            Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING])
        ).count()
        
        # Calculate MRR using current monthly per-seat prices
        mrr = (
            pro_subs * 29
            + pro_plus_subs * 49
            + teams_subs * 39
            + enterprise_subs * 79
        )
        
        return {
            "status": "ok",
            "total_subscriptions": total_subs,
            "pro": pro_subs,
            "pro_plus": pro_plus_subs,
            "teams": teams_subs,
            "enterprise": enterprise_subs,
            "mrr": mrr,
            "arr": mrr * 12
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve stats")
