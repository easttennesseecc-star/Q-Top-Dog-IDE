"""
Snapshot storage utility for conversation histories and workflow state.

Stores JSON snapshots under a filesystem directory (default: backend/snapshots).
Each snapshot is a single JSON file per workflow, timestamped for easy retrieval.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


class SnapshotStore:
    def __init__(self, base_dir: str = "backend/snapshots") -> None:
        self.base_dir = base_dir
        try:
            os.makedirs(self.base_dir, exist_ok=True)
        except Exception:
            # Path creation failures shouldn't break runtime behavior
            pass
        # Optional differential privacy/anonymization feature flag
        self._dp_enabled = str(os.getenv("FEATURE_DIFFERENTIAL_PRIVACY", "false")).lower() in ("1","true","yes","on")

    def _wf_dir(self, workflow_id: str) -> str:
        path = os.path.join(self.base_dir, workflow_id)
        try:
            os.makedirs(path, exist_ok=True)
        except Exception:
            pass
        return path

    def _now_id(self) -> str:
        # Use a sortable timestamp identifier
        return datetime.utcnow().strftime("%Y%m%dT%H%M%S%fZ")

    def _serialize(self, obj: Any) -> Any:
        # Best-effort JSON serialization
        try:
            if is_dataclass(obj) and not isinstance(obj, type):
                return asdict(obj)  # type: ignore[arg-type]
        except Exception:
            pass
        if hasattr(obj, "value"):
            # Enums
            try:
                return obj.value  # type: ignore[no-any-return]
            except Exception:
                return str(obj)
        if isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj
        if isinstance(obj, dict):
            return {str(k): self._serialize(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._serialize(v) for v in obj]
        # Fallback: string repr
        return str(obj)

    def save_snapshot(
        self,
        workflow_id: str,
        snapshot: Dict[str, Any],
        label: Optional[str] = None,
    ) -> Optional[str]:
        """Persist a snapshot to disk. Returns file path on success."""
        try:
            wf_dir = self._wf_dir(workflow_id)
            snap_id = self._now_id()
            name = f"{snap_id}{('-' + label) if label else ''}.json"
            path = os.path.join(wf_dir, name)
            payload = self._serialize(snapshot)
            if self._dp_enabled:
                payload = self._anonymize(payload)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            return path
        except Exception:
            # Non-fatal: logging handled by callers
            return None

    def list_snapshots(self, workflow_id: str) -> List[str]:
        try:
            wf_dir = self._wf_dir(workflow_id)
            files = [os.path.join(wf_dir, f) for f in os.listdir(wf_dir) if f.endswith(".json")]
            return sorted(files)
        except Exception:
            return []

    def load_snapshot(self, file_path: str) -> Optional[Dict[str, Any]]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    # ---- Differential Privacy (placeholder) ----
    def _anonymize(self, data: Any) -> Any:
        """Lightweight anonymization placeholder.

        - Redacts obvious secrets/user identifiers by key heuristic
        - Drops raw tokens
        - Leaves structure intact for debuggability
        """
        try:
            if isinstance(data, dict):
                redacted_keys = {"email", "token", "access_token", "authorization", "password", "ssn", "user_id", "session_id"}
                out: Dict[str, Any] = {}
                for k, v in data.items():
                    kl = str(k).lower()
                    if kl in redacted_keys or any(x in kl for x in ("secret", "apikey", "api_key")):
                        out[k] = "[redacted]"
                    else:
                        out[k] = self._anonymize(v)
                return out
            if isinstance(data, list):
                return [self._anonymize(v) for v in data]
            return data
        except Exception:
            return data
