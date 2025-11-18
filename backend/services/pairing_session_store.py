"""Unified PairingSession model and persistence.

Provides a single lightweight registry for both QR and SMS pairing flows so we
can observe lifecycle transitions (pending -> scanned -> accepted -> expired /
revoked) independent of the underlying implementation details of
`PhonePairingService` and `SMSPairingService`.

Design goals:
 - Low overhead (JSON file persistence; in-memory map)
 - Not security-critical (authoritative validation still in individual services)
 - Useful for diagnostics, audit, future analytics or admin UI
"""

from __future__ import annotations

import json
import secrets
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Any
import threading

import logging

logger = logging.getLogger(__name__)


class SessionStatus(str, Enum):
    PENDING = "pending"      # created, waiting for user action
    SCANNED = "scanned"      # QR scanned (optional intermediate)
    ACCEPTED = "accepted"    # device successfully paired
    EXPIRED = "expired"      # timed out
    REVOKED = "revoked"      # device revoked after acceptance


@dataclass
class PairingSession:
    session_id: str
    user_id: str
    channel: str              # 'qr' | 'sms'
    created_at: datetime
    expires_at: datetime
    status: SessionStatus = SessionStatus.PENDING
    # Tokens / codes
    pairing_token: Optional[str] = None  # QR token
    invite_code: Optional[str] = None    # SMS invite code
    otp_code: Optional[str] = None
    # Device info once accepted
    device_id: Optional[str] = None
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    phone_number: Optional[str] = None
    ip_address: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["created_at"] = self.created_at.isoformat()
        d["expires_at"] = self.expires_at.isoformat()
        d["status"] = self.status.value
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PairingSession":
        data = dict(data)
        data["created_at"] = datetime.fromisoformat(data["created_at"])  # type: ignore
        data["expires_at"] = datetime.fromisoformat(data["expires_at"])  # type: ignore
        data["status"] = SessionStatus(data["status"])  # type: ignore
        return cls(**data)  # type: ignore[arg-type]

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at


class PairingSessionStore:
    def __init__(self, storage_path: Optional[Path] = None, filename: str = "pairing_sessions.json"):
        self.storage_dir = storage_path or Path.home() / ".q-ide" / "pairing"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.file = self.storage_dir / filename
        self._sessions: Dict[str, PairingSession] = {}
        self._lock = threading.Lock()
        self._load()
        self._prune_expired(save=True)

    # CRUD operations -------------------------------------------------
    def create_qr_session(self, user_id: str, pairing_token: str, expires_at: datetime, otp_code: Optional[str], ip: Optional[str]) -> PairingSession:
        return self._create_session(user_id, "qr", expires_at, pairing_token=pairing_token, otp_code=otp_code, ip_address=ip)

    def create_sms_session(self, user_id: str, invite_code: str, expires_at: datetime, otp_code: Optional[str], phone: str, ip: Optional[str]) -> PairingSession:
        return self._create_session(user_id, "sms", expires_at, invite_code=invite_code, otp_code=otp_code, phone_number=phone, ip_address=ip)

    def mark_scanned(self, pairing_token: str) -> None:
        with self._lock:
            for s in self._sessions.values():
                if s.pairing_token == pairing_token and s.status == SessionStatus.PENDING:
                    s.status = SessionStatus.SCANNED
                    self._save_unlocked()
                    return

    def mark_accepted(self, identifier: str, device_id: str, device_name: str, device_type: str) -> None:
        with self._lock:
            for s in self._sessions.values():
                if identifier in (s.pairing_token, s.invite_code):
                    s.status = SessionStatus.ACCEPTED
                    s.device_id = device_id
                    s.device_name = device_name
                    s.device_type = device_type
                    self._save_unlocked()
                    return

    def mark_revoked(self, device_id: str) -> None:
        with self._lock:
            for s in self._sessions.values():
                if s.device_id == device_id and s.status == SessionStatus.ACCEPTED:
                    s.status = SessionStatus.REVOKED
                    self._save_unlocked()
                    return

    def get_session(self, session_id: str) -> Optional[PairingSession]:
        with self._lock:
            return self._sessions.get(session_id)

    def find_by_token(self, token_or_invite: str) -> Optional[PairingSession]:
        with self._lock:
            for s in self._sessions.values():
                if token_or_invite in (s.pairing_token, s.invite_code):
                    return s
            return None

    # Internal helpers ------------------------------------------------
    def _create_session(self, user_id: str, channel: str, expires_at: datetime, **kwargs) -> PairingSession:
        with self._lock:
            session_id = secrets.token_urlsafe(16)
            session = PairingSession(
                session_id=session_id,
                user_id=user_id,
                channel=channel,
                created_at=datetime.utcnow(),
                expires_at=expires_at,
                **kwargs,
            )
            self._sessions[session_id] = session
            self._save_unlocked()
            logger.debug(f"Created {channel} pairing session {session_id}")
            return session

    def _prune_expired(self, save: bool = False) -> None:
        changed = False
        datetime.utcnow()
        for s in list(self._sessions.values()):
            if s.status in {SessionStatus.PENDING, SessionStatus.SCANNED} and s.is_expired():
                s.status = SessionStatus.EXPIRED
                changed = True
        if changed and save:
            self._save_unlocked()

    def _load(self) -> None:
        if not self.file.exists():
            return
        try:
            data = json.loads(self.file.read_text(encoding="utf-8"))
            for entry in data.get("sessions", []):
                session = PairingSession.from_dict(entry)
                self._sessions[session.session_id] = session
            logger.info(f"Loaded {len(self._sessions)} pairing sessions")
        except Exception as e:
            logger.warning(f"Failed to load pairing sessions: {e}")

    def _save_unlocked(self) -> None:
        try:
            doc = {"sessions": [s.to_dict() for s in self._sessions.values()]}
            self.file.write_text(json.dumps(doc, indent=2), encoding="utf-8")
        except Exception as e:
            logger.warning(f"Failed to persist pairing sessions: {e}")


_session_store: Optional[PairingSessionStore] = None


def get_pairing_session_store() -> PairingSessionStore:
    global _session_store
    if _session_store is None:
        _session_store = PairingSessionStore()
    return _session_store
