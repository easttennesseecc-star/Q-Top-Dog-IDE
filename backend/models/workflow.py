"""
Workflow models for Q Assistant Orchestration

Tracks AI workflow state, handoffs between roles, and build progress.
"""

from sqlalchemy import Column, String, DateTime, Enum, JSON, ForeignKey
from typing import Any
from sqlalchemy.orm import relationship
from . import Base
from datetime import datetime
import uuid
import enum


class WorkflowStateEnum(str, enum.Enum):
    """Workflow state enumeration"""
    DISCOVERY = "discovery"
    PLANNING = "planning"
    HANDOFF_TO_CODER = "handoff_to_coder"
    IMPLEMENTATION = "implementation"
    HANDOFF_TO_TESTER = "handoff_to_tester"
    TESTING = "testing"
    HANDOFF_TO_VERIFIER = "handoff_to_verifier"
    VERIFICATION = "verification"
    HANDOFF_TO_RELEASER = "handoff_to_releaser"
    DEPLOYMENT = "deployment"
    COMPLETE = "complete"
    ERROR = "error"


class LLMRoleEnum(str, enum.Enum):
    """LLM role enumeration"""
    Q_ASSISTANT = "q_assistant"
    CODE_WRITER = "code_writer"
    TEST_AUDITOR = "test_auditor"
    VERIFICATION_OVERSEER = "verification_overseer"
    RELEASE_MANAGER = "release_manager"


class BuildWorkflow(Base):
    """
    Tracks a complete build workflow from discovery through deployment.
    
    One workflow per build request, tracks all phases and handoffs.
    """
    __tablename__ = "build_workflows"
    
    # Primary keys
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    build_id = Column(String(36), unique=True, nullable=False, index=True)
    project_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    
    # Workflow state
    current_state: Any = Column(
        Enum(WorkflowStateEnum),
        default=WorkflowStateEnum.DISCOVERY,
        nullable=False,
        index=True
    )
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Phase outputs (JSON storage for flexibility)
    discovery_phase = Column(JSON, nullable=True)  # User requirements
    planning_phase = Column(JSON, nullable=True)   # Implementation plan
    implementation_phase = Column(JSON, nullable=True)  # Code output
    testing_phase = Column(JSON, nullable=True)    # Test results
    verification_phase = Column(JSON, nullable=True)   # Verification checks
    deployment_phase = Column(JSON, nullable=True)     # Deployment details
    
    # Additional metadata
    workflow_metadata = Column(JSON, nullable=True)
    
    # Relationships
    handoffs = relationship(
        "WorkflowHandoff",
        back_populates="workflow",
        cascade="all, delete-orphan",
        lazy="select"
    )
    events = relationship(
        "WorkflowEvent",
        back_populates="workflow",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    def __repr__(self):
        return f"<BuildWorkflow build_id={self.build_id} state={self.current_state}>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "build_id": self.build_id,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "current_state": self.current_state.value if self.current_state else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "discovery_phase": self.discovery_phase,
            "planning_phase": self.planning_phase,
            "implementation_phase": self.implementation_phase,
            "testing_phase": self.testing_phase,
            "verification_phase": self.verification_phase,
            "deployment_phase": self.deployment_phase,
            "handoff_count": len(self.handoffs) if self.handoffs else 0,
        }


class WorkflowHandoff(Base):
    """
    Records handoffs between roles during workflow execution.
    
    Each handoff captures what was passed from one role to the next,
    enabling traceability and debugging.
    """
    __tablename__ = "workflow_handoffs"
    
    # Primary keys
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(
        String(36),
        ForeignKey("build_workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Handoff details
    from_role: Any = Column(Enum(LLMRoleEnum), nullable=False, index=True)
    to_role: Any = Column(Enum(LLMRoleEnum), nullable=True)  # May be None for final state
    from_state: Any = Column(Enum(WorkflowStateEnum), nullable=False)
    to_state: Any = Column(Enum(WorkflowStateEnum), nullable=False)
    
    # Data transferred
    data_transferred = Column(JSON, nullable=True)
    notes = Column(String(500), nullable=True)
    
    # Timing
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    workflow = relationship("BuildWorkflow", back_populates="handoffs")
    
    def __repr__(self):
        return (
            f"<WorkflowHandoff {self.from_role.value} → {self.to_role.value} "
            f"({self.from_state.value} → {self.to_state.value})>"
        )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "from_role": self.from_role.value if self.from_role else None,
            "to_role": self.to_role.value if self.to_role else None,
            "from_state": self.from_state.value if self.from_state else None,
            "to_state": self.to_state.value if self.to_state else None,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "notes": self.notes,
            "data_transferred": self.data_transferred,
        }


class WorkflowEvent(Base):
    """
    Records events that occur during workflow execution.
    
    Used for audit trails, debugging, and analytics.
    """
    __tablename__ = "workflow_events"
    
    # Primary keys
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(
        String(36),
        ForeignKey("build_workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Event details
    event_type = Column(String(50), nullable=False, index=True)
    triggered_by: Any = Column(Enum(LLMRoleEnum), nullable=False)
    event_data = Column(JSON, nullable=True)
    
    # Timing
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    workflow = relationship("BuildWorkflow", back_populates="events")
    
    def __repr__(self):
        return f"<WorkflowEvent {self.event_type} by {self.triggered_by.value}>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "event_type": self.event_type,
            "triggered_by": self.triggered_by.value if self.triggered_by else None,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "event_data": self.event_data,
        }


# ================================
# Database Migration SQL
# ================================

WORKFLOW_MIGRATIONS = """
-- Create build_workflows table
CREATE TABLE IF NOT EXISTS build_workflows (
    id VARCHAR(36) PRIMARY KEY,
    build_id VARCHAR(36) NOT NULL UNIQUE,
    project_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    current_state VARCHAR(50) NOT NULL DEFAULT 'discovery',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at DATETIME,
    discovery_phase JSON,
    planning_phase JSON,
    implementation_phase JSON,
    testing_phase JSON,
    verification_phase JSON,
    deployment_phase JSON,
    metadata JSON,
    KEY idx_build_id (build_id),
    KEY idx_project_id (project_id),
    KEY idx_user_id (user_id),
    KEY idx_current_state (current_state)
);

-- Create workflow_handoffs table
CREATE TABLE IF NOT EXISTS workflow_handoffs (
    id VARCHAR(36) PRIMARY KEY,
    workflow_id VARCHAR(36) NOT NULL,
    from_role VARCHAR(50) NOT NULL,
    to_role VARCHAR(50),
    from_state VARCHAR(50) NOT NULL,
    to_state VARCHAR(50) NOT NULL,
    data_transferred JSON,
    notes VARCHAR(500),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_workflow_id (workflow_id),
    KEY idx_from_role (from_role),
    KEY idx_to_role (to_role),
    KEY idx_timestamp (timestamp),
    CONSTRAINT fk_workflow_handoff_id FOREIGN KEY (workflow_id) REFERENCES build_workflows(id) ON DELETE CASCADE
);

-- Create workflow_events table
CREATE TABLE IF NOT EXISTS workflow_events (
    id VARCHAR(36) PRIMARY KEY,
    workflow_id VARCHAR(36) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    triggered_by VARCHAR(50) NOT NULL,
    event_data JSON,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_workflow_id (workflow_id),
    KEY idx_event_type (event_type),
    KEY idx_timestamp (timestamp),
    CONSTRAINT fk_workflow_event_id FOREIGN KEY (workflow_id) REFERENCES build_workflows(id) ON DELETE CASCADE
);
"""
