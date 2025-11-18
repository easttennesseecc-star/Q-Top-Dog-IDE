"""
Orchestration Workflow API Routes

Endpoints for managing AI workflow orchestration:
- Starting new workflows
- Advancing workflows between roles
- Getting workflow status
- Requesting retries
- Retrieving workflow history
"""

from fastapi import APIRouter, HTTPException, Depends, Body, Path, Request, Header
from sqlalchemy.orm import Session
from typing import Dict, Optional, Any
import logging

from backend.orchestration.workflow_state_machine import (
    WorkflowState,
    LLMRole,
    WorkflowStateTransition,
)
from backend.services.orchestration_service import OrchestrationService
from backend.middleware.tier_validator import require_tier_access

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/workflows", tags=["orchestration"])


# ================================
# Dependency Injection
# ================================

def get_db_manager(request: Request) -> Any:
    """Get workflow database manager from app context"""
    if not hasattr(request.app, 'workflow_db_manager'):
        raise HTTPException(
            status_code=500,
            detail="Workflow database not initialized"
        )
    return request.app.workflow_db_manager


def _tier_dep(user_id: Optional[str] = Header(None, alias="X-User-ID")):
    """Dependency wrapper to validate tier access with header-provided user id."""
    return require_tier_access(feature='webhooks', user_id=user_id)



# ================================
# Request/Response Models
# ================================

class WorkflowStartRequest:
    """Request to start a new workflow"""
    def __init__(
        self,
        project_id: str,
        build_id: str,
        user_id: str,
        requirements: Dict,
        metadata: Optional[Dict] = None,
    ):
        self.project_id = project_id
        self.build_id = build_id
        self.user_id = user_id
        self.requirements = requirements
        self.metadata = metadata


class WorkflowAdvanceRequest:
    """Request to advance workflow to next phase"""
    def __init__(
        self,
        role: str,
        completed_state: str,
        phase_result: Dict,
        next_state: Optional[str] = None,
    ):
        self.role = role
        self.completed_state = completed_state
        self.phase_result = phase_result
        self.next_state = next_state


class WorkflowRetryRequest:
    """Request to retry a workflow phase"""
    def __init__(self, reason: str):
        self.reason = reason


# ================================
# Route Handlers
# ================================

@router.post("/{project_id}/start")
async def start_workflow(
    request: Request,
    project_id: str = Path(..., description="Project ID"),
    build_id: str = Body(..., description="Build ID"),
    user_id_body: str = Body(..., description="User ID"),
    requirements: Dict = Body(..., description="Initial requirements"),
    metadata: Optional[Dict] = Body(None, description="Optional metadata"),
    user_id: Optional[str] = Header(None, alias="X-User-ID"),
    tier_info = Depends(_tier_dep)
):
    """
    Start a new build workflow with database persistence.
    
    Tier Requirements: PRO or higher (webhooks feature)
    
    Initiates Q Assistant discovery phase to gather and analyze requirements.
    Returns workflow ID to be used for subsequent operations.
    
    Args:
        project_id: Project identifier
        build_id: Build identifier
        user_id: User initiating the build
        requirements: Initial requirements/user input
        metadata: Optional metadata about the build
        request: FastAPI request object
        
    Returns:
        {
            "workflow_id": "uuid",
            "initial_state": "discovery",
            "status": "started",
            "next_role": "q_assistant",
            "instructions": "Q Assistant will now gather requirements..."
        }
    """
    try:
        effective_user_id = user_id or user_id_body
        logger.info(
            f"Starting workflow for project {project_id}, build {build_id}, user {effective_user_id}"
        )
        
        # Get database manager from app
        dbm = get_db_manager(request)
        
        # Create orchestration service with DB manager
        orchestration_service = OrchestrationService(db_manager=dbm)
        
        # Start workflow
        workflow_id, initial_state = await orchestration_service.start_workflow(
            project_id=project_id,
            build_id=build_id,
            user_id=effective_user_id,
            initial_requirements=requirements,
            metadata=metadata,
        )
        
        response = {
            "workflow_id": workflow_id,
            "build_id": build_id,
            "initial_state": initial_state.value,
            "status": "started",
            "current_role": "q_assistant",
            "next_role": "q_assistant",
            "instructions": WorkflowStateTransition.get_description(initial_state),
        }
        
        logger.info(f"✅ Workflow {workflow_id} started successfully")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to start workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{workflow_id}/advance")
async def advance_workflow(
    request: Request,
    workflow_id: str = Path(..., description="Workflow ID"),
    role: str = Body(..., description="Role completing the work"),
    completed_state: str = Body(..., description="State that was completed"),
    phase_result: Dict = Body(..., description="Result from completed phase"),
    next_state: Optional[str] = Body(None, description="Optional specific next state"),
):
    """
    Advance workflow when a role completes their work with database persistence.
    
    Called by Q Assistant, Code Writer, Test Auditor, Verification Overseer, or Release Manager
    when they complete their phase. Validates transition, creates handoff record, and
    determines next role.
    
    Args:
        workflow_id: ID of workflow to advance
        role: Role completing the work (q_assistant, code_writer, test_auditor, etc.)
        completed_state: State that was just completed (planning, implementation, etc.)
        phase_result: Output/result from the completed phase
        next_state: Optional - specify exact next state for conditional transitions
        request: FastAPI request object
        
    Returns:
        {
            "workflow_id": "uuid",
            "previous_state": "planning",
            "new_state": "handoff_to_coder",
            "next_role": "code_writer",
            "is_complete": false,
            "handoff_data": {...},
            "state_description": "Code Writer is implementing the solution"
        }
    """
    try:
        logger.info(
            f"Advancing workflow {workflow_id}: {role} completed {completed_state}"
        )
        
        # Parse enums
        try:
            role_enum = LLMRole[role.upper()]
            completed_state_enum = WorkflowState[completed_state.upper()]
            next_state_enum = WorkflowState[next_state.upper()] if next_state else None
        except KeyError as e:
            raise ValueError(f"Invalid role or state: {str(e)}")
        
        # Get database manager
        dbm = get_db_manager(request)
        
        # Create orchestration service with DB manager
        orchestration_service = OrchestrationService(db_manager=dbm)
        
        result = await orchestration_service.advance_workflow(
            workflow_id=workflow_id,
            current_role=role_enum,
            completed_state=completed_state_enum,
            phase_result=phase_result,
            next_state=next_state_enum,
        )
        
        logger.info(f"✅ Workflow {workflow_id} advanced to {result['new_state']}")
        
        return result
        
    except ValueError as e:
        logger.error(f"Invalid workflow advance request: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to advance workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}/status")
async def get_workflow_status(
    request: Request,
    workflow_id: str = Path(..., description="Workflow ID"),
):
    """
    Get comprehensive status of a workflow from backend.database.
    
    Returns current state, progress, completed phases, and next expectations.
    
    Args:
        workflow_id: ID of workflow to check
        request: FastAPI request object
        
    Returns:
        {
            "workflow_id": "uuid",
            "current_state": "testing",
            "current_role": "test_auditor",
            "progress": 50.0,
            "completed_phases": ["discovery", "planning", "implementation"],
            "handoff_history": [...],
            "elapsed_time": "0h 45m",
            "next_expectations": {...}
        }
    """
    try:
        logger.info(f"Getting status for workflow {workflow_id}")
        
        # Get database manager
        dbm = get_db_manager(request)
        
        # Create orchestration service with DB manager
        orchestration_service = OrchestrationService(db_manager=dbm)
        
        status = await orchestration_service.get_workflow_status(workflow_id)
        
        return status
        
    except Exception as e:
        logger.error(f"❌ Failed to get workflow status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{workflow_id}/request-retry")
async def request_workflow_retry(
    workflow_id: str = Path(..., description="Workflow ID"),
    reason: str = Body(..., description="Reason for retry request"),
):
    """
    Request that the previous role retry their work.
    
    Called when current role finds issues in previous phase output.
    Rolls back workflow and notifies previous role to retry.
    
    Args:
        workflow_id: ID of workflow
        reason: Reason for retry (e.g., "Tests failing", "Security issues found")
        
    Returns:
        {
            "workflow_id": "uuid",
            "retry_requested": true,
            "previous_state": "implementation",
            "reason": "Tests failing",
            "notification_sent": true,
            "timestamp": "2025-10-29T..."
        }
    """
    try:
        logger.info(f"Retry requested for workflow {workflow_id}: {reason}")
        
        orchestration_service = OrchestrationService(db=None)
        
        # Get current state from DB (placeholder)
        current_state = WorkflowState.TESTING  # Would fetch from DB
        
        result = await orchestration_service.request_retry(
            workflow_id=workflow_id,
            current_state=current_state,
            reason=reason,
        )
        
        logger.info(f"Retry registered for workflow {workflow_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to request retry: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}/history")
async def get_workflow_history(
    workflow_id: str = Path(..., description="Workflow ID"),
    limit: int = 50,
):
    """
    Get handoff history for a workflow.
    
    Returns all handoff records showing what was passed between roles
    at each phase transition. Useful for debugging and understanding
    what information each role received.
    
    Args:
        workflow_id: ID of workflow
        limit: Maximum number of handoffs to return (default 50)
        
    Returns:
        {
            "workflow_id": "uuid",
            "handoff_count": 5,
            "handoffs": [
                {
                    "from_role": "q_assistant",
                    "to_role": "code_writer",
                    "from_state": "planning",
                    "to_state": "implementation",
                    "timestamp": "...",
                    "data_transferred": {...}
                },
                ...
            ]
        }
    """
    try:
        logger.info(f"Getting history for workflow {workflow_id}")
        
        orchestration_service = OrchestrationService(db=None)
        
        history = await orchestration_service.get_workflow_history(
            workflow_id=workflow_id,
            limit=limit,
        )
        
        return {
            "workflow_id": workflow_id,
            "handoff_count": len(history),
            "handoffs": history,
        }
        
    except Exception as e:
        logger.error(f"Failed to get workflow history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/project/{project_id}/stats")
async def get_project_workflow_stats(
    project_id: str = Path(..., description="Project ID"),
):
    """
    Get workflow statistics for a project.
    
    Returns metrics on all workflows in the project including
    completion rates, average duration, and failure points.
    
    Args:
        project_id: Project identifier
        
    Returns:
        {
            "project_id": "uuid",
            "total_workflows": 42,
            "completed": 38,
            "in_progress": 3,
            "failed": 1,
            "average_duration": "2h 15m",
            "success_rate": 95.2,
            "most_common_failure_point": "testing",
            "average_handoffs": 7.2
        }
    """
    try:
        logger.info(f"Getting workflow stats for project {project_id}")
        
        orchestration_service = OrchestrationService(db=None)
        
        stats = await orchestration_service.get_workflow_stats(project_id)
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get workflow stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{workflow_id}/rollback")
async def rollback_workflow(
    workflow_id: str = Path(..., description="Workflow ID"),
    target_state: str = Body(..., description="State to rollback to"),
    reason: str = Body(..., description="Reason for rollback"),
):
    """
    Rollback workflow to a previous state.
    
    Used when critical errors are detected and workflow needs to
    return to an earlier phase for remediation.
    
    Args:
        workflow_id: ID of workflow
        target_state: State to rollback to (e.g., "implementation")
        reason: Reason for rollback
        
    Returns:
        {
            "workflow_id": "uuid",
            "rollback_successful": true,
            "previous_state": "testing",
            "new_state": "implementation",
            "reason": "Critical security vulnerability found",
            "rolled_back_by": "system",
            "timestamp": "..."
        }
    """
    try:
        logger.warning(f"Rolling back workflow {workflow_id} to {target_state}: {reason}")
        
        try:
            target_state_enum = WorkflowState[target_state.upper()]
        except KeyError:
            raise ValueError(f"Invalid target state: {target_state}")
        
        orchestration_service = OrchestrationService(db=None)
        
        result = await orchestration_service.rollback_workflow(
            workflow_id=workflow_id,
            target_state=target_state_enum,
            reason=reason,
        )
        
        return result
        
    except ValueError as e:
        logger.error(f"Invalid rollback request: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to rollback workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
