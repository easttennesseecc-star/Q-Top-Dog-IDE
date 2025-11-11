/*
 * Unified Sign-In Hub Component
 * Q-IDE - Intelligent Development Environment
 * Single login for GitHub, Copilot, LLM Models, and Repository Access
 */

import React, { useState, useEffect } from 'react';

interface ServiceStatus {
  name: string;
  connected: boolean;
  category: 'authentication' | 'coding' | 'llm';
  icon: string;
  description: string;
  cost?: string;
}

interface UserProfile {
  user_id: string;
  email: string;
  name: string;
  avatar_url?: string;
  github_username?: string;
  github_repos: string[];
  connected_services: Record<string, boolean>;
}

interface AvailableService {
  name: string;
  description: string;
  category: string;
  cost?: string;
  free?: boolean;
  local?: boolean;
  requires?: string[];
}

export const UnifiedSignInHub: React.FC = () => {
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null);
  const [signingIn, setSigningIn] = useState<string | null>(null);
  const [availableServices, setAvailableServices] = useState<Record<string, AvailableService>>({});
  const [addingCredential, setAddingCredential] = useState<string | null>(null);
  const [credentialForm, setCredentialForm] = useState<Record<string, string>>({});
  const [message, setMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null);

  useEffect(() => {
    // Load current session
    const userId = localStorage.getItem('q_ide_user_id');
    if (userId) {
      fetchUserProfile(userId);
    }

    // Load available services
    fetchAvailableServices();
  }, []);

  const fetchUserProfile = async (userId: string) => {
    try {
      const res = await fetch(`/auth/profile/${userId}`);
      if (res.ok) {
        const profile = await res.json();
        setCurrentUser(profile);
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
    }
  };

  const fetchAvailableServices = async () => {
    try {
      const res = await fetch('/auth/services/available');
      if (res.ok) {
        const services = await res.json();
        setAvailableServices(services);
      }
    } catch (error) {
      console.error('Error fetching services:', error);
    }
  };

  const handleOAuthSignIn = async (provider: string) => {
    setSigningIn(provider);
    try {
      const res = await fetch('/auth/oauth/init', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider }),
      });

      if (!res.ok) {
        const error = await res.json();
        setMessage({ type: 'error', text: `Error: ${error.detail}` });
        setSigningIn(null);
        return;
      }

      const data = await res.json();
      
      // Open popup for OAuth
      const width = 500;
      const height = 600;
      const left = window.screenX + (window.outerWidth - width) / 2;
      const top = window.screenY + (window.outerHeight - height) / 2;
      
      const popup = window.open(
        data.auth_url,
        `${provider}_signin`,
        `width=${width},height=${height},left=${left},top=${top}`
      );

      // Check for completion every second
      const checkInterval = setInterval(() => {
        if (!popup || popup.closed) {
          clearInterval(checkInterval);
          // Try to fetch updated profile
          if (currentUser) {
            setTimeout(() => fetchUserProfile(currentUser.user_id), 1000);
          }
          setSigningIn(null);
        }
      }, 1000);
    } catch (error) {
      setMessage({ type: 'error', text: `OAuth error: ${error}` });
      setSigningIn(null);
    }
  };

  const handleAddCredential = async (service: string) => {
    const apiKey = credentialForm[service];
    if (!apiKey) {
      setMessage({ type: 'error', text: 'Please enter an API key' });
      return;
    }

    if (!currentUser) {
      setMessage({ type: 'error', text: 'Please sign in first' });
      return;
    }

    try {
      const res = await fetch('/auth/credentials/add?user_id=' + currentUser.user_id, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          service,
          api_key: apiKey,
          is_active: true,
        }),
      });

      if (res.ok) {
        setMessage({ type: 'success', text: `✅ ${service} configured!` });
        setCredentialForm({ ...credentialForm, [service]: '' });
        setAddingCredential(null);
        fetchUserProfile(currentUser.user_id);
      } else {
        const error = await res.json();
        setMessage({ type: 'error', text: error.detail });
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error}` });
    }
  };

  const handleSignOut = () => {
    setCurrentUser(null);
    localStorage.removeItem('q_ide_user_id');
    localStorage.removeItem('q_ide_user_session');
    setMessage({ type: 'success', text: 'Signed out successfully' });
  };

  // ============================================================================
  // Render: Signed Out View
  // ============================================================================

  if (!currentUser) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-8">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 mb-3">
              🔐 Q-IDE Sign In Hub
            </h1>
            <p className="text-lg text-slate-300 mb-2">
              One login for all your development tools and AI models
            </p>
            <p className="text-sm text-slate-400">
              Connect GitHub, Copilot, Gemini, OpenAI, and more
            </p>
            <div className="mt-4 flex items-center justify-center gap-3">
              <a href="/login" className="text-xs px-3 py-1.5 rounded-md border border-cyan-400/30 hover:border-cyan-400 text-cyan-300">Sign in with email</a>
              <a href="/signup" className="text-xs px-3 py-1.5 rounded-md bg-cyan-600/20 border border-cyan-400/40 hover:bg-cyan-600/30 text-cyan-200">Create free account</a>
            </div>
          </div>

          {/* Message */}
          {message && (
            <div
              className={`mb-8 p-4 rounded-lg border ${
                message.type === 'success'
                  ? 'bg-green-900/20 border-green-600/50 text-green-300'
                  : message.type === 'error'
                  ? 'bg-red-900/20 border-red-600/50 text-red-300'
                  : 'bg-blue-900/20 border-blue-600/50 text-blue-300'
              }`}
            >
              {message.text}
            </div>
          )}

          {/* OAuth Options */}
          <div className="grid md:grid-cols-3 gap-6 mb-12">
            {/* GitHub */}
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 hover:border-slate-600/50 transition">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-3xl">🐙</div>
                <h2 className="text-xl font-semibold text-white">GitHub</h2>
              </div>
              <p className="text-sm text-slate-400 mb-4">
                Access your repositories, enable Copilot, and build features
              </p>
              <button
                onClick={() => handleOAuthSignIn('github')}
                disabled={signingIn === 'github'}
                className="w-full px-4 py-2 bg-gradient-to-r from-slate-700 to-slate-800 hover:from-slate-600 hover:to-slate-700 text-white rounded-lg font-medium transition disabled:opacity-50"
              >
                {signingIn === 'github' ? '⏳ Signing in...' : '✓ Sign in with GitHub'}
              </button>
            </div>

            {/* Google */}
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 hover:border-slate-600/50 transition">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-3xl">🔍</div>
                <h2 className="text-xl font-semibold text-white">Google</h2>
              </div>
              <p className="text-sm text-slate-400 mb-4">
                Access Gemini, Google Cloud, and integrated services
              </p>
              <button
                onClick={() => handleOAuthSignIn('google')}
                disabled={signingIn === 'google'}
                className="w-full px-4 py-2 bg-gradient-to-r from-slate-700 to-slate-800 hover:from-slate-600 hover:to-slate-700 text-white rounded-lg font-medium transition disabled:opacity-50"
              >
                {signingIn === 'google' ? '⏳ Signing in...' : '✓ Sign in with Google'}
              </button>
            </div>

            {/* Microsoft */}
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 hover:border-slate-600/50 transition">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-3xl">⊞</div>
                <h2 className="text-xl font-semibold text-white">Microsoft</h2>
              </div>
              <p className="text-sm text-slate-400 mb-4">
                Access Azure, Office 365, and Microsoft services
              </p>
              <button
                onClick={() => handleOAuthSignIn('microsoft')}
                disabled={signingIn === 'microsoft'}
                className="w-full px-4 py-2 bg-gradient-to-r from-slate-700 to-slate-800 hover:from-slate-600 hover:to-slate-700 text-white rounded-lg font-medium transition disabled:opacity-50"
              >
                {signingIn === 'microsoft' ? '⏳ Signing in...' : '✓ Sign in with Microsoft'}
              </button>
            </div>
          </div>

          {/* Services Grid */}
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-white mb-6">Available Services</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(availableServices).map(([key, service]) => (
                <div key={key} className="bg-slate-800/30 border border-slate-700/30 rounded-lg p-4">
                  <h3 className="font-semibold text-white mb-1">{service.name}</h3>
                  <p className="text-xs text-slate-400 mb-3">{service.description}</p>
                  <div className="flex items-center gap-2 text-xs">
                    {service.free && <span className="text-green-400">✓ Free</span>}
                    {service.local && <span className="text-blue-400">🖥️ Local</span>}
                    {service.cost && <span className="text-yellow-400">💰 {service.cost}</span>}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Info */}
          <div className="bg-slate-800/30 border border-slate-700/30 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-cyan-300 mb-4">✨ What you get:</h3>
            <ul className="space-y-2 text-sm text-slate-300">
              <li>✓ <strong>One login</strong> for all development tools</li>
              <li>✓ <strong>Free tier models</strong> (Ollama, GPT4All) for local development</li>
              <li>✓ <strong>Paid tier models</strong> (OpenAI, Claude, Copilot) with API keys</li>
              <li>✓ <strong>GitHub integration</strong> for repository access and browsing</li>
              <li>✓ <strong>Automatic credential management</strong> - no manual config needed</li>
              <li>✓ <strong>Seamless switching</strong> between models without signing out</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  // ============================================================================
  // Render: Signed In View
  // ============================================================================

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            {currentUser.avatar_url && (
              <img
                src={currentUser.avatar_url}
                alt={currentUser.name}
                className="w-12 h-12 rounded-full border-2 border-cyan-400/50"
              />
            )}
            <div>
              <h1 className="text-2xl font-bold text-white">{currentUser.name}</h1>
              <p className="text-sm text-slate-400">{currentUser.email}</p>
            </div>
          </div>
          <button
            onClick={handleSignOut}
            className="px-4 py-2 bg-red-600/20 text-red-300 rounded-lg hover:bg-red-600/40 border border-red-500/50 transition"
          >
            🚪 Sign Out
          </button>
        </div>

        {/* Message */}
        {message && (
          <div
            className={`mb-8 p-4 rounded-lg border ${
              message.type === 'success'
                ? 'bg-green-900/20 border-green-600/50 text-green-300'
                : message.type === 'error'
                ? 'bg-red-900/20 border-red-600/50 text-red-300'
                : 'bg-blue-900/20 border-blue-600/50 text-blue-300'
            }`}
          >
            {message.text}
          </div>
        )}

        {/* Connected Services */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-white mb-6">🔗 Connected Services</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* GitHub */}
            <div className={`p-6 rounded-lg border ${
              currentUser.connected_services['github']
                ? 'bg-green-900/10 border-green-600/50'
                : 'bg-slate-800/30 border-slate-700/30'
            }`}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">🐙 GitHub</h3>
                <span className={`text-xs font-semibold ${
                  currentUser.connected_services['github']
                    ? 'text-green-400'
                    : 'text-slate-500'
                }`}>
                  {currentUser.connected_services['github'] ? '✓ CONNECTED' : 'NOT CONNECTED'}
                </span>
              </div>
              {currentUser.connected_services['github'] && (
                <>
                  <p className="text-sm text-slate-300 mb-2">
                    <strong>Username:</strong> {currentUser.github_username}
                  </p>
                  <p className="text-sm text-slate-300 mb-4">
                    <strong>Repositories:</strong> {currentUser.github_repos.length}
                  </p>
                  <button className="text-sm text-cyan-400 hover:text-cyan-300">
                    → Browse Repositories
                  </button>
                </>
              )}
            </div>

            {/* Google Gemini */}
            <div className={`p-6 rounded-lg border ${
              currentUser.connected_services['google']
                ? 'bg-green-900/10 border-green-600/50'
                : 'bg-slate-800/30 border-slate-700/30'
            }`}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">🔍 Google</h3>
                <span className={`text-xs font-semibold ${
                  currentUser.connected_services['google']
                    ? 'text-green-400'
                    : 'text-slate-500'
                }`}>
                  {currentUser.connected_services['google'] ? '✓ CONNECTED' : 'NOT CONNECTED'}
                </span>
              </div>
              <p className="text-sm text-slate-400 mb-4">
                Access to Google Gemini, Bard, and Google Cloud services
              </p>
            </div>

            {/* Copilot */}
            <div className={`p-6 rounded-lg border ${
              currentUser.connected_services['github_copilot']
                ? 'bg-green-900/10 border-green-600/50'
                : 'bg-slate-800/30 border-slate-700/30'
            }`}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">⚡ Copilot</h3>
                <span className={`text-xs font-semibold ${
                  currentUser.connected_services['github_copilot']
                    ? 'text-green-400'
                    : 'text-slate-500'
                }`}>
                  {currentUser.connected_services['github_copilot'] ? '✓ CONFIGURED' : 'NOT CONFIGURED'}
                </span>
              </div>
              {!currentUser.connected_services['github_copilot'] && (
                <button
                  onClick={() => setAddingCredential('github_copilot')}
                  className="w-full px-3 py-2 bg-blue-600/20 text-blue-300 rounded-lg hover:bg-blue-600/40 border border-blue-500/50 transition text-sm"
                >
                  🔑 Add API Key
                </button>
              )}
            </div>
          </div>
        </div>

        {/* LLM Models */}
        <div>
          <h2 className="text-2xl font-bold text-white mb-6">🤖 LLM Models</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* OpenAI */}
            <div className="p-6 rounded-lg bg-slate-800/30 border border-slate-700/30">
              <h3 className="text-lg font-semibold text-white mb-2">ChatGPT / GPT-4</h3>
              <p className="text-sm text-slate-400 mb-4">Advanced code generation and analysis</p>
              <button
                onClick={() => setAddingCredential('openai')}
                className="w-full px-3 py-2 bg-orange-600/20 text-orange-300 rounded-lg hover:bg-orange-600/40 border border-orange-500/50 transition text-sm"
              >
                🔑 Add API Key
              </button>
            </div>

            {/* Claude */}
            <div className="p-6 rounded-lg bg-slate-800/30 border border-slate-700/30">
              <h3 className="text-lg font-semibold text-white mb-2">Claude (Anthropic)</h3>
              <p className="text-sm text-slate-400 mb-4">Analysis, writing, and reasoning</p>
              <button
                onClick={() => setAddingCredential('anthropic')}
                className="w-full px-3 py-2 bg-purple-600/20 text-purple-300 rounded-lg hover:bg-purple-600/40 border border-purple-500/50 transition text-sm"
              >
                🔑 Add API Key
              </button>
            </div>

            {/* Gemini */}
            <div className="p-6 rounded-lg bg-slate-800/30 border border-slate-700/30">
              <h3 className="text-lg font-semibold text-white mb-2">Gemini (Free)</h3>
              <p className="text-sm text-slate-400 mb-4">Google's AI model - completely free</p>
              <button
                onClick={() => setAddingCredential('google_gemini')}
                className="w-full px-3 py-2 bg-green-600/20 text-green-300 rounded-lg hover:bg-green-600/40 border border-green-500/50 transition text-sm"
              >
                🔑 Add API Key (Free)
              </button>
            </div>

            {/* Ollama */}
            <div className="p-6 rounded-lg bg-slate-800/30 border border-slate-700/30">
              <h3 className="text-lg font-semibold text-white mb-2">Ollama (Local)</h3>
              <p className="text-sm text-slate-400 mb-4">Run LLMs locally on your machine</p>
              <button
                onClick={() => setAddingCredential('ollama_local')}
                className="w-full px-3 py-2 bg-blue-600/20 text-blue-300 rounded-lg hover:bg-blue-600/40 border border-blue-500/50 transition text-sm"
              >
                ⚙️ Configure Local
              </button>
            </div>

            {/* GPT4All */}
            <div className="p-6 rounded-lg bg-slate-800/30 border border-slate-700/30">
              <h3 className="text-lg font-semibold text-white mb-2">GPT4All (Local)</h3>
              <p className="text-sm text-slate-400 mb-4">Free local AI models</p>
              <button
                onClick={() => setAddingCredential('gpt4all')}
                className="w-full px-3 py-2 bg-blue-600/20 text-blue-300 rounded-lg hover:bg-blue-600/40 border border-blue-500/50 transition text-sm"
              >
                ⚙️ Configure Local
              </button>
            </div>
          </div>
        </div>

        {/* Credential Input Modal */}
        {addingCredential && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
            <div className="bg-slate-900 border border-slate-700 rounded-lg p-6 w-full max-w-md">
              <h3 className="text-xl font-bold text-white mb-4">
                Add {availableServices[addingCredential]?.name || addingCredential}
              </h3>
              <input
                type="password"
                placeholder="API Key or Configuration..."
                value={credentialForm[addingCredential] || ''}
                onChange={(e) =>
                  setCredentialForm({
                    ...credentialForm,
                    [addingCredential]: e.target.value,
                  })
                }
                className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white mb-4 focus:outline-none focus:border-cyan-500"
              />
              <div className="flex gap-3">
                <button
                  onClick={() => setAddingCredential(null)}
                  className="flex-1 px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleAddCredential(addingCredential)}
                  className="flex-1 px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-500"
                >
                  Save
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UnifiedSignInHub;
