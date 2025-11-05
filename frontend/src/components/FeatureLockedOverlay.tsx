/**
 * FeatureLockedOverlay Component
 * Shows when a feature is locked behind a tier upgrade
 * Displays upgrade information and call-to-action
 */

import React, { useState, useEffect } from 'react';

interface FeatureLockedOverlayProps {
  feature: string;
  requiredTier: string;
  currentTier?: string;
  onUpgradeClick?: () => void;
  children?: React.ReactNode;
}

const FeatureLockedOverlay: React.FC<FeatureLockedOverlayProps> = ({
  feature,
  requiredTier,
  currentTier,
  onUpgradeClick,
  children,
}) => {
  const [showOverlay, setShowOverlay] = useState(true);
  const [actualCurrentTier, setActualCurrentTier] = useState(currentTier || null);

  useEffect(() => {
    if (currentTier) {
      return;
    }

    const fetchTier = async () => {
      try {
        const response = await fetch('/api/tier/info');

        if (response.ok) {
          const data = await response.json();
          setActualCurrentTier(data.tier_id);
        }
      } catch (err) {
        // Silent error
      }
    };

    fetchTier();
  }, [currentTier]);

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

  const currentLevel = actualCurrentTier ? tierHierarchy[actualCurrentTier] || 0 : 0;
  const requiredLevel = tierHierarchy[requiredTier] || 1;

  // Only show overlay if current tier is below required
  if (currentLevel >= requiredLevel) {
    return <>{children}</>;
  }

  if (!showOverlay) {
    return <>{children}</>;
  }

  const tierNames: Record<string, string> = {
    free: 'FREE',
    pro: 'PRO',
    pro_plus: 'PRO+',
    pro_team: 'TEAMS',
    teams_small: 'TEAMS (Small)',
    teams_medium: 'TEAMS (Medium)',
    teams_large: 'TEAMS (Large)',
    enterprise_standard: 'Enterprise',
    enterprise_premium: 'Enterprise Plus',
    enterprise_ultimate: 'Enterprise Max',
  };

  const featureNames: Record<string, string> = {
    code_execution: 'Code Execution',
    webhooks: 'Webhooks',
    custom_llms: 'Custom LLMs',
    api_keys: 'API Keys',
    debug_logs: 'Debug Logs',
    team_members: 'Team Members',
    role_based_access: 'Role-Based Access',
    shared_workspaces: 'Shared Workspaces',
    audit_logs: 'Audit Logs',
    hipaa: 'HIPAA Compliance',
    sso_saml: 'SSO/SAML',
    data_residency: 'Data Residency',
  };

  const displayFeature = featureNames[feature] || feature;
  const displayTier = tierNames[requiredTier] || requiredTier;

  return (
    <div className="feature-locked-overlay__container">
      <div className="feature-locked-overlay__content" style={{ opacity: 0.6 }}>
        {children}
      </div>

      <div className="feature-locked-overlay feature-locked-overlay--active">
        <div className="feature-locked-overlay__card">
          <div className="feature-locked-overlay__icon">🔒</div>

          <h3 className="feature-locked-overlay__title">{displayFeature} Locked</h3>

          <p className="feature-locked-overlay__message">
            This feature requires <strong>{displayTier}</strong> tier or higher.
          </p>

          <div className="feature-locked-overlay__details">
            <p className="feature-locked-overlay__current">
              Your current plan: <strong>{(actualCurrentTier || 'FREE').toUpperCase()}</strong>
            </p>
            <p className="feature-locked-overlay__required">
              Required: <strong>{displayTier}</strong>
            </p>
          </div>

          <div className="feature-locked-overlay__actions">
            {onUpgradeClick && (
              <button className="feature-locked-overlay__upgrade-btn" onClick={onUpgradeClick}>
                🚀 Upgrade Now
              </button>
            )}
            <button
              className="feature-locked-overlay__dismiss-btn"
              onClick={() => setShowOverlay(false)}
            >
              Close
            </button>
          </div>

          <a href="/pricing" className="feature-locked-overlay__learn-more">
            View all features →
          </a>
        </div>
      </div>
    </div>
  );
};

export default FeatureLockedOverlay;
