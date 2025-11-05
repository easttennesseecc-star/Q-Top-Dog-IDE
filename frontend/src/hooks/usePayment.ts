/**
 * usePayment.ts
 * React hook for Stripe payment operations
 * 
 * Provides:
 * - Create checkout session
 * - Get subscription status
 * - Download invoices
 * - Manage payment methods
 */

import { useState, useCallback } from 'react';

interface CheckoutSessionResponse {
  status: string;
  sessionId: string;
}

interface SubscriptionResponse {
  tier: string;
  status: string;
  api_calls_used: number;
  api_calls_limit: number;
  current_period_end: number | null;
  cancel_at: number | null;
  stripe_subscription_id: string | null;
}

interface InvoicesResponse {
  status: string;
  invoices: Array<{
    id: string;
    stripe_invoice_id: string;
    number: string;
    amount_paid: number;
    status: string;
    created: number;
    hosted_url: string;
  }>;
}

interface PortalResponse {
  status: string;
  url: string;
}

export const usePayment = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getAuthToken = () => {
    return localStorage.getItem('auth_token') || '';
  };

  const makeRequest = useCallback(
    async <T,>(
      endpoint: string,
      method: string = 'GET',
      body?: unknown
    ): Promise<T> => {
      setError(null);
      setLoading(true);

      try {
        const headers: HeadersInit = {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`,
        };

        const options: RequestInit = {
          method,
          headers,
        };

        if (body) {
          options.body = JSON.stringify(body);
        }

        const response = await fetch(endpoint, options);

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(
            errorData.detail || `Request failed with status ${response.status}`
          );
        }

        return await response.json();
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : 'An error occurred';
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  /**
   * Create a checkout session for tier upgrade
   */
  const createCheckoutSession = useCallback(
    async (priceId: string, trialDays: number = 14): Promise<string> => {
      const data = await makeRequest<CheckoutSessionResponse>(
        '/api/billing/create-checkout-session',
        'POST',
        {
          price_id: priceId,
          trial_days: trialDays,
        }
      );
      return data.sessionId;
    },
    [makeRequest]
  );

  /**
   * Get current subscription status
   */
  const getSubscription = useCallback(async (): Promise<SubscriptionResponse> => {
    return makeRequest<SubscriptionResponse>('/api/billing/subscription');
  }, [makeRequest]);

  /**
   * Get invoice history
   */
  const getInvoices = useCallback(async () => {
    return makeRequest<InvoicesResponse>('/api/billing/invoices');
  }, [makeRequest]);

  /**
   * Open Stripe billing portal
   */
  const openBillingPortal = useCallback(async (): Promise<string> => {
    const data = await makeRequest<PortalResponse>('/api/billing/portal');
    return data.url;
  }, [makeRequest]);

  /**
   * Cancel subscription at end of billing period
   */
  const cancelSubscription = useCallback(async () => {
    return makeRequest('/api/billing/cancel-subscription', 'POST');
  }, [makeRequest]);

  /**
   * Download invoice PDF
   */
  const downloadInvoice = useCallback(
    async (invoiceId: string, hostedUrl: string) => {
      // Open in new tab - Stripe handles the download
      window.open(hostedUrl, '_blank');
    },
    []
  );

  return {
    loading,
    error,
    clearError: () => setError(null),
    createCheckoutSession,
    getSubscription,
    getInvoices,
    openBillingPortal,
    cancelSubscription,
    downloadInvoice,
  };
};

export default usePayment;
