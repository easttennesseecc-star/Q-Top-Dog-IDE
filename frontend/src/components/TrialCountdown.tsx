/**
 * TrialCountdown Component
 * Shows remaining trial days for FREE tier users
 * Prompts to upgrade when trial is ending
 */

import React, { useState, useEffect } from 'react';

interface TrialData {
  is_trial: boolean;
  trial_expiry: string;
  days_remaining: number;
  tier_name: string;
}

interface TrialCountdownProps {
  userId?: string;
  onUpgradeClick?: () => void;
  onDismiss?: () => void;
}

const TrialCountdown: React.FC<TrialCountdownProps> = ({ userId, onUpgradeClick, onDismiss }) => {
  const [trial, setTrial] = useState<TrialData | null>(null);
  const [loading, setLoading] = useState(true);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    const fetchTrialInfo = async () => {
      try {
        setLoading(true);
        const headers: HeadersInit = {
          'Content-Type': 'application/json',
        };

        if (userId) {
          headers['X-User-ID'] = userId;
        }

        const response = await fetch('/api/tier/trial', { headers });

        if (!response.ok) {
          return;
        }

        const data = await response.json();
        setTrial(data);
      } catch (err) {
        // Silent error - trial info is optional
      } finally {
        setLoading(false);
      }
    };

    fetchTrialInfo();
    // Check every hour
    const interval = setInterval(fetchTrialInfo, 3600000);
    return () => clearInterval(interval);
  }, [userId]);

  const handleDismiss = () => {
    setDismissed(true);
    onDismiss?.();
  };

  if (loading || dismissed || !trial || !trial.is_trial) {
    return null;
  }

  const isWarning = trial.days_remaining <= 3;
  const isExpiring = trial.days_remaining <= 0;

  return (
    <div
      className={`trial-countdown ${isExpiring ? 'trial-countdown--expired' : isWarning ? 'trial-countdown--warning' : 'trial-countdown--active'}`}
    >
      <div className="trial-countdown__content">
        <div className="trial-countdown__icon">
          {isExpiring ? '⏰' : isWarning ? '⚠️' : '🎉'}
        </div>

        <div className="trial-countdown__text">
          {isExpiring ? (
            <>
              <h3 className="trial-countdown__title">Trial Expired</h3>
              <p className="trial-countdown__message">
                Your {trial.tier_name} trial has ended. Upgrade now to continue.
              </p>
            </>
          ) : (
            <>
              <h3 className="trial-countdown__title">
                {trial.days_remaining} Day{trial.days_remaining === 1 ? '' : 's'} Left
              </h3>
              <p className="trial-countdown__message">
                Your FREE trial expires {new Date(trial.trial_expiry).toLocaleDateString()}
              </p>
            </>
          )}
        </div>

        <div className="trial-countdown__actions">
          {onUpgradeClick && (
            <button className="trial-countdown__upgrade-btn" onClick={onUpgradeClick}>
              Upgrade Now
            </button>
          )}
          <button className="trial-countdown__dismiss-btn" onClick={handleDismiss}>
            Dismiss
          </button>
        </div>
      </div>

      {isWarning && !isExpiring && (
        <div className="trial-countdown__progress">
          <div
            className="trial-countdown__progress-fill"
            style={{
              width: `${(trial.days_remaining / 14) * 100}%`,
            }}
          />
        </div>
      )}
    </div>
  );
};

export default TrialCountdown;
