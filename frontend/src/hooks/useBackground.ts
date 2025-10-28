import { useEffect, useState } from 'react';
import { registerBlobId } from '../lib/idbStorage';

export type BackgroundKind = 'gradient' | 'animated' | 'particles' | 'image' | 'video' | 'starfield' | 'nebula' | 'palette';
export type BackgroundSetting = {
  kind: BackgroundKind;
  // For large media we store blobs in IndexedDB and reference them by id here.
  imageBlobId?: string | null;
  videoBlobId?: string | null;
  // legacy small data-url preview (kept for migration/fallback)
  imagePreviewUrl?: string | null;
  particleCount?: number; // optional particle count for particle-based backgrounds
  // optional visual tweak
  imageBlur?: boolean;
  lowPowerMode?: boolean;
};

const STORAGE_KEY = 'topdog:background';

export function getBackgroundSetting(): BackgroundSetting {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { kind: 'gradient', particleCount: 12 };
    const parsed = JSON.parse(raw) as any as BackgroundSetting;
    // migrate legacy imageUrl to imagePreviewUrl
    if ((parsed as any).imageUrl && !parsed.imagePreviewUrl) {
      parsed.imagePreviewUrl = (parsed as any).imageUrl;
      delete (parsed as any).imageUrl;
    }
  if (parsed.particleCount == null) parsed.particleCount = 18;
  if (parsed.imageBlur == null) parsed.imageBlur = true;
  if (parsed.lowPowerMode == null) parsed.lowPowerMode = false;
    return parsed;
  } catch (e) {
    console.warn('useBackground: parse failed', e);
    return { kind: 'gradient', particleCount: 18, imageBlur: true, lowPowerMode: false };
  }
}

// Preset profiles used by the UI
export const PARTICLE_PRESETS = {
  low: { label: 'Low', count: 12 },
  medium: { label: 'Medium', count: 48 },
  high: { label: 'High', count: 160 },
} as const;

export function setBackgroundSetting(s: BackgroundSetting) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
    try { window.dispatchEvent(new CustomEvent('topdog:background', { detail: s })); } catch (_) {}
  } catch (e) {
    console.warn('useBackground: persist failed', e);
  }
}

export default function useBackground(): [BackgroundSetting, (s: BackgroundSetting) => void] {
  const [setting, setSetting] = useState<BackgroundSetting>(() => getBackgroundSetting());

  useEffect(() => {
    const onStorage = (e: StorageEvent) => {
      if (e.key === STORAGE_KEY) setSetting(getBackgroundSetting());
    };
    const onCustom = (ev: Event) => {
      const ce = ev as CustomEvent<BackgroundSetting>;
      if (ce && 'detail' in ce) setSetting(ce.detail);
    };
    window.addEventListener('storage', onStorage);
    window.addEventListener('topdog:background', onCustom as EventListener);
    return () => {
      window.removeEventListener('storage', onStorage);
      window.removeEventListener('topdog:background', onCustom as EventListener);
    };
  }, []);

  const setAndPersist = (s: BackgroundSetting) => {
    setBackgroundSetting(s);
    // register any referenced blobs
    if (s.imageBlobId) registerBlobId(s.imageBlobId);
    if (s.videoBlobId) registerBlobId(s.videoBlobId);
    setSetting(s);
  };

  return [setting, setAndPersist];
}
