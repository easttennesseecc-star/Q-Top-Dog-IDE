// frontend/src/components/MediaGeneration.tsx
/**
 * Media Generation Component
 * Supports 3 tiers:
 * 1. FREE: Q Assistant SVG
 * 2. BUDGET: Stable Diffusion (HuggingFace)
 * 3. PREMIUM: Runway AI (images, video, audio)
 */

import React, { useState, useEffect } from 'react';

interface MediaGeneration {
  url: string;
  media_type: string;
  tier: string;
  cost: number;
  time_ms: number;
  timestamp: string;
}

interface ProviderStatus {
  free: any;
  budget: any;
  premium: any;
}

interface UsageStats {
  total_generated: number;
  total_cost: number;
  by_tier: Record<string, { count: number; total_cost: number; avg_time_ms: number }>;
}

const MediaGeneration: React.FC<{ projectId?: string }> = ({ projectId }) => {
  const [description, setDescription] = useState('');
  const [mediaType, setMediaType] = useState<'image' | 'video' | 'audio'>('image');
  const [tier, setTier] = useState<'auto' | 'free' | 'budget' | 'premium'>('auto');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedMedia, setGeneratedMedia] = useState<MediaGeneration | null>(null);
  const [providerStatus, setProviderStatus] = useState<ProviderStatus | null>(null);
  const [usageStats, setUsageStats] = useState<UsageStats | null>(null);
  const [history, setHistory] = useState<MediaGeneration[]>([]);
  const [estimatedCost, setEstimatedCost] = useState<number | null>(null);

  // Fetch provider status on load
  useEffect(() => {
    fetchProviderStatus();
    fetchUsageStats();
    fetchHistory();
  }, []);

  // Estimate cost when description or tier changes
  useEffect(() => {
    if (description.length > 3) {
      estimateCost();
    } else {
      setEstimatedCost(null);
    }
  }, [description, mediaType, tier]);

  const fetchProviderStatus = async () => {
    try {
      const res = await fetch('/api/media/status');
      if (res.ok) {
        const data = await res.json();
        setProviderStatus(data);
      }
    } catch (err) {
      console.error('Failed to fetch provider status:', err);
    }
  };

  const fetchUsageStats = async () => {
    try {
      const res = await fetch('/api/media/usage');
      if (res.ok) {
        const data = await res.json();
        setUsageStats(data);
      }
    } catch (err) {
      console.error('Failed to fetch usage stats:', err);
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch('/api/media/history?limit=10');
      if (res.ok) {
        const data = await res.json();
        setHistory(data.items || []);
      }
    } catch (err) {
      console.error('Failed to fetch history:', err);
    }
  };

  const estimateCost = async () => {
    try {
      const res = await fetch('/api/media/estimate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          description,
          media_type: mediaType,
          tier: tier === 'auto' ? null : tier
        })
      });

      if (res.ok) {
        const data = await res.json();
        setEstimatedCost(data.estimated_cost);
      }
    } catch (err) {
      console.error('Failed to estimate cost:', err);
    }
  };

  const handleGenerate = async () => {
    if (!description.trim()) {
      setError('Please describe what you want to generate');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch('/api/media/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          description: description.trim(),
          media_type: mediaType,
          tier: tier === 'auto' ? null : tier,
          project_id: projectId
        })
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Failed to generate media');
      }

      const data = await res.json();
      setGeneratedMedia(data);
      
      // Refresh stats and history
      fetchUsageStats();
      fetchHistory();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate media');
    } finally {
      setLoading(false);
    }
  };

  const getTierInfo = (tierName: 'free' | 'budget' | 'premium') => {
    if (!providerStatus) return null;
    return providerStatus[tierName];
  };

  const handleDownload = async () => {
    if (!generatedMedia) return;

    try {
      // Convert data URI or URL to blob
      const response = await fetch(generatedMedia.url);
      const blob = await response.blob();
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `media-${Date.now()}.${
        generatedMedia.media_type === 'image' ? 'png' :
        generatedMedia.media_type === 'video' ? 'mp4' :
        'mp3'
      }`;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to download media');
    }
  };

  const handleCopyUrl = () => {
    if (generatedMedia) {
      navigator.clipboard.writeText(generatedMedia.url);
    }
  };

  const clearHistory = async () => {
    // Would need backend implementation
    setHistory([]);
  };

  if (!providerStatus) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin text-2xl">⏳</div>
      </div>
    );
  }

  return (
    <div className="w-full space-y-6 p-4 bg-gradient-to-br from-slate-900 to-slate-800 rounded-lg">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">Media Generation</h2>
        <p className="text-slate-400">
          Generate professional images, videos, and audio with AI-powered tools
        </p>
      </div>

      {/* Provider Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Free Tier */}
        <div className="border border-green-500 bg-green-500/10 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-green-400">Free</h3>
            <span className="text-xs bg-green-500/20 px-2 py-1 rounded text-green-400">ENABLED</span>
          </div>
          <p className="text-sm text-slate-400 mb-3">{getTierInfo('free')?.note}</p>
          <div className="flex items-center justify-between">
            <span className="text-lg font-bold text-green-400">$0</span>
            <span className="text-xs text-slate-500">/image</span>
          </div>
        </div>

        {/* Budget Tier */}
        <div className={`border ${getTierInfo('budget')?.configured ? 'border-blue-500 bg-blue-500/10' : 'border-slate-600 bg-slate-700/50'} rounded-lg p-4`}>
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-blue-400">Budget</h3>
            <span className={`text-xs px-2 py-1 rounded ${
              getTierInfo('budget')?.configured 
                ? 'bg-blue-500/20 text-blue-400' 
                : 'bg-slate-600/20 text-slate-400'
            }`}>
              {getTierInfo('budget')?.configured ? 'CONFIGURED' : 'NOT SET UP'}
            </span>
          </div>
          <p className="text-sm text-slate-400 mb-3">{getTierInfo('budget')?.provider}</p>
          <div className="flex items-center justify-between">
            <span className="text-lg font-bold text-blue-400">$0.01</span>
            <span className="text-xs text-slate-500">/image</span>
          </div>
        </div>

        {/* Premium Tier */}
        <div className={`border ${getTierInfo('premium')?.configured ? 'border-purple-500 bg-purple-500/10' : 'border-slate-600 bg-slate-700/50'} rounded-lg p-4`}>
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-purple-400">Premium</h3>
            <span className={`text-xs px-2 py-1 rounded ${
              getTierInfo('premium')?.configured 
                ? 'bg-purple-500/20 text-purple-400' 
                : 'bg-slate-600/20 text-slate-400'
            }`}>
              {getTierInfo('premium')?.configured ? 'CONFIGURED' : 'NOT SET UP'}
            </span>
          </div>
          <p className="text-sm text-slate-400 mb-3">{getTierInfo('premium')?.provider}</p>
          <div className="flex items-center justify-between">
            <span className="text-lg font-bold text-purple-400">$0.05+</span>
            <span className="text-xs text-slate-500">/image</span>
          </div>
        </div>
      </div>

      {/* Input Section */}
      <div className="space-y-4 bg-slate-800/50 border border-slate-700 rounded-lg p-4">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            What do you want to generate?
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="E.g., 'A wireframe for a social media app home screen' or 'A professional icon of a rocket launching into space'"
            className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 resize-none"
            rows={4}
            disabled={loading}
          />
        </div>

        {/* Media Type Selection */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          <div>
            <label className="text-sm font-medium text-slate-300 mb-2 block">Media Type</label>
            <select
              value={mediaType}
              onChange={(e) => setMediaType(e.target.value as 'image' | 'video' | 'audio')}
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
              disabled={loading}
            >
              <option value="image">Image</option>
              <option value="video">Video</option>
              <option value="audio">Audio</option>
            </select>
          </div>

          {/* Tier Selection */}
          <div>
            <label className="text-sm font-medium text-slate-300 mb-2 block">Tier</label>
            <select
              value={tier}
              onChange={(e) => setTier(e.target.value as any)}
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
              disabled={loading}
            >
              <option value="auto">Auto (Cheapest)</option>
              <option value="free">Free (SVG)</option>
              <option value="budget">Budget (Stable Diffusion)</option>
              <option value="premium">Premium (Runway)</option>
            </select>
          </div>
        </div>

        {/* Cost Estimate */}
        {estimatedCost !== null && (
          <div className="flex items-center gap-2 p-2 bg-blue-500/10 border border-blue-500/30 rounded text-blue-300 text-sm">
            ⚡ Estimated cost: <span className="font-semibold">${estimatedCost.toFixed(4)}</span>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded text-red-300 text-sm">
            ⚠️ {error}
          </div>
        )}

        {/* Generate Button */}
        <button
          onClick={handleGenerate}
          disabled={loading || !description.trim()}
          className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-slate-600 disabled:to-slate-700 text-white font-semibold py-2 px-4 rounded transition-all flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <span className="animate-spin">⏳</span>
              Generating...
            </>
          ) : (
            <>
              ⚡
              Generate Media
            </>
          )}
        </button>
      </div>

      {/* Generated Media Display */}
      {generatedMedia && (
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">Generated Media</h3>
            <div className="flex items-center gap-2 text-sm text-slate-400">
              <span className="bg-slate-700 px-2 py-1 rounded capitalize">{generatedMedia.tier}</span>
              <span className="bg-slate-700 px-2 py-1 rounded">${generatedMedia.cost.toFixed(4)}</span>
              <span className="bg-slate-700 px-2 py-1 rounded">{generatedMedia.time_ms}ms</span>
            </div>
          </div>

          {/* Media Viewer */}
          <div className="bg-black rounded border border-slate-600 overflow-hidden">
            {generatedMedia.media_type === 'image' && (
              <img src={generatedMedia.url} alt="Generated" className="w-full" />
            )}
            {generatedMedia.media_type === 'video' && (
              <video src={generatedMedia.url} className="w-full" controls />
            )}
            {generatedMedia.media_type === 'audio' && (
              <audio src={generatedMedia.url} className="w-full" controls />
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2">
            <button
              onClick={handleDownload}
              className="flex-1 flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded transition-colors"
            >
              ⬇️
              Download
            </button>
            <button
              onClick={handleCopyUrl}
              className="flex-1 flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded transition-colors"
            >
              📋
              Copy URL
            </button>
          </div>
        </div>
      )}

      {/* Usage Stats */}
      {usageStats && usageStats.total_generated > 0 && (
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-white mb-4">Usage Statistics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-slate-700/50 rounded p-3">
              <p className="text-sm text-slate-400">Total Generated</p>
              <p className="text-2xl font-bold text-white">{usageStats.total_generated}</p>
            </div>
            <div className="bg-slate-700/50 rounded p-3">
              <p className="text-sm text-slate-400">Total Cost</p>
              <p className="text-2xl font-bold text-white">${usageStats.total_cost.toFixed(2)}</p>
            </div>
            {Object.entries(usageStats.by_tier).map(([tierName, stats]) => (
              <div key={tierName} className="bg-slate-700/50 rounded p-3">
                <p className="text-sm text-slate-400 capitalize">{tierName}</p>
                <p className="text-lg font-semibold text-white">{(stats as any).count}</p>
                <p className="text-xs text-slate-500">${(stats as any).total_cost.toFixed(2)}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent History */}
      {history.length > 0 && (
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">Recent Generations</h3>
            <button
              onClick={clearHistory}
              className="flex items-center gap-1 text-red-400 hover:text-red-300 text-sm"
            >
              🗑️
              Clear
            </button>
          </div>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {history.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between p-2 bg-slate-700/50 rounded text-sm">
                <div className="flex-1">
                  <span className="text-slate-300 capitalize">{item.media_type}</span>
                  <span className="text-slate-500 ml-2">{new Date(item.timestamp).toLocaleTimeString()}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="bg-slate-600 px-2 py-1 rounded text-xs capitalize text-slate-300">{item.tier}</span>
                  <span className="text-slate-400 text-xs">${item.cost.toFixed(4)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default MediaGeneration;
