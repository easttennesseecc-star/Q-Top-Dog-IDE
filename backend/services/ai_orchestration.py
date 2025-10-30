"""
AI System Integration with Orchestration

Integrates orchestration prompts into Q Assistant AI models.
Manages AI context, state awareness, and automatic workflow progression.
"""

from typing import Dict, Optional, List, Any
from enum import Enum
import logging
from datetime import datetime

from backend.orchestration.workflow_state_machine import WorkflowState, LLMRole
from backend.orchestration.orchestration_prompts import get_orchestration_prompt, get_workflow_context
from backend.services.orchestration_service import OrchestrationService

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
        self.contexts: Dict[str, AIOrchestrationContext] = {}
    
    async def initialize_workflow(
        self,
        workflow_id: str,
        project_id: str,
        build_id: str,
        user_id: str,
        initial_requirements: Dict[str, Any],
    ) -> AIOrchestrationContext:
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
            project_id=project_id,
            build_id=build_id,
            user_id=user_id,
            initial_requirements=initial_requirements,
        )
        
        # Create AI context for Q Assistant
        context = AIOrchestrationContext(
            workflow_id=workflow_id,
            role=LLMRole.Q_ASSISTANT,
        )
        
        # Store context
        self.contexts[workflow_id] = context
        
        logger.info(f"Initialized workflow {workflow_id} with Q Assistant orchestration")
        
        return context
    
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
        context = self.contexts.get(workflow_id)
        if not context:
            raise ValueError(f"No context found for workflow {workflow_id}")
        
        # Add AI response to history
        context.add_message("assistant", ai_response)
        
        # Advance the workflow in orchestration service
        result = await self.orchestration_service.advance_workflow(
            workflow_id=workflow_id,
            current_role=context.role,
            completed_state=context.current_state or WorkflowState.DISCOVERY,
            phase_result=phase_result,
        )
        
        logger.info(f"Advanced workflow {workflow_id} to {result['new_state']}")
        
        return result
    
    def get_context_for_role(self, workflow_id: str, role: LLMRole) -> AIOrchestrationContext:
        """
        Get or create context for a specific role.
        
        Args:
            workflow_id: Workflow ID
            role: AI role
            
        Returns:
            AI orchestration context for the role
        """
        key = f"{workflow_id}:{role.value}"
        
        if key not in self.contexts:
            context = AIOrchestrationContext(workflow_id, role)
            self.contexts[key] = context
        
        return self.contexts[key]
    
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
        context = self.contexts.get(workflow_id)
        if not context:
            raise ValueError(f"No context found for workflow {workflow_id}")
        
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


def get_ai_orchestration_manager() -> AIOrchestrationManager:
    """
    Get the global AI orchestration manager.
    
    Returns:
        The manager instance
        
    Raises:
        RuntimeError: If manager not initialized
    """
    if _orchestration_manager is None:
        raise RuntimeError("AI Orchestration Manager not initialized. Call initialize_ai_orchestration() first.")
    return _orchestration_manager
