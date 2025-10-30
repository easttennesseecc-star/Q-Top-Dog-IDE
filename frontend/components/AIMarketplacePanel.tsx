// Frontend: AI Marketplace Panel Component (React/TypeScript)
// Browse 50+ models, search, filter, select

import React, { useState, useEffect, useCallback } from 'react';
import './AIMarketplacePanel.css';

interface PricingInfo {
  input_cost_per_1k_tokens: number;
  output_cost_per_1k_tokens: number;
}

interface AIModel {
  id: string;
  name: string;
  provider: string;
  description: string;
  capabilities: string[];
  pricing: PricingInfo;
  rating: number;
  usage_count: number;
  context_window: number;
}

interface SearchFilters {
  query: string;
  provider?: string;
  minRating: number;
  maxPrice?: number;
  capability?: string;
}

interface RecommendationScore {
  model_id: string;
  model_name: string;
  score: number;
  reasoning: string[];
  price_rank: number;
  quality_rank: number;
}

const AIMarketplacePanel: React.FC<{ 
  onModelSelected: (modelId: string) => void;
  userToken: string;
}> = ({ onModelSelected, userToken }) => {
  // State Management
  const [models, setModels] = useState<AIModel[]>([]);
  const [filteredModels, setFilteredModels] = useState<AIModel[]>([]);
  const [selectedModel, setSelectedModel] = useState<AIModel | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<'browse' | 'search' | 'recommendations'>('browse');
  const [showDetails, setShowDetails] = useState(false);

  // Filters
  const [filters, setFilters] = useState<SearchFilters>({
    query: '',
    provider: '',
    minRating: 0,
    maxPrice: undefined,
    capability: ''
  });

  // Recommendations
  const [recommendationQuery, setRecommendationQuery] = useState('');
  const [recommendations, setRecommendations] = useState<RecommendationScore[]>([]);
  const [recommendationLoading, setRecommendationLoading] = useState(false);

  // Pagination
  const [currentPage, setCurrentPage] = useState(0);
  const itemsPerPage = 10;

  // Providers list
  const providers = ['openai', 'anthropic', 'google_gemini', 'huggingface', 'ollama', 'cohere'];
  const capabilities = [
    'code_generation',
    'code_completion',
    'code_explanation',
    'bug_detection',
    'refactoring',
    'documentation',
    'reasoning'
  ];

  // ==================== API CALLS ====================

  // Load all models on component mount
  useEffect(() => {
    loadAllModels();
  }, []);

  // Apply filters whenever they change
  useEffect(() => {
    applyFilters();
  }, [models, filters]);

  const loadAllModels = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/v1/marketplace/models', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${userToken}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) throw new Error('Failed to load models');
      
      const data = await response.json();
      setModels(data.data || []);
      setCurrentPage(0);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load models');
    } finally {
      setLoading(false);
    }
  }, [userToken]);

  const searchModels = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/v1/marketplace/models/search', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${userToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(filters)
      });

      if (!response.ok) throw new Error('Search failed');
      
      const data = await response.json();
      setFilteredModels(data.data || []);
      setCurrentPage(0);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setLoading(false);
    }
  }, [filters, userToken]);

  const getRecommendations = useCallback(async () => {
    if (!recommendationQuery.trim()) {
      setError('Please enter a task description');
      return;
    }

    setRecommendationLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/v1/marketplace/recommendations', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${userToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: recommendationQuery,
          budget: 'medium'
        })
      });

      if (!response.ok) throw new Error('Failed to get recommendations');
      
      const data = await response.json();
      setRecommendations(data.data || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get recommendations');
    } finally {
      setRecommendationLoading(false);
    }
  }, [recommendationQuery, userToken]);

  const selectModel = useCallback(async (modelId: string) => {
    try {
      const response = await fetch('/api/v1/marketplace/select-model', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${userToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ model_id: modelId })
      });

      if (!response.ok) throw new Error('Failed to select model');
      
      onModelSelected(modelId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to select model');
    }
  }, [userToken, onModelSelected]);

  // ==================== FILTER APPLICATION ====================

  const applyFilters = () => {
    let filtered = [...models];

    // Text search
    if (filters.query) {
      const q = filters.query.toLowerCase();
      filtered = filtered.filter(m =>
        m.name.toLowerCase().includes(q) ||
        m.description.toLowerCase().includes(q)
      );
    }

    // Provider filter
    if (filters.provider) {
      filtered = filtered.filter(m => m.provider === filters.provider);
    }

    // Rating filter
    if (filters.minRating > 0) {
      filtered = filtered.filter(m => m.rating >= filters.minRating);
    }

    // Capability filter
    if (filters.capability) {
      filtered = filtered.filter(m =>
        m.capabilities.includes(filters.capability)
      );
    }

    // Price filter
    if (filters.maxPrice !== undefined) {
      filtered = filtered.filter(m => {
        const avgPrice = (m.pricing.input_cost_per_1k_tokens + m.pricing.output_cost_per_1k_tokens) / 2;
        return avgPrice <= filters.maxPrice!;
      });
    }

    setFilteredModels(filtered);
    setCurrentPage(0);
  };

  // ==================== UI HELPERS ====================

  const getDisplayModels = () => {
    const models = view === 'browse' ? filteredModels : 
                   view === 'search' ? filteredModels :
                   recommendations.map(r => ({
                     id: r.model_id,
                     name: r.model_name,
                     score: r.score,
                     reasoning: r.reasoning
                   })) as any;

    const start = currentPage * itemsPerPage;
    return models.slice(start, start + itemsPerPage);
  };

  const getTotalPages = () => {
    const total = view === 'browse' ? filteredModels.length :
                  view === 'search' ? filteredModels.length :
                  recommendations.length;
    return Math.ceil(total / itemsPerPage);
  };

  const formatPrice = (price: number) => {
    if (price === 0) return 'Free';
    return `$${(price * 1000).toFixed(4)}/1K tokens`;
  };

  const getProviderColor = (provider: string) => {
    const colors: Record<string, string> = {
      'openai': '#00A67E',
      'anthropic': '#DC2626',
      'google_gemini': '#4285F4',
      'huggingface': '#FFB100',
      'ollama': '#7C3AED',
      'cohere': '#4F46E5'
    };
    return colors[provider] || '#6B7280';
  };

  // ==================== RENDER ====================

  const displayModels = getDisplayModels();
  const totalPages = getTotalPages();

  return (
    <div className="ai-marketplace-panel">
      <div className="marketplace-header">
        <h2>🤖 AI Agent Marketplace</h2>
        <p>50+ models • One-click access • Smart recommendations</p>
      </div>

      {error && (
        <div className="error-banner">
          <span>⚠️ {error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {/* View Selector */}
      <div className="view-selector">
        <button
          className={`view-btn ${view === 'browse' ? 'active' : ''}`}
          onClick={() => { setView('browse'); setCurrentPage(0); }}
        >
          📚 Browse
        </button>
        <button
          className={`view-btn ${view === 'search' ? 'active' : ''}`}
          onClick={() => { setView('search'); setCurrentPage(0); }}
        >
          🔍 Search
        </button>
        <button
          className={`view-btn ${view === 'recommendations' ? 'active' : ''}`}
          onClick={() => { setView('recommendations'); setCurrentPage(0); }}
        >
          ✨ Q Assistant
        </button>
      </div>

      {/* Browse View */}
      {view === 'browse' && (
        <div className="browse-section">
          <div className="filters">
            <input
              type="text"
              placeholder="Search models..."
              value={filters.query}
              onChange={(e) => setFilters({ ...filters, query: e.target.value })}
              className="search-input"
            />

            <select
              value={filters.provider || ''}
              onChange={(e) => setFilters({ ...filters, provider: e.target.value || undefined })}
              className="filter-select"
            >
              <option value="">All Providers</option>
              {providers.map(p => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>

            <select
              value={filters.capability || ''}
              onChange={(e) => setFilters({ ...filters, capability: e.target.value || undefined })}
              className="filter-select"
            >
              <option value="">All Capabilities</option>
              {capabilities.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>

            <div className="rating-filter">
              <label>Min Rating: {filters.minRating}⭐</label>
              <input
                type="range"
                min="0"
                max="5"
                step="0.5"
                value={filters.minRating}
                onChange={(e) => setFilters({ ...filters, minRating: parseFloat(e.target.value) })}
              />
            </div>
          </div>
        </div>
      )}

      {/* Recommendations View */}
      {view === 'recommendations' && (
        <div className="recommendations-section">
          <div className="recommendation-input">
            <input
              type="text"
              placeholder="E.g., 'I need to generate TypeScript code with complex reasoning'"
              value={recommendationQuery}
              onChange={(e) => setRecommendationQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && getRecommendations()}
              className="recommendation-input-field"
            />
            <button
              onClick={getRecommendations}
              disabled={recommendationLoading}
              className="recommendation-btn"
            >
              {recommendationLoading ? 'Loading...' : 'Get Recommendations'}
            </button>
          </div>
        </div>
      )}

      {/* Models Grid */}
      <div className="models-container">
        {loading ? (
          <div className="loading">Loading models...</div>
        ) : displayModels.length === 0 ? (
          <div className="empty-state">
            <p>No models found. Try adjusting your filters.</p>
          </div>
        ) : (
          <div className="models-grid">
            {displayModels.map((model) => (
              <div
                key={model.id}
                className={`model-card ${selectedModel?.id === model.id ? 'selected' : ''}`}
                onClick={() => setSelectedModel(model)}
              >
                <div
                  className="model-provider-badge"
                  style={{ backgroundColor: getProviderColor(model.provider) }}
                >
                  {model.provider}
                </div>

                <h3>{model.name}</h3>
                <p className="description">{model.description}</p>

                {/* Score if from recommendations */}
                {model.score && (
                  <div className="score-badge">
                    Score: {model.score.toFixed(0)}/100
                  </div>
                )}

                <div className="model-stats">
                  <span className="rating">⭐ {model.rating}/5.0</span>
                  <span className="usage">👥 {(model.usage_count / 1000).toFixed(0)}K users</span>
                </div>

                <div className="pricing-info">
                  <span>Input: {formatPrice(model.pricing.input_cost_per_1k_tokens)}</span>
                  <span>Output: {formatPrice(model.pricing.output_cost_per_1k_tokens)}</span>
                </div>

                <div className="capabilities">
                  {model.capabilities.slice(0, 3).map(cap => (
                    <span key={cap} className="capability-tag">{cap}</span>
                  ))}
                  {model.capabilities.length > 3 && (
                    <span className="capability-tag">+{model.capabilities.length - 3}</span>
                  )}
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    selectModel(model.id);
                  }}
                  className="select-btn"
                >
                  Select Model
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="pagination">
          <button
            onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
            disabled={currentPage === 0}
          >
            ← Previous
          </button>
          <span>{currentPage + 1} / {totalPages}</span>
          <button
            onClick={() => setCurrentPage(Math.min(totalPages - 1, currentPage + 1))}
            disabled={currentPage === totalPages - 1}
          >
            Next →
          </button>
        </div>
      )}

      {/* Model Details Panel */}
      {selectedModel && showDetails && (
        <div className="details-panel">
          <button onClick={() => setShowDetails(false)} className="close-btn">✕</button>
          <h3>{selectedModel.name}</h3>
          <p>{selectedModel.description}</p>
          <div>Context Window: {selectedModel.context_window} tokens</div>
          <div>Provider: {selectedModel.provider}</div>
        </div>
      )}
    </div>
  );
};

export default AIMarketplacePanel;
