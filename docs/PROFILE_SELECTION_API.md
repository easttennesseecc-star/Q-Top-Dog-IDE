# Runtime Profile Selection API

Let users choose between Dev and Regulated experiences at runtime. Edition affects verification, triads, banners, and disclaimers.

## Endpoints

- GET /ui/edition
  - Returns: `{ "edition": "dev" | "regulated" }`
  - Resolution order: `X-Edition` header → `td_edition` cookie → `ENABLE_REGULATED_DOMAINS` env

- POST /ui/edition
  - Body: `{ "edition": "dev" | "regulated" }`
  - Sets a `td_edition` cookie (SameSite=Lax) and returns the current edition

- GET /ui/banner
  - Returns: `{ "edition": "dev|regulated", "text": string, "style": "info"|"warning" }`
  - Env-configurable texts: `BANNER_DEV`, `BANNER_REGULATED`

## Chat routing behavior

- `backend/llm_chat_routes.py` checks per-request edition:
  - Header `X-Edition: dev|regulated` overrides cookie/env
  - Regulated mode can require Overwatch (`REQUIRE_OVERWATCH=true`) and block on failures (`BLOCK_ON_OVERWATCH_FAIL=true`)
  - Disclaimer appended via `FORCE_DISCLAIMER_TEXT`

## Example frontend usage

```ts
// Fetch current edition and banner
const ed = await fetch('/ui/edition').then(r => r.json());
const banner = await fetch('/ui/banner').then(r => r.json());

// Switch edition on user selection
await fetch('/ui/edition', {
  method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ edition: 'regulated' })
});

// Send edition along with chat requests (optional, cookie already set)
await fetch('/api/chat', {
  method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Edition': ed.edition },
  body: JSON.stringify({ message: 'Hello' })
});
```

Render a top-of-app banner for `banner.text` with a color by `banner.style`.
