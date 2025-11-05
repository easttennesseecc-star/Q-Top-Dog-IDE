# TopDog UI Style Guide

A clean, modern, and functional look that stays readable during long sessions.

## Design tokens

- Colors
  - Primary: #4F46E5 (indigo-600)
  - Accent: #06B6D4 (cyan-500)
  - Success: #10B981 (emerald-500)
  - Warning: #F59E0B (amber-500)
  - Danger: #EF4444 (red-500)
  - Text: #E5E7EB on dark, #111827 on light
  - Background (dark): #0B1220
  - Surface (dark): #111827
- Typography
  - Headings: Inter, 600 weight
  - Body: Inter 400, 14–16px
  - Code: JetBrains Mono / Menlo, 12–13px
- Spacing
  - 4pt grid (4/8/12/16/24/32)
- Radius & elevation
  - Radius: 8px on surfaces; 6px on inputs
  - Shadows: subtle (e.g., rgba(0,0,0,0.2) 0 2px 8px)

## Components

- Buttons: medium radius, solid primary; ghost for secondary; clear focus ring
- Inputs: 1px border, subtle inner shadow, focus ring #06B6D4
- Cards: surface background, 12–16px padding, title + meta actions
- Tables: zebra striping, sticky header, compact density option

## Dark mode first

- Default to dark mode with high-contrast text (#E5E7EB) and muted surfaces
- Support one-click light mode toggle

## Grafana alignment

- Use dark theme, classic palette, seconds and currency units for SLO panels
- Keep panels 12x8 grid-aligned with concise titles

## CSS variables (example)

```css
:root {
  --td-color-primary: #4F46E5;
  --td-color-accent: #06B6D4;
  --td-bg: #0B1220;
  --td-surface: #111827;
  --td-text: #E5E7EB;
  --td-radius: 8px;
}
```

Adopt Tailwind CSS or a component library (Chakra/Material) to accelerate consistent visuals. 