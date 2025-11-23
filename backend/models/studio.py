from __future__ import annotations

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.models import Base


class StudioExecutionRecord(Base):
    __tablename__ = "studio_execution_records"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, index=True)
    stage_type = Column(String(32), index=True)
    provider_used = Column(String(64))
    capability = Column(String(64))
    success = Column(Boolean, default=True)
    cost_actual = Column(Float, default=0.0)
    result_payload_json = Column(Text)  # JSON string
    error = Column(Text, nullable=True)
    started_at = Column(Float)
    finished_at = Column(Float)
    user_review = relationship("StudioUserReview", back_populates="execution_record", uselist=False)


class StudioUserReview(Base):
    __tablename__ = "studio_user_reviews"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("studio_execution_records.id", ondelete="CASCADE"))
    quality_score = Column(Float)  # 0-1 range
    look_feel_notes = Column(Text)
    dialog_notes = Column(Text)
    approved = Column(Boolean, default=False)
    created_at = Column(Float)

    execution_record = relationship("StudioExecutionRecord", back_populates="user_review")


class StudioProjectState(Base):
    """Persistent per-project budget & aggregated metrics for studio orchestration.

    Falls back to in-memory tracking if DB session not supplied; when DB is
    available values are synchronized on each plan/execute lifecycle.
    """
    __tablename__ = "studio_project_state"

    project_id = Column(Integer, primary_key=True, index=True)
    budget_remaining = Column(Float, default=100.0)
    stages_planned = Column(Integer, default=0)
    stages_executed = Column(Integer, default=0)
    stages_success = Column(Integer, default=0)
    stages_error = Column(Integer, default=0)


class StudioAssetLifecycle(Base):
    """Lifecycle governance for generated studio assets.

    Flags:
    - pinned: asset retained indefinitely (skips cold transition)
    - ephemeral: asset eligible for early cleanup / cold transition
    - cold: asset moved to cold storage tier (simulated flag here)
    - timestamps for governance operations
    """
    __tablename__ = "studio_asset_lifecycle"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(String(128), unique=True, index=True)
    pinned = Column(Boolean, default=False)
    ephemeral = Column(Boolean, default=True)
    cold = Column(Boolean, default=False)
    created_at = Column(Float)
    last_accessed_at = Column(Float)
    cold_transition_at = Column(Float, nullable=True)


class StudioUserAcknowledgment(Base):
    """Persist user acknowledgments for TOS & restricted domain disclaimers.

    Fields:
    - user_id: identifier from auth layer
    - tos_version: version string of accepted Terms of Service
    - disclaimer_ack_at: timestamp of restricted domain disclaimer acknowledgment
    - restricted_enabled: flag indicating user enabled restricted domains (requires safety key)
    - updated_at: last mutation timestamp for optimistic concurrency / auditing
    """
    __tablename__ = "studio_user_ack"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(128), unique=True, index=True)
    tos_version = Column(String(32))
    disclaimer_ack_at = Column(Float, nullable=True)
    restricted_enabled = Column(Boolean, default=False)
    updated_at = Column(Float)


class StudioAuditEntry(Base):
    """Immutable append-only audit chain for moderation & provenance snapshots.

    Fields:
    - kind: category (execution_moderation|provenance_edge|generic)
    - ref_type/ref_id: reference entity
    - payload_json: stored JSON snapshot
    - payload_hash: sha256 of canonical JSON (sorted keys)
    - prev_hash: hash of previous entry in chain (or 'GENESIS')
    - chain_index: monotonic index per kind
    - created_at: timestamp
    """
    __tablename__ = "studio_audit_entries"

    id = Column(Integer, primary_key=True, index=True)
    kind = Column(String(64), index=True)
    ref_type = Column(String(64), index=True)
    ref_id = Column(String(128), index=True)
    payload_json = Column(Text)
    payload_hash = Column(String(128), index=True)
    prev_hash = Column(String(128))
    chain_index = Column(Integer, index=True)
    created_at = Column(Float)


class SafetyKey(Base):
    """Rotatable safety keys with usage tracking.

    Keys stored as sha256 hashes; active flag indicates current accepted key.
    last_used_at updated on successful restricted operation.
    """
    __tablename__ = "studio_safety_keys"

    id = Column(Integer, primary_key=True, index=True)
    key_hash = Column(String(128), unique=True, index=True)
    active = Column(Boolean, default=True, index=True)
    created_at = Column(Float)
    rotated_at = Column(Float, nullable=True)
    last_used_at = Column(Float, nullable=True)
