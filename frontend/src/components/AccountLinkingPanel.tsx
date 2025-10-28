import React, { useState, useEffect } from 'react';

interface LinkedAccount {
  provider: string;
  provider_user: string;
  scope: string;
}

interface AccountLinkingPanelProps {
  sessionId?: string;
}

export const AccountLinkingPanel: React.FC<AccountLinkingPanelProps> = ({ sessionId }) => {
  const [linkedAccounts, setLinkedAccounts] = useState<LinkedAccount[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const BACKEND_URL = import.meta.env?.VITE_BACKEND_URL || 'http://127.0.0.1:8000';

  const fetchLinkedAccounts = async () => {
    if (!sessionId) return;
    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/auth/status?session_id=${sessionId}`);
      const data = await response.json();
      if (data.status === 'authenticated') {
        const accounts = Object.entries(data.linked_accounts || {}).map(([provider, info]: [string, any]) => ({
          provider,
          provider_user: info.provider_user,
          scope: info.scope || '',
        }));
        setLinkedAccounts(accounts);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch linked accounts';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLinkedAccounts();
  }, [sessionId]);

  const handleLinkAccount = (provider: string) => {
    if (!sessionId) {
      setError('Please sign in first');
      return;
    }

    const startUrl = provider === 'github'
      ? `${BACKEND_URL}/auth/github/start?session_id=${sessionId}`
      : `${BACKEND_URL}/auth/google/start`;

    const popup = window.open(startUrl, `${provider}-link`, 'width=500,height=600');

    const listener = (event: MessageEvent) => {
      if (event.origin !== window.location.origin) return;

      if (event.data?.type === `${provider}-link-success`) {
        window.removeEventListener('message', listener);
        popup?.close();
        fetchLinkedAccounts();
      } else if (event.data?.type === `${provider}-link-error`) {
        window.removeEventListener('message', listener);
        popup?.close();
        setError(event.data.error);
      }
    };

    window.addEventListener('message', listener);

    const checkPopup = setInterval(() => {
      if (popup?.closed) {
        clearInterval(checkPopup);
        window.removeEventListener('message', listener);
      }
    }, 1000);
  };

  const availableProviders = ['github', 'openai', 'anthropic'];
  const linkedProviders = linkedAccounts.map(acc => acc.provider);
  const unlinkedProviders = availableProviders.filter(p => !linkedProviders.includes(p));

  return (
    <div className="flex flex-col gap-4 p-4 bg-gray-50 rounded-lg">
      <h3 className="text-lg font-semibold">Linked Accounts</h3>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      {linkedAccounts.length > 0 && (
        <div className="space-y-2">
          {linkedAccounts.map((account) => (
            <div key={account.provider} className="flex items-center justify-between p-2 bg-white rounded">
              <div>
                <p className="font-medium capitalize">{account.provider}</p>
                <p className="text-sm text-gray-600">{account.provider_user}</p>
              </div>
              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">Connected</span>
            </div>
          ))}
        </div>
      )}

      {unlinkedProviders.length > 0 && (
        <div>
          <p className="text-sm text-gray-600 mb-2">Connect additional providers:</p>
          <div className="space-y-2">
            {unlinkedProviders.map((provider) => (
              <button
                key={provider}
                onClick={() => handleLinkAccount(provider)}
                disabled={loading}
                className="w-full px-3 py-2 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 disabled:bg-gray-400"
              >
                + Link {provider.charAt(0).toUpperCase() + provider.slice(1)}
              </button>
            ))}
          </div>
        </div>
      )}

      {linkedAccounts.length > 0 && unlinkedProviders.length === 0 && (
        <p className="text-sm text-gray-600">All providers are connected.</p>
      )}
    </div>
  );
};
