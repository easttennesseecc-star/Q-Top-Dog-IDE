"""
AI Workflow Orchestration API Routes

Endpoints for initiating and managing AI-driven workflow orchestration.
Handles workflow creation, AI context management, and result submission.
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from uuid import uuid4
import logging

from backend.orchestration.workflow_state_machine import WorkflowState, LLMRole
from backend.services.ai_orchestration import (
    get_ai_orchestration_manager,
    AIOrchestrationManager,
)
from backend.services.orchestration_service import OrchestrationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai-workflows", tags=["AI Workflows"])


# ============================================
# Request/Response Models
# ============================================

class WorkflowInitRequest(BaseModel):
    """Request to initialize a new AI-driven workflow"""
    project_id: str
    build_id: str
    user_id: str
    requirements: Dict[str, Any]
    model: Optional[str] = "gpt-4"


class WorkflowInitResponse(BaseModel):
    """Response with workflow initialization details"""
    workflow_id: str
    initial_state: str
    system_prompt: str
    next_action: str


class AIPhaseRequest(BaseModel):
    """Request to submit AI completion for a phase"""
    workflow_id: str
    ai_response: str
    phase_result: Dict[str, Any]


class AIPhaseResponse(BaseModel):
    """Response after phase completion"""
    workflow_id: str
    previous_state: str
    new_state: str
    next_role: Optional[str]
    next_action: str
    is_complete: bool


class WorkflowStatusResponse(BaseModel):
    """Response with workflow status"""
    workflow_id: str
    current_state: str
    progress: float
    completed_phases: list
    next_role: Optional[str]
    is_complete: bool


# ============================================
# Dependency Injection
# ============================================

def get_db_session(request: Request):
    """FastAPI dependency to get a database session."""
    if not hasattr(request.app.state, 'workflow_db_manager'):
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    db_session = None
    try:
        db_session = request.app.state.workflow_db_manager.get_session()
        yield db_session
    finally:
        if db_session:
            db_session.close()

def get_orchestration_service(db=Depends(get_db_session)) -> OrchestrationService:
    """FastAPI dependency to get an OrchestrationService instance."""
    return OrchestrationService(db=db)


# ============================================
# Endpoints
# ============================================

@router.post("/initialize", response_model=WorkflowInitResponse)
async def initialize_workflow(
    req: WorkflowInitRequest,
    ai_manager: AIOrchestrationManager = Depends(get_ai_orchestration_manager),
) -> WorkflowInitResponse:
    """
    Initialize a new AI-driven workflow.
    
    Creates a workflow and returns Q Assistant's system prompt and initial instructions.
    
    Args:
        req: Initialization request with project/user info
        ai_manager: The AI orchestration manager.
        
    Returns:
        Workflow ID, initial state, and Q Assistant's system prompt
    """
    try:
        # Generate IDs
        workflow_id = str(uuid4())
        build_id = req.build_id or str(uuid4())
        
        # Initialize workflow with AI orchestration
        context = await ai_manager.initialize_workflow(
            workflow_id=workflow_id,
            project_id=req.project_id,
            build_id=build_id,
            user_id=req.user_id,
            initial_requirements=req.requirements,
        )
        
        logger.info(f"Initialized workflow {workflow_id}")
        
        return WorkflowInitResponse(
            workflow_id=workflow_id,
            initial_state=context["initial_state"],
            system_prompt=context["system_prompt"],
            next_action="Gather user requirements for the build. Ask clarifying questions and document all specifications.",
        )
    
    except Exception as e:
        logger.error(f"Failed to initialize workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize workflow: {str(e)}")


@router.post("/complete-phase", response_model=AIPhaseResponse)
async def complete_ai_phase(
    req: AIPhaseRequest,
    ai_manager: AIOrchestrationManager = Depends(get_ai_orchestration_manager),
) -> AIPhaseResponse:
    """
    Submit AI completion for a phase and advance workflow.
    
    Args:
        req: Phase completion with AI response and result
        ai_manager: The AI orchestration manager.
        
    Returns:
        Next workflow state and instructions
    """
    try:
        # Advance workflow
        result = await ai_manager.advance_with_ai_result(
            workflow_id=req.workflow_id,
            ai_response=req.ai_response,
            phase_result=req.phase_result,
        )
        
        # Get next action based on new state
        new_state_enum = WorkflowState[result['new_state'].upper().replace('-', '_')]
        next_action = _get_next_action(
            new_state_enum,
            result.get('next_role'),
        )
        
        logger.info(f"Workflow {req.workflow_id} advanced to {result['new_state']}")
        
        return AIPhaseResponse(
            workflow_id=req.workflow_id,
            previous_state=result['previous_state'],
            new_state=result['new_state'],
            next_role=result.get('next_role'),
            next_action=next_action,
            is_complete=result.get('is_complete', False),
        )
    
    except Exception as e:
        logger.error(f"Failed to complete phase: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to complete phase: {str(e)}")


@router.get("/status/{workflow_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    workflow_id: str,
    orchestration_service: OrchestrationService = Depends(get_orchestration_service),
) -> WorkflowStatusResponse:
    """
    Get current status of a workflow.
    
    Args:
        workflow_id: ID of the workflow
        orchestration_service: The orchestration service.
        
    Returns:
        Workflow status including current state and progress
    """
    try:
        # Get status from orchestration service
        status = await orchestration_service.get_workflow_status(workflow_id)
        
        return WorkflowStatusResponse(
            workflow_id=workflow_id,
            current_state=status['current_state'],
            progress=status['progress'],
            completed_phases=status['completed_phases'],
            next_role=status.get('current_role'),
            is_complete=status['status'] == 'complete',
        )
    
    except Exception as e:
        logger.error(f"Failed to get workflow status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get workflow status: {str(e)}")


@router.post("/get-ai-prompt/{workflow_id}")
async def get_ai_prompt(
    workflow_id: str,
    ai_manager: AIOrchestrationManager = Depends(get_ai_orchestration_manager),
    orchestration_service: OrchestrationService = Depends(get_orchestration_service),
) -> Dict[str, Any]:
    """
    Get the current AI prompt for a workflow.
    
    Args:
        workflow_id: ID of the workflow
        ai_manager: The AI orchestration manager.
        orchestration_service: The orchestration service.
        
    Returns:
        Complete AI API request with system and conversation messages
    """
    try:
        # Get current state from orchestration service
        status = await orchestration_service.get_workflow_status(workflow_id)
        current_state_str = status['current_state']
        current_state = WorkflowState(current_state_str)

        # Get AI prompt
        prompt = await ai_manager.get_ai_prompt_for_phase(workflow_id, current_state)
        
        logger.info(f"Generated AI prompt for workflow {workflow_id} state {current_state_str}")
        
        return prompt
    
    except Exception as e:
        logger.error(f"Failed to get AI prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get AI prompt: {str(e)}")


# ============================================
# Helper Functions
# ============================================

def _get_next_action(state: WorkflowState, next_role: Optional[str]) -> str:
    """Get human-readable next action for a state"""
    actions = {
        WorkflowState.DISCOVERY: "Gather requirements from user and prepare specification",
        WorkflowState.PLANNING: "Create detailed implementation plan",
        WorkflowState.HANDOFF_TO_CODER: "Prepare handoff data and notify Code Writer",
        WorkflowState.IMPLEMENTATION: "Implement code based on plan",
        WorkflowState.HANDOFF_TO_TESTER: "Prepare code and test cases for Test Auditor",
        WorkflowState.TESTING: "Test code thoroughly and validate quality",
        WorkflowState.HANDOFF_TO_VERIFIER: "Prepare test results for Verification Overseer",
        WorkflowState.VERIFICATION: "Verify production readiness",
        WorkflowState.HANDOFF_TO_RELEASER: "Prepare deployment for Release Manager",
        WorkflowState.DEPLOYMENT: "Deploy to production",
        WorkflowState.COMPLETE: "Build complete and live!",
    }
    
    return actions.get(state, f"Execute {state.value} phase")
