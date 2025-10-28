# Background Manager — Product Breakdown & Readiness

Generated: 2025-10-25

## Overview

The Background Manager provides configurable, premium, GPU-friendly backgrounds for the Top Dog UI. It supports a local-first experience and stores user choices in browser localStorage. Key capabilities implemented:

- Preset backgrounds: Subtle Gradient (default), Animated Gradient, Particles (floaters), Starfield, Nebula (layered gradients), Blurred Photo (user upload).
- Live preview & selection via Settings → Background and a quick Preview modal.
- Persistence & sync: `topdog:background` in localStorage; updates propagate via Storage events and same-window custom events.
- Performance: Canvas-based renderer (`BackgroundCanvas`) for particles/starfield/nebula to scale to high particle counts. Particle density control available in Settings (range clamped for safety).
- Export/Import and Reset: Download / upload background JSON and reset to default from Settings.

## User flows

1. User opens Settings → Background.
2. User selects a preset (gradient, animated, particles, starfield, nebula) or chooses "Blurred Photo" and uploads an image.
3. Background updates immediately. Uploads are stored as data-URLs in localStorage for offline convenience.
4. User may adjust particle density (slider), preview presets via the Preview modal, export the current background JSON, import a settings file, or reset to default.

## Technical summary

- Files added/modified
  - `src/hooks/useBackground.ts` — persisted background settings, cross-tab sync, typed BackgroundKind.
  - `src/components/BackgroundManager.tsx` — top-level background connector, decides which renderer to show.
  - `src/components/BackgroundCanvas.tsx` — canvas-based renderer for particles, starfield, nebula.
  - `src/components/BackgroundSettings.tsx` — settings UI: presets, uploader, particle slider, export/import, reset, preview button.
  - `src/components/BackgroundPreviewModal.tsx` — preset preview modal.
  - `src/components/BackgroundManager.tsx` — wired into `App.tsx` to render behind the app.
  - `src/App.css` — CSS for background variants, noise overlay, preview modal styles.

- Data/storage model
  - Key: `topdog:background`
  - Shape (example):
    ```json
    { "kind": "image", "imageUrl": "data:image/png;base64,..." }
    ```

- APIs/Events
  - `window.dispatchEvent(new CustomEvent('topdog:background', { detail }))` for same-window updates
  - `storage` event used for cross-tab sync

## Product readiness (high-level)

Readiness is rated on a 1–5 scale where 5 is production-ready.

- UX completeness: 4/5
  - Presets, preview modal, and uploader implemented. Export/import and reset are present.
  - Could be improved with richer preset thumbnails and in-app gallery.

- Performance & scalability: 4/5
  - Canvas-based renderer significantly improves rendering performance for tens to low hundreds of particles.
  - Further optimization available: WebGL fallback, texture atlases, and particle pooling for high counts (>500).

- Accessibility: 3/5
  - Basic keyboard focus/aria present (Settings panel uses normal controls). The preview modal should add focus trapping and better ARIA labels for full accessibility compliance.

- Stability & QA: 4/5
  - Production build passed in this workspace. HMR used for development.
  - Needs cross-browser testing (Safari, iOS) and memory testing for large uploaded images.

- Security & Privacy: 4/5
  - Uploaded images are stored locally (data-URL). This is privacy-friendly but may exhaust localStorage on large images. Option to store compressed images or request remote storage can be added.

- Integration readiness: 5/5
  - The background manager is self-contained and wired into `App.tsx`. Hooks are small and easily callable by other UI components.

Overall readiness: 4/5 — production-quality for desktop/web with recommended follow-ups for accessibility and optional WebGL fallback for mobile/very-high-particle targets.

## Product ratings (summary)

- UX: 4/5 — clean, purposeful controls. Add nicer thumbnails and more palettes for 5/5.
- Performance: 4/5 — Canvas renderer in place. Add WebGL fallback for 5/5.
- Accessibility: 3/5 — needs focus management and ARIA improvements.
- Documentation: 4/5 — this document + inline comments. Add an end-user help modal for 5/5.
- Security/Privacy: 4/5 — local-only by default; consider compression or opt-in remote storage for large images.

## Risks & mitigations

- Large data-URL images may fill localStorage. Mitigation: compress images before storing, or limit size and offer remote upload.
- High particle counts on low-end devices could cause slowdowns. Mitigation: clamp counts, provide mobile-safe preset, or use WebGL.
- Accessibility gaps (modal focus trap / screen reader labels). Mitigation: add role="dialog", focus trap, and ARIA labels in a follow-up.

## Next steps (recommended roadmap)

1. Accessibility pass (2 days) — add focus trap & ARIA for Preview modal and settings controls.
2. Image handling improvements (1–2 days) — client-side compression before storing; file size limit & UX messaging.
3. WebGL fallback (3–5 days) — optional for starfield/nebula for high particle counts and smoother animation on mobile.
4. Preset gallery (1–2 days) — add thumbnail library, color palettes, and save-as-favorite.
5. Integration tests & Cross-browser QA (1–3 days) — test Chrome, Edge, Firefox, Safari on desktop and mobile.

Total estimated work to fully polish: 1–2 developer-weeks (depends on WebGL scope and testing thoroughness).

## How to use (dev notes)

- To change background from console:
  ```js
  localStorage.setItem('topdog:background', JSON.stringify({kind:'animated'}));
  window.dispatchEvent(new Event('topdog:background'));
  ```

- Export / import: Settings → Background → Export/Import.

## Acceptance criteria (what 'done' looks like)

- Users can choose a preset and see immediate changes.
- Uploaded images show as blurred background and persist across reloads.
- Particle density slider changes canvas rendering in real time and respects device limits.
- Export/import round-trips background JSON settings without data loss.

## Implementation notes for reviewers

- Keep `useBackground` minimal and synchronous (localStorage-based) — this keeps state readable server-side if needed.
- Consider moving heavy image processing to a WebWorker if compression is added.

---
If you'd like, I can commit an additional `README` snippet, a short changelog entry, or wire the accessibility changes next. Which would you like me to do?
