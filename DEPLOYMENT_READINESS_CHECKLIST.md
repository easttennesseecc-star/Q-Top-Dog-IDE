# Deployment Readiness Checklist

Date: 2025-11-07

Statuses: PASS | NEEDS-ATTN | N/A

## API Health and Routing
- [/health returns JSON] PASS
  - Implemented early with response_model `HealthCheckResponse`. Not shadowed by SPA catch-all.
- [Readiness endpoints return JSON, not shadowed] PASS
  - Readiness router included before catch-all.

## Inbound Message Spool (Replaces Inbox)
- [/spool/ingest/* endpoints operational] PASS
  - sms, email, api ingestion write one-file-per-message under ASSISTANT_SPOOL_DIR (default ./var/spool/assistant)
- [/spool/next-input returns JSON] PASS
  - Returns {status: ok|empty, message?}; not shadowed by frontend catch-all.
- [Background pump optional] PASS
  - Enabled via ASSISTANT_SPOOL_PUMP=true; rate limited by ASSISTANT_SPOOL_RATE_PER_MIN (default 60) with exponential backoff (ASSISTANT_SPOOL_BACKOFF_MAX_SECONDS, default 5s).
- [/spool/status provides depth + last timestamp] PASS
  - Quick operational introspection for queue depth and processed count.
- [Legacy inbox removed] PASS
  - assistant_inbox* service files deleted; old tests removed.

## Orchestration and Tests
- [Orchestration DB initializes without UNIQUE collisions] PASS
  - Tests use uuid4 for workflow/build IDs; DB init in lifespan.
- [Full test suite] NEEDS-ATTN
  - Run: `python -m pytest -q backend/tests --maxfail=1` and address any regressions.

## Email/SMS Ingestion
- [Email NOTE detection works on subject/body] PASS
  - Logic updated to scan anywhere in subject/body; covered by email tests.
- [SMS flows OK] PASS
  - Inbox add/list validated; triage removed.

## Background and Shutdown
- [Background task manager shuts down cleanly] PASS
  - Lifespan awaits `task_manager.shutdown()` on shutdown; autopilot retired.

## Security & Compliance
- [Security headers (CSP, HSTS, X-Frame-Options, etc.)] PASS
  - Added in security middleware with env-driven CSP.
- [Compliance middleware not blocking dev endpoints] PASS
  - Middleware wraps and returns JSON errors; normal endpoints accessible in dev.

## Pydantic v2 Migration
- [Warnings resolved] PASS
  - DomainConfig, RoleAssignmentRequest updated; no protected namespace warnings.

## Triaged/Removed Features
- [Triage/autopilot removed] PASS
  - Router import removed; tests skipped; no runtime imports.

## How to Run (Windows PowerShell)
```powershell
# Activate venv
& .\.venv\Scripts\Activate.ps1

# Run targeted tests first
python -m pytest -q backend\tests\test_assistant_inbox_e2e.py
python -m pytest -q backend\tests\test_assistant_inbox_admin_ops.py
python -m pytest -q backend\tests\test_assistant_inbox_auto_tasks.py
python -m pytest -q backend\tests\test_assistant_readiness.py
python -m pytest -q backend\tests\test_ai_workflow_orchestration.py
python -m pytest -q backend\tests\test_email_ingestion.py

# Full suite (stop on first failure)
python -m pytest -q backend\tests --maxfail=1
```

## Key Environment Variables
| Variable | Purpose | Default |
|----------|---------|---------|
| ASSISTANT_SPOOL_DIR | Root directory for spool (incoming/done) | ./var/spool/assistant |
| ASSISTANT_SPOOL_PUMP | Enable background pump loop | false |
| ASSISTANT_SPOOL_RATE_PER_MIN | Max messages processed per minute (pump) | 60 |
| ASSISTANT_SPOOL_BACKOFF_MAX_SECONDS | Max backoff on orchestrate failures | 5 |
| REMINDER_LOOP_ENABLED | Enable push reminder loop | false in tests / true otherwise |
| ENABLE_REGULATED_DOMAINS | Toggle regulated (medical/scientific) edition defaults | true |
| CSP_POLICY | Override default Content Security Policy | (generated) |
| DATABASE_URL | Workflow / orchestration DB URL | sqlite:///./topdog_ide.db |
| CANONICAL_HOST | Host used for SEO canonical links | topdog-ide.com |
| ENABLE_HOST_REDIRECT | Enforce redirect to CANONICAL_HOST | false |

## Operational Notes
- Spool files are atomic via temp + os.replace; at-most-once delivery with move to done/.
- Metrics (if prometheus_client installed):
  - spool_pump_messages_total{status}
  - spool_pump_failures_total
  - spool_pump_orchestrate_seconds
- Use `/spool/pump-once` for manual draining in low-volume dev or debugging.
