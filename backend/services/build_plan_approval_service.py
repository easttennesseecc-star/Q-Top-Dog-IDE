"""
Build Plan Approval Service
System generates a plan for every build and requires user approval before execution.
OverWatch monitors to ensure builds follow approved plans.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum


class PlanStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    COMPLETED = "completed"
    DEVIATED = "deviated"  # Plan deviated from approved version


class DeviationType(str, Enum):
    FILE_ADDED = "file_added"
    FILE_REMOVED = "file_removed"
    FILE_MODIFIED = "file_modified"
    DEPENDENCY_ADDED = "dependency_added"
    DEPENDENCY_REMOVED = "dependency_removed"
    COMMAND_CHANGED = "command_changed"
    SCOPE_EXPANDED = "scope_expanded"


@dataclass
class PlanStep:
    """Individual step in the build plan"""
    step_id: str
    order: int
    description: str
    estimated_duration: str
    files_affected: List[str]
    dependencies: List[str]
    risk_level: str  # "low", "medium", "high"
    verification_criteria: str


@dataclass
class BuildPlan:
    """Complete build plan requiring approval"""
    plan_id: str
    workflow_id: str
    generated_at: str
    generated_by: str  # LLM role that generated the plan
    
    # Plan content
    objective: str
    scope: str
    steps: List[Dict[str, Any]]  # List of PlanStep dicts
    estimated_total_duration: str
    risks: List[str]
    dependencies_to_install: List[str]
    files_to_create: List[str]
    files_to_modify: List[str]
    files_to_delete: List[str]
    
    # Approval tracking
    status: PlanStatus
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    rejection_reason: Optional[str] = None
    
    # Execution tracking
    execution_started_at: Optional[str] = None
    execution_completed_at: Optional[str] = None
    deviations: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def __post_init__(self):
        if self.deviations is None:
            self.deviations = []


@dataclass
class PlanDeviation:
    """Detected deviation from approved plan"""
    deviation_id: str
    plan_id: str
    detected_at: str
    deviation_type: DeviationType
    description: str
    actual_action: str
    planned_action: str
    severity: str  # "minor", "major", "critical"
    requires_approval: bool


class BuildPlanApprovalService:
    """Service for managing build plans and approval workflow"""
    
    def __init__(self, storage_dir: str = "./data/build_plans"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_dir / "plans_index.json"
        self._ensure_index()
    
    def _ensure_index(self):
        """Ensure index file exists"""
        if not self.index_file.exists():
            self._save_index({})
    
    def _load_index(self) -> Dict:
        """Load plans index"""
        with open(self.index_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_index(self, index: Dict):
        """Save plans index"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
    
    def _get_plan_file(self, plan_id: str) -> Path:
        """Get path to plan file"""
        return self.storage_dir / f"{plan_id}.json"
    
    def generate_plan(
        self,
        workflow_id: str,
        generated_by: str,
        objective: str,
        scope: str,
        steps: List[PlanStep],
        **kwargs
    ) -> BuildPlan:
        """Generate a new build plan from LLM output"""
        plan_id = f"plan_{workflow_id}_{datetime.utcnow().timestamp()}"
        now = datetime.utcnow().isoformat()
        
        # Calculate estimated total duration
        estimated_minutes = sum(
            int(s.estimated_duration.replace("min", "").strip())
            for s in steps
            if "min" in s.estimated_duration
        )
        estimated_total = f"{estimated_minutes} minutes"
        
        plan = BuildPlan(
            plan_id=plan_id,
            workflow_id=workflow_id,
            generated_at=now,
            generated_by=generated_by,
            objective=objective,
            scope=scope,
            steps=[asdict(s) for s in steps],
            estimated_total_duration=kwargs.get('estimated_total_duration', estimated_total),
            risks=kwargs.get('risks', []),
            dependencies_to_install=kwargs.get('dependencies_to_install', []),
            files_to_create=kwargs.get('files_to_create', []),
            files_to_modify=kwargs.get('files_to_modify', []),
            files_to_delete=kwargs.get('files_to_delete', []),
            status=PlanStatus.PENDING
        )
        
        # Save plan
        plan_file = self._get_plan_file(plan_id)
        with open(plan_file, 'w', encoding='utf-8') as f:
            json.dump(plan.to_dict(), f, indent=2, ensure_ascii=False)
        
        # Update index
        index = self._load_index()
        index[plan_id] = {
            "workflow_id": workflow_id,
            "status": PlanStatus.PENDING,
            "generated_at": now,
            "generated_by": generated_by
        }
        self._save_index(index)
        
        return plan
    
    def get_plan(self, plan_id: str) -> Optional[BuildPlan]:
        """Get a build plan"""
        plan_file = self._get_plan_file(plan_id)
        if not plan_file.exists():
            return None
        
        with open(plan_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return BuildPlan(**data)
    
    def get_plan_by_workflow(self, workflow_id: str) -> Optional[BuildPlan]:
        """Get the latest plan for a workflow"""
        index = self._load_index()
        
        # Find all plans for this workflow
        workflow_plans = [
            (pid, data) for pid, data in index.items()
            if data.get('workflow_id') == workflow_id
        ]
        
        if not workflow_plans:
            return None
        
        # Get the most recent one
        latest = max(workflow_plans, key=lambda x: x[1]['generated_at'])
        return self.get_plan(latest[0])
    
    def approve_plan(self, plan_id: str, approved_by: str) -> Optional[BuildPlan]:
        """Approve a build plan"""
        plan = self.get_plan(plan_id)
        if not plan:
            return None
        
        plan.status = PlanStatus.APPROVED
        plan.approved_by = approved_by
        plan.approved_at = datetime.utcnow().isoformat()
        
        # Save updated plan
        plan_file = self._get_plan_file(plan_id)
        with open(plan_file, 'w', encoding='utf-8') as f:
            json.dump(plan.to_dict(), f, indent=2, ensure_ascii=False)
        
        # Update index
        index = self._load_index()
        if plan_id in index:
            index[plan_id]["status"] = PlanStatus.APPROVED
            index[plan_id]["approved_at"] = plan.approved_at
        self._save_index(index)
        
        return plan
    
    def reject_plan(self, plan_id: str, reason: str) -> Optional[BuildPlan]:
        """Reject a build plan"""
        plan = self.get_plan(plan_id)
        if not plan:
            return None
        
        plan.status = PlanStatus.REJECTED
        plan.rejection_reason = reason
        
        # Save updated plan
        plan_file = self._get_plan_file(plan_id)
        with open(plan_file, 'w', encoding='utf-8') as f:
            json.dump(plan.to_dict(), f, indent=2, ensure_ascii=False)
        
        # Update index
        index = self._load_index()
        if plan_id in index:
            index[plan_id]["status"] = PlanStatus.REJECTED
        self._save_index(index)
        
        return plan
    
    def start_execution(self, plan_id: str) -> Optional[BuildPlan]:
        """Mark plan as executing"""
        plan = self.get_plan(plan_id)
        if not plan or plan.status != PlanStatus.APPROVED:
            return None
        
        plan.status = PlanStatus.EXECUTING
        plan.execution_started_at = datetime.utcnow().isoformat()
        
        # Save updated plan
        plan_file = self._get_plan_file(plan_id)
        with open(plan_file, 'w', encoding='utf-8') as f:
            json.dump(plan.to_dict(), f, indent=2, ensure_ascii=False)
        
        return plan
    
    def record_deviation(
        self,
        plan_id: str,
        deviation_type: DeviationType,
        description: str,
        actual_action: str,
        planned_action: str,
        severity: str = "minor",
        requires_approval: bool = False
    ) -> Optional[PlanDeviation]:
        """Record a deviation from the approved plan"""
        plan = self.get_plan(plan_id)
        if not plan:
            return None
        
        deviation_id = f"dev_{plan_id}_{len(plan.deviations) + 1}"
        deviation = PlanDeviation(
            deviation_id=deviation_id,
            plan_id=plan_id,
            detected_at=datetime.utcnow().isoformat(),
            deviation_type=deviation_type,
            description=description,
            actual_action=actual_action,
            planned_action=planned_action,
            severity=severity,
            requires_approval=requires_approval
        )
        
        plan.deviations.append(asdict(deviation))
        
        # Mark plan as deviated if severity is major or critical
        if severity in ["major", "critical"]:
            plan.status = PlanStatus.DEVIATED
        
        # Save updated plan
        plan_file = self._get_plan_file(plan_id)
        with open(plan_file, 'w', encoding='utf-8') as f:
            json.dump(plan.to_dict(), f, indent=2, ensure_ascii=False)
        
        return deviation
    
    def get_pending_approvals(self) -> List[BuildPlan]:
        """Get all plans pending approval"""
        index = self._load_index()
        pending_plans = [
            pid for pid, data in index.items()
            if data.get('status') == PlanStatus.PENDING
        ]
        plans: List[BuildPlan] = []
        for pid in pending_plans:
            plan = self.get_plan(pid)
            if plan is not None:
                plans.append(plan)
        return plans


# Singleton instance
_plan_approval_service = None

def get_plan_approval_service() -> BuildPlanApprovalService:
    """Get singleton plan approval service instance"""
    global _plan_approval_service
    if _plan_approval_service is None:
        import os
        storage_dir = os.getenv("BUILD_PLANS_DIR", "./data/build_plans")
        _plan_approval_service = BuildPlanApprovalService(storage_dir)
    return _plan_approval_service
