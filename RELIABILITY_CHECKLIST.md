# Top Dog vs Copilot: Reliability Checklist

A practical, verifiable list of guardrails that keep Top Dog stable, non‑hallucinatory, and on‑plan.

Use this as a pre‑flight and regression checklist before releases.

---

## 1) Backend reliability

- Health-first endpoint
  - Contract: `/health` responds 200 JSON regardless of canonical redirects/spa routing
  - Implementation: `backend/main.py` (health registered before redirects/compliance and SPA catch‑all)
  - Verify: curl from cluster returns `{ "status": "ok" }`.

- Canonical redirect safety
  - Contract: never redirect internal/local hosts or paths: `/health`, `/metrics`, `/api`, `/ws`, `/_health`, `/readiness`, `/liveness`, `/snapshots`
  - Implementation: Redirect middleware with explicit exemptions (see `CONFIGURATION_REFERENCE.md`)
  - Verify: requests to exempted paths return 2xx without 30x.

- SPA catch‑all ordering
  - Contract: SPA should not shadow API paths (e.g., `/snapshots`, `/auth`, `/llm`)
  - Implementation: Routers added before SPA; snapshot router registered early
  - Verify: hitting `/snapshots/...` returns JSON, not HTML.

- Snapshot rollback fallback
  - Contract: if primary load fails, fallback path still serves latest good version
  - Implementation: snapshot route fallback (see backend route code for snapshots)
  - Verify: simulate bad snapshot; endpoint falls back gracefully (200 + valid payload).

---

## 2) Hallucination prevention

- Guardrails and tests
  - Contract: risky ops require plan/approval; LLM output is validated
  - Reference: `AI_HALLUCINATION_PREVENTION_FRAMEWORK.md`
  - Verify: unit/integration tests assert plan enforcement and validation.

- Multi‑LLM BYOK routing
  - Contract: route to best model/provider; degrade/fallback on provider failure or low quality
  - Implementation: LLM pool + config; supports local models (Ollama)
  - Verify: disable a provider and ensure routing continues via fallback; compare outputs.

---

## 3) Compliance & on‑rails changes

- Compliance middleware returns JSON
  - Contract: structured error responses; health/monitoring exempt
  - Implementation: Middleware wraps responses with JSON error shape
  - Verify: negative tests return JSON, not HTML.

- Build plan enforcement
  - Contract: meaningful changes go through a plan + approval path (prevent off‑rails edits)
  - Implementation: rules/approvals APIs; surfaced in UI
  - Verify: unapproved risky operation is blocked with actionable message.

---

## 4) CI/CD and self‑healing

- CI checks
  - Contract: tests run on PR; best‑effort type/lint
  - Implementation: `.github/workflows/ci.yml`
  - Verify: red/green gates visible; failing tests block merges.

- In‑cluster smoke
  - Contract: post‑deploy check hits `/health` from inside cluster
  - Implementation: kubectl/curl job
  - Verify: smoke job returns 200 JSON; probes remain green.

- Probes + autoscaling
  - Contract: readiness/liveness tuned; HPA & PDB configured
  - Implementation: Helm values/templates
  - Verify: rollout succeeds; pods Ready; disruptions do not take service down.

---

## 5) Phone pairing & notifications

- SMS pairing resiliency
  - Contract: real SMS via Twilio/AWS SNS if configured; otherwise mock mode logs SMS for dev
  - Implementation: `backend/services/sms_pairing_service.py`
  - Verify: env unset -> mock logs; env set + provider SDK -> real sends succeed.

- QR pairing always available
  - Contract: QR path independent of SMS provider availability
  - Implementation: `/phone/pairing/generate-qr`
  - Verify: generate QR succeeds and pairing flow returns JWT.

- Incoming SMS webhook
  - Contract: Twilio-compatible TwiML response at `/phone/sms/webhook`
  - Implementation: `backend/routes/phone_pairing_api.py`
  - Verify: simulator request returns TwiML `<Message>` body.

---

## 6) Frontend UX reliability

- Theme & contrast controls
  - Contract: global dark/light toggle; high‑contrast mode; readable inputs on all backgrounds
  - Implementation: `frontend/src/components/ThemeContext.tsx` + header/Settings UI; pairing CSS enforces readable inputs
  - Verify: toggle works, persists; pairing dialog inputs are legible.

- Command palette & safety affordances
  - Contract: easy access to rules/approval and config panels
  - Implementation: palette entries + tabs
  - Verify: discoverability and quick navigation confirmed in UX smoke.

---

## Quick links

- Health & routing behavior: `CONFIGURATION_REFERENCE.md`
- Hallucination guardrails: `AI_HALLUCINATION_PREVENTION_FRAMEWORK.md`
- SMS pairing: `backend/services/sms_pairing_service.py`, `backend/routes/phone_pairing_api.py`
- BYOK onboarding: `BYOK_MARKETPLACE_LINKS.md`
- Pricing/ROI: `Q-IDE_MEMBERSHIP_TIERS_PRICING.md`, `ROI_CALCULATOR.md`

---

## Optional manual checks (non-prod)

- From cluster: `curl -sS http://<service>:8000/health` returns `{ "status": "ok" }`
- Hit `/snapshots/...` and ensure JSON response, not HTML
- Trigger SMS invite without providers set; verify mock log output
- Switch theme + high-contrast and verify input readability in the Phone tab
