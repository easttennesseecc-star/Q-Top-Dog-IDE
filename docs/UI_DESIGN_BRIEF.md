# UI Design Brief – World‑Class, Next‑Level

Principles
- Clarity first: minimal cognitive load, strong hierarchy, progressive disclosure
- Speed everywhere: sub‑100ms interactions where possible, optimistic UI patterns
- Cohesive system: design tokens, responsive grid, dark/light, accessible contrast
- Delight with restraint: purposeful motion and micro‑interactions

Core Requirements
- Design system with tokens (color, type, spacing) and component library
- Keyboard‑first workflows and command palette
- Real‑time presence (avatars, cursors, selection highlights)
- Diff/merge UX for collaboration conflicts
- Streaming AI UX (typewriter, partial tokens, cancel/retry)
- Agent UX (status, approvals, logs timeline, safety banners)
- Error states with actionable recovery, not dead‑ends

Performance Budgets
- First contentful paint < 1.5s on mid‑tier devices
- Interactive under 2.5s; route changes < 300ms
- JS bundle budget < 200KB (initial), code‑split aggressively

Accessibility
- WCAG 2.1 AA minimum; prefers‑reduced‑motion support
- Full keyboard nav; visible focus rings; screen reader labels

Tooling & Stack
- React + Vite + TypeScript
- Component library with radix‑primitives + tailwind or CSS vars
- State: RTK Query or TanStack Query for data fetching; WebSocket for presence
- E2E tests for critical flows (Playwright)

Validation
- Usability test scripts for 5 core tasks (auth, open project, edit + chat, run agent, pay)
- Performance profiles on low‑spec hardware
- Accessibility audits (axe, Lighthouse)
