import { useEffect, useState } from 'react';

export type ModelInfo = {
  id: string;
  name: string;
  source?: 'local' | 'remote';
  metadata?: Record<string, any>;
};

const STORAGE_KEY = 'topdog:selected_model';

export function getSelectedModel(): ModelInfo | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as ModelInfo;
  } catch (e) {
    console.warn('useModelResolver: failed to parse selected model', e);
    return null;
  }
}

export function setSelectedModel(m: ModelInfo | null) {
  try {
    if (m === null) {
      localStorage.removeItem(STORAGE_KEY);
    } else {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(m));
    }
    // Notify same-window listeners
    try {
      window.dispatchEvent(new CustomEvent('topdog:selected-model', { detail: m }));
    } catch (_) {
      // ignore
    }
  } catch (e) {
    console.warn('useModelResolver: failed to persist selected model', e);
  }
}

/**
 * React hook exposing the selected model and a setter.
 * Keeps state in sync across tabs (storage event) and same-window updates.
 */
export function useSelectedModel(): [ModelInfo | null, (m: ModelInfo | null) => void] {
  const [model, setModel] = useState<ModelInfo | null>(() => getSelectedModel());

  useEffect(() => {
    const onStorage = (e: StorageEvent) => {
      if (e.key === STORAGE_KEY) {
        setModel(getSelectedModel());
      }
    };

    const onCustom = (ev: Event) => {
      const ce = ev as CustomEvent<ModelInfo | null>;
      if (ce && 'detail' in ce) setModel(ce.detail ?? null);
    };

    window.addEventListener('storage', onStorage);
    window.addEventListener('topdog:selected-model', onCustom as EventListener);
    return () => {
      window.removeEventListener('storage', onStorage);
      window.removeEventListener('topdog:selected-model', onCustom as EventListener);
    };
  }, []);

  const setAndPersist = (m: ModelInfo | null) => {
    setSelectedModel(m);
    setModel(m);
  };

  return [model, setAndPersist];
}

// Convenience: expose a small resolver that prefers local models when provided a list.
export function resolvePreferredModel(available: ModelInfo[] = []): ModelInfo | null {
  const selected = getSelectedModel();
  if (selected) return selected;
  // prefer local sources
  const local = available.find((m) => m.source === 'local');
  if (local) return local;
  return available.length ? available[0] : null;
}

export default useSelectedModel;
