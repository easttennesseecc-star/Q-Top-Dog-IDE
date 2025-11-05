/**
 * TierInfo Component
 * Displays current user's subscription tier with detailed information
 * Shows tier name, price, features, and renewal info
 */

import React, { useState, useEffect } from 'react';

interface TierData {
  tier_id: string;
  name: string;
  price: number;
  daily_call_limit: number;
  team_members: number;
  support_tier: string;
  features: string[];
  is_trial: boolean;
  trial_expiry?: string;
  renewal_date?: string;
}

interface TierInfoProps {
  userId?: string;
  onUpgradeClick?: () => void;
  compact?: boolean;
}

const TierInfo: React.FC<TierInfoProps> = ({ userId, onUpgradeClick, compact = false }) => {
  const [tierData, setTierData] = useState<TierData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTierInfo = async () => {
      try {
        setLoading(true);
        const headers: HeadersInit = {
          'Content-Type': 'application/json',
        };

        if (userId) {
          headers['X-User-ID'] = userId;
        }

        const response = await fetch('/api/tier/info', { headers });

        if (!response.ok) {
          throw new Error(`Failed to fetch tier info: ${response.statusText}`);
        }

        const data = await response.json();
        setTierData(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load tier information');
        setTierData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchTierInfo();
  }, [userId]);

  if (loading) {
    return (
      <div className="tier-info tier-info--loading">
        <div className="tier-info__spinner" />
        <p>Loading tier information...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="tier-info tier-info--error">
        <p className="tier-info__error-text">{error}</p>
      </div>
    );
  }

  if (!tierData) {
    return (
      <div className="tier-info tier-info--empty">
        <p>No tier information available</p>
      </div>
    );
  }

  const tierBadgeColor = {
    free: '#6B7280',
    pro: '#3B82F6',
    pro_plus: '#8B5CF6',
    pro_team: '#EC4899',
    teams_small: '#F59E0B',
    teams_medium: '#EF4444',
    teams_large: '#DC2626',
    enterprise_standard: '#1F2937',
    enterprise_premium: '#111827',
    enterprise_ultimate: '#000000',
  }[tierData.tier_id] || '#6B7280';

  const compactView = (
    <div className="tier-info tier-info--compact" style={{ borderLeftColor: tierBadgeColor }}>
      <div className="tier-info__header-compact">
        <h3 className="tier-info__tier-name">{tierData.name}</h3>
        {tierData.price > 0 && <span className="tier-info__price">${tierData.price}/mo</span>}
      </div>
      {tierData.is_trial && (
        <p className="tier-info__trial-badge">📅 Trial Active</p>
      )}
    </div>
  );

  const fullView = (
    <div className="tier-info" style={{ borderLeftColor: tierBadgeColor }}>
      <div className="tier-info__header">
        <div>
          <h2 className="tier-info__tier-name">{tierData.name}</h2>
          <p className="tier-info__tier-id">Tier: {tierData.tier_id.toUpperCase()}</p>
        </div>
        {tierData.price > 0 && (
          <div className="tier-info__price-section">
            <span className="tier-info__price">${tierData.price}</span>
            <span className="tier-info__period">/month</span>
          </div>
        )}
      </div>

      {tierData.is_trial && tierData.trial_expiry && (
        <div className="tier-info__trial-info">
          <span className="tier-info__trial-badge">📅 Trial Active</span>
          <p className="tier-info__trial-expires">
            Expires: {new Date(tierData.trial_expiry).toLocaleDateString()}
          </p>
        </div>
      )}

      <div className="tier-info__details">
        <div className="tier-info__detail-item">
          <span className="tier-info__detail-label">Daily Limit:</span>
          <span className="tier-info__detail-value">{tierData.daily_call_limit} calls</span>
        </div>
        {tierData.team_members > 0 && (
          <div className="tier-info__detail-item">
            <span className="tier-info__detail-label">Team Members:</span>
            <span className="tier-info__detail-value">{tierData.team_members}</span>
          </div>
        )}
        <div className="tier-info__detail-item">
          <span className="tier-info__detail-label">Support:</span>
          <span className="tier-info__detail-value">{tierData.support_tier}</span>
        </div>
      </div>

      {tierData.renewal_date && (
        <div className="tier-info__renewal">
          <p className="tier-info__renewal-text">
            Next billing: {new Date(tierData.renewal_date).toLocaleDateString()}
          </p>
        </div>
      )}

      {tierData.tier_id === 'free' && onUpgradeClick && (
        <button className="tier-info__upgrade-btn" onClick={onUpgradeClick}>
          🚀 Upgrade to PRO
        </button>
      )}
    </div>
  );

  return compact ? compactView : fullView;
};

export default TierInfo;
