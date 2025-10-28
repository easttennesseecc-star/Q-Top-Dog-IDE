import React from 'react';
import useBackground from '../hooks/useBackground';

const PREVIEW_PRESETS = [
  { kind: 'gradient', label: 'Subtle Gradient' },
  { kind: 'animated', label: 'Animated Gradient' },
  { kind: 'particles', label: 'Particles' },
  { kind: 'starfield', label: 'Starfield' },
  { kind: 'nebula', label: 'Nebula' },
];

export default function BackgroundPreviewModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [setting, setSetting] = useBackground();
  const modalRef = React.useRef<HTMLDivElement | null>(null);
  const firstFocusable = React.useRef<HTMLElement | null>(null);
  const lastFocusable = React.useRef<HTMLElement | null>(null);
  // focus trap
  React.useEffect(() => {
    if (!open) return;
    const prev = document.activeElement as HTMLElement | null;
    const el = modalRef.current;
    if (!el) return;
    const focusable = el.querySelectorAll<HTMLElement>('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
    if (focusable.length > 0) {
      firstFocusable.current = focusable[0];
      lastFocusable.current = focusable[focusable.length - 1];
      firstFocusable.current.focus();
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') { onClose(); }
      if (e.key === 'Tab') {
        if (focusable.length === 0) { e.preventDefault(); return; }
        if (e.shiftKey) {
          if (document.activeElement === firstFocusable.current) {
            lastFocusable.current?.focus();
            e.preventDefault();
          }
        } else {
          if (document.activeElement === lastFocusable.current) {
            firstFocusable.current?.focus();
            e.preventDefault();
          }
        }
      }
    }
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('keydown', onKey);
      prev?.focus();
    };
  }, [open, onClose]);

  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 grid place-items-center" role="dialog" aria-modal="true" aria-labelledby="bg-preview-title">
      <div className="absolute inset-0 bg-black/60" onClick={onClose} />
      <div ref={modalRef} className="relative w-[760px] max-w-[94%] bg-[#071021]/80 border border-white/6 rounded-lg p-4 glass panel-elevated">
        <div className="flex items-center justify-between mb-3">
          <h3 id="bg-preview-title" className="text-lg font-semibold text-cyan-200">Background Presets</h3>
          <button onClick={onClose} aria-label="Close preview" className="btn-secondary">Close</button>
        </div>
        <div className="grid grid-cols-3 gap-3">
          {PREVIEW_PRESETS.map(p => (
            <button key={p.kind} onClick={() => { setSetting({ kind: p.kind as any }); }} className="p-3 bg-black/10 border border-white/6 rounded-lg flex flex-col items-center gap-2">
              <div className="w-full h-24 rounded bg-gradient-to-br from-slate-800 to-slate-900" aria-hidden />
              <div className="text-sm text-slate-200">{p.label}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
