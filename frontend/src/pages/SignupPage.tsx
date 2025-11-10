import React, { useState } from 'react';
import { register, login, storeToken } from '../services/authClient';

export const SignupPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (password !== confirm) {
      setError('Passwords do not match');
      return;
    }
    setLoading(true);
    try {
      const username = email.split('@')[0];
      const reg = await register(email, username, password);
      if (!reg.success) {
        setError(reg.error || 'Signup failed');
      } else {
        // Auto-login after registration
        const resp = await login(email, password);
        if (!resp.success || !resp.data) {
          setError(resp.error || 'Login failed after signup');
        } else {
          storeToken(resp.data.token);
          window.location.href = '/app/viewer';
        }
      }
    } catch (e: any) {
      setError(e?.message ?? 'Signup failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen grid place-items-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-200 p-6">
      <form onSubmit={submit} className="w-full max-w-md bg-slate-900/70 border border-slate-700/40 rounded-xl p-6 space-y-4">
        <h1 className="text-2xl font-bold text-cyan-300">Create your account</h1>
        <p className="text-sm text-slate-400">Start using AI-native development tools</p>
        {error && <div className="text-sm text-red-300 bg-red-900/20 border border-red-700/40 p-2 rounded">{error}</div>}
        <label className="block text-sm">
          <span className="block mb-1 text-slate-300">Email</span>
          <input type="email" required value={email} onChange={e=>setEmail(e.target.value)} className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500" placeholder="you@example.com" />
        </label>
        <label className="block text-sm">
          <span className="block mb-1 text-slate-300">Password</span>
          <input type="password" required value={password} onChange={e=>setPassword(e.target.value)} className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500" placeholder="••••••••" />
        </label>
        <label className="block text-sm">
          <span className="block mb-1 text-slate-300">Confirm Password</span>
          <input type="password" required value={confirm} onChange={e=>setConfirm(e.target.value)} className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500" placeholder="••••••••" />
        </label>
        <button type="submit" disabled={loading} className="w-full py-2 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-semibold disabled:opacity-60">{loading? 'Creating…':'Sign up'}</button>
        <div className="text-xs text-slate-400 text-center">Already have an account? <a href="/login" className="text-cyan-300 hover:text-cyan-200">Sign in</a></div>
      </form>
    </div>
  );
};

export default SignupPage;
