import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { getToken as rawGetToken, storeToken as rawStoreToken, clearToken as rawClearToken, verifyToken } from '../services/authClient';

export interface SafeUserProfile {
  id: string;
  email: string;
  username: string;
  is_founder?: boolean;
  paid?: boolean;
  api_keys_count?: number;
  balance?: {
    available_balance: number;
    total_balance: number;
    spent_balance: number;
  };
  connected_providers?: string[];
}

interface AuthContextShape {
  loading: boolean;
  user: SafeUserProfile | null;
  token: string | null;
  isAuthed: boolean;
  founder: boolean;
  refresh: () => Promise<void>;
  setToken: (tok: string | null) => void;
}

const AuthContext = createContext<AuthContextShape | undefined>(undefined);

const resolveBackend = (): string => {
  const b = (window as any).__VITE_BACKEND_URL || (import.meta as any)?.env?.VITE_BACKEND_URL || (import.meta as any)?.env?.VITE_API_URL || (process as any)?.env?.REACT_APP_BACKEND_URL || '';
  return (b as string).replace(/\/$/, '');
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<SafeUserProfile | null>(null);
  const [token, setTokenState] = useState<string | null>(rawGetToken());

  const setToken = (tok: string | null) => {
    if (tok) rawStoreToken(tok); else rawClearToken();
    setTokenState(tok);
  };

  const refresh = async () => {
    const tok = rawGetToken();
    if (!tok) { setUser(null); setLoading(false); return; }
    const ok = await verifyToken(tok).catch(() => false);
    if (!ok) { setToken(null); setUser(null); setLoading(false); return; }
    try {
      const res = await fetch(`${resolveBackend()}/api/v1/auth/me`, { headers: { Authorization: `Bearer ${tok}` } });
      if (!res.ok) throw new Error('Profile fetch failed');
      const j = await res.json();
      if (j?.success) setUser(j.data as SafeUserProfile);
    } catch (_) {
      /* ignore */
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
    const onMsg = (evt: MessageEvent) => {
      const d = evt.data || {};
      if (d?.type === 'oauth_success' && d?.token) {
        setToken(d.token);
        refresh();
      }
    };
    window.addEventListener('message', onMsg);
    return () => window.removeEventListener('message', onMsg);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const founder = !!user?.is_founder;
  const isAuthed = !!token || !!localStorage.getItem('oauth_session_id');

  const ctx = useMemo<AuthContextShape>(() => ({ loading, user, token, isAuthed, founder, refresh, setToken }), [loading, user, token, isAuthed, founder]);

  return (
    <AuthContext.Provider value={ctx}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const v = useContext(AuthContext);
  if (!v) throw new Error('useAuth must be used within AuthProvider');
  return v;
};
