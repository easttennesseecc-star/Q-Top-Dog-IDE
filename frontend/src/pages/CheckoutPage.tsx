/**
 * CheckoutPage.tsx
 * Stripe checkout integration for tier upgrades
 * 
 * Features:
 * - Stripe Elements form
 * - Tier selection
 * - Trial period configuration
 * - Payment processing
 * - Error handling
 * - Loading states
 */

import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { loadStripe, Stripe, StripeElements } from '@stripe/stripe-js';
import {
  Elements,
  CardElement,
  useStripe,
  useElements,
} from '@stripe/react-stripe-js';
import '../styles/CheckoutPage.css';

interface TierOption {
  tier_name: string;
  monthly_price: number;
  features_count: number;
  icon: string;
}

interface CheckoutContextType {
  tierName: string;
  priceId: string;
  trialDays: number;
}

// ============================================================================
// Payment Processing Component
// ============================================================================

const PaymentForm: React.FC<CheckoutContextType> = ({
  tierName,
  priceId,
  trialDays,
}) => {
  const stripe = useStripe();
  const elements = useElements();
  const navigate = useNavigate();

  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [email, setEmail] = useState('');
  const [cardholderName, setCardholderName] = useState('');

  // Process payment
  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!stripe || !elements) {
      setError('Stripe is not loaded. Please refresh the page.');
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      // Step 1: Create Checkout Session on backend
      const checkoutResponse = await fetch('/api/billing/create-checkout-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          price_id: priceId,
          trial_days: trialDays,
        }),
      });

      if (!checkoutResponse.ok) {
        throw new Error('Failed to create checkout session');
      }

      const { sessionId } = await checkoutResponse.json();

      if (!sessionId) {
        throw new Error('No session ID returned');
      }

      // Step 2: Redirect to Stripe Checkout
      const { error: stripeError } = await stripe.redirectToCheckout({
        sessionId: sessionId,
      });

      if (stripeError) {
        setError(stripeError.message || 'Payment failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Payment processing failed');
      setIsProcessing(false);
    }
  };

  return (
    <form className="payment-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="email">Email Address</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="your@email.com"
          required
          disabled={isProcessing}
        />
      </div>

      <div className="form-group">
        <label htmlFor="name">Cardholder Name</label>
        <input
          id="name"
          type="text"
          value={cardholderName}
          onChange={(e) => setCardholderName(e.target.value)}
          placeholder="Full Name"
          required
          disabled={isProcessing}
        />
      </div>

      <div className="form-group">
        <label htmlFor="card">Card Details</label>
        <CardElement
          id="card"
          options={{
            style: {
              base: {
                fontSize: '16px',
                color: '#424770',
                '::placeholder': {
                  color: '#aab7c4',
                },
              },
              invalid: {
                color: '#fa755a',
              },
            },
          }}
          disabled={isProcessing}
        />
      </div>

      {error && <div className="error-message">{error}</div>}

      <button
        type="submit"
        disabled={isProcessing || !stripe}
        className="submit-button"
      >
        {isProcessing ? (
          <>
            <span className="spinner"></span>
            Processing...
          </>
        ) : (
          `Upgrade to ${tierName.toUpperCase()}`
        )}
      </button>

      <div className="trial-info">
        <p>
          ✨ <strong>{trialDays} days free trial</strong> - No charges during trial
        </p>
        <p>Cancel anytime before trial ends to avoid charges</p>
      </div>
    </form>
  );
};

// ============================================================================
// Checkout Summary Card
// ============================================================================

const CheckoutSummary: React.FC<{
  tier: TierOption;
  trialDays: number;
}> = ({ tier, trialDays }) => {
  const totalCost = (tier.monthly_price * (trialDays / 30)).toFixed(2);

  return (
    <div className="checkout-summary">
      <h3>Order Summary</h3>

      <div className="summary-item">
        <span>Plan:</span>
        <strong>{tier.tier_name} Tier</strong>
      </div>

      <div className="summary-item">
        <span>Monthly Price:</span>
        <strong>${tier.monthly_price.toFixed(2)}</strong>
      </div>

      <div className="summary-item">
        <span>Trial Period:</span>
        <strong>{trialDays} days</strong>
      </div>

      <div className="summary-divider"></div>

      <div className="summary-item total">
        <span>Estimated First Charge:</span>
        <strong>${totalCost}</strong>
      </div>

      <div className="features-included">
        <h4>Included Features:</h4>
        <ul>
          {Array.from({ length: tier.features_count }).map((_, i) => (
            <li key={i}>
              <span className="checkmark">✓</span>
              Feature {i + 1}
            </li>
          ))}
        </ul>
      </div>

      <div className="guarantee">
        <p>💳 Secure payment powered by Stripe</p>
        <p>🔒 Your payment information is encrypted</p>
        <p>📧 Confirmation email will be sent immediately</p>
      </div>
    </div>
  );
};

// ============================================================================
// Main Checkout Page
// ============================================================================

interface CheckoutPageProps {
  stripePromise: Promise<Stripe | null>;
}

const CheckoutPageContent: React.FC<CheckoutPageProps> = ({ stripePromise }) => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [tier, setTier] = useState<TierOption | null>(null);
  const [trialDays] = useState(14);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Get tier from URL parameter
  useEffect(() => {
    const tierParam = searchParams.get('tier');
    if (!tierParam) {
      setError('No tier selected');
      setLoading(false);
      return;
    }

    // Fetch tier details from backend
    const fetchTierDetails = async () => {
      try {
        const response = await fetch('/api/tier/info', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch tier details');
        }

        const data = await response.json();
        const selectedTier = data.tiers?.find(
          (t: TierOption) => t.tier_name.toLowerCase() === tierParam.toLowerCase()
        );

        if (!selectedTier) {
          throw new Error('Tier not found');
        }

        setTier(selectedTier);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load tier details');
      } finally {
        setLoading(false);
      }
    };

    fetchTierDetails();
  }, [searchParams]);

  if (loading) {
    return (
      <div className="checkout-page loading">
        <div className="spinner"></div>
        <p>Loading checkout...</p>
      </div>
    );
  }

  if (error || !tier) {
    return (
      <div className="checkout-page error">
        <div className="error-box">
          <h2>❌ Checkout Error</h2>
          <p>{error || 'Failed to load checkout page'}</p>
          <button onClick={() => navigate('/pricing')}>Back to Pricing</button>
        </div>
      </div>
    );
  }

  const priceId = `price_${tier.tier_name.toLowerCase()}`;

  return (
    <Elements stripe={stripePromise}>
      <div className="checkout-page">
        <div className="checkout-container">
          {/* Header */}
          <div className="checkout-header">
            <button className="back-button" onClick={() => navigate('/pricing')}>
              ← Back to Pricing
            </button>
            <h1>Complete Your Upgrade</h1>
            <p>Join thousands of developers using Q-IDE</p>
          </div>

          {/* Main Content */}
          <div className="checkout-content">
            {/* Left: Payment Form */}
            <div className="payment-section">
              <h2>Payment Method</h2>
              <PaymentForm
                tierName={tier.tier_name}
                priceId={priceId}
                trialDays={trialDays}
              />
            </div>

            {/* Right: Summary */}
            <div className="summary-section">
              <CheckoutSummary tier={tier} trialDays={trialDays} />
            </div>
          </div>

          {/* Footer */}
          <div className="checkout-footer">
            <p>
              Questions? <a href="mailto:support@topdog-ide.com">Contact support</a>
            </p>
            <p>
              Have a coupon? Apply it during the checkout process.
            </p>
          </div>
        </div>
      </div>
    </Elements>
  );
};

export default CheckoutPageContent;
