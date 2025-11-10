/**
 * BillingDashboard.tsx
 * Complete billing management dashboard
 * 
 * Features:
 * - Subscription status
 * - Invoice history
 * - Payment method management
 * - Usage analytics
 * - Download invoices
 */

import React, { useState, useEffect } from 'react';
import '../styles/BillingDashboard.css';

// ============================================================================
// Type Definitions
// ============================================================================

interface Subscription {
  tier: string;
  status: string;
  api_calls_used: number;
  api_calls_limit: number;
  current_period_end: number | null;
  cancel_at: number | null;
  stripe_subscription_id: string | null;
}

interface Invoice {
  id: string;
  stripe_invoice_id: string;
  number: string;
  amount_paid: number;
  status: string;
  created: number;
  period_start: number | null;
  period_end: number | null;
  hosted_url: string;
}

interface BillingAlert {
  id: string;
  message: string;
  severity: 'info' | 'warning' | 'critical';
  created_at: number;
}

// ============================================================================
// Subscription Status Component
// ============================================================================

const SubscriptionStatus: React.FC<{ subscription: Subscription }> = ({
  subscription,
}) => {
  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return '#4caf50';
      case 'trialing':
        return '#2196f3';
      case 'past_due':
        return '#ff9800';
      case 'canceled':
        return '#f44';
      default:
        return '#666';
    }
  };

  const getStatusLabel = (status: string) => {
    return status
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <div className="subscription-status">
      <div className="status-header">
        <h3>Current Subscription</h3>
        <span
          className="status-badge"
          style={{ backgroundColor: getStatusColor(subscription.status) }}
        >
          {getStatusLabel(subscription.status)}
        </span>
      </div>

      <div className="status-content">
        <div className="status-item">
          <span className="label">Plan:</span>
          <span className="value">
            {subscription.tier.toUpperCase()} Tier
          </span>
        </div>

        <div className="status-item">
          <span className="label">API Calls Usage:</span>
          <div className="usage-bar">
            <div
              className="usage-fill"
              style={{
                width: `${(subscription.api_calls_used / subscription.api_calls_limit) * 100}%`,
              }}
            ></div>
          </div>
          <span className="usage-text">
            {subscription.api_calls_used} / {subscription.api_calls_limit} calls
          </span>
        </div>

        {subscription.current_period_end && (
          <div className="status-item">
            <span className="label">Billing Period Ends:</span>
            <span className="value">
              {formatDate(subscription.current_period_end)}
            </span>
          </div>
        )}

        {subscription.cancel_at && (
          <div className="status-item warning">
            <span className="label">⚠️ Cancels At:</span>
            <span className="value">{formatDate(subscription.cancel_at)}</span>
          </div>
        )}
      </div>

      <div className="status-actions">
        <button className="action-button primary">Upgrade Plan</button>
        <button className="action-button secondary">Manage Payments</button>
        {!subscription.cancel_at && (
          <button className="action-button danger">Cancel Subscription</button>
        )}
      </div>
    </div>
  );
};

// ============================================================================
// Invoice History Component
// ============================================================================

const InvoiceHistory: React.FC<{ invoices: Invoice[] }> = ({ invoices }) => {
  const [downloading, setDownloading] = useState<string | null>(null);

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const handleDownload = async (invoice: Invoice) => {
    setDownloading(invoice.id);
    try {
      // Open hosted invoice URL in new tab
      window.open(invoice.hosted_url, '_blank');
    } catch (error) {
      console.error('Failed to download invoice:', error);
    } finally {
      setDownloading(null);
    }
  };

  if (!invoices || invoices.length === 0) {
    return (
      <div className="invoice-history">
        <h3>Invoice History</h3>
        <div className="empty-state">
          <p>📄 No invoices yet</p>
          <p className="subtitle">Your invoices will appear here</p>
        </div>
      </div>
    );
  }

  return (
    <div className="invoice-history">
      <h3>Invoice History</h3>

      <div className="invoice-table">
        <div className="invoice-header">
          <div className="col-date">Date</div>
          <div className="col-number">Invoice #</div>
          <div className="col-amount">Amount</div>
          <div className="col-status">Status</div>
          <div className="col-action">Action</div>
        </div>

        {invoices.map((invoice) => (
          <div key={invoice.id} className="invoice-row">
            <div className="col-date">{formatDate(invoice.created)}</div>
            <div className="col-number">
              {invoice.number || invoice.stripe_invoice_id.slice(0, 8)}
            </div>
            <div className="col-amount">${invoice.amount_paid.toFixed(2)}</div>
            <div className="col-status">
              <span
                className={`status-badge ${invoice.status}`}
              >
                {invoice.status.charAt(0).toUpperCase() + invoice.status.slice(1)}
              </span>
            </div>
            <div className="col-action">
              <button
                onClick={() => handleDownload(invoice)}
                disabled={downloading === invoice.id}
                className="download-button"
              >
                {downloading === invoice.id ? '⏳' : '⬇️'} Download
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ============================================================================
// Payment Method Manager Component
// ============================================================================

const PaymentMethodManager: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleOpenPortal = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/billing/portal', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to open billing portal');
      }

      const { url } = await response.json();
      window.location.href = url;
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to open billing portal'
      );
      setLoading(false);
    }
  };

  return (
    <div className="payment-method-manager">
      <div className="manager-header">
        <h3>Payment Method</h3>
        <p className="description">
          Manage your billing information, payment method, and subscriptions in
          the Stripe billing portal
        </p>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="manager-content">
        <div className="portal-info">
          <div className="icon">🔐</div>
          <div className="text">
            <h4>Stripe Billing Portal</h4>
            <p>Securely manage your payment methods and subscription settings</p>
          </div>
        </div>

        <button
          onClick={handleOpenPortal}
          disabled={loading}
          className="portal-button"
        >
          {loading ? 'Opening...' : '💳 Manage Payments'}
        </button>
      </div>

      <div className="portal-features">
        <h4>In the portal you can:</h4>
        <ul>
          <li>✅ Update payment method</li>
          <li>✅ Change billing email</li>
          <li>✅ View all invoices</li>
          <li>✅ Download receipts</li>
          <li>✅ Update billing address</li>
          <li>✅ Cancel subscription</li>
        </ul>
      </div>
    </div>
  );
};

// ============================================================================
// Billing Alerts Component
// ============================================================================

const BillingAlerts: React.FC<{ alerts: BillingAlert[] }> = ({ alerts }) => {
  if (!alerts || alerts.length === 0) {
    return null;
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'info':
        return '#2196f3';
      case 'warning':
        return '#ff9800';
      case 'critical':
        return '#f44';
      default:
        return '#666';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'info':
        return 'ℹ️';
      case 'warning':
        return '⚠️';
      case 'critical':
        return '🚨';
      default:
        return '📢';
    }
  };

  return (
    <div className="billing-alerts">
      {alerts.map((alert) => (
        <div
          key={alert.id}
          className={`alert alert-${alert.severity}`}
          style={{ borderLeftColor: getSeverityColor(alert.severity) }}
        >
          <span className="alert-icon">{getSeverityIcon(alert.severity)}</span>
          <span className="alert-message">{alert.message}</span>
        </div>
      ))}
    </div>
  );
};

// ============================================================================
// Main Billing Dashboard Component
// ============================================================================

const BillingDashboard: React.FC = () => {
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [alerts, setAlerts] = useState<BillingAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch billing data
  useEffect(() => {
    const fetchBillingData = async () => {
      try {
        const authToken = localStorage.getItem('auth_token');
        if (!authToken) {
          setError('Not authenticated');
          setLoading(false);
          return;
        }

        // Fetch subscription
        const subResponse = await fetch('/api/billing/subscription', {
          headers: { 'Authorization': `Bearer ${authToken}` },
        });

        if (!subResponse.ok) {
          throw new Error('Failed to fetch subscription');
        }

        const subData = await subResponse.json();
        setSubscription(subData);

        // Fetch invoices
        const invResponse = await fetch('/api/billing/invoices', {
          headers: { 'Authorization': `Bearer ${authToken}` },
        });

        if (invResponse.ok) {
          const invData = await invResponse.json();
          setInvoices(invData.invoices || []);
        }

        setError(null);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : 'Failed to fetch billing data'
        );
      } finally {
        setLoading(false);
      }
    };

    fetchBillingData();

    // Refresh every 30 seconds
    const interval = setInterval(fetchBillingData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="billing-dashboard loading">
        <div className="spinner"></div>
        <p>Loading billing information...</p>
      </div>
    );
  }

  if (error && !subscription) {
    return (
      <div className="billing-dashboard error">
        <div className="error-box">
          <h3>❌ Error</h3>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="billing-dashboard">
      <div className="dashboard-header">
        <h1>💳 Billing & Subscription</h1>
        <p>Manage your account, payments, and invoices</p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <BillingAlerts alerts={alerts} />

      <div className="dashboard-grid">
        <div className="dashboard-column">
          {subscription && <SubscriptionStatus subscription={subscription} />}
          <PaymentMethodManager />
        </div>

        <div className="dashboard-column">
          <InvoiceHistory invoices={invoices} />
        </div>
      </div>

      <div className="dashboard-footer">
        <p>
          Need help? <a href="mailto:support@topdog-ide.com">Contact support</a>
        </p>
      </div>
    </div>
  );
};

export default BillingDashboard;
