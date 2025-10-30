// frontend/src/components/MediaSetup.tsx
/**
 * One-click Media Provider Setup
 * Configure API keys for Stable Diffusion and Runway
 */

import React, { useState, useEffect } from 'react';

interface ProviderConfig {
  name: string;
  env_var: string;
  docs_url: string;
  setup_time: string;
  description: string;
  free_tier: boolean;
  free_credits: string;
}

interface ProviderStatus {
  configured: boolean;
  tested: boolean;
  error?: string;
}

const PROVIDERS: Record<string, ProviderConfig> = {
  stable_diffusion: {
    name: 'Stable Diffusion (HuggingFace)',
    env_var: 'STABLE_DIFFUSION_KEY',
    docs_url: 'https://huggingface.co/docs/api-inference/quicktour',
    setup_time: '1-2 minutes',
    description: 'Budget-friendly AI image generation. Start free with community token.',
    free_tier: true,
    free_credits: 'Free Hugging Face account'
  },
  runway: {
    name: 'Runway AI',
    env_var: 'RUNWAY_API_KEY',
    docs_url: 'https://runwayml.com/docs/api',
    setup_time: '2-3 minutes',
    description: 'Professional-grade images, video, and audio generation.',
    free_tier: true,
    free_credits: '$50 free credits on signup'
  }
};

const MediaSetup: React.FC = () => {
  const [statuses, setStatuses] = useState<Record<string, ProviderStatus>>({
    stable_diffusion: { configured: false, tested: false },
    runway: { configured: false, tested: false }
  });

  const [apiKeys, setApiKeys] = useState<Record<string, string>>({
    stable_diffusion: '',
    runway: ''
  });

  const [saving, setSaving] = useState<Record<string, boolean>>({
    stable_diffusion: false,
    runway: false
  });

  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({
    stable_diffusion: false,
    runway: false
  });

  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Try to load existing keys from localStorage
  useEffect(() => {
    const savedKeys = localStorage.getItem('media_provider_keys');
    if (savedKeys) {
      try {
        const parsed = JSON.parse(savedKeys);
        setApiKeys(parsed);
      } catch (err) {
        console.error('Failed to load saved keys:', err);
      }
    }
  }, []);

  const handleKeyChange = (provider: string, value: string) => {
    setApiKeys(prev => ({
      ...prev,
      [provider]: value
    }));
  };

  const handleSaveKey = async (provider: string) => {
    const key = apiKeys[provider];

    if (!key.trim()) {
      setMessage({ type: 'error', text: 'Please enter an API key' });
      return;
    }

    setSaving(prev => ({ ...prev, [provider]: true }));
    setMessage(null);

    try {
      // Save to backend
      const response = await fetch('/api/media/configure', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider,
          api_key: key,
          test: true
        })
      });

      if (response.ok) {
        // Save to localStorage as well
        const saved = localStorage.getItem('media_provider_keys');
        const existing = saved ? JSON.parse(saved) : {};
        existing[provider] = key;
        localStorage.setItem('media_provider_keys', JSON.stringify(existing));

        setStatuses(prev => ({
          ...prev,
          [provider]: { configured: true, tested: true }
        }));

        setMessage({
          type: 'success',
          text: `${PROVIDERS[provider].name} configured successfully! ✓`
        });

        // Clear message after 3 seconds
        setTimeout(() => setMessage(null), 3000);
      } else {
        const error = await response.json();
        setMessage({
          type: 'error',
          text: `Configuration failed: ${error.detail || 'Unknown error'}`
        });

        setStatuses(prev => ({
          ...prev,
          [provider]: { configured: false, tested: false, error: error.detail }
        }));
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Configuration failed';
      setMessage({ type: 'error', text: errorMsg });

      setStatuses(prev => ({
        ...prev,
        [provider]: { configured: false, tested: false, error: errorMsg }
      }));
    } finally {
      setSaving(prev => ({ ...prev, [provider]: false }));
    }
  };

  const handleClearKey = (provider: string) => {
    setApiKeys(prev => ({ ...prev, [provider]: '' }));
    setStatuses(prev => ({
      ...prev,
      [provider]: { configured: false, tested: false }
    }));

    // Remove from localStorage
    const saved = localStorage.getItem('media_provider_keys');
    if (saved) {
      const existing = JSON.parse(saved);
      delete existing[provider];
      localStorage.setItem('media_provider_keys', JSON.stringify(existing));
    }
  };

  const getHuggingFaceKey = () => {
    window.open('https://huggingface.co/settings/tokens', '_blank');
  };

  const getRunwayKey = () => {
    window.open('https://runwayml.com/api', '_blank');
  };

  return (
    <div className="w-full space-y-6 p-4 bg-gradient-to-br from-slate-900 to-slate-800 rounded-lg">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">Media Provider Setup</h2>
        <p className="text-slate-400">
          Configure AI providers for media generation. Start with free tiers!
        </p>
      </div>

      {/* Message */}
      {message && (
        <div
          className={`p-4 rounded-lg border ${
            message.type === 'success'
              ? 'bg-green-500/10 border-green-500 text-green-400'
              : 'bg-red-500/10 border-red-500 text-red-400'
          }`}
        >
          {message.type === 'success' ? '✓' : '✕'} {message.text}
        </div>
      )}

      {/* Quick Start Guide */}
      <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-4">
        <h3 className="font-semibold text-blue-300 mb-2">🚀 Quick Start</h3>
        <ol className="text-sm text-slate-300 space-y-1 list-decimal list-inside">
          <li>Get a free API key (links below)</li>
          <li>Paste it in the field below</li>
          <li>Click "Save & Test"</li>
          <li>Start generating!</li>
        </ol>
      </div>

      {/* Provider Cards */}
      <div className="space-y-4">
        {Object.entries(PROVIDERS).map(([providerKey, provider]) => (
          <div
            key={providerKey}
            className="border border-slate-600 bg-slate-800/50 rounded-lg p-4 space-y-4"
          >
            {/* Header */}
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-lg font-semibold text-white">{provider.name}</h3>
                <p className="text-sm text-slate-400 mt-1">{provider.description}</p>
              </div>
              {statuses[providerKey].configured && (
                <div className="flex items-center gap-2 px-3 py-1 bg-green-500/20 rounded-full text-green-400 text-sm font-medium">
                  ✓ Configured
                </div>
              )}
            </div>

            {/* Info Grid */}
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="bg-slate-700/50 rounded p-2">
                <span className="text-slate-500 block text-xs mb-1">Setup Time</span>
                <span className="text-slate-300">{provider.setup_time}</span>
              </div>
              <div className="bg-slate-700/50 rounded p-2">
                <span className="text-slate-500 block text-xs mb-1">Free Tier</span>
                <span className="text-slate-300">{provider.free_credits}</span>
              </div>
            </div>

            {/* API Key Input */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-slate-300">API Key</label>
              <div className="flex gap-2">
                <input
                  type={showKeys[providerKey] ? 'text' : 'password'}
                  value={apiKeys[providerKey]}
                  onChange={(e) => handleKeyChange(providerKey, e.target.value)}
                  placeholder={`Enter your ${provider.name} API key...`}
                  className="flex-1 bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                />
                <button
                  onClick={() =>
                    setShowKeys(prev => ({
                      ...prev,
                      [providerKey]: !prev[providerKey]
                    }))
                  }
                  className="px-3 py-2 bg-slate-700 hover:bg-slate-600 border border-slate-600 rounded text-slate-300 transition-colors"
                  title={showKeys[providerKey] ? 'Hide' : 'Show'}
                >
                  {showKeys[providerKey] ? '🙈' : '👁️'}
                </button>
              </div>
              {statuses[providerKey].error && (
                <p className="text-sm text-red-400">⚠️ {statuses[providerKey].error}</p>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2 flex-wrap">
              {apiKeys[providerKey] ? (
                <>
                  <button
                    onClick={() => handleSaveKey(providerKey)}
                    disabled={saving[providerKey] || !apiKeys[providerKey].trim()}
                    className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white font-medium py-2 px-4 rounded transition-colors"
                  >
                    {saving[providerKey] ? 'Testing...' : 'Save & Test'}
                  </button>
                  <button
                    onClick={() => handleClearKey(providerKey)}
                    className="px-4 py-2 bg-red-600/20 hover:bg-red-600/30 text-red-400 border border-red-500/50 rounded font-medium transition-colors"
                  >
                    Clear
                  </button>
                </>
              ) : (
                <button
                  onClick={
                    providerKey === 'stable_diffusion' ? getHuggingFaceKey : getRunwayKey
                  }
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded transition-colors flex items-center justify-center gap-2"
                >
                  🔗 Get Free API Key
                </button>
              )}

              <a
                href={provider.docs_url}
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded border border-slate-600 transition-colors font-medium"
              >
                📖 Docs
              </a>
            </div>
          </div>
        ))}
      </div>

      {/* Feature Matrix */}
      <div className="border border-slate-700 bg-slate-800/50 rounded-lg p-4">
        <h3 className="font-semibold text-white mb-4">Feature Comparison</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-left text-slate-400 border-b border-slate-700">
              <tr>
                <th className="pb-2 font-medium">Feature</th>
                <th className="pb-2 font-medium text-center">Free (SVG)</th>
                <th className="pb-2 font-medium text-center">Budget</th>
                <th className="pb-2 font-medium text-center">Premium</th>
              </tr>
            </thead>
            <tbody className="text-slate-300">
              <tr className="border-b border-slate-700/50">
                <td className="py-2">Cost</td>
                <td className="text-center">$0</td>
                <td className="text-center">$0.01/img</td>
                <td className="text-center">$0.05+/img</td>
              </tr>
              <tr className="border-b border-slate-700/50">
                <td className="py-2">Speed</td>
                <td className="text-center">Instant</td>
                <td className="text-center">3-5s</td>
                <td className="text-center">2-10s</td>
              </tr>
              <tr className="border-b border-slate-700/50">
                <td className="py-2">Image Quality</td>
                <td className="text-center">✓ Basic</td>
                <td className="text-center">✓ Good</td>
                <td className="text-center">✓✓ Excellent</td>
              </tr>
              <tr className="border-b border-slate-700/50">
                <td className="py-2">Video Generation</td>
                <td className="text-center">✕</td>
                <td className="text-center">✕</td>
                <td className="text-center">✓</td>
              </tr>
              <tr>
                <td className="py-2">Audio Generation</td>
                <td className="text-center">✕</td>
                <td className="text-center">✕</td>
                <td className="text-center">✓</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Tips */}
      <div className="bg-amber-900/30 border border-amber-700 rounded-lg p-4">
        <h3 className="font-semibold text-amber-300 mb-2">💡 Pro Tips</h3>
        <ul className="text-sm text-slate-300 space-y-1">
          <li>✓ Start with Free tier for testing and wireframes</li>
          <li>✓ Use Budget tier ($0.01/img) for production mockups</li>
          <li>✓ Reserve Premium tier for final deliverables</li>
          <li>✓ All tiers available - no lock-in!</li>
        </ul>
      </div>
    </div>
  );
};

export default MediaSetup;
