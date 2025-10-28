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
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
from typing import List, Dict
from llm_pool import build_llm_pool, build_llm_report, get_best_llms_for_operations
from llm_config_routes import router as llm_config_router
from llm_auth_routes import router as llm_auth_router
from llm_chat_routes import router as llm_chat_router
from build_orchestration_routes import router as build_orchestration_router
from llm_oauth_routes import router as llm_oauth_router
from logger_utils import configure_logger, get_logger
from auto_setup_q_assistant import auto_setup_q_assistant
from llm_auto_auth import check_all_llm_authentication, get_startup_auth_prompt
from auth import (
    create_session, get_session_user, get_user, create_or_get_user,
    exchange_code_for_token, get_google_user_info, get_github_user_info,
    link_account, get_linked_accounts
)

# Initialize logger early
logger = configure_logger(
    name="q-ide-topdog",
    log_dir="./logs",
    level=logging.INFO
)

logger.info("Q-IDE Backend starting up...")

app = FastAPI(
    title="Q-IDE Backend",
    description="Production-ready API for TopDog IDE",
    version="0.1.0"
)

# Security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", os.getenv("ALLOWED_HOST", "localhost")])

# Logging middleware - must be added before other middleware
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        import time
        start_time = time.time()
        
        with logger.context(
            request_id=request.headers.get("X-Request-ID", "unknown"),
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else "unknown"
        ):
            try:
                response = await call_next(request)
                elapsed = time.time() - start_time
                if response.status_code >= 400:
                    logger.warning(
                        f"Request completed with error",
                        status_code=response.status_code,
                        elapsed_seconds=elapsed
                    )
                else:
                    logger.debug(
                        f"Request completed",
                        status_code=response.status_code,
                        elapsed_seconds=elapsed
                    )
                return response
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(
                    f"Request failed",
                    error=e,
                    elapsed_seconds=elapsed
                )
                raise

app.add_middleware(LoggingMiddleware)

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Serve static files for OAuth callback
frontend_static = Path(__file__).resolve().parent.parent / "frontend" / "public"
if frontend_static.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_static)), name="static")

# CORS configuration
cors_origins = [
    "http://localhost:1431",
    "http://127.0.0.1:1431",
    "http://localhost:3000",
]
if os.getenv("ENVIRONMENT") == "production":
    cors_origins = [os.getenv("FRONTEND_URL", "https://q-ide.com")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import HTTPException, Body
import json

app.add_middleware(LoggingMiddleware)

# Include LLM configuration routers
app.include_router(llm_config_router)
app.include_router(llm_auth_router)
app.include_router(llm_chat_router)
app.include_router(build_orchestration_router)
app.include_router(llm_oauth_router)

# Include setup wizard and auto-assignment routers
from setup_wizard import router as setup_wizard_router
from llm_auto_assignment import register_auto_assignment_routes

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
        req = urllib.request.Request('https://api.github.com/user')
        req.add_header('Authorization', f'token {token}')
        req.add_header('Accept', 'application/vnd.github.v3+json')
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
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
        req = urllib.request.Request('https://api.openai.com/v1/models')
        req.add_header('Authorization', f'Bearer {token}')
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
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

class HealthCheckResponse(BaseModel):
    status: str
    version: str


# OAuth configuration (read from env)
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID', '')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET', '')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')


@app.get("/health", response_model=HealthCheckResponse)
def health_check():
    return HealthCheckResponse(status="ok", version=sys.version)


@app.get("/auth/status")
def get_auth_status(session_id: str = None):
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
def google_oauth_callback(code: str = None, error: str = None):
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
def github_oauth_start(session_id: str = None):
    """Redirect to GitHub OAuth consent screen."""
    if not GITHUB_CLIENT_ID:
        return {"status": "error", "message": "GITHUB_CLIENT_ID not set"}
    scope = "user:email repo"
    redirect_uri = f"{BACKEND_URL}/auth/github/callback"
    auth_url = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&redirect_uri={urllib.parse.quote(redirect_uri)}&scope={urllib.parse.quote(scope)}&state={session_id or ''}"
    return {"auth_url": auth_url}


@app.get("/auth/github/callback")
def github_oauth_callback(code: str = None, error: str = None, state: str = None):
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



# LLM Pool endpoint
@app.get("/llm_pool")
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


# Agent orchestration endpoint
from fastapi import Body
from llm_pool import build_llm_pool

class AgentTaskRequest(BaseModel):
    task_type: str
    input_data: dict

class AgentTaskResponse(BaseModel):
    status: str
    message: str
    used_model: str = None
    result: dict = None

@app.post("/agent/orchestrate", response_model=AgentTaskResponse)
def orchestrate_agent_task(request: AgentTaskRequest = Body(...)):
    # Select the best LLM from the pool for the task
    report = build_llm_report()
    pool = report.get("available", [])
    # For now, just pick the first available model (extend with smarter logic as needed)
    selected = pool[0] if pool else None
    if not selected:
        return AgentTaskResponse(status="error", message="No LLMs available", result=None)
    # Simulate task execution (replace with real LLM invocation logic)
    result = {"echo": request.input_data}
    return AgentTaskResponse(status="ok", message="Task processed", used_model=selected.get("name"), result=result)


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
from fastapi import BackgroundTasks
import uuid
import subprocess
from pathlib import Path

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
def get_builds_for_learning(limit: int = 20, skip: int = 0, session_id: str = None):
    """Get build history for LLM learning.
    
    Returns recent builds with their metadata, status, and output.
    Used by coding LLMs to learn from build patterns and failures.
    """
    if session_id and not get_session_user(session_id):
        return {"status": "error", "message": "unauthorized"}
    
    builds = list(BUILD_STORE.values())
    builds_sorted = sorted(builds, key=lambda b: b.get("id"), reverse=True)
    paginated = builds_sorted[skip:skip+limit]
    
    return {
        "status": "ok",
        "builds": paginated,
        "total": len(builds),
        "skip": skip,
        "limit": limit
    }


@app.get("/llm/learning/build/{build_id}")
def get_build_learning_data(build_id: str, session_id: str = None):
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
def get_codebase_for_learning(session_id: str = None):
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
        except Exception as e:
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
            except:
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
                except:
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
def submit_llm_learning_report(request_body: dict, session_id: str = None):
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
        build_id = request_body.get("build_id")
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
from fastapi import Request
from fastapi.responses import StreamingResponse
import asyncio
import json

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


@app.on_event("startup")
async def startup_event():
    """Auto-setup Q Assistant and check LLM authentication on startup"""
    logger.info("Running startup tasks...")
    
    # Auto-setup Q Assistant if needed
    try:
        result = auto_setup_q_assistant()
        if result:
            logger.info(f"✓ Q Assistant auto-configured with: {result.get('name')}")
        else:
            logger.warning("⚠ Q Assistant not auto-configured. Please configure via LLM Setup.")
    except Exception as e:
        logger.error(f"Error in startup auto-setup: {str(e)}")
    
    # Check LLM authentication status
    try:
        auth_status = check_all_llm_authentication()
        prompt = get_startup_auth_prompt()
        
        if auth_status.all_ready:
            logger.info(f"✓ All {len(auth_status.authenticated_llms)} LLMs authenticated and ready")
        else:
            logger.warning(f"⚠ {len(auth_status.missing_credentials)} LLM(s) need credentials:")
            for missing in auth_status.needs_setup:
                logger.warning(f"  - {missing['name']} (assigned to {missing.get('assigned_role', 'role')})")
            logger.info("  → Frontend will prompt user with options")
        
        # Store auth prompt for frontend to display
        app.llm_auth_prompt = prompt
        
    except Exception as e:
        logger.error(f"Error checking LLM authentication: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
