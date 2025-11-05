/**
 * UpgradeButton Component
 * Call-to-action button for upgrading tier
 * Shows current tier and upgrade target
 */

import React, { useState, useEffect } from 'react';

interface UpgradeButtonProps {
  userId?: string;
  targetTier?: string;
  text?: string;
  size?: 'small' | 'medium' | 'large';
  onClick?: () => void;
  className?: string;
}

const UpgradeButton: React.FC<UpgradeButtonProps> = ({
  userId,
  targetTier = 'pro',
  text,
  size = 'medium',
  onClick,
  className = '',
}) => {
  const [currentTier, setCurrentTier] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTier = async () => {
      try {
        const headers: HeadersInit = {
          'Content-Type': 'application/json',
        };

        if (userId) {
          headers['X-User-ID'] = userId;
        }

        const response = await fetch('/api/tier/info', { headers });

        if (response.ok) {
          const data = await response.json();
          setCurrentTier(data.tier_id);
        }
      } catch (err) {
        // Silent error
      } finally {
        setLoading(false);
      }
    };

    fetchTier();
  }, [userId]);

  const tierHierarchy: Record<string, number> = {
    free: 0,
    pro: 1,
    pro_plus: 2,
    pro_team: 3,
    teams_small: 4,
    teams_medium: 5,
    teams_large: 6,
    enterprise_standard: 7,
    enterprise_premium: 8,
    enterprise_ultimate: 9,
  };

  const currentLevel = currentTier ? tierHierarchy[currentTier] || 0 : 0;
  const targetLevel = tierHierarchy[targetTier] || 1;
  const shouldShow = currentLevel < targetLevel;

  if (!shouldShow) {
    return null;
  }

  const tierNames: Record<string, string> = {
    free: 'FREE',
    pro: 'PRO',
    pro_plus: 'PRO+',
    pro_team: 'TEAM',
    teams_small: 'TEAMS (S)',
    teams_medium: 'TEAMS (M)',
    teams_large: 'TEAMS (L)',
    enterprise_standard: 'ENTERPRISE',
    enterprise_premium: 'ENTERPRISE+',
    enterprise_ultimate: 'ENTERPRISE MAX',
  };

  const tierEmoji: Record<string, string> = {
    free: '🆓',
    pro: '⭐',
    pro_plus: '✨',
    pro_team: '👥',
    teams_small: '🏢',
    teams_medium: '🏢',
    teams_large: '🏢',
    enterprise_standard: '🏛️',
    enterprise_premium: '👑',
    enterprise_ultimate: '💎',
  };

  const buttonText =
    text ||
    `${loading ? 'Loading...' : `Upgrade to ${tierNames[targetTier]}`}`;

  const sizeClasses = {
    small: 'upgrade-button--small',
    medium: 'upgrade-button--medium',
    large: 'upgrade-button--large',
  };

  return (
    <button
      className={`upgrade-button ${sizeClasses[size]} ${className}`}
      onClick={onClick}
      disabled={loading}
      title={`Upgrade from ${currentTier?.toUpperCase() || 'FREE'} to ${tierNames[targetTier]}`}
    >
      <span className="upgrade-button__emoji">{tierEmoji[targetTier]}</span>
      <span className="upgrade-button__text">{buttonText}</span>
      <span className="upgrade-button__arrow">→</span>
    </button>
  );
};

export default UpgradeButton;
