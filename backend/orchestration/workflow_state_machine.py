"""
Workflow State Machine for Q Assistant Orchestration

Defines all possible workflow states and valid transitions between them.
Ensures orchestration follows a structured path from discovery to deployment.
"""

from enum import Enum
from typing import Set, Dict, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)


class WorkflowState(str, Enum):
    """All possible states in a build workflow"""
    
    # Discovery phase: Q Assistant gathers requirements
    DISCOVERY = "discovery"
    
    # Planning phase: Q Assistant creates implementation plan
    PLANNING = "planning"
    
    # Handoff to Code Writer
    HANDOFF_TO_CODER = "handoff_to_coder"
    
    # Implementation phase: Code Writer writes code
    IMPLEMENTATION = "implementation"
    
    # Handoff to Test Auditor
    HANDOFF_TO_TESTER = "handoff_to_tester"
    
    # Testing phase: Test Auditor validates code
    TESTING = "testing"
    
    # Handoff to Verification Overseer
    HANDOFF_TO_VERIFIER = "handoff_to_verifier"
    
    # Verification phase: Verification Overseer checks for issues
    VERIFICATION = "verification"
    
    # Handoff to Release Manager
    HANDOFF_TO_RELEASER = "handoff_to_releaser"
    
    # Deployment phase: Release Manager deploys to production
    DEPLOYMENT = "deployment"
    
    # Workflow complete
    COMPLETE = "complete"
    
    # Workflow error - needs manual intervention
    ERROR = "error"


class LLMRole(str, Enum):
    """All LLM roles in the orchestration system"""
    
    Q_ASSISTANT = "q_assistant"
    CODE_WRITER = "code_writer"
    TEST_AUDITOR = "test_auditor"
    VERIFICATION_OVERSEER = "verification_overseer"
    RELEASE_MANAGER = "release_manager"


class WorkflowStateTransition:
    """
    Manages valid state transitions in the workflow.
    Ensures only valid transitions are allowed.
    """
    
    # Define all valid transitions: (from_state, to_state)
    VALID_TRANSITIONS: Set[Tuple[WorkflowState, WorkflowState]] = {
        # Discovery to Planning
        (WorkflowState.DISCOVERY, WorkflowState.PLANNING),
        
        # Planning to Handoff to Coder
        (WorkflowState.PLANNING, WorkflowState.HANDOFF_TO_CODER),
        
        # Handoff to Implementation
        (WorkflowState.HANDOFF_TO_CODER, WorkflowState.IMPLEMENTATION),
        
        # Implementation to Handoff to Tester
        (WorkflowState.IMPLEMENTATION, WorkflowState.HANDOFF_TO_TESTER),
        
        # Handoff to Testing
        (WorkflowState.HANDOFF_TO_TESTER, WorkflowState.TESTING),
        
        # Testing can go to Verification (pass) or back to Implementation (fail/retry)
        (WorkflowState.TESTING, WorkflowState.HANDOFF_TO_VERIFIER),
        (WorkflowState.TESTING, WorkflowState.IMPLEMENTATION),  # Retry
        
        # Verification to Deployment (pass) or back to Implementation (fail/retry)
        (WorkflowState.HANDOFF_TO_VERIFIER, WorkflowState.VERIFICATION),
        (WorkflowState.VERIFICATION, WorkflowState.HANDOFF_TO_RELEASER),
        (WorkflowState.VERIFICATION, WorkflowState.IMPLEMENTATION),  # Retry
        
        # Deployment to Complete
        (WorkflowState.HANDOFF_TO_RELEASER, WorkflowState.DEPLOYMENT),
        (WorkflowState.DEPLOYMENT, WorkflowState.COMPLETE),
        
        # Error state can transition back to previous phases for retry
        (WorkflowState.DISCOVERY, WorkflowState.ERROR),
        (WorkflowState.PLANNING, WorkflowState.ERROR),
        (WorkflowState.IMPLEMENTATION, WorkflowState.ERROR),
        (WorkflowState.TESTING, WorkflowState.ERROR),
        (WorkflowState.VERIFICATION, WorkflowState.ERROR),
        (WorkflowState.DEPLOYMENT, WorkflowState.ERROR),
        
        # From ERROR, can retry to previous phase
        (WorkflowState.ERROR, WorkflowState.DISCOVERY),
        (WorkflowState.ERROR, WorkflowState.PLANNING),
        (WorkflowState.ERROR, WorkflowState.IMPLEMENTATION),
        (WorkflowState.ERROR, WorkflowState.TESTING),
        (WorkflowState.ERROR, WorkflowState.VERIFICATION),
    }
    
    # Map states to responsible roles
    STATE_TO_ROLE: Dict[WorkflowState, LLMRole] = {
        WorkflowState.DISCOVERY: LLMRole.Q_ASSISTANT,
        WorkflowState.PLANNING: LLMRole.Q_ASSISTANT,
        WorkflowState.HANDOFF_TO_CODER: LLMRole.Q_ASSISTANT,
        WorkflowState.IMPLEMENTATION: LLMRole.CODE_WRITER,
        WorkflowState.HANDOFF_TO_TESTER: LLMRole.CODE_WRITER,
        WorkflowState.TESTING: LLMRole.TEST_AUDITOR,
        WorkflowState.HANDOFF_TO_VERIFIER: LLMRole.TEST_AUDITOR,
        WorkflowState.VERIFICATION: LLMRole.VERIFICATION_OVERSEER,
        WorkflowState.HANDOFF_TO_RELEASER: LLMRole.VERIFICATION_OVERSEER,
        WorkflowState.DEPLOYMENT: LLMRole.RELEASE_MANAGER,
        WorkflowState.COMPLETE: LLMRole.RELEASE_MANAGER,
    }
    
    # Map states to human-readable descriptions
    STATE_DESCRIPTIONS: Dict[WorkflowState, str] = {
        WorkflowState.DISCOVERY: "Q Assistant is gathering requirements",
        WorkflowState.PLANNING: "Q Assistant is creating implementation plan",
        WorkflowState.HANDOFF_TO_CODER: "Q Assistant is handing off to Code Writer",
        WorkflowState.IMPLEMENTATION: "Code Writer is implementing the solution",
        WorkflowState.HANDOFF_TO_TESTER: "Code Writer is handing off to Test Auditor",
        WorkflowState.TESTING: "Test Auditor is validating the code",
        WorkflowState.HANDOFF_TO_VERIFIER: "Test Auditor is handing off to Verification Overseer",
        WorkflowState.VERIFICATION: "Verification Overseer is checking for issues",
        WorkflowState.HANDOFF_TO_RELEASER: "Verification Overseer is handing off to Release Manager",
        WorkflowState.DEPLOYMENT: "Release Manager is deploying to production",
        WorkflowState.COMPLETE: "Build is complete and live in production",
        WorkflowState.ERROR: "Workflow encountered an error",
    }
    
    @staticmethod
    def is_valid_transition(from_state: WorkflowState, to_state: WorkflowState) -> bool:
        """
        Check if a transition from one state to another is valid.
        
        Args:
            from_state: Current workflow state
            to_state: Desired next workflow state
            
        Returns:
            True if transition is valid, False otherwise
        """
        if from_state == to_state:
            return False  # Can't transition to same state
        
        is_valid = (from_state, to_state) in WorkflowStateTransition.VALID_TRANSITIONS
        
        if not is_valid:
            logger.warning(
                f"Invalid transition attempted: {from_state.value} → {to_state.value}"
            )
        
        return is_valid
    
    @staticmethod
    def get_next_role(current_state: WorkflowState) -> Optional[LLMRole]:
        """
        Determine which role should handle the next phase after current state.
        
        Args:
            current_state: Current workflow state
            
        Returns:
            LLMRole that should handle the current/next phase
        """
        # Map current state to the role handling that state
        next_role_map = {
            WorkflowState.DISCOVERY: LLMRole.Q_ASSISTANT,
            WorkflowState.PLANNING: LLMRole.Q_ASSISTANT,  # Q_ASSISTANT does both discovery and planning
            WorkflowState.HANDOFF_TO_CODER: LLMRole.CODE_WRITER,
            WorkflowState.IMPLEMENTATION: LLMRole.CODE_WRITER,
            WorkflowState.HANDOFF_TO_TESTER: LLMRole.TEST_AUDITOR,
            WorkflowState.TESTING: LLMRole.TEST_AUDITOR,
            WorkflowState.HANDOFF_TO_VERIFIER: LLMRole.VERIFICATION_OVERSEER,
            WorkflowState.VERIFICATION: LLMRole.VERIFICATION_OVERSEER,
            WorkflowState.HANDOFF_TO_RELEASER: LLMRole.RELEASE_MANAGER,
            WorkflowState.DEPLOYMENT: LLMRole.RELEASE_MANAGER,
            WorkflowState.COMPLETE: None,  # No next role
        }
        
        return next_role_map.get(current_state)
    
    @staticmethod
    def get_description(state: WorkflowState) -> str:
        """
        Get human-readable description of a state.
        
        Args:
            state: Workflow state
            
        Returns:
            Human-readable description
        """
        return WorkflowStateTransition.STATE_DESCRIPTIONS.get(
            state,
            f"Unknown state: {state.value}"
        )
    
    @staticmethod
    def log_transition(
        workflow_id: str,
        from_state: WorkflowState,
        to_state: WorkflowState,
        role: LLMRole,
        reason: Optional[str] = None
    ):
        """
        Log a workflow state transition.
        
        Args:
            workflow_id: ID of the workflow
            from_state: Previous state
            to_state: New state
            role: Role making the transition
            reason: Optional reason for transition
        """
        message = (
            f"Workflow {workflow_id}: {role.value} transitioned "
            f"{from_state.value} → {to_state.value}"
        )
        
        if reason:
            message += f" ({reason})"
        
        logger.info(message)


class WorkflowPhaseData:
    """
    Container for data associated with each workflow phase.
    Stores all context needed to be passed to the next role.
    """
    
    def __init__(self):
        """Initialize empty phase data"""
        self.discovery_phase = None  # Q Assistant requirements extraction
        self.planning_phase = None   # Q Assistant implementation plan
        self.implementation_phase = None  # Code Writer output
        self.testing_phase = None    # Test Auditor results
        self.verification_phase = None   # Verification Overseer checks
        self.deployment_phase = None    # Release Manager deployment
    
    def get_phase_data(self, state: WorkflowState) -> Optional[Dict[str, Any]]:
        """Get data for a specific phase"""
        phase_map = {
            WorkflowState.DISCOVERY: self.discovery_phase,
            WorkflowState.PLANNING: self.planning_phase,
            WorkflowState.IMPLEMENTATION: self.implementation_phase,
            WorkflowState.TESTING: self.testing_phase,
            WorkflowState.VERIFICATION: self.verification_phase,
            WorkflowState.DEPLOYMENT: self.deployment_phase,
        }
        return phase_map.get(state)
    
    def set_phase_data(self, state: WorkflowState, data: Dict[str, Any]):
        """Set data for a specific phase"""
        if state == WorkflowState.DISCOVERY or state == WorkflowState.PLANNING:
            if state == WorkflowState.DISCOVERY:
                self.discovery_phase = data
            else:
                self.planning_phase = data
        elif state == WorkflowState.IMPLEMENTATION:
            self.implementation_phase = data
        elif state == WorkflowState.TESTING:
            self.testing_phase = data
        elif state == WorkflowState.VERIFICATION:
            self.verification_phase = data
        elif state == WorkflowState.DEPLOYMENT:
            self.deployment_phase = data
    
    def to_dict(self) -> Dict:
        """Convert all phase data to dictionary"""
        return {
            "discovery": self.discovery_phase,
            "planning": self.planning_phase,
            "implementation": self.implementation_phase,
            "testing": self.testing_phase,
            "verification": self.verification_phase,
            "deployment": self.deployment_phase,
        }
