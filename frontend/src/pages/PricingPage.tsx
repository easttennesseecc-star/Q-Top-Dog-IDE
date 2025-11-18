/**
 * Dedicated Pricing Page Component
 * Full-page pricing display with all 10 tiers and detailed feature comparison
 */

import React, { useState, useEffect } from 'react';

interface Tier {
  id: string;
  name: string;
  emoji: string;
  price: number;
  description: string;
  features: string[];
  team_members: number;
  daily_api_calls: number;
  support_level: string;
  popular: boolean;
  vertical?: string; // DEVELOPMENT | MEDICAL | SCIENTIFIC
}

interface PricingPageProps {
  userId?: string;
  currentTier?: string;
}

const PricingPage: React.FC<PricingPageProps> = ({ userId = 'guest', currentTier }) => {
  const [tiers, setTiers] = useState<Tier[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTier, setSelectedTier] = useState<string | null>(null);
  const [showComparisonTable, setShowComparisonTable] = useState(false);

  useEffect(() => {
    const fetchTiers = async () => {
      try {
        setLoading(true);
        const headers: HeadersInit = {
          'Content-Type': 'application/json',
        };
        if (userId) {
          headers['X-User-ID'] = userId;
        }

  const response = await fetch('/api/tiers', { headers });
  if (!response.ok) throw new Error('Failed to fetch tiers');
  const data = await response.json();
  // Backend may return an array or { tiers: [...] }
  const normalized = Array.isArray(data) ? data : (data.tiers || []);
  setTiers(normalized);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error loading pricing');
      } finally {
        setLoading(false);
      }
    };

    fetchTiers();
  }, [userId]);

  if (loading) {
    return (
      <div className="pricing-page pricing-page--loading">
        <div className="pricing-page__spinner"></div>
        <p className="pricing-page__loading-text">Loading pricing plans...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="pricing-page pricing-page--error">
        <div className="pricing-page__error-box">
          <p className="pricing-page__error-text">{error}</p>
        </div>
      </div>
    );
  }

  // Aura vertical organization (Development / Medical / Scientific)
  const devTiers = tiers.filter(t => t.vertical === 'DEVELOPMENT');
  const medTiers = tiers.filter(t => t.vertical === 'MEDICAL');
  const sciTiers = tiers.filter(t => t.vertical === 'SCIENTIFIC');

  // All unique features for comparison table
  const allFeatures = Array.from(
    new Set(tiers.flatMap(t => t.features))
  ).sort();

  return (
    <div className="pricing-page">
      {/* Header */}
      <div className="pricing-page__header">
        <h1 className="pricing-page__title">Simple, Transparent Pricing</h1>
        <p className="pricing-page__subtitle">
          Choose the perfect plan for your team. Always one tier up from free.
        </p>
      </div>

      {/* Pricing Toggle */}
      <div className="pricing-page__toggle">
        <button
          onClick={() => setShowComparisonTable(false)}
          className={`pricing-page__toggle-btn ${!showComparisonTable ? 'active' : ''}`}
        >
          Grid View
        </button>
        <button
          onClick={() => setShowComparisonTable(true)}
          className={`pricing-page__toggle-btn ${showComparisonTable ? 'active' : ''}`}
        >
          Comparison Table
        </button>
      </div>

      {!showComparisonTable ? (
        <>
          {/* Development Vertical */}
          {devTiers.length > 0 && (
            <section className="pricing-page__section">
              <h2 className="pricing-page__section-title">Development Suites</h2>
              <p className="pricing-page__section-subtitle">Local-first building, multi-engine game + media synthesis.</p>
              <div className="pricing-page__grid pricing-page__grid--3col">
                {devTiers.map(tier => (
                  <TierCard
                    key={tier.id}
                    tier={tier}
                    isCurrent={tier.id === currentTier}
                    isSelected={tier.id === selectedTier}
                    onSelect={setSelectedTier}
                  />
                ))}
              </div>
            </section>
          )}

          {/* Medical Vertical */}
          {medTiers.length > 0 && (
            <section className="pricing-page__section">
              <h2 className="pricing-page__section-title">Medical Suites</h2>
              <p className="pricing-page__section-subtitle">PHI scrubbing, provenance, compliance readiness.</p>
              <div className="pricing-page__grid pricing-page__grid--3col">
                {medTiers.map(tier => (
                  <TierCard
                    key={tier.id}
                    tier={tier}
                    isCurrent={tier.id === currentTier}
                    isSelected={tier.id === selectedTier}
                    onSelect={setSelectedTier}
                  />
                ))}
              </div>
            </section>
          )}

          {/* Scientific Vertical */}
          {sciTiers.length > 0 && (
            <section className="pricing-page__section">
              <h2 className="pricing-page__section-title">Scientific Suites</h2>
              <p className="pricing-page__section-subtitle">Citation guardrails, provenance, hallucination suppression.</p>
              <div className="pricing-page__grid pricing-page__grid--3col">
                {sciTiers.map(tier => (
                  <TierCard
                    key={tier.id}
                    tier={tier}
                    isCurrent={tier.id === currentTier}
                    isSelected={tier.id === selectedTier}
                    onSelect={setSelectedTier}
                  />
                ))}
              </div>
            </section>
          )}
        </>
      ) : (
        /* Comparison Table View */
        <div className="pricing-page__table-container">
          <table className="pricing-page__comparison-table">
            <thead>
              <tr>
                <th className="pricing-page__table-feature">Feature</th>
                {tiers.map(tier => (
                  <th
                    key={tier.id}
                    className={`pricing-page__table-header ${tier.popular ? 'popular' : ''}`}
                  >
                    <div className="pricing-page__table-header-content">
                      <span className="pricing-page__table-emoji">{tier.emoji}</span>
                      <span className="pricing-page__table-name">{tier.name}</span>
                      <div className="pricing-page__table-price">${tier.price}/mo</div>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {/* Price Row */}
              <tr className="pricing-page__table-row pricing-page__table-row--price">
                <td className="pricing-page__table-label">Starting Price</td>
                {tiers.map(tier => (
                  <td key={tier.id} className="pricing-page__table-cell">
                    <span className="pricing-page__table-value">${tier.price}</span>
                    <span className="pricing-page__table-unit">/month</span>
                  </td>
                ))}
              </tr>

              {/* API Calls Row */}
              <tr className="pricing-page__table-row">
                <td className="pricing-page__table-label">API Calls/Day</td>
                {tiers.map(tier => (
                  <td key={tier.id} className="pricing-page__table-cell">
                    {tier.daily_api_calls === -1 ? (
                      <span className="pricing-page__table-unlimited">Unlimited</span>
                    ) : (
                      <span className="pricing-page__table-value">{tier.daily_api_calls}</span>
                    )}
                  </td>
                ))}
              </tr>

              {/* Team Members Row */}
              <tr className="pricing-page__table-row">
                <td className="pricing-page__table-label">Team Members</td>
                {tiers.map(tier => (
                  <td key={tier.id} className="pricing-page__table-cell">
                    <span className="pricing-page__table-value">{tier.team_members}</span>
                  </td>
                ))}
              </tr>

              {/* Support Row */}
              <tr className="pricing-page__table-row">
                <td className="pricing-page__table-label">Support Level</td>
                {tiers.map(tier => (
                  <td key={tier.id} className="pricing-page__table-cell">
                    <span className="pricing-page__table-support">
                      {tier.support_level}
                    </span>
                  </td>
                ))}
              </tr>

              {/* Features */}
              {allFeatures.map(feature => (
                <tr key={feature} className="pricing-page__table-row">
                  <td className="pricing-page__table-label">{feature}</td>
                  {tiers.map(tier => (
                    <td key={tier.id} className="pricing-page__table-cell pricing-page__table-cell--feature">
                      {tier.features.includes(feature) ? (
                        <span className="pricing-page__check">✓</span>
                      ) : (
                        <span className="pricing-page__cross">✗</span>
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* CTA Section */}
      <div className="pricing-page__cta">
        <h2 className="pricing-page__cta-title">Start Local. Scale Up When Ready.</h2>
        <p className="pricing-page__cta-subtitle">
          Begin with Dev-Free (local + demo models). Move into specialized Aura suites as your compliance or scientific needs grow.
        </p>
        <button className="pricing-page__cta-btn">Launch Dev-Free</button>
      </div>

      {/* FAQ Section */}
      <section className="pricing-page__faq">
        <h2 className="pricing-page__faq-title">Frequently Asked Questions</h2>
        <div className="pricing-page__faq-items">
          <FAQItem
            question="Can I change my plan anytime?"
            answer="Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately."
          />
          <FAQItem
            question="Do you offer discounts for annual billing?"
            answer="Yes! Save 20% when you pay annually. Contact our sales team for custom enterprise pricing."
          />
          <FAQItem
            question="What's included in the free tier?"
            answer="The free tier includes up to 20 API calls per day, 1 team member, and essential features."
          />
          <FAQItem
            question="Is there a setup fee?"
            answer="No setup fees! You only pay for the plan you choose. Cancel anytime without penalties."
          />
        </div>
      </section>
    </div>
  );
};

/**
 * Tier Card Component
 */
interface TierCardProps {
  tier: Tier;
  isCurrent: boolean;
  isSelected: boolean;
  onSelect: (tierId: string) => void;
}

const TierCard: React.FC<TierCardProps> = ({ tier, isCurrent, isSelected, onSelect }) => {
  return (
    <div
      className={`pricing-tier-card ${tier.popular ? 'popular' : ''} ${
        isCurrent ? 'current' : ''
      } ${isSelected ? 'selected' : ''}`}
    >
      {tier.popular && <div className="pricing-tier-card__badge">Most Popular</div>}
      {isCurrent && <div className="pricing-tier-card__current">Current Plan</div>}

      <div className="pricing-tier-card__header">
        <span className="pricing-tier-card__emoji">{tier.emoji}</span>
        <h3 className="pricing-tier-card__name">{tier.name}</h3>
        <p className="pricing-tier-card__description">{tier.description}</p>
      </div>

      <div className="pricing-tier-card__pricing">
        <div className="pricing-tier-card__price">${tier.price}</div>
        <div className="pricing-tier-card__period">/month</div>
      </div>

      <div className="pricing-tier-card__specs">
        <div className="pricing-tier-card__spec">
          <span className="pricing-tier-card__spec-label">API Calls/Day:</span>
          <span className="pricing-tier-card__spec-value">
            {tier.daily_api_calls === -1 ? 'Unlimited' : tier.daily_api_calls}
          </span>
        </div>
        <div className="pricing-tier-card__spec">
          <span className="pricing-tier-card__spec-label">Team Members:</span>
          <span className="pricing-tier-card__spec-value">{tier.team_members}</span>
        </div>
        <div className="pricing-tier-card__spec">
          <span className="pricing-tier-card__spec-label">Support:</span>
          <span className="pricing-tier-card__spec-value">{tier.support_level}</span>
        </div>
      </div>

      <button
        onClick={() => onSelect(tier.id)}
        className={`pricing-tier-card__btn ${isCurrent ? 'current' : ''}`}
        disabled={isCurrent}
      >
        {isCurrent ? 'Current Plan' : 'Choose Plan'}
      </button>

      <div className="pricing-tier-card__features">
        <h4 className="pricing-tier-card__features-title">Includes:</h4>
        <ul className="pricing-tier-card__features-list">
          {tier.features.slice(0, 5).map(feature => (
            <li key={feature} className="pricing-tier-card__feature">
              <span className="pricing-tier-card__feature-check">✓</span>
              <span>{feature}</span>
            </li>
          ))}
          {tier.features.length > 5 && (
            <li className="pricing-tier-card__feature pricing-tier-card__feature--more">
              +{tier.features.length - 5} more features
            </li>
          )}
        </ul>
      </div>
    </div>
  );
};

/**
 * FAQ Item Component
 */
interface FAQItemProps {
  question: string;
  answer: string;
}

const FAQItem: React.FC<FAQItemProps> = ({ question, answer }) => {
  const [open, setOpen] = useState(false);

  return (
    <div className={`pricing-faq-item ${open ? 'open' : ''}`}>
      <button
        className="pricing-faq-item__question"
        onClick={() => setOpen(!open)}
      >
        <span>{question}</span>
        <span className="pricing-faq-item__toggle">▼</span>
      </button>
      {open && (
        <div className="pricing-faq-item__answer">
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
};

export default PricingPage;
