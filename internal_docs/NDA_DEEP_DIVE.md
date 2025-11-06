# Top Dog IDE — Technical Deep Dive (NDA‑Only)

Classification: Confidential — Share only under NDA
Updated: Nov 6, 2025

This document provides a technical overview suitable for security, architecture, and compliance reviews. It references file locations in the repository for verification. Do not publish externally.

## 1. Architecture Overview
- Backend: FastAPI application with modular routers and middleware.
- Key areas: safety/compliance middleware, orchestration services, approvals workflow, inbox triage, messaging, push.
- Observability: Prometheus metrics surfaces and structured logging.

## 2. Safety & Reliability
- Hallucination detection and severity export (OverWatch) — see `backend/main.py` (metrics usage) and `backend/metrics.py`.
- Consistency scoring — see `backend/services/consistency_scoring.py` and tests under `backend/tests`.
- Snapshot retention with restore paths — see `backend/services/snapshot_store.py` and `backend/routes/snapshot_routes.py`.
- SLO burn‑rate gate tooling — see `tools/slo_burn_rate_gate.py`.
- PCG guardrails — see `tools/pcg_guardrails.py`.
- Red‑team runner — see `tools/red_team_runner.py`.

## 3. Compliance & Data Segments
- Middleware: `backend/middleware/compliance_enforcer.py`; enforced via `ComplianceMiddleware` in `backend/main.py`.
- Medical/scientific routing segregation: `backend/routes/med/*`, `backend/routes/science/*`.
- Edition and segment labeling helpers: `_resolve_edition`, `_segment_label` in `backend/main.py`.

## 4. Orchestration & BYOK
- Multi‑LLM pool and auto‑assignment: `backend/llm_pool.py`, `backend/llm_auto_assignment.py`.
- Role‑based workflow orchestration: `backend/services/orchestration_service.py`; DB models in `backend/models/workflow.py`.
- Failover, endpoint selection: methods within orchestration service; see tests referencing orchestration and failover.
- BYOK storage/flows: see `backend/llm_auth_routes.py`, `backend/llm_config_routes.py`, and token helpers in `backend/main.py`.

## 5. Approvals & Remote‑First Flows
- Build plan approvals: `backend/services/build_plan_approval_service.py`, routes in `backend/routes/build_plan_approval_routes.py`.
- SMS/email approvals and parsing: `backend/routes/email_inbound_api.py`, `backend/services/sms_command_handler.py`.
- Assistant inbox + triage (imperative normalization → action): `backend/services/assistant_inbox.py`, `backend/services/assistant_inbox_triage.py`, routes in `backend/routes/assistant_inbox_*`.
- Message Board UIs: `backend/admin_static/board.html`, `backend/admin_static/inbox.html` (admin protection applied at middleware).

## 6. Messaging & Push
- Web Push (VAPID): `backend/services/webpush_sender.py`, registry in `backend/services/push_store.py`.
- Native push (optional): `backend/services/push_native_senders.py` (providers env‑gated), selection in `backend/services/push_service.py`.
- Admin push setup UI (internal/admin‑gated): `backend/admin_static/push.html`.
- Admin protection middleware: `backend/main.py` — `/admin` requires token or private network.

## 7. Observability & Logging
- Prometheus metrics registry and exports: referenced in `backend/main.py` and `backend/metrics.py`.
- Structured logging: `backend/logger_utils.py`, middleware logs request metadata and latencies.
- Health checks and probes: `/health` and monitoring routes in `backend/monitoring_routes.py`.

## 8. Security Posture Highlights
- `/admin` gating: token‑based or private‑network default. 404 for specific sensitive pages (e.g., accidental one‑pager restores).
- No secrets in repo; environment‑based configuration for providers.
- BYOK pattern: keys remain user‑controlled.
- CORS and CSP policies controlled by environment variables.

## 9. Data Handling
- Artifacts served from `./artifacts` (for MMS/media), mounted explicitly.
- Inbox/task stores: file‑backed in dev; swap to DB in production.
- Snapshot/rollback artifacts controlled via API and policy.

## 10. Testing Overview
- Tests under `backend/tests/` cover:
  - Email inbound accept/modify flows
  - Push register/notify
  - Triage E2E (imperative → PLAN → execution → confirmations)
  - Safety/compliance and orchestration behavior
- Additions in this iteration: `test_assistant_inbox_triage_e2e.py`.

## 11. Deployment Notes
- Containerized deployment with Helm chart (see deploy/helm). Configure tokens/keys in secrets.
- Admin token: set `ADMIN_TOKEN` to gate `/admin`; without it, only private networks are allowed.
- Configure VAPID/native push keys by environment.

## 12. Threat Model (Snapshot)
- Risks: public exposure of admin, mishandled credentials, over‑permissive CORS, unsafe content generation.
- Mitigations: admin gating, env‑only secrets, CSP defaults, approval gates, safety filters, metrics watchdogs.
- Residual: operator configuration errors; addressed by checks and docs.

For a live review: we can supply a checklist, sample red‑team run, and config templates under NDA.
