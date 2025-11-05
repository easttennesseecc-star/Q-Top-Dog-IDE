/**
 * PricingComparison Component
 * Displays all tiers in a comparison table
 * Shows features, pricing, and upgrade options
 */

import React, { useState, useEffect } from 'react';

interface Tier {
  tier_id: string;
  name: string;
  price: number;
  daily_call_limit: number;
  team_members: number;
  support_tier: string;
  support_response_hours: number;
  code_execution: boolean;
  webhooks: boolean;
  api_keys: boolean;
  debug_logs: boolean;
  role_based_access: boolean;
  audit_logs: boolean;
  hipaa_ready: boolean;
  sso_saml: boolean;
  on_premise_deploy: boolean;
}

interface PricingComparisonProps {
  userId?: string;
  onSelectTier?: (tier: string) => void;
  compact?: boolean;
}

const PricingComparison: React.FC<PricingComparisonProps> = ({ userId, onSelectTier, compact = false }) => {
  const [tiers, setTiers] = useState<Tier[]>([]);
  const [currentTier, setCurrentTier] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTiers = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/tiers');

        if (!response.ok) {
          throw new Error('Failed to fetch tiers');
        }

        const data = await response.json();
        setTiers(data);

        // Fetch current tier
        const tierResponse = await fetch('/api/tier/info');
        if (tierResponse.ok) {
          const tierData = await tierResponse.json();
          setCurrentTier(tierData.tier_id);
        }

        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load pricing');
        setTiers([]);
      } finally {
        setLoading(false);
      }
    };

    fetchTiers();
  }, [userId]);

  if (loading) {
    return (
      <div className="pricing-comparison pricing-comparison--loading">
        <p>Loading pricing information...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="pricing-comparison pricing-comparison--error">
        <p>{error}</p>
      </div>
    );
  }

  const featureList = [
    { key: 'daily_call_limit', label: 'Daily API Calls' },
    { key: 'team_members', label: 'Team Members' },
    { key: 'code_execution', label: 'Code Execution' },
    { key: 'webhooks', label: 'Webhooks' },
    { key: 'api_keys', label: 'API Keys' },
    { key: 'debug_logs', label: 'Debug Logs' },
    { key: 'role_based_access', label: 'Role-Based Access' },
    { key: 'audit_logs', label: 'Audit Logs' },
    { key: 'hipaa_ready', label: 'HIPAA Compliance' },
    { key: 'sso_saml', label: 'SSO/SAML' },
    { key: 'on_premise_deploy', label: 'On-Premise Deploy' },
  ];

  const displayTiers = compact ? tiers.slice(0, 4) : tiers;

  return (
    <div className="pricing-comparison">
      <div className="pricing-comparison__header">
        <h2 className="pricing-comparison__title">Choose Your Plan</h2>
        <p className="pricing-comparison__subtitle">Select the tier that works best for you</p>
      </div>

      <div className="pricing-comparison__container">
        <div className="pricing-comparison__grid">
          {displayTiers.map((tier) => (
            <div
              key={tier.tier_id}
              className={`pricing-comparison__card ${
                currentTier === tier.tier_id ? 'pricing-comparison__card--current' : ''
              }`}
            >
              <div className="pricing-comparison__card-header">
                <h3 className="pricing-comparison__tier-name">{tier.name}</h3>

                {currentTier === tier.tier_id && (
                  <span className="pricing-comparison__current-badge">Current Plan</span>
                )}
              </div>

              <div className="pricing-comparison__pricing">
                {tier.price === 0 ? (
                  <p className="pricing-comparison__price">Free</p>
                ) : (
                  <>
                    <span className="pricing-comparison__price">${tier.price}</span>
                    <span className="pricing-comparison__period">/month</span>
                  </>
                )}
              </div>

              <div className="pricing-comparison__support">
                <p>{tier.support_tier} Support</p>
                <p className="pricing-comparison__response">
                  Response time: {tier.support_response_hours}h
                </p>
              </div>

              <button
                className={`pricing-comparison__button ${
                  currentTier === tier.tier_id ? 'pricing-comparison__button--current' : ''
                }`}
                onClick={() => onSelectTier?.(tier.tier_id)}
                disabled={currentTier === tier.tier_id}
              >
                {currentTier === tier.tier_id ? '✓ Current Plan' : 'Select Plan'}
              </button>

              <div className="pricing-comparison__features">
                {featureList.map((feature) => {
                  const value = (tier as any)[feature.key];
                  const isBoolean = typeof value === 'boolean';
                  const isIncluded = isBoolean ? value : value > 0;

                  return (
                    <div key={feature.key} className="pricing-comparison__feature">
                      <span className="pricing-comparison__feature-label">{feature.label}</span>
                      <span className="pricing-comparison__feature-value">
                        {isBoolean ? (
                          isIncluded ? (
                            <span className="pricing-comparison__check">✓</span>
                          ) : (
                            <span className="pricing-comparison__x">✗</span>
                          )
                        ) : (
                          <span>{value}</span>
                        )}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {compact && (
        <div className="pricing-comparison__footer">
          <a href="/pricing" className="pricing-comparison__see-all">
            View all plans →
          </a>
        </div>
      )}
    </div>
  );
};

export default PricingComparison;
