# 💳 Stripe Monetization Setup Guide

**Objective**: Build a complete SaaS payment system in Top Dog using Stripe  
**Timeline**: 1 week to integrate (can happen in parallel with Heroku deployment)  
**Revenue Model**: Subscription tiers + usage-based billing  
**Complexity**: Medium (straightforward API integration)

---

## Executive Summary

You're going to add **professional payment processing** to Top Dog using Stripe. This allows you to:

✅ Charge users monthly subscriptions  
✅ Offer multiple pricing tiers  
✅ Track usage and bill accordingly  
✅ Manage billing portal for customers  
✅ Handle failed payments automatically  
✅ Generate revenue reports  

**After this week**: Top Dog becomes a revenue-generating SaaS 💰

---

## Stripe Pricing Tiers Strategy

### Recommended Tier Structure

```
FREE TIER (Forever Free)
├─ LLM API calls: Unlimited*
├─ Projects: Unlimited
├─ Team members: 1
├─ Storage: Unlimited*
└─ Price: $0
   (* with fair use limits to prevent abuse)

PRO TIER ($12/month)
├─ LLM API calls: Unlimited
├─ Projects: Unlimited
├─ Team members: Up to 10
├─ Storage: Unlimited
├─ Priority email support
├─ Advanced analytics
└─ Price: $12/month ($120/year with 2 months free)

TEAMS TIER ($25/seat/month)
├─ Everything in Pro, plus:
├─ Team collaboration features
├─ Advanced permissions & roles
├─ Audit logging
├─ Phone support
├─ Custom branding options
├─ Team analytics & reporting
└─ Price: $25/seat/month (team of 5-50)

ENTERPRISE (Custom)
├─ Unlimited everything
├─ Dedicated account manager
├─ SLA agreement (99.9% uptime)
├─ Custom integrations
├─ White-label options
├─ On-premise deployment option
└─ Price: Custom (starting $500+/month)
```

**Why This Structure?**
- Free tier: attracts massive user base (millions), monetizes via ads/sponsorships later
- Pro ($12) = $1/month effective cost for professionals (obvious ROI)
- Teams ($25/seat) = perfect for small/medium teams, scales linearly
- Enterprise = handles large organizations with custom needs

---

## Step 1: Stripe Account Setup (Day 1 - 2 hours)

### Create Stripe Account

```bash
# Go to: https://dashboard.stripe.com/register
# Sign up with email
# Verify email
# Add business info
# Connect bank account (for payouts)
```

**What You'll Get:**
- **Publishable Key**: `pk_test_...` (use in frontend)
- **Secret Key**: `sk_test_...` (use in backend - KEEP PRIVATE)
- **API Keys Page**: https://dashboard.stripe.com/test/apikeys

**Security Rule:**
```
NEVER commit Secret Key to GitHub
ALWAYS store in Heroku Config Vars
```

### Get Your API Keys

```bash
# Backend environment variables to set (Heroku):
heroku config:set \
  STRIPE_SECRET_KEY="sk_test_..." \
  STRIPE_PUBLISHABLE_KEY="pk_test_..." \
  STRIPE_WEBHOOK_SECRET="whsec_..." \
  --app Top Dog-backend

# Frontend environment variables to set (Heroku):
heroku config:set \
  VITE_STRIPE_PUBLISHABLE_KEY="pk_test_..." \
  --app Top Dog-frontend
```

### Set Up Products in Stripe Dashboard

```
STRIPE DASHBOARD STEPS:

1. Go to: https://dashboard.stripe.com/products

2. Create product "Pro Plan"
   ├─ Name: "Top Dog Pro"
   ├─ Description: "Professional features"
   ├─ Billing: Recurring
   ├─ Price: $12.00/month
   └─ Save

3. Create product "Teams Plan"
   ├─ Name: "Top Dog Teams"
   ├─ Description: "Team collaboration"
   ├─ Billing: Recurring
   ├─ Price: $25.00/month per seat
   └─ Save

4. Note the Price IDs:
   ├─ Pro: price_1A2B3C...
   └─ Teams: price_2D3E4F...
```

**Store Price IDs in Backend:**
```python
# backend/config.py or environment variables
STRIPE_PRICE_IDS = {
    "pro": "price_1A2B3C...",
    "teams": "price_2D3E4F...",
}
```

---

## Step 2: Backend Stripe Integration (Days 2-3 - 16 hours)

### Install Stripe SDK

```bash
# In backend directory
pip install stripe

# Add to requirements.txt
stripe==7.10.0
```

### Create Stripe Service Module

**File**: `backend/services/stripe_service.py`

```python
import stripe
import os
from datetime import datetime
from typing import Optional, Dict, List

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class StripeService:
    """Handle all Stripe operations"""
    
    @staticmethod
    def create_customer(user_id: str, email: str, name: str) -> str:
        """Create a Stripe customer from a user"""
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={"user_id": user_id}
        )
        return customer.id

    @staticmethod
    def create_subscription(
        customer_id: str,
        price_id: str,
        trial_days: int = 14
    ) -> Dict:
        """Create a subscription for a customer"""
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            trial_period_days=trial_days,
            payment_behavior="default_incomplete",
            expand=["latest_invoice.payment_intent"],
        )
        return subscription

    @staticmethod
    def cancel_subscription(subscription_id: str) -> Dict:
        """Cancel a subscription"""
        subscription = stripe.Subscription.delete(subscription_id)
        return subscription

    @staticmethod
    def get_subscription(subscription_id: str) -> Dict:
        """Get subscription details"""
        subscription = stripe.Subscription.retrieve(subscription_id)
        return subscription

    @staticmethod
    def create_portal_session(customer_id: str, return_url: str) -> str:
        """Create a link to Stripe billing portal"""
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        return session.url

    @staticmethod
    def create_checkout_session(
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
    ) -> str:
        """Create a checkout session for upgrading plan"""
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
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return session.id

    @staticmethod
    def handle_webhook(event: Dict) -> Dict:
        """Handle Stripe webhook events"""
        
        if event["type"] == "customer.subscription.created":
            subscription = event["data"]["object"]
            # Update user plan in database
            return {"status": "subscription_created"}
            
        elif event["type"] == "customer.subscription.updated":
            subscription = event["data"]["object"]
            # Update user plan in database
            return {"status": "subscription_updated"}
            
        elif event["type"] == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            # Downgrade user to free plan
            return {"status": "subscription_cancelled"}
            
        elif event["type"] == "invoice.payment_succeeded":
            invoice = event["data"]["object"]
            # Send receipt email
            return {"status": "payment_succeeded"}
            
        elif event["type"] == "invoice.payment_failed":
            invoice = event["data"]["object"]
            # Send payment failure email
            return {"status": "payment_failed"}
            
        return {"status": "event_received"}
```

### Create Database Schema for Billing

**File**: `backend/models/subscription.py`

```python
from sqlalchemy import Column, String, DateTime, Integer, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    TEAMS = "teams"
    ENTERPRISE = "enterprise"

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(String, primary_key=True)  # Stripe subscription ID
    user_id = Column(String, ForeignKey("users.id"), unique=True)
    stripe_customer_id = Column(String, unique=True)
    stripe_subscription_id = Column(String)
    tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    status = Column(String)  # active, trialing, past_due, canceled
    
    # Billing info
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancel_at = Column(DateTime, nullable=True)
    canceled_at = Column(DateTime, nullable=True)
    
    # Usage tracking
    api_calls_used = Column(Integer, default=0)
    api_calls_limit = Column(Integer, default=100)  # Free tier limit
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="subscription")
```

### API Endpoints for Subscription Management

**File**: `backend/routes/billing.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import stripe
from services.stripe_service import StripeService
from models.subscription import Subscription
from db import get_db

router = APIRouter(prefix="/api/billing", tags=["billing"])

@router.post("/create-checkout-session/{price_id}")
async def create_checkout(
    price_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create Stripe checkout session for upgrade"""
    try:
        # Get or create customer
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).first()
        
        if not subscription or not subscription.stripe_customer_id:
            customer_id = StripeService.create_customer(
                current_user.id,
                current_user.email,
                current_user.name
            )
            if not subscription:
                subscription = Subscription(
                    user_id=current_user.id,
                    stripe_customer_id=customer_id
                )
                db.add(subscription)
                db.commit()
            else:
                subscription.stripe_customer_id = customer_id
                db.commit()
        
        customer_id = subscription.stripe_customer_id
        
        # Create checkout session
        session_id = StripeService.create_checkout_session(
            customer_id=customer_id,
            price_id=price_id,
            success_url=f"{FRONTEND_URL}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{FRONTEND_URL}/billing/cancel"
        )
        
        return {"sessionId": session_id}
    
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/portal")
async def create_portal_session(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create link to Stripe billing portal"""
    try:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).first()
        
        if not subscription or not subscription.stripe_customer_id:
            raise HTTPException(status_code=404, detail="No subscription found")
        
        portal_url = StripeService.create_portal_session(
            customer_id=subscription.stripe_customer_id,
            return_url=f"{FRONTEND_URL}/dashboard"
        )
        
        return {"url": portal_url}
    
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/subscription")
async def get_subscription(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get current subscription info"""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        # Create free tier subscription
        subscription = Subscription(
            user_id=current_user.id,
            tier="free",
            api_calls_limit=100
        )
        db.add(subscription)
        db.commit()
    
    return {
        "tier": subscription.tier,
        "status": subscription.status,
        "api_calls_used": subscription.api_calls_used,
        "api_calls_limit": subscription.api_calls_limit,
        "current_period_end": subscription.current_period_end,
        "cancel_at": subscription.cancel_at
    }

@router.post("/webhook")
async def handle_webhook(
    request: Request,
    db = Depends(get_db)
):
    """Handle Stripe webhook events"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle events
    if event["type"] == "customer.subscription.created":
        subscription_obj = event["data"]["object"]
        # Update database
        subscription = db.query(Subscription).filter(
            Subscription.stripe_customer_id == subscription_obj["customer"]
        ).first()
        if subscription:
            subscription.stripe_subscription_id = subscription_obj["id"]
            subscription.status = subscription_obj["status"]
            subscription.tier = "starter"  # or determine from price_id
            db.commit()
    
    elif event["type"] == "customer.subscription.deleted":
        subscription_obj = event["data"]["object"]
        subscription = db.query(Subscription).filter(
            Subscription.stripe_customer_id == subscription_obj["customer"]
        ).first()
        if subscription:
            subscription.tier = "free"
            subscription.status = "canceled"
            db.commit()
    
    return {"received": True}
```

### Register Webhook in Stripe

```bash
# Go to: https://dashboard.stripe.com/webhooks

# Click "Add Endpoint"
# Endpoint URL: https://Top Dog-backend.herokuapp.com/api/billing/webhook
# Select events:
#   ├─ customer.subscription.created
#   ├─ customer.subscription.updated
#   ├─ customer.subscription.deleted
#   ├─ invoice.payment_succeeded
#   └─ invoice.payment_failed

# Click "Create Endpoint"
# Copy "Signing Secret"
# Add to Heroku:
heroku config:set STRIPE_WEBHOOK_SECRET="whsec_..." --app Top Dog-backend
```

---

## Step 3: Frontend Stripe Integration (Days 3-4 - 16 hours)

### Install Stripe React Library

```bash
# In frontend directory
npm install @stripe/react-stripe-js @stripe/js

# Add to package.json dependencies
```

### Create Billing Page Component

**File**: `frontend/src/pages/BillingPage.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import { loadStripe } from '@stripe/js';
import { EmbeddedCheckoutProvider, EmbeddedCheckout } from '@stripe/react-stripe-js';
import axios from 'axios';

const stripePromise = loadStripe(
  import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY
);

export function BillingPage() {
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCheckout, setShowCheckout] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState(null);

  useEffect(() => {
    fetchSubscription();
  }, []);

  const fetchSubscription = async () => {
    try {
      const response = await axios.get('/api/billing/subscription');
      setSubscription(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch subscription:', error);
      setLoading(false);
    }
  };

  const handleUpgrade = async (priceId: string) => {
    try {
      const response = await axios.post(`/api/billing/create-checkout-session/${priceId}`);
      const stripe = await stripePromise;
      const { error } = await stripe.redirectToCheckout({
        sessionId: response.data.sessionId,
      });
      if (error) console.error(error);
    } catch (error) {
      console.error('Checkout failed:', error);
    }
  };

  const handleBillingPortal = async () => {
    try {
      const response = await axios.get('/api/billing/portal');
      window.location.href = response.data.url;
    } catch (error) {
      console.error('Portal failed:', error);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="billing-container">
      <h1>Billing & Plans</h1>

      {/* Current Plan */}
      <div className="current-plan">
        <h2>Current Plan</h2>
        <p>You are on the <strong>{subscription?.tier}</strong> plan</p>
        <p>API Calls: {subscription?.api_calls_used} / {subscription?.api_calls_limit}</p>
        {subscription?.tier !== 'free' && (
          <button onClick={handleBillingPortal}>
            Manage Billing
          </button>
        )}
      </div>

      {/* Pricing Tiers */}
      <div className="pricing-tiers">
        <PricingCard
          name="Pro"
          price="$12"
          features={['Unlimited projects', '10 team members', 'Priority support']}
          isActive={subscription?.tier === 'pro'}
          onUpgrade={() => handleUpgrade('price_1A2B3C...')}
        />

        <PricingCard
          name="Teams"
          price="$25/seat"
          features={['Unlimited projects', 'Advanced permissions', 'Phone support']}
          isActive={subscription?.tier === 'teams'}
          onUpgrade={() => handleUpgrade('price_2D3E4F...')}
        />
      </div>
    </div>
  );
}

function PricingCard({ name, price, calls, features, isActive, onUpgrade }) {
  return (
    <div className={`pricing-card ${isActive ? 'active' : ''}`}>
      <h3>{name}</h3>
      <p className="price">{price}/month</p>
      <p className="calls">{calls} API calls</p>
      <ul>
        {features.map((f, i) => (
          <li key={i}>{f}</li>
        ))}
      </ul>
      {!isActive && (
        <button onClick={onUpgrade} className="upgrade-btn">
          Upgrade
        </button>
      )}
      {isActive && <span className="active-badge">Current Plan</span>}
    </div>
  );
}
```

### Create Styles for Billing Page

**File**: `frontend/src/styles/billing.css`

```css
.billing-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.current-plan {
  background: #f0f4f8;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 40px;
}

.pricing-tiers {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 40px;
}

.pricing-card {
  border: 2px solid #ddd;
  border-radius: 8px;
  padding: 30px;
  text-align: center;
  transition: all 0.3s ease;
}

.pricing-card:hover {
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  transform: translateY(-5px);
}

.pricing-card.active {
  border-color: #007bff;
  background: #f0f4f8;
}

.pricing-card h3 {
  font-size: 24px;
  margin-bottom: 10px;
}

.pricing-card .price {
  font-size: 36px;
  font-weight: bold;
  color: #007bff;
  margin: 10px 0;
}

.pricing-card .calls {
  color: #666;
  font-size: 14px;
  margin-bottom: 20px;
}

.pricing-card ul {
  list-style: none;
  padding: 0;
  margin-bottom: 20px;
  text-align: left;
}

.pricing-card li {
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.pricing-card li:last-child {
  border-bottom: none;
}

.upgrade-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  width: 100%;
  transition: background 0.3s ease;
}

.upgrade-btn:hover {
  background: #0056b3;
}

.active-badge {
  display: inline-block;
  background: #28a745;
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 12px;
  margin-top: 10px;
}
```

### Add Billing Link to Navigation

**File**: `frontend/src/components/Navigation.tsx`

```typescript
// Add this to your navigation menu
<Link to="/billing">
  <span className="nav-icon">💳</span>
  Billing & Plans
</Link>
```

---

## Step 4: Usage Tracking (Days 4-5 - 12 hours)

### Track API Calls Per User

**File**: `backend/middleware/usage_tracker.py`

```python
from models.subscription import Subscription
from db import get_db

async def track_usage(request, call_next, db):
    """Middleware to track API usage"""
    response = await call_next(request)
    
    # Get current user from request
    user = request.state.user
    if user:
        # Get subscription
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user.id
        ).first()
        
        if subscription:
            # Increment API calls
            subscription.api_calls_used += 1
            
            # Check limit
            if subscription.api_calls_used >= subscription.api_calls_limit:
                response.status_code = 429  # Too Many Requests
                return {
                    "error": "API limit exceeded",
                    "upgrade_url": "/api/billing/upgrade"
                }
            
            db.commit()
    
    return response
```

### Register Middleware in FastAPI

```python
# backend/main.py
from middleware.usage_tracker import track_usage

app.middleware("http")(track_usage)
```

### Reset Monthly Usage

**File**: `backend/tasks/reset_usage.py`

```python
from celery import shared_task
from models.subscription import Subscription
from datetime import datetime
from db import SessionLocal

@shared_task
def reset_monthly_usage():
    """Reset API usage at start of each month"""
    db = SessionLocal()
    
    subscriptions = db.query(Subscription).all()
    for subscription in subscriptions:
        if subscription.current_period_start and \
           subscription.current_period_start.month != datetime.now().month:
            subscription.api_calls_used = 0
    
    db.commit()
```

**Add to Heroku Scheduler:**
```bash
# From Heroku dashboard, add:
python -m tasks.reset_usage  # Run daily
```

---

## Step 5: Email Notifications (Day 6 - 8 hours)

### Send Receipt Emails

**File**: `backend/services/email_service.py`

```python
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os

class EmailService:
    
    @staticmethod
    def send_invoice_receipt(email: str, invoice_data: dict):
        """Send payment receipt email"""
        subject = "Top Dog Invoice Receipt"
        
        html_content = f"""
        <h1>Thank you for your payment!</h1>
        <p>Invoice Date: {invoice_data['date']}</p>
        <p>Amount: ${invoice_data['amount']}</p>
        <p>Plan: {invoice_data['plan']}</p>
        <p><a href="{invoice_data['invoice_url']}">View Invoice</a></p>
        """
        
        EmailService._send_email(email, subject, html_content)
    
    @staticmethod
    def send_payment_failed(email: str, error: str):
        """Send payment failure email"""
        subject = "Top Dog Payment Failed"
        
        html_content = f"""
        <h1>Payment Failed</h1>
        <p>We couldn't process your payment.</p>
        <p>Error: {error}</p>
        <p><a href="/api/billing/portal">Update Payment Method</a></p>
        """
        
        EmailService._send_email(email, subject, html_content)
    
    @staticmethod
    def _send_email(to_email: str, subject: str, html_content: str):
        """Generic email sender"""
        from_email = os.getenv("SENDGRID_FROM_EMAIL")
        
        # Using SendGrid for production
        import sendgrid
        from sendgrid.helpers.mail import Mail
        
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        
        sg = sendgrid.SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        sg.send(message)
```

---

## Step 6: Testing (Day 7 - 8 hours)

### Test Stripe Locally

```bash
# Install Stripe CLI
# https://stripe.com/docs/stripe-cli

# Download and install for your OS
# Login to Stripe
stripe login

# Test webhook locally
stripe listen --forward-to localhost:8000/api/billing/webhook

# In another terminal, trigger test events
stripe trigger customer.subscription.created

# Check your backend logs
```

### Test Checkout Flow

```
TEST CREDIT CARDS (Stripe Test Mode):

Success: 4242 4242 4242 4242
Decline: 4000 0000 0000 0002
Require 3D Secure: 4000 0025 0000 3155

Expiry: Any future date (e.g., 12/25)
CVC: Any 3 digits (e.g., 123)
```

### Test Payment Webhook

```python
# backend/tests/test_billing.py
import pytest
from services.stripe_service import StripeService

def test_subscription_created():
    """Test subscription creation webhook"""
    event = {
        "type": "customer.subscription.created",
        "data": {
            "object": {
                "id": "sub_test123",
                "customer": "cus_test456",
                "status": "active"
            }
        }
    }
    
    result = StripeService.handle_webhook(event)
    assert result["status"] == "subscription_created"

def test_subscription_canceled():
    """Test subscription cancellation webhook"""
    event = {
        "type": "customer.subscription.deleted",
        "data": {
            "object": {
                "customer": "cus_test456"
            }
        }
    }
    
    result = StripeService.handle_webhook(event)
    assert result["status"] == "subscription_cancelled"
```

---

## Step 7: Dashboard & Analytics (Day 7+ - Optional)

### Create Revenue Dashboard

**File**: `frontend/src/pages/AdminDashboard.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import axios from 'axios';

export function AdminDashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    const response = await axios.get('/api/admin/stats');
    setStats(response.data);
  };

  if (!stats) return <div>Loading...</div>;

  return (
    <div className="admin-dashboard">
      <h1>Revenue Dashboard</h1>
      
      <div className="stats-grid">
        <StatCard
          title="Monthly Recurring Revenue"
          value={`$${stats.mrr}`}
          change={stats.mrr_change}
        />
        <StatCard
          title="Active Subscriptions"
          value={stats.active_subs}
          change={stats.subs_change}
        />
        <StatCard
          title="Churn Rate"
          value={`${stats.churn_rate}%`}
          change={-stats.churn_change}
        />
        <StatCard
          title="ARPU"
          value={`$${stats.arpu}`}
          change={stats.arpu_change}
        />
      </div>

      <div className="charts">
        <RevenueChart data={stats.revenue_by_month} />
        <PlanDistribution data={stats.plan_distribution} />
      </div>
    </div>
  );
}

function StatCard({ title, value, change }) {
  return (
    <div className="stat-card">
      <h3>{title}</h3>
      <p className="stat-value">{value}</p>
      <p className={`stat-change ${change >= 0 ? 'positive' : 'negative'}`}>
        {change >= 0 ? '↑' : '↓'} {Math.abs(change)}%
      </p>
    </div>
  );
}
```

### Create Admin Endpoints

**File**: `backend/routes/admin.py`

```python
from fastapi import APIRouter, Depends
from models.subscription import Subscription
from db import get_db
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/stats")
async def get_revenue_stats(db = Depends(get_db)):
    """Get revenue and subscription statistics"""
    
    # Active subscriptions
    active_subs = db.query(Subscription).filter(
        Subscription.status == "active"
    ).count()
    
    # Calculate MRR (Monthly Recurring Revenue)
    pro_subs = db.query(Subscription).filter(
        Subscription.tier == "pro",
        Subscription.status == "active"
    ).count()
    
    teams_subs = db.query(Subscription).filter(
        Subscription.tier == "teams",
        Subscription.status == "active"
    ).count()
    
    mrr = (pro_subs * 12) + (teams_subs * 25)
    
    # Calculate churn
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    churned = db.query(Subscription).filter(
        Subscription.canceled_at >= thirty_days_ago,
        Subscription.status == "canceled"
    ).count()
    
    churn_rate = (churned / active_subs * 100) if active_subs > 0 else 0
    
    return {
        "mrr": mrr,
        "active_subs": active_subs,
        "churn_rate": round(churn_rate, 2),
        "arpu": round(mrr / active_subs, 2) if active_subs > 0 else 0,
        "pro_subs": pro_subs,
        "teams_subs": teams_subs,
    }
```

---

## Step 8: Deployment Checklist

### Before Going Live

```
STRIPE PRODUCTION SETUP:

✅ Switch from test keys to live keys
✅ Update all environment variables to production keys
✅ Configure CORS for production domain
✅ Set up email notifications (SendGrid)
✅ Enable fraud detection in Stripe dashboard
✅ Set up PCI compliance
✅ Test full checkout flow in production
✅ Monitor webhook deliveries
✅ Set up Stripe alerts for failed payments
✅ Create refund policy
✅ Create pricing FAQ
✅ Test payment methods (card, Apple Pay, Google Pay)
✅ Verify error handling and messages
```

### Production Environment Variables

```bash
# Set on Heroku
heroku config:set \
  STRIPE_SECRET_KEY="sk_live_..." \
  STRIPE_PUBLISHABLE_KEY="pk_live_..." \
  STRIPE_WEBHOOK_SECRET="whsec_live_..." \
  ENVIRONMENT="production" \
  --app Top Dog-backend
```

---

## Revenue Projections

### Year 1-3 Financial Model

```
YEAR 1:
├─ Free users: 5M (network effects)
├─ Pro users: 100K-250K × $120/year = $12M-$30M
├─ Teams: 10K-50K teams × $300/year = $15M-$75M
├─ Enterprise: 50-100 customers × $20K avg = $1M-$2M
└─ TOTAL YEAR 1: $28M-$107M

YEAR 2:
├─ Free users: 15M
├─ Pro users: 500K-1M × $120/year = $60M-$120M
├─ Teams: 100K-200K teams × $300/year = $30M-$60M
├─ Enterprise: 150-300 customers × $30K avg = $4.5M-$9M
└─ TOTAL YEAR 2: $94M-$369M

YEAR 3:
├─ Free users: 30M
├─ Pro users: 1.5M-2M × $120/year = $180M-$240M
├─ Teams: 500K-1M teams × $300/year = $150M-$300M
├─ Enterprise: 500-1000 customers × $40K avg = $20M-$40M
└─ TOTAL YEAR 3: $350M-$1B+
```

### Conservative vs Aggressive Scenarios

**Conservative (Product-focused, organic growth)**
- Year 1: $30-50M (steady, word-of-mouth)
- Year 2: $100-200M (accelerating)
- Year 3: $300-500M (market leader)

**Aggressive (Sales-driven, marketing investment)**
- Year 1: $50-107M (funded marketing, partnerships)
- Year 2: $200-369M (enterprise sales team)
- Year 3: $600M-$1B (market dominance)

---

## Common Issues & Solutions

### Issue: Webhook Not Triggering
**Solution**: 
- Check webhook endpoint is accessible from internet
- Verify signing secret in Heroku matches Stripe dashboard
- Check logs: `heroku logs --tail --app Top Dog-backend`

### Issue: Checkout Redirects to Wrong URL
**Solution**:
- Verify success_url in checkout session creation
- Check FRONTEND_URL environment variable is correct

### Issue: Payment Succeeds But Subscription Not Created
**Solution**:
- Verify webhook handler in backend
- Check database connection
- Review Stripe dashboard for webhook delivery status

### Issue: Customer Can't Access Billing Portal
**Solution**:
- Verify customer_id exists in Stripe
- Check return_url is accessible
- Verify browser allows third-party cookies

---

## Next Steps

1. **This Week**: Set up Stripe account + integrate backend (Days 1-4)
2. **Next Week**: Integrate frontend + testing (Days 5-7)
3. **Deploy**: Push to Heroku with billing live
4. **Monitor**: Track revenue, churn, customer success
5. **Optimize**: A/B test pricing, features, messaging

---

**Timeline**: 1 week to integrate  
**Effort**: ~50 hours (1-2 developers)  
**Complexity**: Medium  
**Revenue Impact**: 💰 Turns Top Dog into a revenue-generating SaaS

**You're ready to monetize!** 🚀💰

