import React, { useEffect, useState } from 'react';
import useBackground, { BackgroundSetting } from '../hooks/useBackground';
import BackgroundCanvas from './BackgroundCanvas';
import BackgroundMedia from './BackgroundMedia';
import { isLowPowerDevice, isMobileDevice } from '../lib/deviceHints';

export default function BackgroundManager() {
  const [setting] = useBackground();
  const [deviceLowPower, setDeviceLowPower] = useState(false);
  const [deviceMobile, setDeviceMobile] = useState(false);
  useEffect(() => {
    setDeviceLowPower(isLowPowerDevice());
    setDeviceMobile(isMobileDevice());
    const t = setInterval(() => {
      setDeviceLowPower(isLowPowerDevice());
    }, 60000);
    return () => clearInterval(t);
  }, []);

  const renderByKind = (s: BackgroundSetting) => {
    switch (s.kind) {
      case 'animated':
        return <div className="bg-animated" />;
      case 'particles':
        return <BackgroundCanvas kind="particles" count={s.particleCount ?? 12} />;
      case 'starfield':
        return <BackgroundCanvas kind="starfield" count={s.particleCount ?? 12} />;
      case 'nebula':
        return <BackgroundCanvas kind="nebula" count={Math.max(12, Math.floor((s.particleCount ?? 12) / 2))} />;
      case 'image':
        return (
          <div className="absolute inset-0">
            <BackgroundMedia imageBlobId={s.imageBlobId} previewUrl={s.imagePreviewUrl ?? undefined} blur={s.imageBlur ?? true} />
          </div>
        );
      case 'video':
        // Respect low-power preference or automatic device heuristics
        if (s.lowPowerMode || deviceLowPower || deviceMobile) {
          // show poster/preview but do not autoplay video
          return (
            <div className="absolute inset-0">
              <BackgroundMedia videoBlobId={s.videoBlobId} previewUrl={s.imagePreviewUrl ?? undefined} blur={false} />
            </div>
          );
        }
        return (
          <div className="absolute inset-0">
            <BackgroundMedia videoBlobId={s.videoBlobId} previewUrl={s.imagePreviewUrl ?? undefined} blur={false} />
          </div>
        );
      case 'gradient':
      default:
        return (
          <>
            <div className="bg-gradient" />
            <div className="bg-noise" />
          </>
        );
    }
  };

  return (
    <div aria-hidden className="fixed inset-0 pointer-events-none -z-10">
      {renderByKind(setting)}
    </div>
  );
}
