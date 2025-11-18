"""
Snapshot API routes

Provides endpoints to list and fetch conversation/workflow snapshots
stored under backend/snapshots/<workflow_id>/.

- GET /snapshots/{workflow_id} -> list available snapshots (metadata)
- GET /snapshots/{workflow_id}/{snapshot} -> fetch snapshot JSON
  - The {snapshot} param can be a file name (e.g., 20240101T120000000000Z-init.json)
    or the keyword "latest" to return the most recent snapshot.

Access can be gated with the environment variable ENABLE_SNAPSHOT_API.
Set to "false" to disable these routes in production environments.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Mapping

from fastapi import APIRouter, HTTPException, Request, Body
from pydantic import BaseModel

from backend.services.snapshot_store import SnapshotStore
from backend.services.orchestration_service import OrchestrationService
from backend.orchestration.workflow_state_machine import WorkflowState
from backend.auth import get_session_user


router = APIRouter(prefix="/snapshots", tags=["snapshots"])


def _api_enabled() -> bool:
    return str(os.getenv("ENABLE_SNAPSHOT_API", "true")).lower() in ("1", "true", "yes", "on")


def _parse_snapshot_name(file_path: Path) -> Dict[str, Optional[str]]:
    """Parse timestamp and optional label from a snapshot file name.

    Expected pattern: <timestamp>[-label].json
    Returns dict with keys: timestamp, label
    """
    stem = file_path.stem  # without .json
    # Split into timestamp and optional label (using the last '-' only to support labels with dashes)
    if "-" in stem:
        ts, label = stem.split("-", 1)
    else:
        ts, label = stem, None
    return {"timestamp": ts, "label": label}


def _require_snapshot_auth(request: Request) -> None:
    """Optionally enforce session auth based on REQUIRE_SNAPSHOT_AUTH env flag.

    Accepts session via:
    - Query param: ?session_id=...
    - Header: X-Session-Id: ...
    """
    must_auth = str(os.getenv("REQUIRE_SNAPSHOT_AUTH", "false")).lower() in ("1", "true", "yes", "on")
    if not must_auth:
        return
    # Try query param first, then header
    session_id = request.query_params.get("session_id") or request.headers.get("X-Session-Id")
    if not session_id:
        raise HTTPException(status_code=401, detail="session_id required")
    user_id = get_session_user(session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="invalid session")


def _split_label(label: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Split a label into base and detail.

    Rules:
    - checkpoint-<name> -> ("checkpoint", <name>)
    - checkpoint -> ("checkpoint", None)
    - pre-advance/post-advance (and other non-checkpoint labels) remain intact with no detail
    - None/empty -> (None, None)
    """
    if not label:
        return (None, None)
    if label == "checkpoint":
        return ("checkpoint", None)
    if label.startswith("checkpoint-"):
        return ("checkpoint", label[len("checkpoint-"):])
    return (label, None)


@router.get("/labels")
def get_snapshot_labels(include_checkpoint: bool = True):
    if not _api_enabled():
        raise HTTPException(status_code=404, detail="Not found")
    labels = ["init", "pre-advance", "post-advance"]
    if include_checkpoint:
        labels.append("checkpoint")
    return {"labels": labels}


@router.get("/{workflow_id}")
def list_snapshots(
    workflow_id: str,
    request: Request,
    limit: int = 50,
    offset: int = 0,
    label_base: Optional[str] = None,
    include_path: bool = False,
):
    if not _api_enabled():
        raise HTTPException(status_code=404, detail="Not found")
    _require_snapshot_auth(request)

    store = SnapshotStore()
    files = store.list_snapshots(workflow_id)

    # Use Mapping to avoid dict invariance issues when values are unions
    results_all: List[Mapping[str, object]] = []
    for f in files:
        p = Path(f)
        meta = _parse_snapshot_name(p)
        label = meta.get("label") or ""
        base, detail = _split_label(label)
        if label_base and (base or "") != label_base:
            continue
        try:
            size = p.stat().st_size
        except Exception:
            size = None
        item = {
            "file": p.name,
            "timestamp": meta.get("timestamp"),
            "label": label,
            "label_base": base,
            "label_detail": detail,
            "size": size,
        }
        if include_path:
            item["path"] = str(p)
        results_all.append(item)

    # Pagination
    total = len(results_all)
    start = max(0, offset)
    end = max(start, min(total, start + max(1, min(limit, 200))))
    results = results_all[start:end]

    return {"workflow_id": workflow_id, "count": len(results), "total": total, "offset": offset, "limit": limit, "snapshots": results}


@router.get("/{workflow_id}/checkpoints")
def list_checkpoints(
    workflow_id: str,
    request: Request,
    limit: int = 50,
    offset: int = 0,
    include_path: bool = False,
):
    if not _api_enabled():
        raise HTTPException(status_code=404, detail="Not found")
    _require_snapshot_auth(request)

    store = SnapshotStore()
    files = store.list_snapshots(workflow_id)
    results_all: List[Mapping[str, object]] = []
    for f in files:
        p = Path(f)
        meta = _parse_snapshot_name(p)
        label = (meta.get("label") or "")
        if label and str(label).startswith("checkpoint"):
            try:
                size = p.stat().st_size
            except Exception:
                size = None
            base = label.split("-", 1)[0] if label else None
            detail = label.split("-", 1)[1] if (label and "-" in label) else None
            item = {
                "file": p.name,
                "timestamp": meta.get("timestamp"),
                "label": label,
                "label_base": base,
                "label_detail": detail,
                "size": size,
            }
            if include_path:
                item["path"] = str(p)
            results_all.append(item)

    total = len(results_all)
    start = max(0, offset)
    end = max(start, min(total, start + max(1, min(limit, 200))))
    results = results_all[start:end]

    return {"workflow_id": workflow_id, "count": len(results), "total": total, "offset": offset, "limit": limit, "checkpoints": results}


class CheckpointRequest(BaseModel):
    label: Optional[str] = None


@router.post("/{workflow_id}/checkpoint")
async def create_checkpoint(workflow_id: str, request: Request, body: Optional[CheckpointRequest] = Body(default=None)):
    """Create a labeled checkpoint snapshot for a workflow by capturing current status.

    Body: { "label": "optional-custom-label" }
    """
    if not _api_enabled():
        raise HTTPException(status_code=404, detail="Not found")
    _require_snapshot_auth(request)

    # Optionally obtain DB session and query status; tolerate missing DB in test/dev
    status: dict = {}
    try:
        if hasattr(request.app, 'workflow_db_manager'):
            db = request.app.workflow_db_manager.get_session()
            svc = OrchestrationService(db=db)
        else:
            svc = OrchestrationService(db=None)
        # Try to fetch status even without DB (svc handles in-memory/test mode)
        status = await svc.get_workflow_status(workflow_id)  # type: ignore[assignment]
    except Exception:
        # Proceed with minimal checkpoint if status cannot be loaded
        status = {}

    current_state = (status or {}).get("current_state")
    if not current_state:
        # Fallback to storing minimal checkpoint
        current_state = "unknown"

    label_suffix = f"checkpoint{('-' + body.label) if (body and body.label) else ''}"
    payload = {
        "kind": "checkpoint",
        "workflow_id": workflow_id,
        "created_at": status.get("timestamp") if isinstance(status, dict) else None,
        "current_state": current_state,
        "status": status,
    }

    store = SnapshotStore()
    path = store.save_snapshot(workflow_id, payload, label=label_suffix)
    if not path:
        raise HTTPException(status_code=500, detail="Failed to save checkpoint snapshot")

    p = Path(path)
    meta = _parse_snapshot_name(p)
    return {
        "workflow_id": workflow_id,
        "file": p.name,
        "timestamp": meta.get("timestamp"),
        "label": meta.get("label"),
        "path": str(p),
    }


@router.get("/{workflow_id}/{snapshot}")
def fetch_snapshot(workflow_id: str, snapshot: str, request: Request):
    if not _api_enabled():
        raise HTTPException(status_code=404, detail="Not found")
    _require_snapshot_auth(request)

    store = SnapshotStore()
    files = store.list_snapshots(workflow_id)
    if not files:
        raise HTTPException(status_code=404, detail="No snapshots found for workflow")

    # Disallow path traversal; snapshot must be a simple filename
    if snapshot.lower() == "latest":
        target_path = Path(files[-1])  # list_snapshots returns sorted list
    else:
        if ("/" in snapshot) or ("\\" in snapshot) or (".." in snapshot) or not snapshot.endswith(".json"):
            raise HTTPException(status_code=400, detail="Invalid snapshot identifier")
        # Find exact match among files
        matches = [Path(f) for f in files if Path(f).name == snapshot]
        if not matches:
            raise HTTPException(status_code=404, detail="Snapshot not found")
        target_path = matches[0]

    data = store.load_snapshot(str(target_path))
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to load snapshot")

    # Provide some metadata alongside the payload
    meta = _parse_snapshot_name(target_path)
    return {
        "workflow_id": workflow_id,
        "file": target_path.name,
        "timestamp": meta.get("timestamp"),
        "label": meta.get("label"),
        "data": data,
    }


class RollbackRequest(BaseModel):
    label: Optional[str] = None


@router.post("/{workflow_id}/rollback-to-checkpoint")
async def rollback_to_checkpoint(workflow_id: str, request: Request, body: Optional[RollbackRequest] = Body(default=None)):
    if not _api_enabled():
        raise HTTPException(status_code=404, detail="Not found")
    _require_snapshot_auth(request)

    store = SnapshotStore()
    files = store.list_snapshots(workflow_id)
    if not files:
        raise HTTPException(status_code=404, detail="No snapshots found for workflow")

    # Find target checkpoint file
    target: Optional[Path] = None
    candidates: list[Path] = [Path(f) for f in files]
    if body and body.label:
        # Look for exact checkpoint-<label>
        for p in candidates:
            meta = _parse_snapshot_name(p)
            if (meta.get("label") or "") == f"checkpoint-{body.label}":
                target = p
                break
        if target is None:
            raise HTTPException(status_code=404, detail="Named checkpoint not found")
    else:
        # Latest checkpoint in sorted list
        for p in reversed(candidates):
            meta = _parse_snapshot_name(p)
            if (meta.get("label") or "").startswith("checkpoint"):
                target = p
                break
        if target is None:
            raise HTTPException(status_code=404, detail="No checkpoints found")

    # Load and validate snapshot; if invalid, try to fall back to the most recent valid checkpoint
    snap = store.load_snapshot(str(target))
    if not snap or snap.get("kind") != "checkpoint" or not isinstance(snap.get("current_state"), str):
        # Attempt fallback search for a valid checkpoint in reverse chronological order
        fallback: Optional[Dict[str, object]] = None
        fallback_path: Optional[Path] = None
        for p in reversed(candidates):
            meta = _parse_snapshot_name(p)
            if (meta.get("label") or "").startswith("checkpoint"):
                data = store.load_snapshot(str(p))
                if data and data.get("kind") == "checkpoint" and isinstance(data.get("current_state"), str):
                    fallback = data
                    fallback_path = p
                    break
        if fallback is None:
            raise HTTPException(status_code=400, detail="Invalid checkpoint snapshot")
        snap = fallback
        target = fallback_path or target

    state_str = snap.get("current_state")
    if not isinstance(state_str, str):
        raise HTTPException(status_code=400, detail="Checkpoint missing current_state")

    # Obtain service (with or without DB) and call rollback
    try:
        if hasattr(request.app, 'workflow_db_manager'):
            db = request.app.workflow_db_manager.get_session()
            svc = OrchestrationService(db=db)
        else:
            svc = OrchestrationService(db=None)
        # Map string to enum; tolerate lower/upper; fallback to DISCOVERY if unknown
        try:
            target_state = WorkflowState[state_str.upper()]
        except KeyError:
            target_state = WorkflowState.DISCOVERY
        result = await svc.rollback_workflow(
            workflow_id=workflow_id,
            target_state=target_state,
            reason=f"Rollback to checkpoint: {Path(target).name}",
        )
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Unknown workflow state in checkpoint: {state_str}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rollback failed: {e}")

    return {"status": "ok", "rolled_back": True, "checkpoint": target.name, "result": result}


 
