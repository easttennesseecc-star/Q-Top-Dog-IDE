# Editions and Profiles

To reduce complexity for general software/game development while retaining regulated controls for medical/scientific work, run TopDog IDE as two editions from the same codebase.

## Editions

- Dev Edition (default for software/game dev)
  - ENABLE_REGULATED_DOMAINS=false
  - No domain triads; Overwatch is opt-in via `X-Overwatch-LLM` header
  - Standard CSP/CORS (you can still harden if desired)
  - Simpler UI with fewer compliance prompts
- Regulated Edition (medical/science)
  - ENABLE_REGULATED_DOMAINS=true
  - Domain triads active (MED/SCIENCE_* envs)
  - Overwatch on by default via domain triad/global default
  - Tighter policies, documentation banners and disclaimers

## How to switch editions

1. Set `ENABLE_REGULATED_DOMAINS` in your environment (ConfigMap, dotenv, or container env):
   - Dev Edition: `ENABLE_REGULATED_DOMAINS=false`
   - Regulated Edition: `ENABLE_REGULATED_DOMAINS=true`
2. Optional: remove MED_/SCIENCE_ triads from ConfigMap for Dev Edition to avoid confusion.
3. In Regulated Edition, supply per-domain triads:
   - `MED_PRIMARY_LLM`, `MED_SECONDARY_LLM`, `MED_OVERWATCH_LLM`
   - `SCIENCE_PRIMARY_LLM`, `SCIENCE_SECONDARY_LLM`, `SCIENCE_OVERWATCH_LLM`

## Behavior differences in code

- `backend/llm_chat_routes.py`
  - If `ENABLE_REGULATED_DOMAINS=false`, `X-Domain` is ignored for triads and Overwatch is only applied when explicitly set via `X-Overwatch-LLM`.
  - The legacy `/api/chat/science` route returns 404 when regulated features are disabled.

## K8s guidance

Keep a single base manifest (`k8s/01-configmap.yaml` has `ENABLE_REGULATED_DOMAINS`). For Dev Edition, override it to `false` via environment-specific kustomize/Helm values.

## UI differences

Follow `docs/UI_STYLE_GUIDE.md` for a clean, modern look. In Dev Edition, hide regulated-only menu items and disclaimers; in Regulated Edition, surface domain selection, verification status, and compliance notices.
