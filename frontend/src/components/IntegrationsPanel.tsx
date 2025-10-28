import { useEffect, useState } from 'react'

export default function IntegrationsPanel({ onClose }: { onClose: () => void }) {
  const [provider, setProvider] = useState<'github'|'openai'>('github')
  const [token, setToken] = useState('')
  const [status, setStatus] = useState<string | null>(null)
  const [savedMask, setSavedMask] = useState<string | null>(null)

  const backend = (typeof window !== 'undefined' && (window as any).__VITE_BACKEND_URL) || import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000'

  useEffect(() => {
    // fetch current token mask
    fetch(`${backend}/auth/token/${provider}`).then(r => r.json()).then(j => {
      if (j?.status === 'ok') setSavedMask(j.token_masked)
      else setSavedMask(null)
    }).catch(() => setSavedMask(null))
  }, [provider])

  const save = async () => {
    setStatus('validating')
    try {
      const v = await fetch(`${backend}/auth/token/validate`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, token }),
      }).then(r => r.json())
      if (v?.status === 'ok') {
        await fetch(`${backend}/auth/token/pat`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ provider, token }) })
        setStatus('saved')
        setSavedMask(token.slice(0,6) + '...' + token.slice(-4))
        setToken('')
      } else {
        setStatus('error: ' + JSON.stringify(v))
      }
    } catch (e:any) {
      setStatus('error: ' + e?.message)
    }
  }

  const removeToken = async () => {
    await fetch(`${backend}/auth/token/${provider}`, { method: 'DELETE' })
    setSavedMask(null)
    setStatus('removed')
  }

  return (
    <div className="p-4 bg-[#071226]/95 border-2 border-cyan-700 rounded-2xl shadow-2xl text-cyan-200 w-96">
      <div className="flex items-center justify-between mb-3">
        <div className="text-lg font-semibold">Integrations</div>
        <button aria-label="close-integrations" onClick={onClose} className="px-2 py-1 bg-red-600 rounded">Close</button>
      </div>
      <div className="mb-2">
        <label className="text-sm">Provider</label>
        <select value={provider} onChange={e => setProvider(e.target.value as any)} className="w-full p-2 rounded bg-[#0f1720]/60">
          <option value="github">GitHub (PAT)</option>
          <option value="openai">OpenAI (API Key)</option>
        </select>
      </div>
      <div className="mb-2 text-sm">Current: {savedMask ?? <em>not connected</em>}</div>
      <div className="mb-2">
        <label className="text-sm">Paste token</label>
        <input aria-label="integration-token" value={token} onChange={e => setToken(e.target.value)} className="w-full p-2 rounded bg-[#0f1720]/60" />
      </div>
      <div className="flex gap-2">
        <button aria-label="save-integration" onClick={save} className="btn-primary">Validate & Save</button>
        <button aria-label="remove-integration" onClick={removeToken} className="btn-secondary">Remove</button>
      </div>
      {status && <div className="mt-3 text-sm">{status}</div>}
      <div className="mt-3 text-xs text-gray-400">Note: Stored locally for development only. Do not paste production secrets here.</div>
    </div>
  )
}
