"""
Domain configuration loader/saver and env applier.
Allows switching between domains like q-ide.net and topdog-ide.com at runtime
and persisting the preference for next startup.
"""
from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from pathlib import Path
import os
import json

CONFIG_FILENAME = "domain_config.json"
CONFIG_PATH = Path(__file__).resolve().parents[1] / CONFIG_FILENAME

class DomainConfig(BaseModel):
    canonical_host: str = Field(default="topdog-ide.com", description="Primary canonical host")
    alternate_hosts: List[str] = Field(default_factory=lambda: ["www.topdog-ide.com"], description="Alternate hosts allowed for redirect exemption")
    frontend_url: str = Field(default="https://topdog-ide.com")
    backend_url: str = Field(default="https://api.topdog-ide.com")
    cors_origins: List[str] = Field(default_factory=lambda: [
        "http://localhost:1431",
        "http://127.0.0.1:1431",
        "http://localhost:3000",
        "http://localhost:5173",
        "https://topdog-ide.com",
        "https://www.topdog-ide.com",
        "https://api.topdog-ide.com",
    ])
    enable_host_redirect: bool = Field(default=True)
    sitemap_hosts: List[str] = Field(default_factory=lambda: ["www.topdog-ide.com"])  # for sitemap.xml lines
    # Pydantic v2: replace inner Config with model_config
    model_config = ConfigDict(extra="ignore")


def load_config() -> DomainConfig:
    try:
        if CONFIG_PATH.exists():
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            return DomainConfig(**data)
    except Exception:
        pass
    return DomainConfig()


def save_config(cfg: DomainConfig) -> None:
    try:
        CONFIG_PATH.write_text(cfg.model_dump_json(indent=2), encoding="utf-8")
    except Exception:
        # Non-fatal in runtime context
        pass


def apply_to_env(cfg: DomainConfig) -> None:
    # Update process env so request-time lookups (CSP headers, robots, sitemap) reflect immediately
    os.environ["CANONICAL_HOST"] = cfg.canonical_host
    os.environ["FRONTEND_URL"] = cfg.frontend_url
    os.environ["BACKEND_URL"] = cfg.backend_url
    os.environ["ENABLE_HOST_REDIRECT"] = "true" if cfg.enable_host_redirect else "false"
    os.environ["ALTERNATE_HOSTS"] = ",".join(cfg.alternate_hosts)
    os.environ["SITEMAP_HOSTS"] = ",".join(cfg.sitemap_hosts)
    # CORS middleware is constructed at startup; we persist for next boot
    os.environ["CORS_ORIGINS"] = ",".join(cfg.cors_origins)


def load_and_apply(app) -> DomainConfig:
    cfg = load_config()
    apply_to_env(cfg)
    try:
        app.state.domain_config = cfg
    except Exception:
        setattr(app, "domain_config", cfg)  # legacy fallback
    return cfg
