"""
API routes to inspect and update domain configuration at runtime.
Changes are applied to environment variables immediately and persisted to domain_config.json for next startup.
Note: Some middleware like CORS is constructed at startup; a restart may be required for full effect.
"""
from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Dict, Any
from backend.services.domain_config import (
    DomainConfig,
    load_config,
    save_config,
    apply_to_env,
)

router = APIRouter(prefix="/api/domain", tags=["Domain"])

class SaveResponse(BaseModel):
    status: str
    applied: Dict[str, Any]
    restart_required: bool = True


@router.get("/config", response_model=DomainConfig)
def get_domain_config():
    return load_config()


@router.post("/config", response_model=SaveResponse)
def set_domain_config(cfg: DomainConfig):
    # Persist and apply to current process
    save_config(cfg)
    apply_to_env(cfg)
    return SaveResponse(
        status="ok",
        applied=cfg.model_dump(),
        restart_required=True,  # CORS & middleware built at startup
    )


@router.get("/diagnose")
def diagnose_domain(request: Request):
    """Return current host vs configured canonical and recommended redirect target."""
    host = (request.headers.get("host") or "").split(":")[0]
    cfg = load_config()
    canonical = cfg.canonical_host
    should_redirect = host and canonical and host != canonical and host not in cfg.alternate_hosts
    scheme = "https" if request.url.scheme in ("https",) else request.url.scheme
    target = f"{scheme}://{canonical}{request.url.path}"
    return {
        "status": "ok",
        "request_host": host,
        "canonical_host": canonical,
        "alternate_hosts": cfg.alternate_hosts,
        "should_redirect": should_redirect,
        "redirect_to": target,
    }
