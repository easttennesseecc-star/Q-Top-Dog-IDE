/**
 * UsageBar Component
 * Displays API call usage with visual progress bar
 * Shows current usage against daily limit with percentage
 */

import React, { useState, useEffect } from 'react';

interface UsageData {
  used: number;
  limit: number;
  remaining: number;
  reset_time: string;
}

interface UsageBarProps {
  userId?: string;
  showPercentage?: boolean;
  showLabel?: boolean;
}

const UsageBar: React.FC<UsageBarProps> = ({ userId, showPercentage = true, showLabel = true }) => {
  const [usage, setUsage] = useState<UsageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUsage = async () => {
      try {
        setLoading(true);
        const headers: HeadersInit = {
          'Content-Type': 'application/json',
        };

        if (userId) {
          headers['X-User-ID'] = userId;
        }

        const response = await fetch('/api/tier/usage', { headers });

        if (!response.ok) {
          throw new Error('Failed to fetch usage data');
        }

        const data = await response.json();
        setUsage(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load usage');
        setUsage(null);
      } finally {
        setLoading(false);
      }
    };

    fetchUsage();
    // Refresh every 10 seconds
    const interval = setInterval(fetchUsage, 10000);
    return () => clearInterval(interval);
  }, [userId]);

  if (loading) {
    return (
      <div className="usage-bar usage-bar--loading">
        <div className="usage-bar__skeleton" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="usage-bar usage-bar--error">
        <p className="usage-bar__error">{error}</p>
      </div>
    );
  }

  if (!usage) {
    return null;
  }

  const percentage = (usage.used / usage.limit) * 100;
  const isWarning = percentage >= 75;
  const isExceeded = percentage >= 100;

  let barColor = '#10B981'; // green
  if (isExceeded) {
    barColor = '#EF4444'; // red
  } else if (isWarning) {
    barColor = '#F59E0B'; // amber
  }

  const resetDate = new Date(usage.reset_time);
  const now = new Date();
  const hoursUntilReset = Math.ceil((resetDate.getTime() - now.getTime()) / (1000 * 60 * 60));

  return (
    <div className={`usage-bar ${isExceeded ? 'usage-bar--exceeded' : isWarning ? 'usage-bar--warning' : ''}`}>
      {showLabel && (
        <div className="usage-bar__header">
          <span className="usage-bar__label">Daily API Usage</span>
          <span className="usage-bar__count">
            {usage.used} / {usage.limit}
          </span>
        </div>
      )}

      <div className="usage-bar__container">
        <div
          className="usage-bar__fill"
          style={{
            width: `${Math.min(percentage, 100)}%`,
            backgroundColor: barColor,
          }}
        />
      </div>

      <div className="usage-bar__footer">
        {showPercentage && <span className="usage-bar__percentage">{Math.round(percentage)}%</span>}
        <span className="usage-bar__remaining">
          {isExceeded ? '⚠️ Limit exceeded' : `${usage.remaining} remaining`}
        </span>
        <span className="usage-bar__reset">Resets in {hoursUntilReset}h</span>
      </div>

      {isExceeded && (
        <div className="usage-bar__alert">
          <p>You've exceeded your daily limit. Upgrade to PRO for more calls.</p>
        </div>
      )}
    </div>
  );
};

export default UsageBar;
