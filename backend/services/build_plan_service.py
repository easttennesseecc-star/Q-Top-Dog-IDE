"""
Build Plan Generation & Approval System
Generates plans for builds and requires user approval before execution
Overwatch monitors to ensure plan compliance
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum
import json
import sqlite3
from pathlib import Path
from contextlib import contextmanager


class BuildPlanStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class BuildStep(BaseModel):
    """Individual step in a build plan"""
    id: str
    description: str
    command: Optional[str] = None
    files_to_modify: List[str] = []
    dependencies: List[str] = []  # IDs of steps that must complete first
    estimated_duration: Optional[int] = None  # seconds
    risks: List[str] = []
    status: str = "pending"


class BuildPlan(BaseModel):
    """Complete build plan requiring approval"""
    id: Optional[str] = None
    user_id: str
    workspace_path: str
    title: str
    description: str
    steps: List[BuildStep]
    status: BuildPlanStatus = BuildPlanStatus.DRAFT
    created_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    approval_notes: Optional[str] = None
    metadata: Dict[str, Any] = {}


class BuildPlanService:
    """Service for managing build plans and approvals"""
    
    def __init__(self, db_path: str = "./data/build_plans.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS build_plans (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    workspace_path TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    steps TEXT NOT NULL,
                    status TEXT DEFAULT 'draft',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    approved_at TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    approval_notes TEXT,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS build_plan_changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_id TEXT NOT NULL,
                    step_id TEXT,
                    change_type TEXT NOT NULL,
                    change_description TEXT,
                    approved_by_user BOOLEAN DEFAULT 0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (plan_id) REFERENCES build_plans(id)
                )
            """)
    
    def create_plan(self, plan: BuildPlan) -> BuildPlan:
        """Create a new build plan"""
        import uuid
        plan.id = str(uuid.uuid4())
        plan.created_at = datetime.utcnow()
        plan.status = BuildPlanStatus.PENDING_APPROVAL
        
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO build_plans 
                (id, user_id, workspace_path, title, description, steps, status, created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                plan.id,
                plan.user_id,
                plan.workspace_path,
                plan.title,
                plan.description,
                json.dumps([step.dict() for step in plan.steps]),
                plan.status,
                plan.created_at.isoformat(),
                json.dumps(plan.metadata)
            ))
        
        return plan
    
    def get_plan(self, plan_id: str) -> Optional[BuildPlan]:
        """Retrieve a build plan"""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM build_plans WHERE id = ?", (plan_id,)
            ).fetchone()
            
            if row:
                return self._row_to_plan(row)
        return None
    
    def approve_plan(self, plan_id: str, approval_notes: Optional[str] = None) -> Optional[BuildPlan]:
        """Approve a build plan for execution"""
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE build_plans 
                SET status = ?, approved_at = ?, approval_notes = ?
                WHERE id = ?
            """, (
                BuildPlanStatus.APPROVED,
                datetime.utcnow().isoformat(),
                approval_notes,
                plan_id
            ))
        
        return self.get_plan(plan_id)
    
    def reject_plan(self, plan_id: str, rejection_notes: str) -> Optional[BuildPlan]:
        """Reject a build plan"""
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE build_plans 
                SET status = ?, approval_notes = ?
                WHERE id = ?
            """, (
                BuildPlanStatus.REJECTED,
                rejection_notes,
                plan_id
            ))
        
        return self.get_plan(plan_id)
    
    def start_execution(self, plan_id: str) -> Optional[BuildPlan]:
        """Mark plan as in progress"""
        plan = self.get_plan(plan_id)
        if not plan:
            raise ValueError("Plan not found")
        if plan.status != BuildPlanStatus.APPROVED:
            raise ValueError("Can only execute approved plans")
        
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE build_plans 
                SET status = ?, started_at = ?
                WHERE id = ?
            """, (
                BuildPlanStatus.IN_PROGRESS,
                datetime.utcnow().isoformat(),
                plan_id
            ))
        
        return self.get_plan(plan_id)
    
    def log_change(self, plan_id: str, step_id: Optional[str], change_type: str, 
                   description: str, approved: bool = False):
        """Log a change during build execution"""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO build_plan_changes 
                (plan_id, step_id, change_type, change_description, approved_by_user)
                VALUES (?, ?, ?, ?, ?)
            """, (plan_id, step_id, change_type, description, approved))
    
    def get_pending_approval_plans(self, user_id: str) -> List[BuildPlan]:
        """Get all plans pending approval for a user"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM build_plans 
                WHERE user_id = ? AND status = ?
                ORDER BY created_at DESC
            """, (user_id, BuildPlanStatus.PENDING_APPROVAL)).fetchall()
            
            return [self._row_to_plan(row) for row in rows]
    
    def _row_to_plan(self, row: sqlite3.Row) -> BuildPlan:
        steps_data = json.loads(row['steps'])
        return BuildPlan(
            id=row['id'],
            user_id=row['user_id'],
            workspace_path=row['workspace_path'],
            title=row['title'],
            description=row['description'],
            steps=[BuildStep(**step) for step in steps_data],
            status=BuildPlanStatus(row['status']),
            created_at=datetime.fromisoformat(row['created_at']),
            approved_at=datetime.fromisoformat(row['approved_at']) if row['approved_at'] else None,
            started_at=datetime.fromisoformat(row['started_at']) if row['started_at'] else None,
            completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None,
            approval_notes=row['approval_notes'],
            metadata=json.loads(row['metadata']) if row['metadata'] else {}
        )
