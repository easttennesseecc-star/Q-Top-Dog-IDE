"""
Quellum TopDog IDE Backend Entry Point
Production-ready Python backend for agent orchestration and analytics
"""


import sys
import os
import urllib.parse
import logging
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException, APIRouter
from fastapi.responses import RedirectResponse, FileResponse, PlainTextResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import subprocess
import uuid
from fastapi import Body, UploadFile, File, Form
from contextlib import asynccontextmanager
import asyncio

from backend.llm_pool import build_llm_report, get_best_llms_for_operations
from backend.llm_config_routes import router as llm_config_router
from backend.llm_auth_routes import router as llm_auth_router
from backend.llm_chat_routes import router as llm_chat_router
from backend.build_orchestration_routes import router as build_orchestration_router
from backend.llm_oauth_routes import router as llm_oauth_router
 

from backend.routes.orchestration_workflow import router as orchestration_workflow_router
from backend.routes.med.interop import router as med_interop_router
from backend.routes.med.diagnostic import router as med_diagnostic_router
from backend.routes.med.trials import router as med_trials_router
from backend.routes.science.rwe import router as science_rwe_router
from backend.routes.science.multimodal import router as science_multimodal_router
from backend.routes.snapshot_routes import router as snapshot_router
from backend.media_routes import router as media_router
from backend.routes.ai_workflow_routes import router as ai_workflow_router
from backend.routes.rules_api import router as rules_api_router
from backend.routes.phone_pairing_api import router as phone_pairing_router
from backend.routes.away_api import router as away_router
from backend.routes.sms_log_api import router as sms_log_router
from backend.routes.email_inbound_api import router as email_inbound_router
from backend.routes.push_api import router as push_router
from backend.routes.pricing_routes import router as pricing_routes
from backend.routes.assistant_readiness import router as assistant_readiness_router
from backend.routes.tasks_api import router as tasks_router
from backend.routes.user_notes_routes import router as user_notes_router
from backend.routes.build_rules_routes import router as build_rules_router
from backend.routes.build_plan_approval_routes import router as build_plan_approval_router
from backend.routes.test_solver_routes import router as test_solver_router
from backend.routes.domain_config_routes import router as domain_config_router
from backend.routes.marketplace_fastapi import marketplace_router, agent_router, marketplace_auth_router

from backend.middleware.compliance_enforcer import ComplianceEnforcer
from backend.services.workflow_db_manager import init_workflow_database, WorkflowDatabaseManager
from backend.services.orchestration_service import OrchestrationService
from backend.middleware.rules_enforcement import RulesEnforcementMiddleware
from backend.services.ai_orchestration import initialize_ai_orchestration
from backend.logger_utils import configure_logger
from backend.auto_setup_q_assistant import auto_setup_q_assistant
from backend.llm_auto_auth import check_all_llm_authentication, get_startup_auth_prompt
from backend.setup_wizard import router as setup_wizard_router
from backend.llm_auto_assignment import register_auto_assignment_routes
from backend.auth import (
    create_session, get_session_user, get_user, create_or_get_user,
    exchange_code_for_token, get_google_user_info, get_github_user_info,
    link_account, get_linked_accounts
)

# Optional routers that may fail to import in certain profiles
billing_router: Optional[APIRouter]
assistant_router: Optional[APIRouter]
spool_ingest_router: Optional[APIRouter]
try:
    from backend.routes.billing import router as billing_router  # type: ignore[assignment]
except Exception:
    billing_router = None
try:
    from backend.assistant_routes import router as assistant_router  # type: ignore[assignment]
except Exception:
    assistant_router = None
try:
    from backend.routes.spool_ingest_api import router as spool_ingest_router  # type: ignore[assignment]
except Exception:
    spool_ingest_router = None

EMAIL_ROUTER_ENABLED = True

# Define alias after all module-level imports are declared to satisfy E402
_Body = Body

# Initialize logger early
logger = configure_logger(
    name="q-ide-topdog",
    log_dir="./logs",
    level=logging.INFO
)

logger.info("Q-IDE Backend starting up...")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan handler to replace deprecated startup events."""
    logger.info("Running startup tasks (lifespan)...")
    # Load persisted domain configuration and apply env overrides early
    try:
        from backend.services.domain_config import load_and_apply
        load_and_apply(app)
        logger.info("Domain configuration loaded and applied")
    except Exception as e:
        logger.warning(f"Domain configuration not loaded: {e}")
    # Detect test environment to avoid starting background loops that can hang pytest
    def _is_testing_env() -> bool:
        try:
            if os.getenv("PYTEST_CURRENT_TEST"):
                return True
            env = (os.getenv("ENVIRONMENT") or "").lower().strip()
            if env in ("test", "testing"):  # conventional flags
                return True
        except Exception:
            pass
        return False

    # Initialize workflow orchestration database
    try:
        database_url = os.getenv(
            "DATABASE_URL",
            "sqlite:///./topdog_ide.db"
        )
        logger.info(f"Initializing workflow database: {database_url.split('/')[-1]}")

        db_manager = WorkflowDatabaseManager(database_url)
        app.workflow_db_manager = db_manager  # type: ignore[attr-defined]

        if init_workflow_database(db_manager):
            logger.info("Workflow orchestration database initialized and ready")
        else:
            logger.error("Workflow database initialization FAILED - orchestration will not work")
            # In a real scenario, we might want to prevent the app from starting.
            # For now, we log an error and continue, but tests will fail.
    except Exception as e:
        logger.error(f"Error initializing workflow database: {str(e)}")

    # Initialize AI Orchestration Manager
    try:
        logger.info("Initializing AI orchestration system...")
        orchestration_service = OrchestrationService(
            db_manager=getattr(app, 'workflow_db_manager', None)
        )
        ai_manager = initialize_ai_orchestration(orchestration_service)
        app.state.ai_orchestration_manager = ai_manager
        # Expose orchestration service for downstream selection/failover policies
        try:
            app.state.orchestration_service = orchestration_service  # type: ignore[attr-defined]
        except Exception:
            setattr(app, 'orchestration_service', orchestration_service)  # legacy fallback
        logger.info("AI orchestration service available (feature flags control behavior)")
    except Exception as e:
        logger.error(f"Error initializing AI orchestration: {str(e)}")

    async def _run_heavy_startup_tasks() -> None:
        """Run non-critical, potentially slow startup work in background.

        This prevents blocking the server from becoming ready, allowing
        Kubernetes startup/readiness probes to pass quickly.
        """
        if _is_testing_env():
            return
        # Auto-setup Q Assistant if needed (best-effort, non-blocking for readiness)
        try:
            result = auto_setup_q_assistant()
            if result:
                logger.info(f"Q Assistant auto-configured with: {result.get('name')}")
            else:
                logger.warning("Q Assistant not auto-configured. Please configure via LLM Setup.")
        except Exception as e:
            logger.error(f"Error in startup auto-setup: {str(e)}")
        # Check LLM authentication status (network-dependent; do not block readiness)
        try:
            auth_status = check_all_llm_authentication()
            prompt = get_startup_auth_prompt()
            if auth_status.all_ready:
                logger.info(f"All {len(auth_status.authenticated_llms)} LLMs authenticated and ready")
            else:
                logger.warning(f"{len(auth_status.missing_credentials)} LLM(s) need credentials:")
                for missing in auth_status.needs_setup:
                    llm_name = missing.get('name', missing.get('llm_id', 'Unknown'))
                    assigned_role = missing.get('assigned_role', 'role')
                    logger.warning(f"  - {llm_name} (assigned to {assigned_role})")
                logger.info("  -> Frontend will prompt user with options")
            # Store auth prompt for frontend to display
            app.llm_auth_prompt = prompt  # type: ignore[attr-defined]
        except Exception as e:
            logger.error(f"Error checking LLM authentication: {str(e)}")

    # Schedule heavy/optional startup tasks without blocking readiness
    try:
        asyncio.get_running_loop().create_task(_run_heavy_startup_tasks())
    except RuntimeError:
        # Fallback if loop not running yet
        try:
            loop = asyncio.new_event_loop()
            loop.create_task(_run_heavy_startup_tasks())
        except Exception:
            pass

    # Start push reminder loop (disabled during tests unless explicitly enabled)
    reminder_task = None
    stop_event = asyncio.Event()
    spool_task = None
    try:
        enable_reminders = os.getenv("REMINDER_LOOP_ENABLED", "true").lower() in ("1", "true", "yes")
        if _is_testing_env():
            # Default off in tests unless forced via REMINDER_LOOP_ENABLED=true
            enable_reminders = os.getenv("REMINDER_LOOP_ENABLED", "false").lower() in ("1", "true", "yes")
        
        if enable_reminders:
            from backend.services.push_reminder import reminder_loop
            # Create the task so it can be properly managed and shut down
            reminder_task = asyncio.create_task(reminder_loop(stop_event))
            app.state._reminder_stop = stop_event
            logger.info("Push reminder loop started.")
        else:
            logger.info("Push reminder loop disabled by environment (REMINDER_LOOP_ENABLED=false or testing)")

        # Spool background pump (optional lightweight inbound automation)
        try:
            from backend.services import spool_pump
            if spool_pump.is_enabled_in_env():
                logger.info("Starting spool pump loop (ASSISTANT_SPOOL_PUMP enabled)")
                spool_stop = asyncio.Event()
                spool_task = asyncio.create_task(spool_pump.pump_loop(app, spool_stop))
                app.state._spool_stop = spool_stop
            else:
                logger.info("Spool pump disabled (ASSISTANT_SPOOL_PUMP not true)")
        except Exception as e:
            logger.warning(f"Spool pump not started: {e}")
    except Exception as e:
        logger.warning(f"Push reminder loop not configured: {e}")

    # Autopilot loop retired — do not start
    logger.info("Assistant autopilot has been retired and will not be started")

    # Yield to run the application
    yield

    # On shutdown, stop reminder loop
    try:
        if reminder_task and not reminder_task.done():
            logger.info("Attempting to stop reminder loop...")
            stop_event.set()
            reminder_task.cancel()
            await reminder_task
            logger.info("Reminder loop stopped.")
    except asyncio.CancelledError:
        logger.info("Reminder loop cancelled successfully.")
    except Exception as e:
        logger.error(f"Error during reminder loop shutdown: {e}")
        pass
        # Autopilot retired; nothing to stop

    # Stop spool pump loop
    try:
        if spool_task and not spool_task.done():
            logger.info("Stopping spool pump loop...")
            app.state._spool_stop.set()  # type: ignore[attr-defined]
            spool_task.cancel()
            await spool_task
            logger.info("Spool pump loop stopped.")
    except asyncio.CancelledError:
        logger.info("Spool pump cancelled successfully.")
    except Exception as e:
        logger.error(f"Error stopping spool pump: {e}")

    # On shutdown, gracefully shut down the background task manager
    try:
        from backend.services.background_task_manager import get_background_task_manager
        task_manager = get_background_task_manager()
        if task_manager:
            await task_manager.shutdown()
    except Exception as e:
        logger.error(f"Error during background task manager shutdown: {e}")


app = FastAPI(
    title="Q-IDE Backend",
    description="Production-ready API for TopDog IDE",
    version="0.1.0",
    lifespan=lifespan,
)

class HealthCheckResponse(BaseModel):
    status: str
    version: str


# Define health endpoint early so it is not shadowed by the frontend catch-all route
@app.get("/health", response_model=HealthCheckResponse)
def health_check(request: Request):
    """Simple health check endpoint - returns JSON status"""
    try:
        return {"status": "ok", "version": app.version}
    except Exception as e:
        logger.error(f"Health check error: {e}", exc_info=True)
        # This part of the code will likely not be reached due to response_model validation,
        # but it's good practice for handling unexpected errors.
        raise HTTPException(status_code=500, detail=str(e))

# Request ID correlation (first-in-chain)
class RequestIDMiddleware(BaseHTTPMiddleware):
    """Ensures every request has a stable request ID for correlation.

    - Accepts incoming X-Request-ID or X-Correlation-ID
    - Generates UUIDv4 if missing
    - Exposes on request.state.request_id and response header X-Request-ID
    """
    async def dispatch(self, request: Request, call_next):
        import uuid as _uuid
        incoming = (
            request.headers.get("X-Request-ID")
            or request.headers.get("X-Correlation-ID")
        )
        rid = incoming or str(_uuid.uuid4())
        try:
            request.state.request_id = rid
        except Exception:
            pass
        response = await call_next(request)
        try:
            response.headers["X-Request-ID"] = rid
        except Exception:
            pass
        return response

# Logging middleware - place early to capture total time and correlate with request id
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        import time
        start_time = time.time()
        # Metrics import is local to avoid hard dependency issues
        try:
            from backend.metrics import HTTP_REQUESTS as _HTTP_REQUESTS  # type: ignore[assignment]
        except Exception:
            _HTTP_REQUESTS = None  # type: ignore[assignment]

        # Prefer request.state.request_id populated by RequestIDMiddleware
        try:
            req_id = getattr(request.state, "request_id", None) or request.headers.get("X-Request-ID", "unknown")
        except Exception:
            req_id = request.headers.get("X-Request-ID", "unknown")

        with logger.context(
            request_id=req_id,
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else "unknown"
        ):
            try:
                response = await call_next(request)
                elapsed = time.time() - start_time
                if response.status_code >= 400:
                    logger.warning(
                        "Request completed with error",
                        status_code=response.status_code,
                        elapsed_seconds=elapsed
                    )
                # Record HTTP requests metric
                try:
                    if _HTTP_REQUESTS is not None:
                        endpoint = request.url.path
                        _HTTP_REQUESTS.labels(endpoint=endpoint, status=str(response.status_code)).inc()
                except Exception:
                    pass
                else:
                    logger.debug(
                        "Request completed",
                        status_code=response.status_code,
                        elapsed_seconds=elapsed
                    )
                return response
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(
                    "Request failed",
                    error=e,
                    elapsed_seconds=elapsed
                )
                try:
                    if _HTTP_REQUESTS is not None:
                        endpoint = request.url.path
                        _HTTP_REQUESTS.labels(endpoint=endpoint, status="500").inc()
                except Exception:
                    pass
                raise

# Register correlation and logging FIRST
app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)

# Custom middleware to allow health checks from any host (required for K8s probes)
class SelectiveHostMiddleware(BaseHTTPMiddleware):
    """Skip host validation for health checks and allow K8s probes from any IP"""
    async def dispatch(self, request: Request, call_next):
        # Allow /health endpoint from any host (K8s probes need this)
        if request.url.path == "/health":
            return await call_next(request)

        # Allow other monitoring endpoints from any host
        if request.url.path.startswith("/health/") or request.url.path.startswith("/metrics"):
            return await call_next(request)

        # For other endpoints, validate host header (optional - can be disabled in production)
        # Currently allowing all hosts to simplify Kubernetes deployment
        return await call_next(request)

# Security middleware - now using selective host validation
app.add_middleware(SelectiveHostMiddleware)

# Rules enforcement middleware - enforces user rules for ALL AI models
app.add_middleware(RulesEnforcementMiddleware)

# Compliance enforcement middleware - HIPAA/SOC2/FEDRAMP for medical/scientific workspaces
class ComplianceMiddleware(BaseHTTPMiddleware):
    """Enforces compliance requirements for regulated workspaces"""
    async def dispatch(self, request: Request, call_next):
        try:
            await ComplianceEnforcer.enforce_compliance(request)
            return await call_next(request)
        except HTTPException as he:
            # Convert compliance exceptions into proper HTTP responses
            return JSONResponse(status_code=he.status_code, content={"detail": he.detail})
        except Exception:
            # Fallback: ensure we don't leak unhandled errors from middleware
            logger.error("Unhandled error in ComplianceMiddleware", exc_info=True)
            return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

app.add_middleware(ComplianceMiddleware)

# Admin surface protection — prevent accidental public exposure of /admin
@app.middleware("http")
async def admin_protect_middleware(request: Request, call_next):
    path = request.url.path or ""
    if path.startswith("/admin"):
        # Specifically block any accidentally included comparison/onepager page
        if path.lower().endswith("/onepager.html"):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})
        # Strategy:
        # 1) If ADMIN_TOKEN is set, require header X-Admin-Token or cookie admin_token to match
        # 2) Else, allow only localhost/private networks by default; block public WAN
        token_env = os.getenv("ADMIN_TOKEN", "").strip()
        client_ip = request.client.host if request.client else ""
        def _is_private(ip: str) -> bool:
            try:
                return (
                    ip in ("127.0.0.1", "::1", "localhost") or
                    ip.startswith("10.") or ip.startswith("192.168.") or ip.startswith("172.16.") or ip.startswith("172.17.") or ip.startswith("172.18.") or ip.startswith("172.19.") or ip.startswith("172.2")
                )
            except Exception:
                return False
        if token_env:
            provided = request.headers.get("X-Admin-Token") or request.cookies.get("admin_token") or ""
            if provided != token_env:
                return JSONResponse(status_code=403, content={"detail": "Forbidden: admin token required"})
        else:
            # Default posture: restrict to private networks
            if not _is_private(client_ip):
                return JSONResponse(status_code=403, content={"detail": "Forbidden: /admin restricted to private network"})
    return await call_next(request)
def _resolve_edition(request: Request) -> str:
    """Determine current edition: 'regulated' or 'dev'. Order: header, cookie, env."""
    try:
        hdr = request.headers.get("X-Edition", "").lower().strip()
        if hdr in ("dev", "regulated"):
            return hdr
    except Exception:
        pass
    try:
        cookie = request.cookies.get("td_edition", "").lower().strip()
        if cookie in ("dev", "regulated"):
            return cookie
    except Exception:
        pass
    env_enabled = str(os.getenv("ENABLE_REGULATED_DOMAINS", "true")).lower() in ("1","true","yes")
    return "regulated" if env_enabled else "dev"


def _plan_label(req: Optional[Request] = None) -> str:
    try:
        if req is not None:
            hdr = req.headers.get("X-Plan", "").strip()
            if hdr:
                return hdr
    except Exception:
        pass
    return os.getenv("DEFAULT_PLAN", "Pro")


def _segment_label(req: Optional[Request] = None) -> str:
    # Prefer explicit header first
    try:
        if req is not None:
            hdr = (req.headers.get("X-Data-Segment", "") or "").strip().lower()
            if hdr in ("general", "medical", "scientific"):
                return hdr
    except Exception:
        pass
    # Fall back to edition/env
    try:
        ed = _resolve_edition(req) if req is not None else (
            "regulated" if str(os.getenv("ENABLE_REGULATED_DOMAINS", "true")).lower() in ("1","true","yes") else "dev"
        )
        if ed == "regulated":
            return os.getenv("DEFAULT_REGULATED_SEGMENT", "medical").lower()
    except Exception:
        pass
    return os.getenv("DEFAULT_DATA_SEGMENT", "general").lower()


@app.get("/ui/edition")
def get_edition(request: Request):
    edition = _resolve_edition(request)
    return {"edition": edition}


class EditionRequest(BaseModel):
    edition: str


@app.post("/ui/edition")
def set_edition(req: EditionRequest, request: Request):
    ed = (req.edition or "").lower().strip()
    if ed not in ("dev", "regulated"):
        return JSONResponse(status_code=400, content={"error": "edition must be 'dev' or 'regulated'"})
    resp = JSONResponse({"edition": ed})
    # Cookie scoped to backend domain; HttpOnly=false so frontend can read if desired; set Secure in TLS environments
    resp.set_cookie(key="td_edition", value=ed, httponly=False, samesite="lax")
    return resp


@app.get("/ui/banner")
def get_banner(request: Request):
    ed = _resolve_edition(request)
    if ed == "regulated":
        text = os.getenv("BANNER_REGULATED", "Regulated profile active: medical/scientific safeguards enforced.")
        style = "warning"
    else:
        text = os.getenv("BANNER_DEV", "Developer profile: fast path, Overwatch optional.")
        style = "info"
    return {"edition": ed, "text": text, "style": style}

def _parse_list_env(var_name: str, default: list[str] | None = None) -> list[str]:
    raw = os.getenv(var_name, "")
    if not raw:
        return default or []
    # Support comma or newline separated lists
    parts = [p.strip() for p in raw.replace("\r", "").replace("\t", ",").split("\n")]
    items: list[str] = []
    for line in parts:
        if not line:
            continue
        for sub in line.split(","):
            s = sub.strip()
            if s:
                items.append(s)
    return items

# Add security headers and CSP middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    # Only meaningful once behind TLS; harmless if set early
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    # Content Security Policy (configurable)
    csp = os.getenv("CSP_POLICY")
    if not csp:
        frontend = os.getenv("FRONTEND_URL", "https://topdog-ide.com")
        backend = os.getenv("BACKEND_URL", "https://api.topdog-ide.com")
        # Conservative default; adjust 'unsafe-inline' only if required by frontend
        csp = (
            "default-src 'self'; "
            f"connect-src 'self' {frontend} {backend} https: wss:; "
            "img-src 'self' data: https:; "
            "font-src 'self' https: data:; "
            "style-src 'self' 'unsafe-inline' https:; "
            "script-src 'self' 'unsafe-inline' https:; "
            "frame-ancestors 'self'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
    response.headers["Content-Security-Policy"] = csp
    return response

# Serve static files for OAuth callback
frontend_static = Path(__file__).resolve().parent.parent / "frontend" / "public"
if frontend_static.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_static)), name="static")

# Minimal admin snapshots browser (static HTML)
admin_static = Path(__file__).resolve().parent / "admin_static"
if admin_static.exists():
    app.mount("/admin", StaticFiles(directory=str(admin_static), html=True), name="admin")

# Serve artifacts (images/files) for MMS/media sharing) using a writable path
# Priority:
# 1) ARTIFACTS_DIR env
# 2) QIDE_CONFIG_DIR/artifacts
# 3) /tmp/artifacts
_artifacts_env = os.getenv("ARTIFACTS_DIR")
if _artifacts_env:
    artifacts_dir = Path(_artifacts_env)
else:
    qide_cfg_dir = os.getenv("QIDE_CONFIG_DIR")
    if qide_cfg_dir:
        artifacts_dir = Path(qide_cfg_dir) / "artifacts"
    else:
        artifacts_dir = Path("/tmp/artifacts")

try:
    artifacts_dir.mkdir(parents=True, exist_ok=True)
except Exception:
    # If for some reason creation fails, fall back to /tmp/artifacts
    artifacts_dir = Path("/tmp/artifacts")
    try:
        artifacts_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

if artifacts_dir.exists():
    app.mount("/artifacts", StaticFiles(directory=str(artifacts_dir)), name="artifacts")

# IMPORTANT: Register critical API routers that shouldn't be shadowed by the
# frontend catch-all BEFORE mounting the frontend catch-all.
# Snapshot APIs were previously returning HTML due to catch-all precedence.
app.include_router(snapshot_router)
# Also include media, assistant, and test-solver routers early to avoid catch-all shadowing
app.include_router(media_router, prefix="/api")  # Media generation/config/status
if assistant_router is not None:
    app.include_router(assistant_router, prefix="/api")  # Assistant orchestration (plan + UI draft)
app.include_router(test_solver_router)  # Test Solver API (must be before frontend catch-all)
app.include_router(domain_config_router)  # Domain configuration API
app.include_router(assistant_readiness_router)  # Assistant readiness/capabilities (ensure before catch-all)
# Spool ingestion API should be before frontend catch-all to avoid shadowing
if 'spool_ingest_router' in globals() and spool_ingest_router is not None:
    app.include_router(spool_ingest_router)

# LLM Pool endpoint
@app.get("/api/llm_pool")
def get_llm_pool():
    """Return a report of available local LLMs and any excluded critical models.

    The response includes two keys: 'available' (list) and 'excluded' (list).
    """
    with logger.context(endpoint="/llm_pool"):
        try:
            logger.info("Fetching LLM pool report...")
            report = build_llm_report()
            available_count = len(report.get("available", []))
            excluded_count = len(report.get("excluded", []))
            logger.info(
                "LLM pool fetched successfully",
                available=available_count,
                excluded=excluded_count
            )
            return report
        except Exception as e:
            logger.error("Failed to fetch LLM pool", error=e)
            raise

# Backward compatibility alias (old frontend called /llm_pool without /api prefix)
@app.get("/llm_pool")
def get_llm_pool_alias():
    """Alias for /api/llm_pool to avoid 404/HTML catch-all issues in legacy UI."""
    return get_llm_pool()

# OAuth panel normalization: provide provider listing & login initiation endpoints
@app.get("/llm_auth/providers")
def oauth_list_providers():
    """Return simplified OAuth provider metadata for frontend panel."""
    providers = [
        {"id": "google", "name": "Google", "description": "Google Gemini & AI Studio", "configured": bool(os.getenv("GOOGLE_CLIENT_ID")), "oauth_enabled": True},
        {"id": "github", "name": "GitHub", "description": "GitHub account for Copilot", "configured": bool(os.getenv("GITHUB_CLIENT_ID")), "oauth_enabled": True},
        {"id": "openai", "name": "OpenAI", "description": "OpenAI OAuth (future) / use API key", "configured": False, "oauth_enabled": False},
        {"id": "anthropic", "name": "Anthropic", "description": "Claude via API key", "configured": False, "oauth_enabled": False},
    ]
    return {"providers": providers}

@app.get("/llm_auth/login/{provider}")
def oauth_login(provider: str):
    """Initiate login by returning auth URL (when supported)."""
    provider = provider.lower().strip()
    if provider == "google":
        if not GOOGLE_CLIENT_ID:
            return {"success": False, "client_required": True}
        scope = "openid profile email"
        redirect_uri = f"{BACKEND_URL}/auth/google/callback"
        auth_url = (
            "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
                "client_id": GOOGLE_CLIENT_ID,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": scope,
            })
        )
        return {"success": True, "oauth_url": auth_url}
    if provider == "github":
        if not GITHUB_CLIENT_ID:
            return {"success": False, "client_required": True}
        scope = "user:email repo"
        redirect_uri = f"{BACKEND_URL}/auth/github/callback"
        auth_url = (
            "https://github.com/login/oauth/authorize?" + urllib.parse.urlencode({
                "client_id": GITHUB_CLIENT_ID,
                "redirect_uri": redirect_uri,
                "scope": scope,
            })
        )
        return {"success": True, "oauth_url": auth_url}
    # Unsupported provider -> instruct API key flow
    return {"success": False, "client_required": True, "message": "Use API key flow for this provider"}

# Persist selected LLM server-side (maps to coding or q_assistant role)
class LLMSelectionPayload(BaseModel):
    llm_id: str
    role: Optional[str] = None  # default to coding

@app.post("/llm_selection")
def persist_llm_selection(payload: LLMSelectionPayload = _Body(...)):
    """Persist chosen LLM into role assignments for cross-device continuity."""
    role = (payload.role or "coding").strip()
    from backend.llm_config import save_role_assignment, list_available_providers
    providers = list_available_providers()
    if payload.llm_id not in providers:
        return JSONResponse(status_code=400, content={"detail": "Unknown LLM"})
    if not save_role_assignment(role, payload.llm_id):
        return JSONResponse(status_code=500, content={"detail": "Failed to persist selection"})
    return {"status": "ok", "assigned_role": role, "llm_id": payload.llm_id}


@app.get("/llm_pool/best")
def get_best_llms(count: int = 3):
    """Return the top N auto-selected best LLMs for operations.
    
    This endpoint returns LLMs ranked by quality/priority:
    1. Cloud services (Copilot, Gemini, ChatGPT, Grok) - highest priority
    2. Local CLIs (Ollama, Llama, etc) - medium priority  
    3. Running processes - lower priority
    4. Local model files - lowest priority
    
    Use this to auto-populate operation slots with the best available options.
    Includes priority_score for each LLM showing why it was selected.
    """
    with logger.context(endpoint="/llm_pool/best", count=count):
        try:
            # Clamp count to reasonable range
            count = min(max(1, count), 5)
            logger.info(f"Fetching best {count} LLMs for operations...")
            best = get_best_llms_for_operations(count)
            logger.info(
                "Best LLMs fetched successfully",
                returned=len(best),
                requested=count
            )
            return {
                "best": best,
                "count": len(best),
                "requested": count,
                "note": "LLMs are ranked by priority score (higher = better). Cloud services like Copilot have highest priority."
            }
        except Exception as e:
            logger.error("Failed to fetch best LLMs", error=e)
            return {"best": [], "count": 0, "error": str(e)}


# Mount frontend React app (placed AFTER API routers and SEO endpoints so it does not shadow them)
# Moved BELOW all API router registrations to avoid shadowing (catch-all must be last)

# CORS configuration (env-driven)
cors_origins = _parse_list_env("CORS_ORIGINS")
if not cors_origins:
    # Fallback by environment
    if os.getenv("ENVIRONMENT") == "production":
        cors_origins = [os.getenv("FRONTEND_URL", "https://topdog-ide.com")]
    else:
        cors_origins = [
            "http://localhost:1431",
            "http://127.0.0.1:1431",
            "http://localhost:3000",
            "http://localhost:5173",
        ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional canonical host redirect (SEO). Enable with ENABLE_HOST_REDIRECT=true and set CANONICAL_HOST.
ENABLE_HOST_REDIRECT = os.getenv("ENABLE_HOST_REDIRECT", "false").lower() in {"1", "true", "yes"}
CANONICAL_HOST = os.getenv("CANONICAL_HOST", "")
ALTERNATE_HOSTS = _parse_list_env("ALTERNATE_HOSTS")  # e.g. "www.topdog-ide.com"

# Paths that should never be redirected (health checks, API endpoints, etc.)
NO_REDIRECT_PATHS = {"/health", "/metrics", "/api", "/ws", "/_health", "/readiness", "/liveness", "/snapshots", "/.well-known"}

@app.middleware("http")
async def canonical_redirect_middleware(request: Request, call_next):
    # Skip redirect for health checks, API endpoints, and internal cluster traffic
    path = request.url.path
    if any(path.startswith(no_redirect) for no_redirect in NO_REDIRECT_PATHS):
        return await call_next(request)
    
    if ENABLE_HOST_REDIRECT and CANONICAL_HOST:
        host = request.headers.get("host", "")
        hostname = host.split(":")[0] if host else ""
        
        # Skip redirect for internal cluster traffic (localhost, pod IPs, service names)
        if hostname in ("localhost", "127.0.0.1", "topdog", "topdog-topdog") or hostname.startswith("10."):
            return await call_next(request)
        
        # Redirect if host doesn't match canonical and we either allow any or it's explicitly listed
        should_redirect = hostname and hostname != CANONICAL_HOST and (
            not ALTERNATE_HOSTS or hostname in ALTERNATE_HOSTS
        )
        if should_redirect:
            url = request.url.replace(scheme="https", netloc=CANONICAL_HOST)
            return RedirectResponse(url=str(url), status_code=308)
    return await call_next(request)

 

# Logging middleware already added earlier; avoid duplicate registration which can double-log requests
# (Original duplicate call removed)

# Monitoring routes (expose health and metrics dashboards)
try:
    from backend.monitoring_routes import router as monitoring_router
    app.include_router(monitoring_router)
except Exception as e:
    logger.warning(f"Monitoring routes not loaded: {e}")

# Optional dev-only middleware introspection
@app.get("/__debug/middlewares")
def debug_middlewares(request: Request):
    if os.getenv("ENABLE_DEBUG_ENDPOINTS", "false").lower() not in ("1", "true", "yes"):
        return JSONResponse(status_code=404, content={"detail": "Not Found"})
    try:
        reg_order = [m.cls.__name__ for m in app.user_middleware]
        exec_order = list(reversed(reg_order))  # Outer→inner approximation
        return {
            "status": "ok",
            "registered_order": reg_order,
            "approx_execution_order": exec_order,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

# Include LLM configuration routers
app.include_router(llm_config_router)
app.include_router(llm_auth_router)
app.include_router(llm_chat_router)
app.include_router(build_orchestration_router)
app.include_router(llm_oauth_router)
if billing_router is not None:
    app.include_router(billing_router)
app.include_router(pricing_routes)
app.include_router(orchestration_workflow_router)
app.include_router(med_interop_router)
app.include_router(med_diagnostic_router)
app.include_router(med_trials_router)
app.include_router(science_rwe_router)
app.include_router(science_multimodal_router)
app.include_router(ai_workflow_router)
app.include_router(rules_api_router)  # Rules management API
app.include_router(phone_pairing_router)  # Phone pairing & remote control API
app.include_router(away_router)  # Away mode management (pair/unpair/status)
app.include_router(sms_log_router)  # SMS conversation logs
app.include_router(user_notes_router)  # User notes & explanations API
app.include_router(build_rules_router)  # Build rules & manifest API (QR code concept)
app.include_router(build_plan_approval_router)  # Build plan generation & approval
app.include_router(marketplace_router)  # AI model marketplace (FastAPI port)
app.include_router(agent_router)  # Agent chat endpoints (marketplace integration)
app.include_router(marketplace_auth_router)  # Marketplace auth endpoints
if EMAIL_ROUTER_ENABLED and email_inbound_router:
    app.include_router(email_inbound_router)  # Email inbound webhook for ACCEPT/DECLINE/MODIFY
app.include_router(push_router)  # Push registration and notify API
# Legacy assistant inbox removed (spool ingestion supersedes it)
# Include readiness early to avoid catch-all shadowing (was previously after mount section)
app.include_router(tasks_router)  # Tasks (persistent todos)
# test_solver_router included earlier to avoid catch-all shadowing
# media and assistant routers are already included above (pre-catch-all)

# Mount frontend React app (placed AFTER API routers and SEO endpoints so it does not shadow them)
frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist.exists() and (frontend_dist / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend_catchall(full_path: str):
        """Catch-all route to serve React app for client-side routing"""
        from fastapi import HTTPException
        from fastapi.responses import PlainTextResponse
        # If SEO endpoints are requested, serve them directly
        if full_path == "robots.txt":
            return PlainTextResponse(robots_txt())
        if full_path == "sitemap.xml":
            # sitemap_xml() already returns a Response with media_type="application/xml"
            # Return it directly instead of wrapping in PlainTextResponse
            return sitemap_xml()
        # Google Search Console file verification support
        google_token = os.getenv("GOOGLE_SITE_VERIFICATION_TOKEN")
        if google_token and full_path == f"google{google_token}.html":
            return PlainTextResponse(f"google-site-verification: {google_token}")
        # Bing Webmaster Tools file verification support
        if full_path == "BingSiteAuth.xml":
            bing_token = os.getenv("BING_SITE_VERIFICATION_TOKEN")
            if bing_token:
                from fastapi import Response
                xml = (
                    "<?xml version=\"1.0\"?>\n"
                    f"<users><user>{bing_token}</user></users>\n"
                )
                return Response(content=xml, media_type="application/xml")
        # Don't intercept API routes or explicit SEO endpoints
        if full_path.startswith((
            "api/", "auth/", "llm/", "metrics", "health", "admin/", "snapshots", "build", "consistency", "pfs", "verification", "assets/", "assistant/"
        )) or full_path in ("robots.txt", "sitemap.xml"):
            raise HTTPException(status_code=404, detail="Not found")
        
        file_path = frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        else:
            # Return index.html for client-side routing
            return FileResponse(str(frontend_dist / "index.html"))

# Compliance status endpoint for medical/scientific workspaces
@app.get("/api/compliance/status")
async def get_compliance_status(
    request: Request,
    profile: str = "default"
):
    """
    Check compliance status for a workspace profile.
    Used by frontend to show upgrade prompts for medical/scientific workspaces.
    """
    from backend.middleware.compliance_enforcer import WorkspaceProfile
    
    try:
        workspace_profile = WorkspaceProfile(profile.lower())
    except ValueError:
        return {"error": f"Invalid profile: {profile}"}
    
    user_tier = ComplianceEnforcer.get_user_tier(request)
    return ComplianceEnforcer.get_compliance_status(workspace_profile, user_tier)

app.include_router(setup_wizard_router)
register_auto_assignment_routes(app)

# Simple dev token storage (local file for development only)
DEV_TOKENS_FILE = Path(__file__).resolve().parent.parent / '.dev_tokens.json'

def read_dev_tokens() -> Dict[str, str]:
    try:
        if DEV_TOKENS_FILE.exists():
            return json.loads(DEV_TOKENS_FILE.read_text())
    except Exception:
        pass
    return {}

def write_dev_tokens(tokens: Dict[str, str]):
    try:
        DEV_TOKENS_FILE.write_text(json.dumps(tokens))
    except Exception as e:
        print('Failed to write dev tokens:', e)


class TokenRequest(BaseModel):
    provider: str
    token: str


@app.post('/auth/token/pat')
def save_pat(req: TokenRequest = Body(...)):
    """Save a Personal Access Token for a provider (dev-only).

    Body: { provider: 'github'|'openai', token: 'xxxxx' }
    """
    provider = req.provider
    token = req.token
    if not provider or not token:
        raise HTTPException(status_code=400, detail='provider and token required')
    tokens = read_dev_tokens()
    tokens[provider] = token
    write_dev_tokens(tokens)
    return { 'status': 'ok', 'provider': provider }


@app.get('/auth/token/{provider}')
def get_token(provider: str):
    tokens = read_dev_tokens()
    t = tokens.get(provider)
    if not t:
        return { 'status': 'missing' }
    # mask token for safety
    masked = t[:6] + '...' + t[-4:] if len(t) > 12 else '****'
    return { 'status': 'ok', 'provider': provider, 'token_masked': masked }


@app.delete('/auth/token/{provider}')
def delete_token(provider: str):
    tokens = read_dev_tokens()
    if provider in tokens:
        tokens.pop(provider)
        write_dev_tokens(tokens)
    return { 'status': 'ok', 'provider': provider }


@app.post('/auth/token/validate')
def validate_token(req: TokenRequest = Body(...)):
    provider = req.provider
    token = req.token
    if provider == 'github':
        # Use stdlib to avoid extra dependencies
        import urllib.request
        import json as _json
        request_obj = urllib.request.Request('https://api.github.com/user')
        request_obj.add_header('Authorization', f'token {token}')
        request_obj.add_header('Accept', 'application/vnd.github.v3+json')
        try:
            with urllib.request.urlopen(request_obj, timeout=5) as resp:
                body = resp.read().decode('utf-8')
                j = _json.loads(body)
                return {'status': 'ok', 'provider': 'github', 'username': j.get('login')}
        except urllib.error.HTTPError as he:
            try:
                body = he.read().decode('utf-8')
            except Exception:
                body = ''
            return {'status': 'error', 'code': he.code, 'body': body}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    elif provider == 'openai':
        import urllib.request
        request_obj = urllib.request.Request('https://api.openai.com/v1/models')
        request_obj.add_header('Authorization', f'Bearer {token}')
        try:
            with urllib.request.urlopen(request_obj, timeout=5) as resp:
                return {'status': 'ok', 'provider': 'openai'}
        except urllib.error.HTTPError as he:
            try:
                body = he.read().decode('utf-8')
            except Exception:
                body = ''
            return {'status': 'error', 'code': he.code, 'body': body}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    else:
        raise HTTPException(status_code=400, detail='unknown provider')

    # Duplicate HealthCheckResponse definition removed (defined earlier around initial health endpoint).


# OAuth configuration (read from env)
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID', '')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET', '')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')


@app.get("/")
def root():
    """Landing page with API information"""
    return {
        "app": "Top Dog (Aura) IDE",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "api_docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "llm_pool": "/llm-pool",
            "llm_report": "/llm-report",
        },
        "message": "Welcome to Top Dog (Aura) IDE API"
    }




# SEO endpoints: robots.txt and sitemap.xml
@app.get("/robots.txt", response_class=PlainTextResponse)
def robots_txt():
    primary = os.getenv("CANONICAL_HOST", "topdog-ide.com")
    others = _parse_list_env("SITEMAP_HOSTS", ["www.topdog-ide.com"])  # additional hosts for sitemap lines
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: https://{primary}/sitemap.xml",
    ]
    for h in others:
        if h and h != primary:
            lines.append(f"Sitemap: https://{h}/sitemap.xml")
    # Disallow internal or ephemeral paths if configured
    disallow_paths = _parse_list_env("ROBOTS_DISALLOW", [])
    for p in disallow_paths:
        lines.append(f"Disallow: {p}")
    return "\n".join(lines) + "\n"


@app.get("/sitemap.xml", response_class=PlainTextResponse)
def sitemap_xml():
    primary = os.getenv("CANONICAL_HOST", "topdog-ide.com")
    base_urls = [primary]
    for h in _parse_list_env("SITEMAP_HOSTS", ["www.topdog-ide.com"]):
        if h and h not in base_urls:
            base_urls.append(h)
    # Minimal URL set; extend as needed
    # Public marketing & product pages for sitemap (expand as needed)
    paths = [
        "/",
        "/health",
        "/features",
        "/pricing",
        "/how-it-works",
        "/security",
        "/blog",
        "/docs",
        "/support",
        "/contact",
        "/features/ai-pair-programming",
        "/features/code-refactoring",
        "/features/security-scanning",
        "/features/debugging",
        "/features/test-generation",
        "/pricing/free",
        "/pricing/pro",
        "/pricing/teams",
        "/pricing/enterprise",
        "/top-dog-ide",
        "/q-ide"  # legacy brand landing retained intentionally
    ]
    entries = []
    now = datetime.utcnow().strftime("%Y-%m-%d")
    for host in base_urls:
        for p in paths:
            loc = f"https://{host}{p}"
            entries.append(f"    <url><loc>{loc}</loc><lastmod>{now}</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>")
    xml = "\n".join([
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
        "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">",
        *entries,
        "</urlset>",
    ])
    from fastapi import Response
    return Response(content=xml, media_type="application/xml")


# Bing verification explicit endpoint (works even without frontend assets)
@app.get("/BingSiteAuth.xml", response_class=PlainTextResponse)
def bing_site_auth():
    token = os.getenv("BING_SITE_VERIFICATION_TOKEN")
    if not token:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")
    from fastapi import Response
    xml = (
        "<?xml version=\"1.0\"?>\n"
        f"<users><user>{token}</user></users>\n"
    )
    return Response(content=xml, media_type="application/xml")


# Google verification explicit endpoint (independent of frontend mount)
@app.get("/google{token}.html", response_class=PlainTextResponse)
def google_site_verification(token: str):
    expected = os.getenv("GOOGLE_SITE_VERIFICATION_TOKEN")
    if not expected or token != expected:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")
    return f"google-site-verification: {token}"


# SEO landing pages for brand queries
@app.get("/top-dog-ide", response_class=PlainTextResponse)
def top_dog_landing():
    canonical = os.getenv("CANONICAL_HOST", "topdog-ide.com")
    org_jsonld = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Top Dog IDE (Q‑IDE)",
        "url": f"https://{canonical}/",
        "logo": f"https://{canonical}/assets/logo.png"
    }
    app_jsonld = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "Top Dog IDE",
        "applicationCategory": "DeveloperApplication",
        "operatingSystem": "Windows, macOS, Linux",
        "offers": {"@type": "Offer", "price": "0"}
    }
    html = (
        "<!doctype html><html lang=\"en\"><head>"
        "<meta charset=\"utf-8\">"
        "<title>Top Dog IDE (Q‑IDE) — AI Development Environment</title>"
        f"<link rel=\"canonical\" href=\"https://{canonical}/\">"
        "<meta name=\"description\" content=\"Top Dog IDE — also known as Q‑IDE — AI IDE with 53+ LLMs for coding, refactoring, debugging.\">"
        f"<script type=\"application/ld+json\">{json.dumps(org_jsonld)}</script>"
        f"<script type=\"application/ld+json\">{json.dumps(app_jsonld)}</script>"
        "</head><body>"
        "<h1>Top Dog IDE (Q‑IDE)</h1>"
        "<p>Top Dog IDE — also known as Q‑IDE — is an AI IDE for developers. Build faster with Aura Development.</p>"
        "<p><a href=\"/\">Go to homepage</a></p>"
        "</body></html>"
    )
    return html


@app.get("/q-ide", response_class=PlainTextResponse)
def q_ide_landing():
    canonical = os.getenv("CANONICAL_HOST", "topdog-ide.com")
    website_jsonld = {
        "@context": "https://schema.org",
        "@type": "Website",
        "name": "Top Dog IDE (Q‑IDE)",
        "url": f"https://{canonical}/"
    }
    html = (
        "<!doctype html><html lang=\"en\"><head>"
        "<meta charset=\"utf-8\">"
        "<title>Q‑IDE (Top Dog IDE) — AI IDE</title>"
        f"<link rel=\"canonical\" href=\"https://{canonical}/\">"
        "<meta name=\"description\" content=\"Q‑IDE (Top Dog IDE): AI development environment with 53+ LLMs.\">"
        f"<script type=\"application/ld+json\">{json.dumps(website_jsonld)}</script>"
        "</head><body>"
        "<h1>Q‑IDE (Top Dog IDE)</h1>"
        "<p>Q‑IDE (Top Dog IDE) is an AI IDE with refactoring, debugging, and 53+ large language models.</p>"
        "<p><a href=\"/\">Go to homepage</a></p>"
        "</body></html>"
    )
    return html


@app.get("/auth/status")
def get_auth_status(session_id: Optional[str] = None):
    """Get current user profile and linked accounts."""
    if not session_id:
        return {"status": "unauthenticated"}
    user_id = get_session_user(session_id)
    if not user_id:
        return {"status": "unauthenticated"}
    user = get_user(user_id)
    if not user:
        return {"status": "error"}
    linked = get_linked_accounts(user_id)
    return {
        "status": "authenticated",
        "user": user,
        "linked_accounts": {provider: {"provider_user": acc.get("provider_user")} for provider, acc in linked.items()},
    }


@app.get("/auth/google/start")
def google_oauth_start():
    """Redirect to Google OAuth consent screen."""
    if not GOOGLE_CLIENT_ID:
        return {"status": "error", "message": "GOOGLE_CLIENT_ID not set"}
    scope = "openid profile email"
    redirect_uri = f"{BACKEND_URL}/auth/google/callback"
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={GOOGLE_CLIENT_ID}&redirect_uri={urllib.parse.quote(redirect_uri)}&response_type=code&scope={urllib.parse.quote(scope)}"
    return {"auth_url": auth_url}


@app.get("/auth/google/callback")
def google_oauth_callback(code: Optional[str] = None, error: Optional[str] = None):
    """Handle Google OAuth callback."""
    if error:
        callback_url = f"/static/oauth-callback.html?status=error&message={urllib.parse.quote(error)}&provider=google"
        return RedirectResponse(url=callback_url)
    if not code:
        callback_url = f"/static/oauth-callback.html?status=error&message={urllib.parse.quote('No code provided')}&provider=google"
        return RedirectResponse(url=callback_url)

    redirect_uri = f"{BACKEND_URL}/auth/google/callback"
    token_data = exchange_code_for_token(
        code, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, redirect_uri,
        "https://oauth2.googleapis.com/token"
    )
    if not token_data or "access_token" not in token_data:
        callback_url = f"/static/oauth-callback.html?status=error&message={urllib.parse.quote('Failed to exchange code')}&provider=google"
        return RedirectResponse(url=callback_url)

    user_info = get_google_user_info(token_data['access_token'])
    if not user_info:
        callback_url = f"/static/oauth-callback.html?status=error&message={urllib.parse.quote('Failed to fetch user info')}&provider=google"
        return RedirectResponse(url=callback_url)

    google_id = user_info['id']
    email = user_info.get('email', '')
    name = user_info.get('name', 'User')
    picture = user_info.get('picture', '')

    create_or_get_user(google_id, email, name, picture)
    session_id = create_session(google_id)

    # Redirect to callback page with session_id
    callback_url = f"/static/oauth-callback.html?status=success&session_id={session_id}&provider=google&email={urllib.parse.quote(email)}&name={urllib.parse.quote(name)}&picture={urllib.parse.quote(picture)}"
    return RedirectResponse(url=callback_url)


@app.get("/auth/github/start")
def github_oauth_start(session_id: Optional[str] = None):
    """Redirect to GitHub OAuth consent screen."""
    if not GITHUB_CLIENT_ID:
        return {"status": "error", "message": "GITHUB_CLIENT_ID not set"}
    scope = "user:email repo"
    redirect_uri = f"{BACKEND_URL}/auth/github/callback"
    auth_url = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&redirect_uri={urllib.parse.quote(redirect_uri)}&scope={urllib.parse.quote(scope)}&state={session_id or ''}"
    return {"auth_url": auth_url}


@app.get("/auth/github/callback")
def github_oauth_callback(code: Optional[str] = None, error: Optional[str] = None, state: Optional[str] = None):
    """Handle GitHub OAuth callback; state contains session_id for account linking."""
    if error:
        callback_url = f"/static/oauth-callback.html?status=error&message={urllib.parse.quote(error)}&provider=github"
        return RedirectResponse(url=callback_url)
    if not code:
        callback_url = f"/static/oauth-callback.html?status=error&message={urllib.parse.quote('No code provided')}&provider=github"
        return RedirectResponse(url=callback_url)

    redirect_uri = f"{BACKEND_URL}/auth/github/callback"
    token_data = exchange_code_for_token(
        code, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, redirect_uri,
        "https://github.com/login/oauth/access_token"
    )
    if not token_data or "access_token" not in token_data:
        callback_url = f"/static/oauth-callback.html?status=error&message={urllib.parse.quote('Failed to exchange code')}&provider=github"
        return RedirectResponse(url=callback_url)

    github_token = token_data['access_token']
    user_info = get_github_user_info(github_token)
    if not user_info:
        callback_url = f"/static/oauth-callback.html?status=error&message={urllib.parse.quote('Failed to fetch GitHub user info')}&provider=github"
        return RedirectResponse(url=callback_url)

    # Link the GitHub account to the current user (if state/session_id provided)
    github_username = user_info.get('login', 'user')
    if state:
        user_id = get_session_user(state)
        if user_id:
            link_account(user_id, "github", github_username, github_token, "user:email repo")
            callback_url = f"/static/oauth-callback.html?status=success&session_id={state}&provider=github&username={urllib.parse.quote(github_username)}"
        else:
            callback_url = f"/static/oauth-callback.html?status=error&message={urllib.parse.quote('Invalid session')}&provider=github"
    else:
        # No state; create new session for GitHub sign-in
        session_id = create_session(github_username)
        callback_url = f"/static/oauth-callback.html?status=success&session_id={session_id}&provider=github&username={urllib.parse.quote(github_username)}"
    
    return RedirectResponse(url=callback_url)



# LLM Pool endpoint - MOVED TO BEFORE FRONTEND CATCH-ALL


# Agent orchestration endpoint
 

class AgentTaskRequest(BaseModel):
    task_type: str
    input_data: dict

class AgentTaskResponse(BaseModel):
    status: str
    message: str
    used_model: Optional[str] = None
    result: Optional[dict] = None

class LLMSelectionRequest(BaseModel):
    llm_id: str
    role: Optional[str] = None  # default to 'coding' if not provided

@app.post("/llm/select")
def select_llm(req: LLMSelectionRequest):
    """Persist a user-selected LLM by assigning it to a role (default 'coding').

    This promotes localStorage selection to server-side config so multi-device sessions
    and Q Assistant auto-selection honor the choice.
    """
    try:
        role = (req.role or "coding").strip()
        from backend.llm_config import save_role_assignment, list_available_providers
        providers = list_available_providers()
        if req.llm_id not in providers:
            return JSONResponse(status_code=404, content={"error": f"Unknown LLM: {req.llm_id}"})
        if role not in ["coding", "q_assistant", "analysis", "testing", "local"]:
            # Allow minimal controlled set; could expand later
            return JSONResponse(status_code=400, content={"error": f"Unsupported role: {role}"})
        ok = save_role_assignment(role, req.llm_id)
        if not ok:
            return JSONResponse(status_code=500, content={"error": "Failed to persist assignment"})
        return {"status": "ok", "role": role, "llm_id": req.llm_id}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/agent/orchestrate")
def orchestrate_agent_task(req_body: AgentTaskRequest, req: Request):
    # Safety prefilter and hallucination severity
    try:
        prompt = None
        if isinstance(req_body.input_data, dict):
            prompt = req_body.input_data.get("prompt")
        if prompt:
            from backend.services.safety_prefilter import evaluate_prompt
            decision = evaluate_prompt(str(prompt))
            # Export hallucination severity regardless of allow/deny
            try:
                from backend.metrics import HALLUCINATION_SEVERITY
                if HALLUCINATION_SEVERITY is not None:
                    HALLUCINATION_SEVERITY.labels(
                        component="orchestrator",
                        plan=_plan_label(req),
                        data_segment=_segment_label(req)
                    ).set(float(decision.get("severity", 0.0)))
            except Exception:
                pass
            if not decision.get("safe", True):
                try:
                    from backend.metrics import record_llm_request
                    if record_llm_request is not None:
                        record_llm_request(outcome="blocked", failure_cost_usd=1.0)
                except Exception:
                    pass
                return AgentTaskResponse(status="error", message="unsafe prompt blocked", result={"reasons": decision.get("reasons", [])})
    except Exception:
        pass
    # Select the best LLM from the pool for the task
    report = build_llm_report()
    pool = report.get("available", [])
    # Prefer orchestrator's failover policy when enabled; fallback to first available
    try:
        endpoint_name = None
        try:
            svc = getattr(app.state, 'orchestration_service', None)  # type: ignore[attr-defined]
        except Exception:
            svc = getattr(app, 'orchestration_service', None)
        if svc is not None and hasattr(svc, 'choose_endpoint'):
            endpoint_name = svc.choose_endpoint({
                "task_type": req_body.task_type,
            })
        if not endpoint_name:
            endpoint_name = os.getenv('DEFAULT_LLM_ENDPOINT', 'primary-llm')
        # Map chosen endpoint name to pool entry
        selected = next((m for m in pool if m.get('name') == endpoint_name), None)
        if selected is None and pool:
            selected = pool[0]
    except Exception:
        selected = pool[0] if pool else None
    if not selected:
        return AgentTaskResponse(status="error", message="No LLMs available", result=None)
    # Simulate task execution (replace with real LLM invocation logic)
    result = {"echo": req_body.input_data}
    # Compute-aware AI budget: adapt depth and tokens
    try:
        from backend.services.ai_budget import compute_budget, Budget
        env_enabled = str(os.getenv("ENABLE_REGULATED_DOMAINS", "true")).lower() in ("1","true","yes")
        edition = "regulated" if env_enabled else "dev"
        max_tokens = int(os.getenv("AI_BUDGET_MAX_TOKENS", "4000"))
        max_tools = int(os.getenv("AI_BUDGET_MAX_TOOLS", "3"))
        max_seconds = float(os.getenv("AI_BUDGET_MAX_SECONDS", "2.0"))
        # Tighter defaults in regulated mode
        if edition == "regulated":
            max_tokens = min(max_tokens, 2000)
            max_tools = min(max_tools, 2)
        budget = Budget(max_tokens=max_tokens, max_tools=max_tools, max_seconds=max_seconds)
        with compute_budget(budget) as bt:
            # Rough token estimate based on prompt length
            est_tokens = 4 * len(str(req_body.input_data).split())
            bt.add_tokens(min(est_tokens, bt.budget.max_tokens))
            # Adaptive tool depth: scale down if close to limits
            tool_depth = 1 if bt.budget.max_tools <= 1 else (2 if bt.budget.max_tools <= 2 else 3)
            if bt.tokens > 0.8 * bt.budget.max_tokens:
                tool_depth = max(1, tool_depth - 1)
            bt.tools = tool_depth
            adapted = {
                "tool_depth": tool_depth,
                "max_tokens": bt.budget.max_tokens,
                "max_tools": bt.budget.max_tools,
                "max_seconds": bt.budget.max_seconds,
                "scaled_down": bt.tokens > 0.8 * bt.budget.max_tokens,
            }
            result["budget"] = {
                "tokens": bt.tokens,
                "tools": bt.tools,
                "seconds": bt.seconds,
                "within_limits": bt.within_limits(),
                "adaptation": adapted,
            }
    except Exception:
        pass
    # Optional: formal verification of reasoning trace
    try:
        trace = None
        if isinstance(req_body.input_data, dict):
            trace = req_body.input_data.get("reasoning_trace")
        if trace:
            from backend.services.formal_verification import FormalVerificationService
            fvs = FormalVerificationService()
            vres = fvs.verify(trace)
            result["verification"] = {
                "ok": vres.ok,
                "proved": vres.proved,
                "missing_goals": vres.missing_goals,
                "steps_checked": vres.steps_checked,
                "errors": vres.errors,
            }
            # Persist verification summary into snapshots if workflow_id provided
            try:
                wf_id = req_body.input_data.get("workflow_id")
                if wf_id:
                    from backend.services.snapshot_store import SnapshotStore
                    store = SnapshotStore()
                    store.save_snapshot(
                        workflow_id=str(wf_id),
                        snapshot={"verification": result["verification"], "ts": datetime.utcnow().isoformat()},
                        label="verification",
                    )
            except Exception:
                pass
    except Exception:
        pass
    # Reliability and cost instrumentation (best-effort)
    try:
        from backend.metrics import record_llm_request
    except Exception:
        record_llm_request = None  # type: ignore
    try:
        failure_cost = 0.0
        # Optional: allow client to pass suggested failure cost in request for modeling
        # e.g., request.input_data["failure_cost_usd"]
        fc = req_body.input_data.get("failure_cost_usd") if isinstance(req_body.input_data, dict) else None
        if isinstance(fc, (int, float)):
            failure_cost = float(fc)
        if record_llm_request is not None:
            record_llm_request(outcome="ok", failure_cost_usd=failure_cost)
    except Exception:
        pass

    # Auto-consistency exporter with real inference when available (budget-aware)
    try:
        if isinstance(req_body.input_data, dict) and req_body.input_data.get("prompt"):
            if os.getenv("ENABLE_AUTOCONSISTENCY", "true").lower() in ("1","true","yes"):
                from backend.services.consistency_scoring import ConsistencyScoringAgent
                from backend.metrics import CONSISTENCY_SCORE
                agent = ConsistencyScoringAgent()
                n = 3
                try:
                    b = result.get("budget", {})
                    if b and b.get("tokens", 0) > 0.8 * b.get("adaptation", {}).get("max_tokens", 4000):
                        n = 2
                except Exception:
                    pass
                def _llm(p: str) -> str:
                    try:
                        from backend.services.inference import llm_infer
                        return llm_infer(p, max_tokens=64)
                    except Exception:
                        return f"{p.strip().lower()} -> {selected.get('name','llm')}"
                prompt_str = str(req_body.input_data.get("prompt", "")) if isinstance(req_body.input_data, dict) else ""
                res = agent.evaluate(prompt_str, _llm, n=n)
                if CONSISTENCY_SCORE is not None:
                    CONSISTENCY_SCORE.labels(
                        component="orchestrator",
                        plan=_plan_label(req),
                        data_segment=_segment_label(req)
                    ).set(float(res.score))
    except Exception:
        pass
    return AgentTaskResponse(status="ok", message="Task processed", used_model=selected.get("name"), result=result)


# --- Consistency Score SLI endpoints ---
class ConsistencyScorePayload(BaseModel):
    score: Optional[float] = None
    outputs: Optional[List[str]] = None
    component: Optional[str] = "orchestrator"


_LAST_CONSISTENCY_SCORE: Optional[float] = None


@app.post("/consistency/sli")
def post_consistency_sli(payload: ConsistencyScorePayload, req: Request):
    global _LAST_CONSISTENCY_SCORE
    try:
        from backend.metrics import CONSISTENCY_SCORE
    except Exception:
        CONSISTENCY_SCORE = None  # type: ignore
    score: Optional[float] = payload.score
    if score is None and payload.outputs:
        try:
            from backend.services.consistency_scoring import ConsistencyScoringAgent
            agent = ConsistencyScoringAgent()
            score = agent.compute_score(payload.outputs)
        except Exception:
            score = None
    if score is None:
        return JSONResponse(status_code=400, content={"error": "score or outputs[] required"})
    _LAST_CONSISTENCY_SCORE = max(0.0, min(1.0, float(score)))
    try:
        if CONSISTENCY_SCORE is not None:
            CONSISTENCY_SCORE.labels(
                component=(payload.component or "orchestrator"),
                plan=_plan_label(req),
                data_segment=_segment_label(req)
            ).set(_LAST_CONSISTENCY_SCORE)
    except Exception:
        pass
    return {"status": "ok", "score": _LAST_CONSISTENCY_SCORE}


@app.get("/consistency/sli")
def get_consistency_sli():
    return {"status": "ok", "score": _LAST_CONSISTENCY_SCORE}


class ConsistencyComputePayload(BaseModel):
    prompt: str
    n: Optional[int] = 3
    component: Optional[str] = "orchestrator"


@app.post("/consistency/compute")
def post_consistency_compute(payload: ConsistencyComputePayload, req: Request):
    try:
        from backend.services.consistency_scoring import ConsistencyScoringAgent
        from backend.metrics import CONSISTENCY_SCORE
    except Exception:
        return JSONResponse(status_code=400, content={"error": "dependencies unavailable"})
    agent = ConsistencyScoringAgent()
    # Dev-mode lightweight mock LLM
    def _mock_llm(p: str) -> str:
        return f"{p.strip().lower()} -> ok"
    res = agent.evaluate(payload.prompt, _mock_llm, n=(payload.n or 3))
    score = max(0.0, min(1.0, float(res.score)))
    try:
        CONSISTENCY_SCORE.labels(
            component=(payload.component or "orchestrator"),
            plan=_plan_label(req),
            data_segment=_segment_label(req)
        ).set(score)
    except Exception:
        pass
    return {"status": "ok", "score": score, "pairwise": res.pairwise}


# --- Player Frustration Score (PFS) ---
class PfsPayload(BaseModel):
    game: Optional[str] = "default"
    score: float


@app.post("/pfs")
def post_pfs(payload: PfsPayload):
    try:
        from backend.metrics import PFS_SCORE
    except Exception:
        PFS_SCORE = None  # type: ignore
    val = max(0.0, min(1.0, float(payload.score)))
    try:
        if PFS_SCORE is not None:
            PFS_SCORE.labels(game=(payload.game or "default")).set(val)
    except Exception:
        pass
    return {"status": "ok", "score": val}


@app.get("/pfs")
def get_pfs(game: str = "default"):
    # We do not maintain last value here beyond Prometheus; endpoint returns OK to avoid tight coupling
    return {"status": "ok", "game": game}


# --- Verification Check endpoint ---
class VerificationPayload(BaseModel):
    reasoning_trace: dict
    invariants: Optional[dict] = None
    workflow_id: Optional[str] = None


@app.post("/verification/check")
def verification_check(payload: VerificationPayload):
    try:
        from backend.services.formal_verification import FormalVerificationService
        from backend.services.attestation import compute_proof_hash
        # Prefer pluggable signer if configured
        try:
            from backend.services.kms import get_signer
            signer = get_signer()
        except Exception:
            signer = None
        fvs = FormalVerificationService()
        vres = fvs.verify(payload.reasoning_trace)
        invariants = payload.invariants or {"goals": payload.reasoning_trace.get("goals", [])}
        proof_hash = compute_proof_hash(invariants)
        artifact = {
            "verification": {
                "ok": vres.ok,
                "proved": vres.proved,
                "missing_goals": vres.missing_goals,
                "steps_checked": vres.steps_checked,
                "errors": vres.errors,
            },
            "invariants": invariants,
            "proof_hash": proof_hash,
        }
        if signer is not None:
            signature, pubkey = signer.sign(artifact)
        else:
            from backend.services.attestation import generate_keypair, get_env_signing_keypair, sign_artifact
            kp = get_env_signing_keypair()
            if kp:
                sk, pk = kp
            else:
                sk, pk = generate_keypair()
            signature, pubkey = sign_artifact(artifact, sk)
        record = {"artifact": artifact, "signature_b64": signature, "public_key_b64": pubkey}

        # Snapshot persist if workflow_id present
        if payload.workflow_id:
            try:
                from backend.services.snapshot_store import SnapshotStore
                SnapshotStore().save_snapshot(str(payload.workflow_id), record, label="attestation")
            except Exception:
                pass
        return {"status": "ok", "attestation": record}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


# --- Hallucination Severity ---
class HallucinationPayload(BaseModel):
    severity: float
    component: Optional[str] = "orchestrator"


@app.post("/hallucination/sli")
def post_hallucination(payload: HallucinationPayload, req: Request):
    try:
        from backend.metrics import HALLUCINATION_SEVERITY
    except Exception:
        HALLUCINATION_SEVERITY = None  # type: ignore
    val = max(0.0, min(1.0, float(payload.severity)))
    try:
        if HALLUCINATION_SEVERITY is not None:
            HALLUCINATION_SEVERITY.labels(
                component=(payload.component or "orchestrator"),
                plan=_plan_label(req),
                data_segment=_segment_label(req)
            ).set(val)
    except Exception:
        pass
    return {"status": "ok", "severity": val}


# --- Assets generation (multimodal orchestration placeholder) ---
class AssetGenPayload(BaseModel):
    spec: dict  # includes constraints like {"poly_count": 2000, "palette": "dark"}
    workflow_id: Optional[str] = None


@app.post("/assets/generate")
def generate_asset(payload: AssetGenPayload):
    import subprocess
    import sys
    import json as _json
    meta = payload.spec or {}
    # Run guardrails first
    try:
        proc = subprocess.run(
            [sys.executable, "tools/pcg_guardrails.py"],
            input=_json.dumps(meta).encode("utf-8"),
            capture_output=True,
            check=False,
        )
        if proc.returncode != 0:
            return JSONResponse(status_code=400, content={"error": proc.stdout.decode("utf-8")})
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"guardrails error: {e}"})

    # Mock asset artifacts and provenance labels
    artifact = {
        "type": "mesh",
        "format": "obj",
        "provenance": {
            "generated_by": "asset-orchestrator",
            "ts": datetime.utcnow().isoformat(),
            "labels": {"poly_count": meta.get("poly_count"), "palette": meta.get("palette")},
        },
        "uri": "s3://bucket/mock/asset.obj",
    }
    if payload.workflow_id:
        try:
            from backend.services.snapshot_store import SnapshotStore
            SnapshotStore().save_snapshot(str(payload.workflow_id), {"asset": artifact}, label="asset")
        except Exception:
            pass
    # Export a high consistency score for deterministic asset build steps
    try:
        from backend.metrics import CONSISTENCY_SCORE
        if CONSISTENCY_SCORE is not None:
            CONSISTENCY_SCORE.labels(
                component="assets",
                plan=_plan_label(None),
                data_segment=_segment_label(None)
            ).set(0.95)
    except Exception:
        pass
    return {"status": "ok", "asset": artifact}


# --- Async Assets generation with manifests ---
class AssetGenAsyncPayload(BaseModel):
    spec: dict
    workflow_id: Optional[str] = None


ASYNC_ASSETS: Dict[str, Dict] = {}


def _ensure_artifacts_dir() -> Path:
    root = Path(__file__).resolve().parent.parent
    d = root / "artifacts"
    d.mkdir(exist_ok=True)
    return d


def _bg_generate_asset(job_id: str, payload: AssetGenAsyncPayload):
    import json as _json
    ASYNC_ASSETS[job_id]["status"] = "running"
    try:
        # Reuse guardrails
        import subprocess
        import sys
        proc = subprocess.run(
            [sys.executable, "tools/pcg_guardrails.py"],
            input=_json.dumps(payload.spec).encode("utf-8"),
            capture_output=True,
            check=False,
        )
        if proc.returncode != 0:
            ASYNC_ASSETS[job_id]["status"] = "failed"
            ASYNC_ASSETS[job_id]["error"] = proc.stdout.decode("utf-8")
            return
        # Create manifest + dummy artifact
        outdir = _ensure_artifacts_dir()
        artifact_path = outdir / f"{job_id}.bin"
        artifact_path.write_bytes(b"mock-bytes")
        manifest = {
            "id": job_id,
            "created_at": datetime.utcnow().isoformat(),
            "provenance": {
                "generated_by": "asset-orchestrator-async",
                "labels": {"poly_count": payload.spec.get("poly_count"), "palette": payload.spec.get("palette")},
            },
            "artifact_uri": str(artifact_path),
        }
        (outdir / f"{job_id}.manifest.json").write_text(_json.dumps(manifest, indent=2))
        ASYNC_ASSETS[job_id]["status"] = "completed"
        ASYNC_ASSETS[job_id]["manifest"] = manifest
        if payload.workflow_id:
            try:
                from backend.services.snapshot_store import SnapshotStore
                SnapshotStore().save_snapshot(str(payload.workflow_id), {"asset_manifest": manifest}, label="asset-manifest")
            except Exception:
                pass
    except Exception as e:
        ASYNC_ASSETS[job_id]["status"] = "failed"
        ASYNC_ASSETS[job_id]["error"] = str(e)


@app.post("/assets/generate-async")
def api_generate_async(payload: AssetGenAsyncPayload, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    ASYNC_ASSETS[job_id] = {"status": "queued"}
    background_tasks.add_task(_bg_generate_asset, job_id, payload)
    return {"status": "ok", "job_id": job_id}


@app.get("/assets/generate-async/{job_id}")
def api_generate_async_status(job_id: str):
    info = ASYNC_ASSETS.get(job_id)
    if not info:
        return JSONResponse(status_code=404, content={"error": "not found"})
    return {"status": "ok", "job": info}


# --- Assets upload with richer provenance ---
@app.post("/assets/generate-async/upload")
async def api_generate_async_upload(background_tasks: BackgroundTasks, file: UploadFile = File(...), workflow_id: Optional[str] = Form(None), spec: Optional[str] = Form(None)):
    job_id = str(uuid.uuid4())
    ASYNC_ASSETS[job_id] = {"status": "queued"}
    # Save file immediately
    outdir = _ensure_artifacts_dir()
    data = await file.read()
    fpath = outdir / f"{job_id}-{file.filename}"
    fpath.write_bytes(data)
    # Compute hash
    import hashlib
    sha256 = hashlib.sha256(data).hexdigest()
    # Parse spec if provided
    try:
        meta = json.loads(spec) if spec else {}
    except Exception:
        meta = {}
    def _bg():
        ASYNC_ASSETS[job_id]["status"] = "running"
        try:
            manifest = {
                "id": job_id,
                "created_at": datetime.utcnow().isoformat(),
                "provenance": {
                    "generated_by": "asset-orchestrator-async",
                    "labels": meta,
                    "dataset_lineage": meta.get("dataset_lineage", []),
                    "sbom": meta.get("sbom", {}),
                },
                "inputs": {
                    "upload": {
                        "filename": file.filename,
                        "sha256": sha256,
                        "size": len(data),
                    }
                },
                "artifact_uri": str(fpath),
            }
            (outdir / f"{job_id}.manifest.json").write_text(json.dumps(manifest, indent=2))
            ASYNC_ASSETS[job_id]["status"] = "completed"
            ASYNC_ASSETS[job_id]["manifest"] = manifest
            if workflow_id:
                try:
                    from backend.services.snapshot_store import SnapshotStore
                    SnapshotStore().save_snapshot(str(workflow_id), {"asset_manifest": manifest}, label="asset-manifest")
                except Exception:
                    pass
        except Exception as e:
            ASYNC_ASSETS[job_id]["status"] = "failed"
            ASYNC_ASSETS[job_id]["error"] = str(e)
    background_tasks.add_task(_bg)
    return {"status": "ok", "job_id": job_id, "file": {"name": file.filename, "sha256": sha256}}


# --- Deterministic seed and commitment ---
class DeterminismPayload(BaseModel):
    game_state: dict
    inputs: dict
    agent_config: Optional[dict] = None
    workflow_id: Optional[str] = None


@app.post("/determinism/seed")
def post_determinism_seed(payload: DeterminismPayload):
    try:
        from backend.services.determinism import derive_seed, commitment
        full = {
            "game_state": payload.game_state,
            "inputs": payload.inputs,
            "agent_config": payload.agent_config or {},
        }
        seed = derive_seed(full)
        commit = commitment(full)
        record = {"seed": seed, "commitment": commit}
        if payload.workflow_id:
            try:
                from backend.services.snapshot_store import SnapshotStore
                SnapshotStore().save_snapshot(str(payload.workflow_id), record, label="determinism")
            except Exception:
                pass
        return {"status": "ok", **record}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


# Simple in-memory snapshot store for demo purposes
SNAPSHOT_STORE: Dict[int, Dict] = {
    1: {"id": 1, "status": "pending"},
    2: {"id": 2, "status": "pending"},
    3: {"id": 3, "status": "pending"},
}


@app.post("/snapshots/{snapshot_id}/approve")
async def approve_snapshot(snapshot_id: int):
    # Simulate processing time
    import asyncio
    await asyncio.sleep(0.4)
    if snapshot_id not in SNAPSHOT_STORE:
        return {"status": "error", "message": "Snapshot not found"}
    # Simulate a possible server error for id 999 (used in tests) or query param
    # For real world, add auth & persistence here
    SNAPSHOT_STORE[snapshot_id]["status"] = "approved"
    return {"status": "ok", "snapshot": SNAPSHOT_STORE[snapshot_id]}


@app.post("/snapshots/{snapshot_id}/request-change")
async def request_change_snapshot(snapshot_id: int):
    import asyncio
    await asyncio.sleep(0.4)
    if snapshot_id not in SNAPSHOT_STORE:
        return {"status": "error", "message": "Snapshot not found"}
    SNAPSHOT_STORE[snapshot_id]["status"] = "requested"
    return {"status": "ok", "snapshot": SNAPSHOT_STORE[snapshot_id]}


# --- Simple local build runner (dev spike) ---

# In-memory build queue store
BUILD_STORE: Dict[str, Dict] = {}


def run_local_build(build_id: str):
    """Runs the local build script and captures output into BUILD_STORE."""
    BUILD_STORE[build_id]["status"] = "running"
    BUILD_STORE[build_id]["log"] = ""
    try:
        # Run the project's run_tests.py script which exists in build-health/
        script = Path(__file__).resolve().parent.parent / 'build-health' / 'run_tests.py'
        if not script.exists():
            BUILD_STORE[build_id]["status"] = "error"
            BUILD_STORE[build_id]["log"] = f"Build script not found: {script}"
            return
        # Execute the script and stream output
        proc = subprocess.Popen([sys.executable, str(script)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if proc.stdout is not None:
            for line in proc.stdout:
                BUILD_STORE[build_id]["log"] += line
        proc.wait()
        BUILD_STORE[build_id]["status"] = "success" if proc.returncode == 0 else "failed"
    except Exception as e:
        BUILD_STORE[build_id]["status"] = "error"
        BUILD_STORE[build_id]["log"] += f"\nException: {e}"


@app.post("/build/run")
def api_run_build(background_tasks: BackgroundTasks):
    """Enqueue and run a local build; returns a build id for polling."""
    bid = str(uuid.uuid4())
    BUILD_STORE[bid] = {"id": bid, "status": "queued", "log": ""}
    # Schedule background execution
    background_tasks.add_task(run_local_build, bid)
    return {"status": "ok", "build_id": bid}


@app.get("/build/{build_id}")
def api_get_build(build_id: str):
    info = BUILD_STORE.get(build_id)
    if not info:
        return {"status": "error", "message": "build not found"}
    return {"status": "ok", "build": info}


@app.get("/llm/learning/builds")
def get_builds_for_learning(limit: int = 20, skip: int = 0, session_id: Optional[str] = None):
    """Get build history for LLM learning.
    
    Returns recent builds with their metadata, status, and output.
    Used by coding LLMs to learn from build patterns and failures.
    """
    if session_id and not get_session_user(session_id):
        return {"status": "error", "message": "unauthorized"}
    
    builds = list(BUILD_STORE.values())
    builds_sorted = sorted(builds, key=lambda b: str(b.get("id", "")), reverse=True)
    paginated = builds_sorted[skip:skip+limit]
    
    return {
        "status": "ok",
        "builds": paginated,
        "total": len(builds),
        "skip": skip,
        "limit": limit
    }


@app.get("/llm/learning/build/{build_id}")
def get_build_learning_data(build_id: str, session_id: Optional[str] = None):
    """Get detailed build data for LLM learning including logs, metadata, and runtime info.
    
    Response includes:
    - Build metadata (id, status, created_at, duration)
    - Full build log/output
    - Build context (which test/command was run)
    - Failure analysis (if applicable)
    """
    if session_id and not get_session_user(session_id):
        return {"status": "error", "message": "unauthorized"}
    
    build = BUILD_STORE.get(build_id)
    if not build:
        return {"status": "error", "message": "build not found"}
    
    # Analyze the log for errors and warnings
    log_lines = build.get("log", "").split("\n")
    errors = [line for line in log_lines if "error" in line.lower() or "failed" in line.lower()]
    warnings = [line for line in log_lines if "warning" in line.lower()]
    
    return {
        "status": "ok",
        "build": {
            "id": build.get("id"),
            "status": build.get("status"),
            "log": build.get("log"),
            "log_summary": {
                "total_lines": len(log_lines),
                "error_count": len(errors),
                "warning_count": len(warnings),
                "errors": errors[:10],  # First 10 errors
                "warnings": warnings[:10],  # First 10 warnings
            }
        }
    }


@app.get("/llm/learning/codebase")
def get_codebase_for_learning(session_id: Optional[str] = None):
    """Get codebase structure and key files for LLM learning.
    
    Returns:
    - Project structure (folders and file tree)
    - Key source files (Python, TypeScript, etc.)
    - Configuration files (package.json, pyproject.toml, etc.)
    - Build scripts and test runners
    
    Used by coding LLMs to understand the project structure and build system.
    """
    if session_id and not get_session_user(session_id):
        return {"status": "error", "message": "unauthorized"}
    
    workspace_root = Path(__file__).resolve().parent.parent
    
    def get_file_tree(path, max_depth=3, current_depth=0, ignore_dirs={'.venv', '.git', 'node_modules', '__pycache__', '.pytest_cache', 'dist', 'build'}):
        """Recursively build file tree structure."""
        if current_depth >= max_depth:
            return None
        
        try:
            items = []
            for item in sorted(path.iterdir()):
                if item.name.startswith('.') and item.name not in {'.gitignore', '.env'}:
                    continue
                if item.is_dir() and item.name in ignore_dirs:
                    continue
                
                if item.is_file():
                    items.append({
                        "type": "file",
                        "name": item.name,
                        "path": str(item.relative_to(workspace_root)),
                        "size": item.stat().st_size
                    })
                elif item.is_dir():
                    subtree = get_file_tree(item, max_depth, current_depth + 1, ignore_dirs)
                    if subtree:
                        items.append({
                            "type": "directory",
                            "name": item.name,
                            "path": str(item.relative_to(workspace_root)),
                            "children": subtree
                        })
            return items
        except Exception:
            return None
    
    # Get key config files
    key_files = {}
    config_files = [
        'package.json', 'pyproject.toml', 'setup.py', 'tsconfig.json',
        'vite.config.ts', 'pytest.ini', 'Dockerfile', '.env.example'
    ]
    
    for config_file in config_files:
        config_path = workspace_root / config_file
        if config_path.exists() and config_path.is_file():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    key_files[config_file] = f.read()[:2000]  # First 2000 chars
            except Exception:
                pass
    
    # Get backend Python files
    backend_files = []
    backend_dir = workspace_root / 'backend'
    if backend_dir.exists():
        for py_file in backend_dir.glob('*.py'):
            if py_file.name != '__pycache__':
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        backend_files.append({
                            "name": py_file.name,
                            "path": str(py_file.relative_to(workspace_root)),
                            "lines": len(content.split('\n')),
                            "preview": content[:500]  # First 500 chars
                        })
                except Exception:
                    pass
    
    return {
        "status": "ok",
        "codebase": {
            "workspace_root": str(workspace_root),
            "file_tree": get_file_tree(workspace_root),
            "key_config_files": key_files,
            "backend_files": backend_files,
            "structure_summary": {
                "has_backend": (workspace_root / 'backend').exists(),
                "has_frontend": (workspace_root / 'frontend').exists(),
                "has_tests": (workspace_root / 'backend').exists() and any((workspace_root / 'backend').glob('test_*.py')),
            }
        }
    }


@app.post("/llm/learning/report")
def submit_llm_learning_report(request_body: dict, session_id: Optional[str] = None):
    """LLM submits analysis/learning report about a build or codebase.
    
    Example body:
    {
        "build_id": "uuid",
        "type": "failure_analysis" | "code_improvement" | "test_coverage",
        "analysis": "detailed findings",
        "recommendations": ["rec1", "rec2"],
        "confidence": 0.85
    }
    
    This allows your coding LLM to record its learnings and insights.
    """
    if session_id and not get_session_user(session_id):
        return {"status": "error", "message": "unauthorized"}
    
    try:
        build_id_val = request_body.get("build_id")
        if not isinstance(build_id_val, str):
            return {"status": "error", "message": "build_id must be a string"}
        build_id = build_id_val
        report_type = request_body.get("type")
        analysis = request_body.get("analysis")
        recommendations = request_body.get("recommendations", [])
        confidence = request_body.get("confidence", 0.5)
        
        if not all([build_id, report_type, analysis]):
            return {"status": "error", "message": "missing required fields"}
        
        # Store the report with the build
        build = BUILD_STORE.get(build_id)
        if build:
            if "llm_reports" not in build:
                build["llm_reports"] = []
            
            report = {
                "type": report_type,
                "analysis": analysis,
                "recommendations": recommendations,
                "confidence": confidence,
                "timestamp": str(Path(__file__).resolve())
            }
            build["llm_reports"].append(report)
            
            return {
                "status": "ok",
                "message": "report stored",
                "report_id": len(build["llm_reports"]) - 1
            }
        else:
            return {"status": "error", "message": "build not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# --- LLM Streaming Endpoint ---
 

async def fake_llm_stream(prompt: str):
    # Simulate streaming LLM output in chunks
    chunks = ["Hello, ", "world!", " This is a streamed response."]
    for i, chunk in enumerate(chunks):
        data = {
            "data": chunk,
            "done": i == len(chunks) - 1
        }
        yield f"data: {json.dumps(data)}\n\n"
        await asyncio.sleep(0.5)

@app.post("/llm_stream")
async def llm_stream(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "")
    # Replace fake_llm_stream with real LLM streaming logic as needed
    return StreamingResponse(fake_llm_stream(prompt), media_type="text/event-stream")

# --- Prometheus Metrics Endpoint ---
try:
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

    @app.get("/metrics")
    async def metrics():
        data = generate_latest()
        return PlainTextResponse(content=data.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)
except Exception as e:
    logger.warning(f"Prometheus /metrics not enabled: {e}")


# Removed deprecated startup_event; logic moved to lifespan handler above


def _run_dev_server() -> None:
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    _run_dev_server()
