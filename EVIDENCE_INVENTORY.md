# System Evidence Inventory

This file provides a concrete, auditable snapshot of the Q‑Top‑Dog‑IDE repository for detailed review. It lists key components with exact paths and their purpose, plus validation results and git history probes for disputed areas.

## Backend (FastAPI) — key files
- `backend/main.py` — Backend entrypoint. Sets up:
  - Middleware: selective host/health, RulesEnforcement, Compliance, security headers, canonical redirect, logging with metrics.
  - Routers mounted: LLM config/auth/chat/oauth, build orchestration, orchestration workflow, medical (interop/diagnostic/trials), science (RWE/multimodal), rules API, phone pairing API, user notes, build rules, build plan approval, monitoring routes, snapshots API.
  - Endpoints: `/health`, `/ui/edition`, `/ui/banner`, `/robots.txt`, `/sitemap.xml`, `/`, `/agent/orchestrate`, consistency/hallucination/PFS SLIs, asset generation (sync/async/upload), determinism seed/commitment, snapshot approve/request-change, build run/polling, LLM learning endpoints, SSE `/llm_stream`, `/metrics`.
  - Frontend static/catch‑all mounting under `/assets` and `/` after API routers.

- `backend/services/` — Core services (selected highlights):
  - `game_container_manager.py` — Docker orchestration for game engines:
    - `start_godot_container(project_id, project_path, config)` — builds/starts Godot container; maps debug/preview ports; tracks status.
    - `start_unreal_container(project_id, project_path, config)` — builds/starts Unreal container; maps debug/preview/PIE ports; tracks status.
    - Stop/status/logs/list helpers and port mapping retrieval.
  - `game_engine_router.py` — Multi‑engine code intelligence router:
    - Engines: Construct 3, Godot, Unity, Unreal.
    - Handlers: completions, hover, diagnostics, definition for each engine.
    - Language server mappings per engine.
  - Additional notable services: `ai_orchestration.py`, `consistency_scoring.py`, `formal_verification.py`, `refactoring_engine.py`, `python_language_server.py`, `typescript_language_server.py`, `orchestration_service.py`, `workflow_db_manager.py`, `safety_prefilter.py`, `semantic_analysis.py`, `debug_adapter.py`, `trial_expiry_job.py`, `snapshot_store.py`, `stripe_service.py`, `voice_profiling_engine.py`.

- `backend/api/v1/` — Feature API blueprints/routes:
  - `game_engine_routes.py` — REST API under `/api/v1/game-engine`:
    - Projects: list/register/switch (supports construct3, godot, unity, unreal at router level).
    - Code intelligence: completions/hover/diagnostics/definition via MultiEngineRouter.
    - Containers: start/list/status/logs/stop — start supports `godot` and `unreal` only; others 400.
  - Other route modules: `ai_marketplace_routes.py`, `intellisense.py`, `refactoring.py`, `voice.py`, `customization.py`, `debug.py`.

- `backend/routes/` — Production routers:
  - `ai_workflow_routes.py`, `orchestration_workflow.py`, `billing.py`, `rules_api.py`, `phone_pairing_api.py`, `snapshot_routes.py`, `build_rules_routes.py`, `build_plan_approval_routes.py`, medical `med/*`, science `science/*`, `user_notes_routes.py`.

- Middleware:
  - `backend/middleware/compliance_enforcer.py`, `rules_enforcement.py`, `tier_validator.py` — Compliance and rules enforcement used by `main.py`.

## Backend tests
- Directory: `backend/tests/`
- Notable test files (subset):
  - `test_game_engine_integration.py` — Registers Construct 3/Godot/Unity/Unreal, performs completions for each, validates language servers; checks container manager behavior.
  - `test_health_and_compliance.py` — Health OK; compliance enforcement behaviors.
  - Others: `test_consistency_scoring.py`, `test_formal_verification.py`, `test_e2e_intellisense*.py`, `test_workflow_orchestration.py`, `test_snapshot_routes.py`, `test_ai_marketplace.py`, `test_voice_profiling.py`, etc.

## Frontend (React + Vite + TypeScript + Tauri)
- `frontend/` — app shell and build system.
  - `src/App.tsx` — Core UI, tabs/tests exist; panels for LLM, rules, builds, etc.
  - `src/pages/*`, `src/components/*`, `src/services/*`, `src-tauri/*`.
  - Config: `package.json`, `vite.config.ts`, `tsconfig*.json`, `tailwind.config.js`.
  - Tests: React/Vitest and Playwright configs and test outputs present.

## Scripts, deployment, and ops
- Root scripts: `BUILD_WINDOWS*.ps1`, `deploy.sh`, `Deploy-Phase7.ps1`, `docker-build*.{ps1,sh}`, `RUN_Q-IDE.bat`, launcher scripts, `INSTALL*`, `VERIFY_REQUIREMENTS.bat`.
- Kubernetes/ops: `k8s/`, `monitoring/`, Prometheus `/metrics` route in backend, `RUNBOOKS/`.
- Docker: `Dockerfile`, `docker-compose*.yml`, `container/`.

## Documentation breadth
- Extensive docs across pricing, deployment, compliance, orchestration, marketplace, medical/science, multi‑engine strategy, etc.
- Indexes: `DOCUMENTATION_INDEX.md`, `COMPLETE_DOCUMENTATION_INDEX.md`, `MASTER_IMPLEMENTATION_CHECKLIST.md`, `MANIFEST.md`, many completion summaries.

## Contested areas — proof by search
- GameMaker in backend code: NOT FOUND.
  - Backend search for `GameMaker|Game Maker|GameMakerStudio` → no matches in `backend/**`.
  - Mentions exist in strategy/pricing docs only (e.g., `CONSTRUCT3_INTEGRATION_STRATEGY.md`, `Q-IDE_COMPLETE_CAPABILITY_INVENTORY.md`).
- Construct 3 containers: NOT IMPLEMENTED.
  - Router supports Construct 3 (handlers + language servers) in `backend/services/game_engine_router.py`.
  - `backend/api/v1/game_engine_routes.py` container start path supports only `godot` and `unreal`; others return 400.
- Godot/Unreal integrations: PRESENT end‑to‑end.
  - Container functions: `backend/services/game_container_manager.py` → `start_godot_container(...)`, `start_unreal_container(...)`.
  - API usage: `backend/api/v1/game_engine_routes.py` → branches to `container_manager.start_godot_container(...)` and `start_unreal_container(...)`.
  - Tests: `backend/tests/test_game_engine_integration.py` exercises router features and container manager behavior.

## Git history probes (integrity check)
- `git log -S GameMaker --all` → hits are documentation commits only (pricing/strategy). No code removals detected.
- `git log -S "Construct 3" --all` → documentation and chore commits; no evidence of previously removed container code.

## Validation snapshot (quality gates)
- Tests (targeted):
  - Ran: `backend/tests/test_game_engine_integration.py` → PASS (23 passed).
- Lint/Typecheck: not executed in this snapshot.
- Build: not executed in this snapshot.

## Conclusions
- The program is intact and production‑oriented: rich backend, comprehensive routers/middleware/endpoints, real tests, and a full frontend.
- Godot and Unreal integrations are implemented with containers and code‑intel routing.
- Construct 3 is integrated at the router level (code intelligence), but has no container start implementation.
- GameMaker is not implemented in backend code (docs only). No evidence it existed and was removed.

## Fast follow options
- Add `Construct 3` container adapter + `/containers/start` wiring.
- Scaffold `GameMaker` stubs (router/adapter/routes + README) and plan container/runtime strategy.
- Run full test suite and optional linters; produce a CI artifact with PASS/FAIL summary.
