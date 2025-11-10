import React, { useEffect, useState } from 'react';

type LLMItem = { 
  name?: string; 
  path?: string; 
  pid?: number; 
  source?: string; 
  reason?: string;
  type?: string;
  status?: string;
  endpoint?: string;
  note?: string;
  priority_score?: number;
};

export default function LLMPoolPanel() {
  const [report, setReport] = useState<{ available: LLMItem[]; excluded: LLMItem[] } | null>(null);
  const [best, setBest] = useState<LLMItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<LLMItem | null>(null);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [loadingBest, setLoadingBest] = useState(false);

  useEffect(() => { 
    load();
    loadBest();
  }, []);

  async function load() {
    setLoading(true); setError(null);
    try {
      // Use API-prefixed endpoint defined by backend
      const res = await fetch('/api/llm_pool');
      if (!res.ok) throw new Error(await res.text());
      // Guard against HTML catch-all responses
      const contentType = res.headers.get('content-type') || '';
      if (!contentType.includes('application/json')) {
        const text = await res.text();
        throw new Error(`Unexpected response (not JSON): ${text.slice(0, 120)}...`);
      }
      const j = await res.json();
      setReport({ available: j.available || [], excluded: j.excluded || [] });
    } catch (e:any) {
      setError(e.message || String(e));
    } finally { setLoading(false); }
  }

  async function loadBest() {
    setLoadingBest(true);
    try {
      const res = await fetch('/llm_pool/best?count=3');
      if (!res.ok) throw new Error(await res.text());
      const j = await res.json();
      setBest(j.best || []);
      
      // Auto-select the best LLM if not already selected
      const savedLLM = localStorage.getItem('selectedLLM');
      if (!savedLLM && j.best && j.best.length > 0) {
        // Auto-populate with the best available LLM
        const bestLLM = j.best[0];
        localStorage.setItem('selectedLLM', JSON.stringify(bestLLM));
        localStorage.setItem('llmAutoSelected', 'true');
        
        // Log the auto-selection
        const auditRaw = localStorage.getItem('llmAudit');
        const audit = auditRaw ? JSON.parse(auditRaw) : [];
        audit.push({ 
          at: new Date().toISOString(), 
          action: 'auto_select', 
          model: bestLLM,
          priority_score: bestLLM.priority_score,
          who: 'system' 
        });
        localStorage.setItem('llmAudit', JSON.stringify(audit));
      }
    } catch (e:any) {
      // Silent fail for best LLMs - not critical
      console.warn('Could not load best LLMs:', e.message);
    } finally { setLoadingBest(false); }
  }

  function attemptSelect(item: LLMItem) {
    setSelected(item); setConfirmOpen(true);
  }

  function confirmSelect() {
    if (!selected) return;
    // Write selected to localStorage and append an audit entry
    try {
      localStorage.setItem('selectedLLM', JSON.stringify(selected));
      localStorage.setItem('llmAutoSelected', 'false');
      const auditRaw = localStorage.getItem('llmAudit');
      const audit = auditRaw ? JSON.parse(auditRaw) : [];
      audit.push({ at: new Date().toISOString(), action: 'select', model: selected, who: 'user' });
      localStorage.setItem('llmAudit', JSON.stringify(audit));
    } catch (e) {
      // ignore
    }
    // Persist selection server-side so roles honor it across sessions (default role=coding)
    try {
      fetch('/llm/select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ llm_id: (selected.name || '').toLowerCase(), role: 'coding' })
      }).catch(()=>{});
    } catch {}
    setConfirmOpen(false);
    setSelected(null);
    // small UI feedback: reload report so selected model can be seen as active by other code
    load();
    alert('Selected LLM saved. The app will use the selected local model for local-only operations.');
  }

  return (
    <div className="p-3 bg-[#23272e] rounded-md border border-cyan-900/20 text-cyan-100 w-full max-w-2xl">
      <div className="flex items-center justify-between mb-4">
        <strong className="text-lg">LLM Pool Management</strong>
        <div className="text-xs text-gray-400">{loading ? 'Loading…' : 'Ready'}</div>
      </div>
      {error && <div className="text-red-400 text-sm mb-3 p-2 bg-red-900/20 rounded">{error}</div>}

      {/* Auto-Selected Best LLMs Section */}
      {best.length > 0 && (
        <div className="mb-4 p-3 bg-green-900/20 border border-green-700/30 rounded-lg">
          <div className="text-xs font-semibold text-green-300 mb-2 flex items-center gap-2">
            <span>✨ Auto-Selected Best Options</span>
            {loadingBest && <span className="text-xs text-gray-400">(loading...)</span>}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
            {best.map((b, idx) => (
              <div key={idx} className="p-2 bg-[#1e2128] border border-green-600/40 hover:border-green-500/60 rounded cursor-pointer transition-all" onClick={() => attemptSelect(b)}>
                <div className="font-semibold text-xs text-green-200">{b.name || b.path || `LLM ${idx+1}`}</div>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs px-1.5 py-0.5 rounded bg-green-700/40 text-green-300">
                    {b.source || 'local'}
                  </span>
                  {b.priority_score !== undefined && (
                    <span className="text-xs text-green-400 font-mono">#{b.priority_score}</span>
                  )}
                </div>
                <div className="text-xs text-gray-400 mt-1 truncate">{b.endpoint || b.path || 'Local'}</div>
              </div>
            ))}
          </div>
          <div className="text-xs text-gray-400 mt-2">Click any option to select it, or choose manually from the list below.</div>
        </div>
      )}

      <div className="mb-4">
        <div className="text-sm font-semibold text-cyan-300 mb-2 flex items-center gap-2">
          <span>Available LLMs</span>
          <span className="text-xs bg-cyan-900/40 px-2 py-0.5 rounded">{report?.available.length || 0}</span>
        </div>
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {report?.available.length ? report!.available.map((a, idx) => {
            const getSourceBadgeColor = (source?: string) => {
              switch(source) {
                case 'vscode': return 'bg-blue-500/20 text-blue-200';
                case 'web': return 'bg-purple-500/20 text-purple-200';
                case 'service': return 'bg-green-500/20 text-green-200';
                case 'process': return 'bg-yellow-500/20 text-yellow-200';
                case 'cli': return 'bg-orange-500/20 text-orange-200';
                default: return 'bg-cyan-500/20 text-cyan-200';
              }
            };
            
            return (
              <div key={idx} className="p-2.5 bg-[#1e2128] hover:bg-[#252d35] rounded border border-white/5 hover:border-cyan-500/30 transition-all">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="font-semibold text-sm text-cyan-100 flex items-center gap-2">
                      {a.name || a.path || `local-${idx}`}
                      {a.priority_score !== undefined && (
                        <span className="text-xs text-gray-400 font-mono bg-gray-800/40 px-1.5 py-0.5 rounded">
                          Priority: {a.priority_score}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2 mt-1 flex-wrap">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${getSourceBadgeColor(a.source)}`}>
                        {a.source || 'unknown'}
                      </span>
                      {a.type && <span className="text-xs text-gray-400">{a.type}</span>}
                      {a.status && <span className="text-xs text-gray-400">• {a.status}</span>}
                    </div>
                    {(a.endpoint || a.path) && (
                      <div className="text-xs text-gray-400 mt-1 truncate">{a.endpoint || a.path}</div>
                    )}
                    {a.note && (
                      <div className="text-xs text-gray-400 italic mt-1">{a.note}</div>
                    )}
                  </div>
                  <button 
                    onClick={() => attemptSelect(a)} 
                    className="px-2 py-1 rounded bg-cyan-700 hover:bg-cyan-600 text-white text-xs flex-shrink-0 transition-colors"
                  >
                    Select
                  </button>
                </div>
              </div>
            );
          }) : <div className="text-gray-400 text-sm">No available assistants found.</div>}
        </div>
      </div>

      <div>
        <div className="text-sm font-semibold text-rose-300 mb-2 flex items-center gap-2">
          <span>Excluded (Critical)</span>
          <span className="text-xs bg-rose-900/40 px-2 py-0.5 rounded">{report?.excluded.length || 0}</span>
        </div>
        <div className="space-y-2 max-h-32 overflow:auto">
          {report?.excluded.length ? report!.excluded.map((e, idx) => (
            <div key={idx} className="p-2 bg-[#1a1f26] rounded border border-rose-900/30 text-sm">
              <div className="font-semibold text-sm text-rose-300">{e.name || e.path || `excluded-${idx}`}</div>
              <div className="text-xs text-gray-400">{e.reason || e.path || ''}</div>
            </div>
          )) : <div className="text-gray-400 text-sm">No excluded critical models.</div>}
        </div>
      </div>

      {/* Confirmation modal */}
      {confirmOpen && selected && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-[#0f1724] p-4 rounded w-[420px] border border-cyan-900/30">
            <h3 className="font-bold mb-2">Confirm selection</h3>
            <p className="text-sm text-gray-300 mb-3">You're about to select <strong>{selected.name || selected.path}</strong> as the local assistant. This will only affect local, user-approved operations and will not call external critical-system models.</p>
            <div className="flex items-center gap-2 mb-3">
              <input id="ack" type="checkbox" onChange={(e)=>{ const btn = document.getElementById('confirm-llm-btn') as HTMLButtonElement; if(btn) btn.disabled = !e.target.checked; }} />
              <label htmlFor="ack" className="text-sm text-gray-300">I understand and opt in to using this local model.</label>
            </div>
            <div className="flex justify-end gap-2">
              <button onClick={()=>{ setConfirmOpen(false); setSelected(null); }} className="px-3 py-1 rounded bg-transparent border border-gray-600 text-gray-200">Cancel</button>
              <button id="confirm-llm-btn" onClick={confirmSelect} disabled className="px-3 py-1 rounded bg-cyan-600 text-white">Confirm</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
