/**
 * UpgradeModal Component
 * Modal dialog for upgrade confirmation and selection
 * Shows tier benefits and upgrade process
 */

import React, { useState } from 'react';

interface UpgradeModalProps {
  isOpen: boolean;
  onClose: () => void;
  targetTier?: string;
  currentTier?: string;
  userId?: string;
  onUpgradeSuccess?: () => void;
}

const UpgradeModal: React.FC<UpgradeModalProps> = ({
  isOpen,
  onClose,
  targetTier = 'pro',
  currentTier,
  userId,
  onUpgradeSuccess,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) {
    return null;
  }

  const handleUpgrade = async () => {
    try {
      setLoading(true);
      setError(null);

      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };

      if (userId) {
        headers['X-User-ID'] = userId;
      }

      const response = await fetch(`/api/tier/upgrade/${targetTier}`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ tier_id: targetTier }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Upgrade failed');
      }

      onUpgradeSuccess?.();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upgrade failed');
    } finally {
      setLoading(false);
    }
  };

  const tierInfo: Record<string, { emoji: string; color: string; benefits: string[] }> = {
    pro: {
      emoji: '⭐',
      color: '#3B82F6',
      benefits: [
        'Unlimited API calls',
        'Priority support',
        'Code execution feature',
        'Webhook support',
        'API key management',
        'Debug logs access',
      ],
    },
    pro_plus: {
      emoji: '✨',
      color: '#8B5CF6',
      benefits: [
        'Everything in PRO',
        'Custom LLM models',
        'Advanced analytics',
        'Batch processing',
        'Export capabilities',
      ],
    },
    pro_team: {
      emoji: '👥',
      color: '#EC4899',
      benefits: [
        'Everything in PRO+',
        'Team collaboration',
        'Role-based access',
        'Shared workspaces',
        'Audit logs',
        'Up to 10 team members',
      ],
    },
  };

  const info = tierInfo[targetTier] || tierInfo.pro;

  return (
    <div className="upgrade-modal__overlay" onClick={onClose}>
      <div className="upgrade-modal" onClick={(e) => e.stopPropagation()}>
        <button className="upgrade-modal__close" onClick={onClose}>
          ✕
        </button>

        <div className="upgrade-modal__header" style={{ borderTopColor: info.color }}>
          <span className="upgrade-modal__icon">{info.emoji}</span>
          <h2 className="upgrade-modal__title">Upgrade Your Plan</h2>
          <p className="upgrade-modal__subtitle">Get more features and usage</p>
        </div>

        <div className="upgrade-modal__body">
          {error && (
            <div className="upgrade-modal__error">
              <p>{error}</p>
            </div>
          )}

          <div className="upgrade-modal__benefits">
            <h3 className="upgrade-modal__benefits-title">What You'll Get:</h3>
            <ul className="upgrade-modal__benefits-list">
              {info.benefits.map((benefit, index) => (
                <li key={index} className="upgrade-modal__benefit">
                  <span className="upgrade-modal__benefit-check">✓</span>
                  <span>{benefit}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="upgrade-modal__pricing" style={{ backgroundColor: `${info.color}20` }}>
            <p className="upgrade-modal__pricing-label">
              {targetTier === 'pro' ? 'Starting at' : 'From'}
            </p>
            <p className="upgrade-modal__pricing-amount">
              {targetTier === 'pro' && '$20'}
              {targetTier === 'pro_plus' && '$45'}
              {targetTier === 'pro_team' && '$75'}
              <span className="upgrade-modal__pricing-period">/month</span>
            </p>
          </div>

          <div className="upgrade-modal__actions">
            <button
              className="upgrade-modal__upgrade-btn"
              onClick={handleUpgrade}
              disabled={loading}
              style={{ backgroundColor: info.color }}
            >
              {loading ? (
                <>
                  <span className="upgrade-modal__spinner" />
                  Processing...
                </>
              ) : (
                `Upgrade to ${targetTier.toUpperCase()}`
              )}
            </button>

            <button className="upgrade-modal__cancel-btn" onClick={onClose} disabled={loading}>
              Cancel
            </button>
          </div>

          <p className="upgrade-modal__footer">
            Your upgrade will be processed immediately. You'll have access to all premium
            features right away.
          </p>
        </div>
      </div>
    </div>
  );
};

export default UpgradeModal;
