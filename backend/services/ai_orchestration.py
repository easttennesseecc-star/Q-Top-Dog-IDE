"""
AI System Integration with Orchestration

Integrates orchestration prompts into Q Assistant AI models.
Manages AI context, state awareness, and automatic workflow progression.
"""

from typing import Dict, Optional, List, Any, Awaitable, Union
from enum import Enum
import logging
from datetime import datetime
from fastapi import Request

from backend.orchestration.workflow_state_machine import WorkflowState, LLMRole
from backend.orchestration.orchestration_prompts import get_orchestration_prompt, get_workflow_context
from backend.services.orchestration_service import OrchestrationService
from backend.services.snapshot_store import SnapshotStore
from backend.orchestration.workflow_state_machine import WorkflowStateTransition

logger = logging.getLogger(__name__)


class AIModelType(Enum):
    """Supported AI model types"""
    GPT4 = "gpt-4"
    GPT35 = "gpt-3.5-turbo"
    CLAUDE = "claude-3-opus"
    LOCAL = "local-model"


class AIOrchestrationContext:
    """
    Manages AI context for orchestration.
    Maintains state, prompts, and conversation history for each role.
    """
    
    def __init__(self, workflow_id: str, role: LLMRole, model_type: AIModelType = AIModelType.GPT4):
        """
        Initialize AI orchestration context.
        
        Args:
            workflow_id: ID of the workflow
            role: AI role (q_assistant, code_writer, etc.)
            model_type: Which AI model to use
        """
        self.workflow_id = workflow_id
        self.role = role
        self.model_type = model_type
        self.system_prompt = get_orchestration_prompt(role.value)
        self.conversation_history: List[Dict[str, str]] = []
        self.context_data: Dict[str, Any] = {}
        self.created_at = datetime.utcnow()
        self.current_state: Optional[WorkflowState] = None
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_system_message(self, current_state: WorkflowState) -> Dict[str, str]:
        """
        Get the full system message for the AI model.
        
        Args:
            current_state: Current workflow state
            
        Returns:
            System message dict for API call
        """
        self.current_state = current_state
        workflow_context = get_workflow_context(self.workflow_id, current_state.value)
        
        full_prompt = f"{self.system_prompt}\n\n{workflow_context}"
        
        return {
            "role": "system",
            "content": full_prompt
        }
    
    def get_conversation_messages(self) -> List[Dict[str, str]]:
        """Get all messages for API call (excluding system)"""
        return self.conversation_history
    
    def build_api_request(self, current_state: WorkflowState) -> Dict[str, Any]:
        """
        Build a complete API request for the AI model.
        
        Args:
            current_state: Current workflow state
            
        Returns:
            Request dict for AI API
        """
        messages = [
            self.get_system_message(current_state),
            *self.get_conversation_messages()
        ]
        
        return {
            "model": self.model_type.value,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,
            "top_p": 0.9,
        }


class _ContextAwaitableProxy:
    """Proxy that can be used directly or awaited to obtain the context.
    This allows tests that call get_context_for_role() with or without await to succeed.
    """
    def __init__(self, ctx: AIOrchestrationContext):
        self._ctx = ctx

    def __getattr__(self, item):
        return getattr(self._ctx, item)

    def __repr__(self) -> str:
        return f"<ContextProxy {self._ctx}>"

    def __await__(self):
        if False:
            yield  # make this a generator-compatible method
        return self._ctx


class AIOrchestrationManager:
    """
    Manages AI-driven workflow orchestration.
    Coordinates between AI models and orchestration service.
    """
    
    def __init__(self, orchestration_service: OrchestrationService):
        """
        Initialize AI orchestration manager.
        
        Args:
            orchestration_service: Service for workflow management
        """
        self.orchestration_service = orchestration_service
        self.snapshot_store = SnapshotStore()

    async def _get_or_create_context(self, workflow_id: str, role: LLMRole) -> AIOrchestrationContext:
        """
        Creates a transient context for a role. In a real-world scenario,
        this might load conversation history from a database.
        """
        # For now, we create a new context each time.
        # A future implementation could persist/load history.
        return AIOrchestrationContext(workflow_id=workflow_id, role=role)
    
    async def initialize_workflow(
        self,
        workflow_id: str,
        project_id: str,
        build_id: str,
        user_id: str,
        initial_requirements: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Initialize a new workflow with AI orchestration.
        
        Args:
            workflow_id: ID for the workflow
            project_id: Project identifier
            build_id: Build identifier
            user_id: User who initiated the build
            initial_requirements: Initial requirements from user
            
        Returns:
            AI orchestration context for Q Assistant
        """
        # Start the workflow in orchestration service
        workflow_id, initial_state = await self.orchestration_service.start_workflow(
            workflow_id=workflow_id,
            project_id=project_id,
            build_id=build_id,
            user_id=user_id,
            initial_requirements=initial_requirements,
        )
        
        # Create a transient AI context for the initial role
        context = await self._get_or_create_context(workflow_id, LLMRole.Q_ASSISTANT)
        
        logger.info(f"Initialized workflow {workflow_id} with Q Assistant orchestration")
        # Initial snapshot for clean baseline
        try:
            self.take_snapshot(workflow_id, label="init")
        except Exception:
            logger.debug("Snapshot init failed (non-fatal)")
        
        return {
            "workflow_id": workflow_id,
            "initial_state": initial_state.value,
            "system_prompt": context.system_prompt,
        }
    
    async def advance_with_ai_result(
        self,
        workflow_id: str,
        ai_response: str,
        phase_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Advance workflow based on AI model completion.
        
        Args:
            workflow_id: Workflow ID
            ai_response: The AI's response/completion
            phase_result: Structured result from the phase
            
        Returns:
            Result from orchestration service
        """
        # Get current workflow status to determine current state and role
        status = await self.orchestration_service.get_workflow_status(workflow_id)
        if not status:
            raise ValueError(f"Could not retrieve status for workflow {workflow_id}")

        current_state = WorkflowState(status["current_state"])
        current_role = LLMRole(status["current_role"])

        # Get a transient context for the current role
        context = await self._get_or_create_context(workflow_id, current_role)
        context.current_state = current_state # Set current state for context
        
        # Add AI response to history (in this transient context)
        context.add_message("assistant", ai_response)
        
        # Pre-advance snapshot to capture inputs
        try:
            self.take_snapshot(
                workflow_id,
                label="pre-advance",
                extra={
                    "ai_response": ai_response,
                    "phase_result": phase_result,
                    "completed_state": current_state.value,
                },
            )
        except Exception:
            logger.debug("Snapshot pre-advance failed (non-fatal)")
        
        # Advance the workflow in orchestration service
        result = await self.orchestration_service.advance_workflow(
            workflow_id=workflow_id,
            current_role=context.role,
            completed_state=current_state,
            phase_result=phase_result,
        )
        
        logger.info(f"Advanced workflow {workflow_id} to {result['new_state']}")
        # Post-advance snapshot to capture outputs
        try:
            self.take_snapshot(
                workflow_id,
                label="post-advance",
                extra={
                    "result": result,
                },
            )
        except Exception:
            logger.debug("Snapshot post-advance failed (non-fatal)")
        
        return result
    
    # A context-like return type that can be used directly or awaited
    ContextLike = Union[AIOrchestrationContext, Awaitable[AIOrchestrationContext]]

    def get_context_for_role(self, workflow_id: str, role: LLMRole) -> ContextLike:
        """
        Get or create context for a specific role.
        
        Args:
            workflow_id: Workflow ID
            role: AI role
            
        Returns:
            AI orchestration context for the role
        """
        # This now returns a transient context
        context = AIOrchestrationContext(workflow_id, role)
        
        # Return a proxy that is both usable directly and awaitable
        return _ContextAwaitableProxy(context)

    def take_snapshot(self, workflow_id: str, label: Optional[str] = None, extra: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Capture a snapshot of all role contexts for a workflow to aid conversation continuity."""
        # This method is now more complex as contexts are not stored.
        # For snapshotting, we'd need to fetch state and reconstruct.
        # For now, we'll log that it's a simplified implementation.
        logger.debug("take_snapshot is simplified and does not capture full context history.")
        
        snapshot: Dict[str, Any] = {
            "workflow_id": workflow_id,
            "timestamp": datetime.utcnow().isoformat(),
            "contexts": [], # Contexts are no longer stored in a dict
        }
        if extra:
            snapshot["extra"] = extra

        path = self.snapshot_store.save_snapshot(workflow_id, snapshot, label=label)
        if path:
            logger.info(f"Saved (simplified) snapshot for workflow {workflow_id}: {path}")
        else:
            logger.debug(f"Failed to save snapshot for workflow {workflow_id} (non-fatal)")
        return path
    
    async def get_ai_prompt_for_phase(
        self,
        workflow_id: str,
        current_state: WorkflowState,
    ) -> Dict[str, Any]:
        """
        Get complete AI prompt for current phase.
        
        Args:
            workflow_id: Workflow ID
            current_state: Current workflow state
            
        Returns:
            Complete AI API request dict
        """
        # Determine the role for the current state
        role = WorkflowStateTransition.get_next_role(current_state)
        if not role:
            # Fallback for terminal or initial states
            status = await self.orchestration_service.get_workflow_status(workflow_id)
            role = LLMRole(status["current_role"])

        context = await self._get_or_create_context(workflow_id, role)
        
        return context.build_api_request(current_state)


# Global manager instance
_orchestration_manager: Optional[AIOrchestrationManager] = None


def initialize_ai_orchestration(orchestration_service: OrchestrationService) -> AIOrchestrationManager:
    """
    Initialize the global AI orchestration manager.
    
    Args:
        orchestration_service: Orchestration service instance
        
    Returns:
        Initialized manager
    """
    global _orchestration_manager
    _orchestration_manager = AIOrchestrationManager(orchestration_service)
    logger.info("AI Orchestration Manager initialized")
    return _orchestration_manager


# ... existing code ...
def get_ai_orchestration_manager(request: Request) -> "AIOrchestrationManager":
    """
    Get the AI orchestration manager from the request state.
    This function is designed to be used as a FastAPI dependency.
    """
    manager = getattr(request.app.state, "ai_orchestration_manager", None)
    if manager is None:
        raise RuntimeError("AI Orchestration Manager not initialized.")
    return manager
