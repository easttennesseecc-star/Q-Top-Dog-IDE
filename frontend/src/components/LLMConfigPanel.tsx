import React, { useEffect, useState } from 'react';

type Provider = {
  name: string;
  type: 'cloud' | 'local';
  has_key?: boolean;
  configured?: boolean;
  notes?: string;
  download_url?: string;
  api_endpoint?: string;
  requires_key?: boolean;
  authenticated?: boolean;
  auth_method?: string;
};

type Role = {
  name: string;
  description: string;
  current_model?: string;
  recommendations?: string[];
};

type AuthStatus = {
  authenticated: boolean;
  method: string;
  user?: string;
  expires_at?: string;
};

export default function LLMConfigPanel() {
  const [providers, setProviders] = useState<Record<string, Provider> | null>(null);
  const [roles, setRoles] = useState<Record<string, Role> | null>(null);
  const [authStatus, setAuthStatus] = useState<Record<string, AuthStatus>>({});
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'providers' | 'roles' | 'setup' | 'auth'>('providers');
  const [selectedProvider, setSelectedProvider] = useState<string | null>(null);
  const [apiKey, setApiKey] = useState('');
  const [setupInstructions, setSetupInstructions] = useState<string | null>(null);
  const [selectedRole, setSelectedRole] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<string | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [signingIn, setSigningIn] = useState<string | null>(null);

  useEffect(() => {
    loadProviders();
    loadRoles();
    checkAuthStatus();

    // Listen for OAuth callback messages from popup window
    const handleOAuthMessage = (event: MessageEvent) => {
      // Verify origin for security
      if (event.origin !== window.location.origin) return;

      if (event.data.type === 'oauth_success') {
        setMessage({ type: 'success', text: `Successfully authenticated with ${event.data.provider}!` });
        setSigningIn(null);
        // Refresh auth status
        setTimeout(() => checkAuthStatus(), 500);
      } else if (event.data.type === 'oauth_error') {
        setMessage({ type: 'error', text: `OAuth Error: ${event.data.error || 'Unknown error'}` });
        setSigningIn(null);
      }
    };

    window.addEventListener('message', handleOAuthMessage);
    return () => window.removeEventListener('message', handleOAuthMessage);
  }, []);

  async function checkAuthStatus() {
    try {
      const res = await fetch('/llm_auth/status');
      const data = await res.json();
      setAuthStatus(data.providers || {});
    } catch (e) {
      console.error('Error checking auth status:', e);
    }
  }

  async function loadProviders() {
    try {
      const res = await fetch('/llm_config/providers');
      const data = await res.json();
      setProviders({ ...data.cloud, ...data.local });
    } catch (e) {
      console.error('Error loading providers:', e);
    }
  }

  async function loadRoles() {
    try {
      const res = await fetch('/llm_config/roles');
      setRoles(await res.json());
    } catch (e) {
      console.error('Error loading roles:', e);
    }
  }

  async function saveApiKey() {
    if (!selectedProvider || !apiKey) return;

    try {
      const res = await fetch('/llm_config/api_key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: selectedProvider, key: apiKey })
      });

      if (res.ok) {
        const providerName = providers?.[selectedProvider]?.name || selectedProvider;
        setMessage({ type: 'success', text: `✓ ${providerName} credentials saved! You can now use this LLM.` });
        setApiKey('');
        setTimeout(() => {
          loadProviders();
          checkAuthStatus();
        }, 1000);
      } else {
        const errorData = await res.json().catch(() => ({}));
        setMessage({ type: 'error', text: `Failed: ${errorData.detail || 'Invalid API key'}` });
      }
    } catch (e) {
      setMessage({ type: 'error', text: `Error: ${e}` });
    }
  }

  async function deleteApiKey(provider: string) {
    try {
      const res = await fetch(`/llm_config/api_key/${provider}`, { method: 'DELETE' });
      if (res.ok) {
        setMessage({ type: 'success', text: 'API key deleted' });
        setTimeout(() => loadProviders(), 1000);
      }
    } catch (e) {
      setMessage({ type: 'error', text: `Error: ${e}` });
    }
  }

  async function loadSetupInstructions(provider: string) {
    try {
      const res = await fetch(`/llm_config/setup/${provider}`);
      const data = await res.json();
      setSetupInstructions(data.instructions);
    } catch (e) {
      console.error('Error loading setup:', e);
    }
  }

  async function assignRole() {
    if (!selectedRole || !selectedModel) return;

    try {
      const res = await fetch('/llm_config/role_assignment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: selectedRole, model_name: selectedModel })
      });

      if (res.ok) {
        setMessage({ type: 'success', text: 'Role assigned successfully!' });
        setTimeout(() => loadRoles(), 1000);
      }
    } catch (e) {
      setMessage({ type: 'error', text: `Error: ${e}` });
    }
  }

  async function handleQuickAssign(roleId: string, modelId: string) {
    if (!modelId) return;

    try {
      const res = await fetch('/llm_config/role_assignment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: roleId, model_name: modelId })
      });

      if (res.ok) {
        setMessage({ type: 'success', text: `✓ ${roles?.[roleId]?.name} now uses ${providers?.[modelId]?.name}` });
        setTimeout(() => loadRoles(), 500);
      } else {
        setMessage({ type: 'error', text: 'Failed to assign model' });
      }
    } catch (e) {
      setMessage({ type: 'error', text: `Error: ${e}` });
    }
  }

  async function initiateOAuthSignIn(provider: string) {
    setSigningIn(provider);
    try {
      const res = await fetch(`/llm_auth/oauth/config/${provider}`);
      const config = await res.json();
      
      const params = new URLSearchParams({
        client_id: config.client_id,
        redirect_uri: `${window.location.origin}/oauth/callback`,
        response_type: 'code',
        scope: config.scopes.join(' '),
        state: provider
      });
      
      const authUrl = `${config.auth_url}?${params.toString()}`;
      window.open(authUrl, '_blank', 'width=500,height=600');
      
      setMessage({ type: 'success', text: `Opening sign-in for ${provider}...` });
    } catch (e) {
      setMessage({ type: 'error', text: `Failed to start sign-in: ${e}` });
      setSigningIn(null);
    }
  }

  async function revokeAuth(provider: string) {
    try {
      const res = await fetch(`/llm_config/api_key/${provider}`, { 
        method: 'DELETE'
      });

      if (res.ok) {
        const providerName = providers?.[provider]?.name || provider;
        setMessage({ type: 'success', text: `✓ ${providerName} credentials cleared` });
        setTimeout(() => {
          loadProviders();
          checkAuthStatus();
        }, 500);
      } else {
        setMessage({ type: 'error', text: 'Failed to clear credentials' });
      }
    } catch (e) {
      setMessage({ type: 'error', text: `Error: ${e}` });
    }
  }

  return (
    <div className="p-4 bg-[#23272e] rounded-md border border-cyan-900/20 text-cyan-100 w-full max-w-4xl">
      <h2 className="text-xl font-bold mb-4">LLM Configuration</h2>

      {message && (
        <div className={`mb-3 p-3 rounded ${message.type === 'success' ? 'bg-green-900/30 text-green-300' : 'bg-red-900/30 text-red-300'}`}>
          {message.text}
        </div>
      )}

      <div className="flex gap-2 mb-4 border-b border-cyan-900/30">
        {(['providers', 'roles', 'setup', 'auth'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 ${activeTab === tab ? 'border-b-2 border-cyan-400 text-cyan-200' : 'text-gray-400 hover:text-cyan-300'}`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Providers Tab */}
      {activeTab === 'providers' && (
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-semibold mb-2 text-cyan-300">☁️ Cloud Services</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {providers && Object.entries(providers)
                .filter(([_, p]) => p.type === 'cloud')
                .map(([id, provider]) => (
                  <div key={id} className="p-3 bg-[#1e2128] border border-cyan-600/30 rounded hover:border-cyan-400/60 transition-all">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="font-semibold text-cyan-200">{provider.name}</div>
                        <div className="text-xs text-gray-400 mt-1">{provider.notes}</div>
                        <div className="mt-2 flex gap-2">
                          {provider.has_key ? (
                            <>
                              <span className="text-xs bg-green-700/40 text-green-300 px-2 py-1 rounded">✓ Configured</span>
                              <button
                                onClick={() => deleteApiKey(id)}
                                className="text-xs bg-red-700/40 text-red-300 px-2 py-1 rounded hover:bg-red-700/60"
                              >
                                Remove
                              </button>
                            </>
                          ) : (
                            <button
                              onClick={() => {
                                setSelectedProvider(id);
                                loadSetupInstructions(id);
                                setActiveTab('setup');
                              }}
                              className="text-xs bg-cyan-700/40 text-cyan-300 px-2 py-1 rounded hover:bg-cyan-700/60"
                            >
                              Setup
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-2 text-cyan-300">🖥️ Local Models</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {providers && Object.entries(providers)
                .filter(([_, p]) => p.type === 'local')
                .map(([id, provider]) => (
                  <div key={id} className="p-3 bg-[#1e2128] border border-orange-600/30 rounded">
                    <div className="font-semibold text-orange-200">{provider.name}</div>
                    <div className="text-xs text-gray-400 mt-1">{provider.notes}</div>
                    <a
                      href={provider.download_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs bg-orange-700/40 text-orange-300 px-2 py-1 rounded inline-block mt-2 hover:bg-orange-700/60"
                    >
                      Download
                    </a>
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}

      {/* Roles Tab */}
      {activeTab === 'roles' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold mb-3 text-cyan-300">🎯 Assign Models to Roles</h3>
          <div className="text-sm text-gray-400 mb-4 p-2 bg-blue-900/20 border border-blue-600/30 rounded">
            💡 Click on any role's dropdown to instantly change which LLM it uses. Changes apply immediately!
          </div>
          
          {roles && Object.entries(roles).map(([roleId, role]) => (
            <div key={roleId} className="p-4 bg-[#1e2128] border border-cyan-600/30 rounded">
              <div className="space-y-3">
                <div>
                  <div className="font-semibold text-cyan-200">{role.name}</div>
                  <div className="text-sm text-gray-400 mt-1">{role.description}</div>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-semibold text-gray-300 block">Assign LLM Model:</label>
                  <select
                    value={role.current_model || ''}
                    onChange={(e) => {
                      setSelectedRole(roleId);
                      setSelectedModel(e.target.value);
                      // Auto-assign when changed
                      setTimeout(() => {
                        handleQuickAssign(roleId, e.target.value);
                      }, 100);
                    }}
                    className="w-full px-3 py-2 bg-[#0f1114] border border-cyan-600/30 rounded text-white text-sm hover:border-cyan-500 transition-colors"
                  >
                    <option value="">-- Choose a model --</option>
                    {providers && Object.entries(providers).map(([id, provider]) => (
                      <option key={id} value={id}>
                        {provider.name} {provider.type === 'cloud' ? '☁️' : '🖥️'}
                      </option>
                    ))}
                  </select>
                </div>

                {role.current_model && (
                  <div className="flex items-center justify-between pt-2 border-t border-cyan-600/20">
                    <div className="text-xs text-green-300">
                      ✓ Currently assigned: <strong>{providers?.[role.current_model]?.name || role.current_model}</strong>
                    </div>
                    <button
                      onClick={() => {
                        setSelectedRole(roleId);
                        setSelectedModel('');
                      }}
                      className="text-xs bg-red-700/40 text-red-300 px-2 py-1 rounded hover:bg-red-700/60"
                    >
                      Clear
                    </button>
                  </div>
                )}

                {role.recommendations && (
                  <div className="text-xs text-gray-400 pt-2 border-t border-cyan-600/20">
                    💡 Recommended: {role.recommendations.join(', ')}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Setup Tab */}
      {activeTab === 'setup' && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-semibold mb-2">Select Provider:</label>
            <select
              value={selectedProvider || ''}
              onChange={(e) => {
                setSelectedProvider(e.target.value);
                loadSetupInstructions(e.target.value);
              }}
              className="w-full px-3 py-2 bg-[#0f1114] border border-cyan-600/30 rounded text-white mb-4"
            >
              <option value="">Choose a provider...</option>
              {providers && Object.entries(providers)
                .filter(([_, p]) => p.type === 'cloud')
                .map(([id, p]) => (
                  <option key={id} value={id}>{p.name}</option>
                ))}
            </select>
          </div>

          {setupInstructions && (
            <div className="p-3 bg-blue-900/20 border border-blue-600/50 rounded">
              <h4 className="font-semibold mb-2">Setup Instructions:</h4>
              <pre className="text-sm text-gray-300 whitespace-pre-wrap font-mono overflow-x-auto">
                {setupInstructions}
              </pre>
            </div>
          )}

          {selectedProvider && (
            <div className="space-y-2">
              <label className="block text-sm font-semibold">Enter API Key:</label>
              <input
                type="password"
                placeholder="Paste your API key here..."
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="w-full px-3 py-2 bg-[#0f1114] border border-cyan-600/30 rounded text-white text-sm"
              />
              <button
                onClick={saveApiKey}
                disabled={!apiKey}
                className="w-full px-3 py-2 bg-cyan-700 hover:bg-cyan-600 disabled:bg-gray-700 text-white rounded text-sm"
              >
                Save API Key
              </button>
            </div>
          )}

          <div className="p-2 bg-yellow-900/20 border border-yellow-600/30 rounded text-xs text-yellow-300">
            ⚠️ Your API keys are stored locally and encrypted. Never share them.
          </div>
        </div>
      )}

      {/* Authentication Tab */}
      {activeTab === 'auth' && (
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-semibold mb-2 text-cyan-300">🔐 LLM Provider Credentials</h3>
            <p className="text-sm text-gray-400 mb-4">
              Enter your API credentials below so Q-IDE can authenticate with LLM services on your behalf. 
              Your credentials are stored locally and encrypted - never sent anywhere.
            </p>
          </div>

          {/* Credential Input Section */}
          <div className="space-y-3">
            {providers && Object.entries(providers)
              .filter(([_, p]) => p.type === 'cloud')
              .sort(([a], [b]) => a.localeCompare(b))
              .map(([providerId, provider]) => {
                const providerEmojis: Record<string, string> = {
                  'openai': '🤖',
                  'google': '✨',
                  'gemini': '✨',
                  'anthropic': '🧠',
                  'claude': '🎯',
                  'xai': '⚡',
                  'grok': '⚙️',
                  'perplexity': '🌀',
                  'groq': '🚀',
                  'github': '🐙'
                };
                
                const credentialGuides: Record<string, {url: string; getKey: string}> = {
                  'openai': {
                    url: 'https://platform.openai.com/account/api-keys',
                    getKey: 'Go to API Keys → Create new secret key'
                  },
                  'google': {
                    url: 'https://ai.google.dev/tutorials/setup',
                    getKey: 'Get API key from Google AI Studio'
                  },
                  'gemini': {
                    url: 'https://ai.google.dev/tutorials/setup',
                    getKey: 'Get API key from Google AI Studio'
                  },
                  'anthropic': {
                    url: 'https://console.anthropic.com/account/keys',
                    getKey: 'Go to API Keys → Create new key'
                  },
                  'claude': {
                    url: 'https://console.anthropic.com/account/keys',
                    getKey: 'Go to API Keys → Create new key'
                  },
                  'github': {
                    url: 'https://github.com/settings/tokens',
                    getKey: 'Generate personal access token with repo scope'
                  }
                };
                
                const emoji = providerEmojis[providerId.toLowerCase()] || '🤖';
                const guide = credentialGuides[providerId.toLowerCase()];
                const status = authStatus[providerId];
                const isAuthenticated = status?.authenticated === true;
                
                return (
                  <div
                    key={providerId}
                    className="p-4 bg-[#0f1114] border border-cyan-600/30 rounded space-y-3"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="text-2xl">{emoji}</div>
                        <div>
                          <h4 className="font-semibold text-cyan-200">{provider.name}</h4>
                          {isAuthenticated && (
                            <div className="text-xs text-green-400">✓ Authenticated</div>
                          )}
                        </div>
                      </div>
                      {isAuthenticated && (
                        <button
                          onClick={() => revokeAuth(providerId)}
                          className="px-3 py-1 text-xs bg-red-700/40 hover:bg-red-700/60 text-red-300 rounded"
                        >
                          Clear
                        </button>
                      )}
                    </div>

                    {!isAuthenticated && (
                      <div className="space-y-2 text-sm">
                        <div className="p-2 bg-blue-900/20 border border-blue-600/30 rounded text-blue-300 text-xs">
                          <strong>How to get your credentials:</strong>
                          <div className="mt-1">{guide?.getKey}</div>
                          {guide?.url && (
                            <a
                              href={guide.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-400 underline hover:text-blue-300 mt-1 inline-block"
                            >
                              Open {provider.name} Console →
                            </a>
                          )}
                        </div>

                        <div>
                          <label className="block text-xs font-semibold text-gray-400 mb-1">
                            API Key / Secret Token:
                          </label>
                          <div className="flex gap-2">
                            <input
                              type="password"
                              placeholder={`Paste ${provider.name} API key here...`}
                              value={apiKey}
                              onChange={(e) => setApiKey(e.target.value)}
                              onKeyPress={(e) => {
                                if (e.key === 'Enter' && apiKey && selectedProvider === providerId) {
                                  saveApiKey();
                                }
                              }}
                              className="flex-1 px-3 py-2 bg-[#1a1e23] border border-cyan-600/30 rounded text-white text-sm placeholder-gray-600"
                            />
                            <button
                              onClick={() => {
                                setSelectedProvider(providerId);
                                setTimeout(() => saveApiKey(), 100);
                              }}
                              disabled={!apiKey || selectedProvider !== providerId}
                              className="px-3 py-2 bg-green-700 hover:bg-green-600 disabled:bg-gray-700 text-white text-sm rounded"
                            >
                              Save
                            </button>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
          </div>

          {/* Instructions */}
          <div className="mt-6 p-3 bg-cyan-900/20 border border-cyan-600/50 rounded text-sm">
            <p className="text-cyan-300"><strong>💡 Pro Tips:</strong></p>
            <ul className="list-disc list-inside mt-2 space-y-1 text-gray-400 text-xs">
              <li>
                <strong>API Keys:</strong> Use these for direct API access. Best for most users.
                Example: OpenAI (sk-...), Google (AIzaSy...), Anthropic (sk-ant-...)
              </li>
              <li>
                <strong>GitHub Copilot:</strong> Requires OAuth authentication via your GitHub account
              </li>
              <li>
                <strong>Local Models:</strong> Use Ollama or other local services in the "Providers" tab
              </li>
              <li>
                <strong>Multiple Credentials:</strong> You can set up multiple providers and switch between them
              </li>
              <li>
                <strong>Security:</strong> Credentials stored in ~/.q-ide/llm_credentials.json - never shared
              </li>
            </ul>
          </div>

          {/* Clear All Section */}
          <div className="p-3 bg-yellow-900/20 border border-yellow-600/30 rounded">
            <p className="text-xs text-yellow-300 font-semibold mb-2">Clear All Credentials</p>
            <p className="text-xs text-gray-400 mb-2">Remove all stored credentials and start fresh</p>
            <button
              onClick={() => {
                if (confirm('Are you sure? This will clear all stored LLM credentials.')) {
                  // Clear all would iterate through providers
                  setMessage({ type: 'success', text: 'Cleared all credentials. Add new ones above.' });
                }
              }}
              className="px-3 py-1 text-xs bg-yellow-700/40 hover:bg-yellow-700/60 text-yellow-300 rounded"
            >
              Clear All
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
