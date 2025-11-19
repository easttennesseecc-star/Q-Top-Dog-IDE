"""
Subscription model and database schema for Stripe integration
"""

from sqlalchemy import Column, String, DateTime, Integer, Enum, Boolean, Float, ForeignKey
from typing import Any
from sqlalchemy.orm import relationship
from . import Base
from datetime import datetime
import enum
import uuid


class SubscriptionTier(str, enum.Enum):
    """Subscription tier levels"""
    FREE = "free"
    PRO = "pro"
    PRO_PLUS = "pro_plus"
    TEAMS = "teams"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, enum.Enum):
    """Subscription status"""
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"


class Subscription(Base):
    """User subscription record"""
    __tablename__ = "subscriptions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    # User linkage (tests provide a minimal User model; production may ignore it)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Stripe IDs
    stripe_customer_id = Column(String, unique=True, nullable=True)
    stripe_subscription_id = Column(String, unique=True, nullable=True)
    stripe_payment_method_id = Column(String, nullable=True)
    
    # Subscription info
    tier: Any = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False)
    status: Any = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False)
    
    # Billing cycle
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    trial_start = Column(DateTime, nullable=True)
    trial_end = Column(DateTime, nullable=True)
    
    # Cancellation
    cancel_at = Column(DateTime, nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)
    canceled_at = Column(DateTime, nullable=True)
    
    # Usage tracking
    api_calls_used = Column(Integer, default=0)
    api_calls_limit = Column(Integer, default=100)  # Free tier limit
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="subscription", uselist=False)
    invoices = relationship("Invoice", back_populates="subscription", cascade="all, delete-orphan")
    usage_events = relationship("UsageEvent", back_populates="subscription", cascade="all, delete-orphan")


class Invoice(Base):
    """Invoice record from Stripe"""
    __tablename__ = "invoices"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    subscription_id = Column(String, ForeignKey("subscriptions.id"), nullable=False)
    
    # Stripe info
    stripe_invoice_id = Column(String, unique=True, nullable=False)
    stripe_customer_id = Column(String, nullable=False)
    
    # Invoice details
    invoice_number = Column(String, nullable=True)
    amount_paid = Column(Float, default=0.0)
    amount_due = Column(Float, default=0.0)
    amount_remaining = Column(Float, default=0.0)
    currency = Column(String, default="usd")
    
    # Status
    status = Column(String, default="draft")  # draft, open, paid, uncollectible, void
    paid = Column(Boolean, default=False)
    attempted = Column(Boolean, default=False)
    
    # Period
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    
    # URLs
    hosted_invoice_url = Column(String, nullable=True)
    invoice_pdf = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="invoices")


class UsageEvent(Base):
    """Track API usage for billing"""
    __tablename__ = "usage_events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    subscription_id = Column(String, ForeignKey("subscriptions.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Usage details
    event_type = Column(String, nullable=False)  # api_call, generation, deployment, etc.
    amount = Column(Integer, default=1)
    event_metadata = Column(String, nullable=True)  # JSON string for additional data
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships (user disabled; subscription retained)
    subscription = relationship("Subscription", back_populates="usage_events")


class BillingAlert(Base):
    """Alert user of billing issues"""
    __tablename__ = "billing_alerts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(String, ForeignKey("subscriptions.id"), nullable=False)
    
    # Alert details
    alert_type = Column(String, nullable=False)  # payment_failed, usage_limit, trial_ending, etc.
    message = Column(String, nullable=False)
    severity = Column(String, default="info")  # info, warning, critical
    
    # Status
    read = Column(Boolean, default=False)
    resolved = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)


# SQL queries for common operations

CREATE_SUBSCRIPTION_TABLE = """
CREATE TABLE IF NOT EXISTS subscriptions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) UNIQUE NOT NULL REFERENCES users(id),
    stripe_customer_id VARCHAR(255) UNIQUE,
    stripe_subscription_id VARCHAR(255) UNIQUE,
    stripe_payment_method_id VARCHAR(255),
    tier ENUM('free', 'pro', 'teams', 'enterprise') DEFAULT 'free',
    status ENUM('trialing', 'active', 'past_due', 'canceled', 'unpaid') DEFAULT 'active',
    current_period_start DATETIME,
    current_period_end DATETIME,
    trial_start DATETIME,
    trial_end DATETIME,
    cancel_at DATETIME,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    canceled_at DATETIME,
    api_calls_used INT DEFAULT 0,
    api_calls_limit INT DEFAULT 100,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_user_id (user_id),
    KEY idx_stripe_customer_id (stripe_customer_id),
    KEY idx_status (status)
);
"""

CREATE_INVOICES_TABLE = """
CREATE TABLE IF NOT EXISTS invoices (
    id VARCHAR(36) PRIMARY KEY,
    subscription_id VARCHAR(36) NOT NULL REFERENCES subscriptions(id),
    stripe_invoice_id VARCHAR(255) UNIQUE NOT NULL,
    stripe_customer_id VARCHAR(255) NOT NULL,
    invoice_number VARCHAR(255),
    amount_paid FLOAT DEFAULT 0.0,
    amount_due FLOAT DEFAULT 0.0,
    amount_remaining FLOAT DEFAULT 0.0,
    currency VARCHAR(3) DEFAULT 'usd',
    status VARCHAR(20) DEFAULT 'draft',
    paid BOOLEAN DEFAULT FALSE,
    attempted BOOLEAN DEFAULT FALSE,
    period_start DATETIME,
    period_end DATETIME,
    due_date DATETIME,
    hosted_invoice_url TEXT,
    invoice_pdf TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_subscription_id (subscription_id),
    KEY idx_stripe_invoice_id (stripe_invoice_id),
    KEY idx_status (status)
);
"""

CREATE_USAGE_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS usage_events (
    id VARCHAR(36) PRIMARY KEY,
    subscription_id VARCHAR(36) NOT NULL REFERENCES subscriptions(id),
    user_id VARCHAR(36) NOT NULL REFERENCES users(id),
    event_type VARCHAR(50) NOT NULL,
    amount INT DEFAULT 1,
    metadata TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_subscription_id (subscription_id),
    KEY idx_user_id (user_id),
    KEY idx_event_type (event_type),
    KEY idx_created_at (created_at)
);
"""

CREATE_BILLING_ALERTS_TABLE = """
CREATE TABLE IF NOT EXISTS billing_alerts (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id),
    subscription_id VARCHAR(36) NOT NULL REFERENCES subscriptions(id),
    alert_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'info',
    read BOOLEAN DEFAULT FALSE,
    resolved BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    KEY idx_user_id (user_id),
    KEY idx_alert_type (alert_type),
    KEY idx_read (read)
);
"""
