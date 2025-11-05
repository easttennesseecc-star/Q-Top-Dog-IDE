"""
Build Plan Approval API Routes
Endpoints for plan generation, approval, and deviation tracking
"""

from fastapi import APIRouter, HTTPException, Path as PathParam
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from backend.services.build_plan_approval_service import (
    get_plan_approval_service,
    BuildPlan,
    PlanStep,
    DeviationType,
    PlanStatus
)

router = APIRouter(prefix="/api/v1/build-plans", tags=["build-plans"])


class PlanStepRequest(BaseModel):
    step_id: str
    order: int
    description: str
    estimated_duration: str
    files_affected: List[str]
    dependencies: List[str]
    risk_level: str = Field(..., pattern="^(low|medium|high)$")
    verification_criteria: str


class GeneratePlanRequest(BaseModel):
    workflow_id: str
    generated_by: str
    objective: str
    scope: str
    steps: List[PlanStepRequest]
    risks: Optional[List[str]] = []
    dependencies_to_install: Optional[List[str]] = []
    files_to_create: Optional[List[str]] = []
    files_to_modify: Optional[List[str]] = []
    files_to_delete: Optional[List[str]] = []
    estimated_total_duration: Optional[str] = None


class ApprovalRequest(BaseModel):
    approved_by: str


class RejectionRequest(BaseModel):
    reason: str


class DeviationRequest(BaseModel):
    deviation_type: DeviationType
    description: str
    actual_action: str
    planned_action: str
    severity: str = Field(default="minor", pattern="^(minor|major|critical)$")
    requires_approval: bool = False


@router.post("/", response_model=Dict, status_code=201)
async def generate_plan(request: GeneratePlanRequest):
    """Generate a new build plan"""
    service = get_plan_approval_service()
    
    steps = [
        PlanStep(
            step_id=s.step_id,
            order=s.order,
            description=s.description,
            estimated_duration=s.estimated_duration,
            files_affected=s.files_affected,
            dependencies=s.dependencies,
            risk_level=s.risk_level,
            verification_criteria=s.verification_criteria
        )
        for s in request.steps
    ]
    
    plan = service.generate_plan(
        workflow_id=request.workflow_id,
        generated_by=request.generated_by,
        objective=request.objective,
        scope=request.scope,
        steps=steps,
        risks=request.risks,
        dependencies_to_install=request.dependencies_to_install,
        files_to_create=request.files_to_create,
        files_to_modify=request.files_to_modify,
        files_to_delete=request.files_to_delete,
        estimated_total_duration=request.estimated_total_duration
    )
    
    return plan.to_dict()


@router.get("/{plan_id}")
async def get_plan(plan_id: str = PathParam(..., description="Plan ID")):
    """Get a specific build plan"""
    service = get_plan_approval_service()
    plan = service.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan.to_dict()


@router.get("/workflow/{workflow_id}")
async def get_workflow_plan(workflow_id: str):
    """Get the latest plan for a workflow"""
    service = get_plan_approval_service()
    plan = service.get_plan_by_workflow(workflow_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No plan found for this workflow")
    return plan.to_dict()


@router.post("/{plan_id}/approve")
async def approve_plan(
    plan_id: str,
    request: ApprovalRequest
):
    """Approve a build plan"""
    service = get_plan_approval_service()
    plan = service.approve_plan(plan_id, request.approved_by)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"message": "Plan approved", "plan": plan.to_dict()}


@router.post("/{plan_id}/reject")
async def reject_plan(
    plan_id: str,
    request: RejectionRequest
):
    """Reject a build plan"""
    service = get_plan_approval_service()
    plan = service.reject_plan(plan_id, request.reason)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"message": "Plan rejected", "plan": plan.to_dict()}


@router.post("/{plan_id}/start-execution")
async def start_execution(plan_id: str):
    """Start executing an approved plan"""
    service = get_plan_approval_service()
    plan = service.start_execution(plan_id)
    if not plan:
        raise HTTPException(
            status_code=400,
            detail="Plan not found or not approved"
        )
    return {"message": "Execution started", "plan": plan.to_dict()}


@router.post("/{plan_id}/deviations")
async def record_deviation(
    plan_id: str,
    request: DeviationRequest
):
    """Record a deviation from the approved plan"""
    service = get_plan_approval_service()
    deviation = service.record_deviation(
        plan_id=plan_id,
        deviation_type=request.deviation_type,
        description=request.description,
        actual_action=request.actual_action,
        planned_action=request.planned_action,
        severity=request.severity,
        requires_approval=request.requires_approval
    )
    if not deviation:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"message": "Deviation recorded", "deviation": deviation}


@router.get("/pending/all")
async def get_pending_approvals():
    """Get all plans pending approval"""
    service = get_plan_approval_service()
    pending = service.get_pending_approvals()
    return {
        "count": len(pending),
        "plans": [p.to_dict() for p in pending]
    }
