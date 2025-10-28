import { useEffect, useState } from 'react';

export function KubePanel() {
  const [contexts, setContexts] = useState<any[]>([]);
  const [current, setCurrent] = useState<string | null>(null);
  const [pods, setPods] = useState<any[]>([]);
  const [ns, setNs] = useState('default');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function fetchContexts() {
    setLoading(true); setError(null);
    try {
      const res = await fetch('/api/kube/contexts');
      if (!res.ok) throw new Error(await res.text());
      const j = await res.json();
      setContexts(j.contexts || []);
      setCurrent(j['currentContext'] || j['current-context'] || null);
    } catch (e:any) {
      setError(e.message || String(e));
    } finally { setLoading(false); }
  }
  async function fetchPods() {
    setLoading(true); setError(null);
    try {
      const res = await fetch('/api/kube/pods?namespace=' + encodeURIComponent(ns));
      if (!res.ok) throw new Error(await res.text());
      const j = await res.json();
      setPods((j.items || []).map((p:any) => ({ name: p.metadata.name, status: p.status.phase })));
    } catch (e:any) {
      setError(e.message || String(e));
    } finally { setLoading(false); }
  }

  useEffect(() => { fetchContexts(); fetchPods(); }, []);

  const [sampleMode, setSampleMode] = useState(false);
  async function fetchInfo() {
    try {
      const res = await fetch('/api/kube/info');
      if (!res.ok) return;
      const j = await res.json();
      setSampleMode(Boolean(j.sampleMode));
    } catch (e) {
      // ignore
    }
  }

  useEffect(() => { fetchInfo(); }, []);

  return (
    <div className="p-2 bg-[#23272e] rounded-md border border-cyan-900/20 text-cyan-100">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-bold">Kubernetes</h3>
        <div className="flex items-center gap-2">
          {sampleMode && <div className="text-xs text-yellow-300 font-semibold px-2 py-1 bg-yellow-900/10 rounded">Sample mode</div>}
          <div className="text-xs text-gray-400">{loading ? 'Loading…' : 'Ready'}</div>
        </div>
      </div>
      {error && <div className="text-red-400 text-sm mb-2">{error}</div>}
      <div className="mb-2">
        <div className="text-xs text-gray-400 mb-1">Contexts</div>
        <ul className="list-disc ml-4 text-sm">
          {contexts.map((c:any) => <li key={c.name} className={c.name===current? 'text-cyan-300 font-semibold':'text-gray-200'}>{c.name}</li>)}
          {contexts.length===0 && <li className="text-gray-400 text-sm">No contexts found</li>}
        </ul>
      </div>
      <div className="mb-2">
        <div className="flex items-center gap-2 mb-1">
          <div className="text-xs text-gray-400">Pods ({ns})</div>
          <input value={ns} onChange={e=>setNs(e.target.value)} className="bg-[#1e2128] text-cyan-200 px-2 py-1 rounded text-sm" />
          <button onClick={fetchPods} className="ml-auto px-2 py-1 bg-cyan-900/30 text-cyan-200 rounded text-sm">Refresh</button>
        </div>
        <ul className="text-sm">
          {pods.map(p=> <li key={p.name} className="mb-1">{p.name} <span className="text-gray-400 ml-2">{p.status}</span></li>)}
          {pods.length===0 && <li className="text-gray-400">No pods</li>}
        </ul>
      </div>
    </div>
  );
}

export default KubePanel;
