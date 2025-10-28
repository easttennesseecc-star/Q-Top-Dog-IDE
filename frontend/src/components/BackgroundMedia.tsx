import React, { useEffect, useState } from 'react';
import { getBlob } from '../lib/idbStorage';

export default function BackgroundMedia({ imageBlobId, videoBlobId, previewUrl, blur }: { imageBlobId?: string | null; videoBlobId?: string | null; previewUrl?: string | null; blur?: boolean }) {
  const [objectUrl, setObjectUrl] = useState<string | null>(previewUrl ?? null);

  useEffect(() => {
    let mounted = true;
    let url: string | null = previewUrl ?? null;
    async function load() {
      try {
        if (imageBlobId) {
          const b = await getBlob(imageBlobId);
          if (!mounted) return;
          if (b) {
            url = URL.createObjectURL(b);
            setObjectUrl(url);
          }
        } else if (videoBlobId) {
          const b = await getBlob(videoBlobId);
          if (!mounted) return;
          if (b) {
            url = URL.createObjectURL(b);
            setObjectUrl(url);
          }
        }
      } catch (e) {
        console.warn('BackgroundMedia load failed', e);
      }
    }
    load();
    return () => {
      mounted = false;
      if (url) {
        try { URL.revokeObjectURL(url); } catch (_) {}
      }
    };
  }, [imageBlobId, videoBlobId, previewUrl]);

  if (videoBlobId && objectUrl) {
    return (
      <video
        className="absolute inset-0 w-full h-full object-cover"
        src={objectUrl}
        muted
        autoPlay
        loop
        playsInline
      />
    );
  }

  if (imageBlobId && objectUrl) {
    return (
      <img src={objectUrl} alt="background" className="absolute inset-0 w-full h-full object-cover" style={{ filter: blur ? 'brightness(.78) saturate(.9) blur(.6px)' : 'brightness(.88) saturate(.95)' }} />
    );
  }

  if (previewUrl) {
    return <img src={previewUrl} alt="background-preview" className="absolute inset-0 w-full h-full object-cover" style={{ filter: blur ? 'brightness(.78) saturate(.9) blur(.6px)' : 'brightness(.88) saturate(.95)' }} />;
  }

  return null;
}
