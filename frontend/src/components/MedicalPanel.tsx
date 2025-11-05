import React, { useState } from 'react';

export default function MedicalPanel() {
  const [json, setJson] = useState<string>('');
  const [result, setResult] = useState<any>(null);
  const backendBase = (window as any).__VITE_BACKEND_URL || '';
  const toApi = (p: string) => `${String(backendBase).replace(/\/$/, '')}${p.startsWith('/')? p : '/'+p}`;

  const callApi = async (path: string, body: any) => {
    try {
      const res = await fetch(toApi(path), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      const j = await res.json();
      setResult(j);
    } catch (e:any) { setResult({ error: e?.message || String(e) }); }
  };

  return (
    <div className="space-y-4">
      <div className="text-sm text-cyan-200 font-semibold">Medical Tools</div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-black/20 border border-white/5 rounded-lg p-3 space-y-2">
          <div className="text-xs text-slate-300/80">FHIR/OMOP Translation</div>
          <textarea className="w-full h-32 bg-white/5 border border-white/10 rounded p-2 text-xs text-slate-100"
            placeholder="Paste FHIR bundle JSON or OMOP JSON" value={json} onChange={(e)=>setJson(e.target.value)} />
          <div className="flex gap-2">
            <button className="rounded bg-cyan-500 text-[#071018] text-xs font-semibold px-3 py-1" onClick={()=>{
              let obj:any = {}; try{ obj = JSON.parse(json||'{}'); }catch{ }
              callApi('/med/interop/fhir/to-omop', obj);
            }}>FHIR ➜ OMOP</button>
            <button className="rounded bg-white/10 text-slate-100 text-xs font-semibold px-3 py-1" onClick={()=>{
              let obj:any = {}; try{ obj = JSON.parse(json||'{}'); }catch{ }
              callApi('/med/interop/omop/to-fhir', { data: obj });
            }}>OMOP ➜ FHIR</button>
          </div>
        </div>

        <div className="bg-black/20 border border-white/5 rounded-lg p-3 space-y-2">
          <div className="text-xs text-slate-300/80">Narrative Diagnostic</div>
          <div className="flex gap-2">
            <button className="rounded bg-cyan-500 text-[#071018] text-xs font-semibold px-3 py-1" onClick={()=>{
              let obj:any = {}; try{ obj = JSON.parse(json||'{}'); }catch{ }
              callApi('/med/diagnostic/narrative', { fhir: obj, reading_level: 'patient-friendly' });
            }}>From FHIR</button>
            <button className="rounded bg-white/10 text-slate-100 text-xs font-semibold px-3 py-1" onClick={()=>{
              callApi('/med/diagnostic/narrative', { text: json, reading_level: 'patient-friendly' });
            }}>From Text</button>
          </div>
        </div>

        <div className="bg-black/20 border border-white/5 rounded-lg p-3 space-y-2 md:col-span-2">
          <div className="text-xs text-slate-300/80">Virtual Trial Simulator</div>
          <button className="rounded bg-cyan-500 text-[#071018] text-xs font-semibold px-3 py-1" onClick={()=>{
            const design = {
              title: 'Example Trial', population_size: 100, duration_days: 30,
              arms: [ { name: 'control', size: 50, effect_mean: 0, effect_std: 1 }, { name: 'treatment', size: 50, effect_mean: 0.4, effect_std: 1 } ]
            };
            callApi('/med/trials/simulate', design);
          }}>Run Example Trial</button>
        </div>
      </div>

      {result && (
        <pre className="bg-black/30 border border-white/5 rounded p-3 text-xs text-slate-200 overflow-auto max-h-64">{JSON.stringify(result, null, 2)}</pre>
      )}
    </div>
  );
}
