"""
Build Orchestration API Routes
Endpoints for managing the 5-LLM build pipeline
"""

from fastapi import APIRouter, HTTPException, Body, WebSocket, BackgroundTasks, Header, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import json
import asyncio
from datetime import datetime

from build_orchestrator import (
    orchestrator, BuildProject, BuildPhaseResult, BuildPhase, LLMAssignment
)
from llm_roles_descriptor import (
    LLMRole, get_all_roles, get_role_by_name, get_role_context
)
from llm_config import get_q_assistant_llm
from middleware.tier_validator import require_tier_access

router = APIRouter(prefix="/api/builds", tags=["builds"])

# ============================================================================
# Data Models for Requests/Responses
# ============================================================================

class CreateProjectRequest(BaseModel):
    project_id: str
    project_name: str
    description: str


class AssignLLMRequest(BaseModel):
    role: str  # e.g., "q_assistant", "code_writer", etc.
    llm_id: str
    llm_name: str
    llm_provider: str


class SetRequirementsRequest(BaseModel):
    """Q Assistant submits extracted requirements"""
    requirements: Dict[str, Any]
    design_specs: Dict[str, Any]
    implementation_plan: Dict[str, Any]


class SetImplementationRequest(BaseModel):
    """Code Writer submits implementation"""
    source_code_summary: str
    implementation: Dict[str, Any]


class SetTestResultsRequest(BaseModel):
    """Test Auditor submits test results"""
    test_results: Dict[str, Any]
    test_coverage: float
    critical_issues: List[str]


class SetVerificationRequest(BaseModel):
    """Verification Overseer submits verification report"""
    verification_report: Dict[str, Any]
    go_no_go_decision: str  # "go", "no_go", "go_with_conditions"


class SetReleaseInfoRequest(BaseModel):
    """Release Manager submits release information"""
    release_notes: str
    documentation: Dict[str, str]
    deployment_plan: Dict[str, Any]


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/create")
async def create_project(
    req: CreateProjectRequest,
    user_id: str = Header(None, alias="X-User-ID"),
    tier_info = Depends(lambda: require_tier_access(
        feature='code_execution',
        user_id=user_id
    ))
):
    """Create a new build project
    
    Tier Requirements: PRO or higher (code_execution feature)
    """
    try:
        project = orchestrator.create_project(
            req.project_id,
            req.project_name,
            req.description
        )
        return {
            "status": "ok",
            "project": project.to_dict(),
            "message": f"Project '{req.project_name}' created"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{project_id}")
async def get_project(project_id: str):
    """Get project details"""
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {
        "status": "ok",
        "project": project.to_dict()
    }


@router.get("")
async def list_projects():
    """List all projects"""
    projects = orchestrator.list_projects()
    return {
        "status": "ok",
        "projects": projects,
        "count": len(projects)
    }


@router.post("/{project_id}/assign-llm")
async def assign_llm(project_id: str, req: AssignLLMRequest):
    """Assign an LLM to a role for this project"""
    if not orchestrator.get_project(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not get_role_by_name(req.role):
        raise HTTPException(status_code=400, detail=f"Invalid role: {req.role}")
    
    success = orchestrator.assign_llm_to_role(
        project_id,
        req.role,
        req.llm_id,
        req.llm_name,
        req.llm_provider
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to assign LLM")
    
    project = orchestrator.get_project(project_id)
    return {
        "status": "ok",
        "message": f"LLM assigned to {req.role}",
        "project": project.to_dict()
    }


@router.get("/{project_id}/phase")
async def get_current_phase(project_id: str):
    """Get current build phase information"""
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    phase_info = orchestrator.get_current_phase_info(project_id)
    return {
        "status": "ok",
        "phase_info": phase_info,
        "project_status": project.status
    }


@router.get("/{project_id}/context")
async def get_project_context(project_id: str):
    """Get full project context (for sharing with LLMs)"""
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    context = orchestrator.get_project_context(project_id)
    return {
        "status": "ok",
        "context": context
    }


@router.post("/{project_id}/requirements")
async def set_requirements(project_id: str, req: SetRequirementsRequest):
    """Q Assistant submits extracted requirements"""
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project.requirements = req.requirements
    project.design_specs = req.design_specs
    project.implementation_plan = req.implementation_plan
    
    phase_result = BuildPhaseResult(
        phase=BuildPhase.DISCOVERY.value,
        status="success",
        llm_role=LLMRole.Q_ASSISTANT.value,
        output={
            "requirements_extracted": True,
            "requirements_count": len(req.requirements),
            "design_specs_provided": len(req.design_specs) > 0,
            "implementation_plan_provided": len(req.implementation_plan) > 0
        },
        next_phase=BuildPhase.PLANNING.value
    )
    
    orchestrator.record_phase_result(project_id, phase_result)
    
    project = orchestrator.get_project(project_id)
    return {
        "status": "ok",
        "message": "Requirements recorded",
        "project": project.to_dict()
    }


@router.post("/{project_id}/implementation")
async def set_implementation(project_id: str, req: SetImplementationRequest):
    """Code Writer submits implementation"""
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project.implementation = req.implementation
    project.source_code_summary = req.source_code_summary
    
    phase_result = BuildPhaseResult(
        phase=BuildPhase.IMPLEMENTATION.value,
        status="success",
        llm_role=LLMRole.CODE_WRITER.value,
        output={
            "implementation_complete": True,
            "features_count": len(req.implementation.get("features", [])) if isinstance(req.implementation.get("features"), list) else 0
        },
        next_phase=BuildPhase.TESTING.value
    )
    
    orchestrator.record_phase_result(project_id, phase_result)
    
    project = orchestrator.get_project(project_id)
    return {
        "status": "ok",
        "message": "Implementation recorded",
        "project": project.to_dict()
    }


@router.post("/{project_id}/test-results")
async def set_test_results(project_id: str, req: SetTestResultsRequest):
    """Test Auditor submits test results"""
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project.test_results = req.test_results
    project.test_coverage = req.test_coverage
    project.critical_issues = req.critical_issues
    
    status = "success" if req.test_coverage >= 0.80 and len(req.critical_issues) == 0 else "warning"
    
    phase_result = BuildPhaseResult(
        phase=BuildPhase.TESTING.value,
        status=status,
        llm_role=LLMRole.TEST_AUDITOR.value,
        output={
            "tests_passed": req.test_results.get("tests_passed", 0),
            "tests_failed": req.test_results.get("tests_failed", 0),
            "coverage": req.test_coverage
        },
        issues=req.critical_issues,
        next_phase=BuildPhase.VERIFICATION.value
    )
    
    orchestrator.record_phase_result(project_id, phase_result)
    
    project = orchestrator.get_project(project_id)
    return {
        "status": "ok",
        "message": "Test results recorded",
        "project": project.to_dict()
    }


@router.post("/{project_id}/verification")
async def set_verification(project_id: str, req: SetVerificationRequest):
    """Verification Overseer submits verification report"""
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if req.go_no_go_decision not in ["go", "no_go", "go_with_conditions"]:
        raise HTTPException(status_code=400, detail="Invalid go/no-go decision")
    
    project.verification_report = req.verification_report
    project.go_no_go_decision = req.go_no_go_decision
    
    next_phase = BuildPhase.RELEASE.value if req.go_no_go_decision in ["go", "go_with_conditions"] else BuildPhase.FAILED.value
    status = "success" if req.go_no_go_decision in ["go", "go_with_conditions"] else "failed"
    
    phase_result = BuildPhaseResult(
        phase=BuildPhase.VERIFICATION.value,
        status=status,
        llm_role=LLMRole.VERIFICATION_OVERSEER.value,
        output={
            "go_no_go": req.go_no_go_decision,
            "report_items": len(req.verification_report)
        },
        next_phase=next_phase
    )
    
    orchestrator.record_phase_result(project_id, phase_result)
    
    project = orchestrator.get_project(project_id)
    return {
        "status": "ok",
        "message": f"Verification complete: {req.go_no_go_decision}",
        "project": project.to_dict()
    }


@router.post("/{project_id}/release")
async def set_release_info(project_id: str, req: SetReleaseInfoRequest):
    """Release Manager submits release information"""
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project.release_notes = req.release_notes
    project.documentation = req.documentation
    project.deployment_plan = req.deployment_plan
    
    phase_result = BuildPhaseResult(
        phase=BuildPhase.RELEASE.value,
        status="success",
        llm_role=LLMRole.RELEASE_MANAGER.value,
        output={
            "release_notes_provided": len(req.release_notes) > 0,
            "documentation_count": len(req.documentation),
            "deployment_plan_ready": len(req.deployment_plan) > 0
        },
        next_phase=BuildPhase.COMPLETED.value
    )
    
    orchestrator.record_phase_result(project_id, phase_result)
    
    project = orchestrator.get_project(project_id)
    project.status = "completed"
    project.completed_at = datetime.utcnow().isoformat()
    
    orchestrator._save_project(project)
    
    return {
        "status": "ok",
        "message": "Release prepared - Project complete!",
        "project": project.to_dict()
    }


# ============================================================================
# LLM Role Information Endpoints
# ============================================================================

@router.get("/roles/list")
async def list_llm_roles():
    """Get information about all 5 LLM roles"""
    roles = get_all_roles()
    role_data = []
    for role in roles:
        role_data.append({
            "position": role.position_number,
            "role": role.role.value,
            "title": role.title,
            "description": role.description[:200] + "..." if len(role.description) > 200 else role.description
        })
    
    return {
        "status": "ok",
        "roles": role_data,
        "total": len(role_data)
    }


@router.get("/roles/{role_name}")
async def get_llm_role_info(role_name: str):
    """Get detailed information about a specific LLM role"""
    role_context = get_role_context(role_name)
    if not role_context:
        raise HTTPException(status_code=404, detail=f"Role not found: {role_name}")
    
    return {
        "status": "ok",
        "role": role_context
    }


@router.post("/{project_id}/setup-team")
async def setup_team(project_id: str, assignments: Dict[str, Dict] = Body(...)):
    """
    Bulk assign LLMs to all roles at once
    
    Body:
    {
        "q_assistant": {"llm_id": "...", "llm_name": "...", "llm_provider": "..."},
        "code_writer": {...},
        "test_auditor": {...},
        "verification_overseer": {...},
        "release_manager": {...}
    }
    """
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    assigned_roles = []
    failed_roles = []
    
    for role_name, llm_info in assignments.items():
        success = orchestrator.assign_llm_to_role(
            project_id,
            role_name,
            llm_info.get("llm_id"),
            llm_info.get("llm_name"),
            llm_info.get("llm_provider")
        )
        
        if success:
            assigned_roles.append(role_name)
        else:
            failed_roles.append(role_name)
    
    if failed_roles:
        raise HTTPException(status_code=400, detail=f"Failed to assign: {failed_roles}")
    
    project = orchestrator.get_project(project_id)
    return {
        "status": "ok",
        "message": f"Team setup complete: {len(assigned_roles)} roles assigned",
        "assigned_roles": assigned_roles,
        "project": project.to_dict()
    }


@router.post("/{project_id}/q-assistant/chat")
async def q_assistant_chat(project_id: str, message: Dict[str, str] = Body(...)):
    """
    Chat endpoint for Q Assistant voice/text conversation
    Handles requirement extraction and team coordination
    """
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get Q Assistant LLM assignment
    q_assistant_assignment = project.llm_assignments.get(LLMRole.Q_ASSISTANT.value)
    if not q_assistant_assignment:
        raise HTTPException(status_code=400, detail="Q Assistant not assigned for this project")
    
    user_message = message.get("message", "")
    if not user_message:
        raise HTTPException(status_code=400, detail="No message provided")
    
    # This is a placeholder - real implementation would:
    # 1. Get the Q Assistant LLM instance
    # 2. Send message with system prompt from llm_roles_descriptor
    # 3. Stream or return response
    # 4. Update project context with extracted information
    
    return {
        "status": "ok",
        "message": "Q Assistant received message",
        "assistant_id": q_assistant_assignment.llm_id,
        "assistant_name": q_assistant_assignment.llm_name,
        "response": "I've received your message. I'll help coordinate the build team..."
    }
