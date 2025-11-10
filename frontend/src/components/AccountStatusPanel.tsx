import React, { useEffect, useState } from 'react';
import { useAuth } from './AuthContext';

interface ApiKeyMeta {
  id: string;
  provider: string;
  status: string;
  created_at: string;
  usage_count: number;
}

export const AccountStatusPanel: React.FC = () => {
  const { user, token, loading: authLoading, founder, refresh } = useAuth();
  const [keys, setKeys] = useState<ApiKeyMeta[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const backendBase = (
    (window as any).__VITE_BACKEND_URL ||
    (import.meta as any)?.env?.VITE_BACKEND_URL ||
    (import.meta as any)?.env?.VITE_API_URL ||
    (process as any)?.env?.REACT_APP_BACKEND_URL ||
    ''
  ) as string;
  const toApi = (path: string) => `${backendBase.replace(/\/$/, '')}${path.startsWith('/')?path:'/'+path}`;

  useEffect(() => {
    const tok = token;
    if (!tok) { setLoading(false); return; }
    const run = async () => {
      try {
        const kRes = await fetch(toApi('/api/v1/auth/api-keys'), { headers: { Authorization: `Bearer ${tok}` } });
        if (kRes.ok) {
          const kJson = await kRes.json();
          if (kJson.success && Array.isArray(kJson.data)) setKeys(kJson.data as ApiKeyMeta[]);
        }
      } catch (e: any) {
        setError(e.message || 'Error loading account status');
      } finally {
        setLoading(false);
      }
    };
    run();
  }, [token]);

  if (loading || authLoading) return (
    <div className="space-y-3 animate-pulse">
      <div className="h-20 rounded-lg bg-white/5 border border-white/10" />
      <div className="h-24 rounded-lg bg-white/5 border border-white/10" />
      <div className="h-28 rounded-lg bg-white/5 border border-white/10" />
    </div>
  );
  if (error) return <div className="text-xs text-red-400">{error}</div>;
  if (!user) return <div className="text-xs text-slate-400">Not signed in.</div>;

  const badge = founder ? 'FOUNDER (bypass active)' : (user.paid ? 'PAID USER' : 'FREE USER');

  const revokeKey = async (key_id: string) => {
    if (!token) return;
    const res = await fetch(toApi('/api/v1/auth/credentials/revoke'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ key_id })
    });
    if (res.ok) {
      // Refresh keys
      setKeys(prev => prev.filter(k => k.id !== key_id));
    }
  };

  const rotateKey = async (key_id: string) => {
    if (!token) return;
    const new_api_key = window.prompt('Enter new API key value:');
    if (!new_api_key) return;
    const res = await fetch(toApi('/api/v1/auth/credentials/rotate'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ key_id, new_api_key })
    });
    if (res.ok) {
      const j = await res.json();
      if (j.success && j.data) {
        setKeys(prev => [j.data as ApiKeyMeta, ...prev.filter(k => k.id !== key_id)]);
      }
    }
  };

  return (
    <div className="space-y-4 text-xs">
      <div className="p-3 rounded-lg border border-white/10 bg-black/20">
        <div className="flex items-center justify-between mb-1">
          <div className="font-semibold text-cyan-200">Account</div>
          {founder && <span className="px-2 py-0.5 rounded bg-gradient-to-r from-cyan-600 to-blue-600 text-[10px] text-white font-semibold">FOUNDER</span>}
        </div>
        <div className="grid grid-cols-2 gap-x-4 gap-y-1">
          <div className="text-slate-400">Email</div><div className="text-slate-200 truncate" title={user.email}>{user.email}</div>
          <div className="text-slate-400">User</div><div className="text-slate-200">{user.username}</div>
          <div className="text-slate-400">Status</div><div className="text-slate-200">{badge}</div>
          <div className="text-slate-400">API Keys</div><div className="text-slate-200">{user.api_keys_count || keys.length}</div>
        </div>
      </div>

      {user.balance && (
        <div className="p-3 rounded-lg border border-white/10 bg-black/10">
          <div className="font-semibold text-cyan-200 mb-1">Balance</div>
          <div className="grid grid-cols-2 gap-x-4 gap-y-1">
            <div className="text-slate-400">Available</div><div className="text-green-300">{founder ? '∞ (bypass)' : user.balance.available_balance.toFixed(2)}</div>
            <div className="text-slate-400">Total</div><div className="text-slate-200">{user.balance.total_balance.toFixed(2)}</div>
            <div className="text-slate-400">Spent</div><div className="text-slate-200">{user.balance.spent_balance.toFixed(2)}</div>
          </div>
        </div>
      )}

      {Array.isArray((user as any).connected_providers) && (
        <div className="p-3 rounded-lg border border-white/10 bg-black/10">
          <div className="font-semibold text-cyan-200 mb-2">Connected Providers</div>
          {!(user as any).connected_providers?.length && <div className="text-slate-400">None</div>}
          <div className="flex flex-wrap gap-2">
            {(user as any).connected_providers?.map((p: string) => (
              <span key={p} className="text-[10px] px-2 py-0.5 rounded bg-slate-700/40 text-slate-200 border border-slate-600/40">{p}</span>
            ))}
          </div>
        </div>
      )}

      <div className="p-3 rounded-lg border border-white/10 bg-black/10">
        <div className="font-semibold text-cyan-200 mb-2">API Keys</div>
        {keys.length === 0 && <div className="text-slate-400">None added</div>}
        <ul className="space-y-1">
          {keys.map(k => (
            <li key={k.id} className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-3">
                <span className="text-slate-300">{k.provider}</span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-slate-700/40 text-slate-200 border border-slate-600/40">{k.status.toUpperCase()}</span>
              </div>
              <div className="flex items-center gap-2">
                <button onClick={() => rotateKey(k.id)} className="text-[10px] px-2 py-0.5 rounded border border-cyan-400/40 text-cyan-200 hover:bg-cyan-500/10">Rotate</button>
                <button onClick={() => revokeKey(k.id)} className="text-[10px] px-2 py-0.5 rounded border border-red-400/40 text-red-200 hover:bg-red-500/10">Revoke</button>
              </div>
            </li>
          ))}
        </ul>
        <div className="mt-2 text-[10px] text-slate-500">Encrypted at rest; plaintext never stored.</div>
      </div>
    </div>
  );
};

export default AccountStatusPanel;
