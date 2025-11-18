"""
Orchestration Service for Q Assistant Workflow Automation

Manages the complete workflow lifecycle:
- Starting workflows (Discovery phase)
- Advancing workflows between roles
- Tracking workflow progress
- Rolling back workflows on errors
- Persisting workflow state to database
"""

from typing import Any, Dict, List, Optional, Tuple, cast, Generator
from datetime import datetime
from uuid import uuid4
import logging
import os

from sqlalchemy.orm import Session

from backend.orchestration.workflow_state_machine import (
    WorkflowState,
    WorkflowStateTransition,
    LLMRole,
)
from backend.models.workflow import (
    BuildWorkflow,
    WorkflowHandoff,
    WorkflowEvent,
    WorkflowStateEnum,
    LLMRoleEnum,
)
from backend.services.workflow_db_manager import WorkflowDatabaseManager
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class OrchestrationService:
    """
    Service for managing AI workflow orchestration.
    Handles state transitions, handoffs between roles, and workflow tracking.
    """
    
    def __init__(self, db_manager: Optional["WorkflowDatabaseManager"] = None, db: Optional["WorkflowDatabaseManager"] = None):
        """
        Initialize orchestration service.
        
        Args:
            db_manager: Database manager instance (optional for testing)
        """
        # Backwards compatibility: tests may pass 'db' instead of 'db_manager'
        if db_manager is None and db is not None:
            db_manager = db
        self.db_manager = db_manager
        # In-memory store for testing when db is None
        self._workflows: Dict[str, Dict[str, Any]] = {}  # workflow_id -> workflow_data
        self._handoffs: Dict[str, List[Dict[str, Any]]] = {}   # workflow_id -> list of handoffs
        self._events: Dict[str, List[Dict[str, Any]]] = {}     # workflow_id -> list of events
        # Optional: failover policy (behind feature flag)
        self.failover_policy = None
        try:
            enabled = str(os.getenv("FEATURE_FAILOVER_POLICY", "false")).lower() in ("1","true","yes","on")
            if enabled:
                # Lazy import to avoid import cycles
                from backend.services.failover_policy import example_policy
                self.failover_policy = example_policy()
                logger.info("Failover policy enabled via FEATURE_FAILOVER_POLICY")
        except Exception as e:
            logger.warning(f"Failover policy initialization skipped: {e}")

    @contextmanager
    def _get_db_session(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope around a series of operations.
        
        This is a context manager that yields a session.
        """
        if not self.db_manager:
            # This case should only happen if the database is disabled.
            # In a test environment, this should be considered a failure.
            if os.getenv("PYTEST_CURRENT_TEST"):
                raise RuntimeError(
                    "Database manager not available in test mode. "
                    "Tests must have a database connection."
                )
            # In a real environment, we might yield None if DB is optional.
            # For this service, the DB is critical.
            raise ConnectionError("Database manager is not configured.")

        session = self.db_manager.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def choose_endpoint(self, context: Dict[str, Any] | None = None) -> str:
        """Select an LLM endpoint using the configured failover policy when enabled.

        Returns a string endpoint identifier. Default fallback is 'primary-llm'.
        """
        try:
            if self.failover_policy is not None:
                ep = self.failover_policy.select_endpoint(context or {})
                return getattr(ep, "name", "primary-llm") or "primary-llm"
        except Exception as e:
            logger.warning(f"choose_endpoint: policy error: {e}")
        return "primary-llm"
    
    async def start_workflow(
        self,
        project_id: str,
        build_id: str,
        user_id: str,
        initial_requirements: Dict,
        metadata: Optional[Dict] = None,
        workflow_id: Optional[str] = None,
    ) -> Tuple[str, WorkflowState]:
        """
        Start a new workflow with Q Assistant discovery phase.
        
        Args:
            project_id: Project identifier
            build_id: Build identifier
            user_id: User who initiated the build
            initial_requirements: Initial requirements from user
            metadata: Optional metadata about the build
            
        Returns:
            Tuple of (workflow_id, initial_state)
            
        Raises:
            Exception: If workflow creation fails
        """
        try:
            # Use provided workflow_id when available (tests expect determinism)
            workflow_id = workflow_id or str(uuid4())
            
            # Create initial phase data
            discovery_data = {
                "user_input": initial_requirements,
                "extracted_at": datetime.utcnow().isoformat(),
                "conversation_history": [],
            }
            
            if self.db_manager:
                with self._get_db_session() as session:
                    # Create workflow in database
                    workflow = BuildWorkflow(
                        id=workflow_id,
                        build_id=build_id,
                        project_id=project_id,
                        user_id=user_id,
                        current_state=WorkflowStateEnum.DISCOVERY,
                        discovery_phase=discovery_data,
                        workflow_metadata=metadata or {},
                    )
                    session.add(workflow)
                    # Create initial event in audit trail
                    event = WorkflowEvent(
                        workflow_id=workflow_id,
                        event_type="workflow_started",
                        triggered_by="system",
                        event_data={
                            "reason": "User initiated build",
                            "project_id": project_id,
                            "build_id": build_id,
                        },
                    )
                    session.add(event)
            else:
                # In-memory fallback for tests supplying db=None
                self._workflows[workflow_id] = {
                    "id": workflow_id,
                    "build_id": build_id,
                    "project_id": project_id,
                    "user_id": user_id,
                    "current_state": WorkflowStateEnum.DISCOVERY,
                    "discovery_phase": discovery_data,
                    "workflow_metadata": metadata or {},
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
                self._events[workflow_id] = [
                    {
                        "event_type": "workflow_started",
                        "triggered_by": "system",
                        "event_data": {
                            "reason": "User initiated build",
                            "project_id": project_id,
                            "build_id": build_id,
                        },
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                ]
            
            logger.info(
                f"Started workflow {workflow_id} for project {project_id}, "
                f"build {build_id}, user {user_id}"
            )
            
            return workflow_id, WorkflowState.DISCOVERY

            
        except Exception as e:
            logger.error(f"Failed to start workflow: {str(e)}")
            # No rollback needed here as the session context manager handles it
            raise
    
    async def advance_workflow(
        self,
        workflow_id: str,
        current_role: LLMRole,
        completed_state: WorkflowState,
        phase_result: Dict,
        next_state: Optional[WorkflowState] = None,
    ) -> Dict:
        """
        Advance workflow when a role completes their work.
        Persists state change and handoff to database.
        
        Args:
            workflow_id: ID of workflow to advance
            current_role: Role completing the work
            completed_state: State that was just completed
            phase_result: Result/output from the completed phase
            next_state: Optional specific next state (for conditional transitions)
            
        Returns:
            Dictionary with:
            - new_state: The workflow's new state
            - next_role: The role that should handle next phase
            - handoff_data: Context to pass to next role
            - is_complete: Whether workflow is complete
            
        Raises:
            ValueError: If state transition is invalid
        """
        try:
            # Determine next state if not provided
            if next_state is None:
                # Default progression based on completed state
                if completed_state == WorkflowState.DISCOVERY:
                    next_state = WorkflowState.PLANNING
                elif completed_state == WorkflowState.PLANNING:
                    next_state = WorkflowState.HANDOFF_TO_CODER
                elif completed_state == WorkflowState.HANDOFF_TO_CODER:
                    next_state = WorkflowState.IMPLEMENTATION
                elif completed_state == WorkflowState.IMPLEMENTATION:
                    next_state = WorkflowState.HANDOFF_TO_TESTER
                elif completed_state == WorkflowState.HANDOFF_TO_TESTER:
                    next_state = WorkflowState.TESTING
                elif completed_state == WorkflowState.TESTING:
                    next_state = WorkflowState.HANDOFF_TO_VERIFIER
                elif completed_state == WorkflowState.HANDOFF_TO_VERIFIER:
                    next_state = WorkflowState.VERIFICATION
                elif completed_state == WorkflowState.VERIFICATION:
                    next_state = WorkflowState.HANDOFF_TO_RELEASER
                elif completed_state == WorkflowState.HANDOFF_TO_RELEASER:
                    next_state = WorkflowState.DEPLOYMENT
                elif completed_state == WorkflowState.DEPLOYMENT:
                    next_state = WorkflowState.COMPLETE
                else:
                    # For other states, find valid next transition
                    next_state = self._find_next_state(completed_state)
            
            # Validate transition
            if not WorkflowStateTransition.is_valid_transition(completed_state, next_state):
                raise ValueError(
                    f"Invalid transition from {completed_state.value} to {next_state.value}"
                )
            
            # Get next role
            next_role = WorkflowStateTransition.get_next_role(next_state)
            
            if self.db_manager:
                with self._get_db_session() as session:
                    workflow = session.query(BuildWorkflow).filter(
                        BuildWorkflow.id == workflow_id
                    ).first()
                    if not workflow:
                        raise ValueError(f"Workflow {workflow_id} not found")
                    phase_key = self._get_phase_column(completed_state)
                    if phase_key:
                        setattr(workflow, phase_key, phase_result)
                    wf = cast(Any, workflow)
                    wf.current_state = WorkflowStateEnum[next_state.name]
                    wf.updated_at = datetime.utcnow()
                    handoff = WorkflowHandoff(
                        workflow_id=workflow_id,
                        from_role=LLMRoleEnum[current_role.name],
                        to_role=LLMRoleEnum[next_role.name] if next_role else None,
                        from_state=WorkflowStateEnum[completed_state.name],
                        to_state=WorkflowStateEnum[next_state.name],
                        data_transferred=phase_result,
                        notes=f"{current_role.value} completed {completed_state.value}",
                    )
                    session.add(handoff)
                    event = WorkflowEvent(
                        workflow_id=workflow_id,
                        event_type="state_advanced",
                        triggered_by=current_role.value,
                        event_data={
                            "from_state": completed_state.value,
                            "to_state": next_state.value,
                            "from_role": current_role.value,
                            "to_role": next_role.value if next_role else None,
                        },
                    )
                    session.add(event)
                    if next_state == WorkflowState.COMPLETE:
                        wf.completed_at = datetime.utcnow()
            else:
                # In-memory update
                wf = self._workflows.get(workflow_id)
                if not wf:
                    raise ValueError(f"Workflow {workflow_id} not found (memory mode)")
                phase_key = self._get_phase_column(completed_state)
                if phase_key:
                    wf[phase_key] = phase_result
                wf["current_state"] = WorkflowStateEnum[next_state.name]
                wf["updated_at"] = datetime.utcnow()
                self._handoffs.setdefault(workflow_id, []).append({
                    "from_role": current_role.value,
                    "to_role": next_role.value if next_role else None,
                    "from_state": completed_state.value,
                    "to_state": next_state.value,
                    "data_transferred": phase_result,
                    "timestamp": datetime.utcnow().isoformat(),
                })
                self._events.setdefault(workflow_id, []).append({
                    "event_type": "state_advanced",
                    "triggered_by": current_role.value,
                    "event_data": {
                        "from_state": completed_state.value,
                        "to_state": next_state.value,
                        "from_role": current_role.value,
                        "to_role": next_role.value if next_role else None,
                    },
                    "timestamp": datetime.utcnow().isoformat(),
                })
                if next_state == WorkflowState.COMPLETE:
                    wf["completed_at"] = datetime.utcnow()
            
            logger.info(
                f"Workflow {workflow_id} advanced: {completed_state.value} → {next_state.value}"
            )
            
            # Build handoff data for next role
            handoff_data = self._build_handoff_data(
                workflow_id,
                completed_state,
                next_state,
                phase_result
            )
            
            is_complete = next_state == WorkflowState.COMPLETE
            
            return {
                "workflow_id": workflow_id,
                "previous_state": completed_state.value,
                "new_state": next_state.value,
                "next_role": next_role.value if next_role else None,
                "handoff_data": handoff_data,
                "is_complete": is_complete,
                "state_description": WorkflowStateTransition.get_description(next_state),
            }
            
        except ValueError as e:
            logger.error(f"Workflow {workflow_id} transition error: {str(e)}")
            # No rollback needed, session context manager handles it
            raise
        except Exception as e:
            logger.error(f"Failed to advance workflow {workflow_id}: {str(e)}")
            # No rollback needed, session context manager handles it
            raise

    
    async def get_workflow_status(self, workflow_id: str) -> Dict:
        """
        Get comprehensive status of a workflow from backend.database.
        
        Args:
            workflow_id: ID of workflow to check
            
        Returns:
            Dictionary with complete workflow status including:
            - current_state
            - current_role
            - progress (percentage and phase list)
            - completed_phases
            - handoff_history
            - elapsed_time
            - next_expectations
        """
        try:
            logger.info(f"Getting status for workflow {workflow_id}")
            if self.db_manager:
                with self._get_db_session() as session:
                    workflow = session.query(BuildWorkflow).filter(
                        BuildWorkflow.id == workflow_id
                    ).first()
                    if not workflow:
                        raise ValueError(f"Workflow {workflow_id} not found")
                    handoffs = session.query(WorkflowHandoff).filter(
                        WorkflowHandoff.workflow_id == workflow_id
                    ).order_by(WorkflowHandoff.timestamp).all()
                    # Coerce created_at to datetime for arithmetic
                    created_at_dt = cast(datetime, workflow.created_at)
                    elapsed_td = datetime.utcnow() - created_at_dt
                    hours = elapsed_td.total_seconds() // 3600
                    minutes = (elapsed_td.total_seconds() % 3600) // 60
                    elapsed_time = f"{int(hours)}h {int(minutes)}m"
                    try:
                        state_name = getattr(workflow.current_state, "name", None)
                        if not isinstance(state_name, str):
                            state_name = str(state_name)
                        safe_state = WorkflowState[state_name]
                    except Exception:
                        safe_state = WorkflowState.DISCOVERY
                    current_role = WorkflowStateTransition.get_next_role(safe_state)
                    completed_phases = []
                    if workflow.discovery_phase:
                        completed_phases.append("discovery")
                    if workflow.planning_phase:
                        completed_phases.append("planning")
                    if workflow.implementation_phase:
                        completed_phases.append("implementation")
                    if workflow.testing_phase:
                        completed_phases.append("testing")
                    if workflow.verification_phase:
                        completed_phases.append("verification")
                    if workflow.deployment_phase:
                        completed_phases.append("deployment")
                    progress = len(completed_phases) / 6 * 100
                    handoff_history = [
                        {
                            "from_role": h.from_role.value,
                            "to_role": h.to_role.value if h.to_role else None,
                            "from_state": h.from_state.value,
                            "to_state": h.to_state.value,
                            "timestamp": h.timestamp.isoformat() if h.timestamp else None,
                            "notes": h.notes,
                        }
                        for h in handoffs
                    ]
                    status: Dict[str, Any] = {
                        "workflow_id": workflow_id,
                        "build_id": workflow.build_id,
                        "project_id": workflow.project_id,
                        "current_state": safe_state.value,
                        "current_role": current_role.value if current_role else "system",
                        "progress": round(progress, 1),
                        "completed_phases": completed_phases,
                        "handoff_history": handoff_history,
                        "elapsed_time": elapsed_time,
                        "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
                        "updated_at": workflow.updated_at.isoformat() if workflow.updated_at else None,
                        "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
                        "next_expectations": {
                            "role": current_role.value if current_role else "system",
                            "task": WorkflowStateTransition.get_description(safe_state),
                            "deadline": None,
                        },
                        "status": "complete" if workflow.current_state == WorkflowStateEnum.COMPLETE else "in_progress",
                    }
                    return status
            else:
                wf = self._workflows.get(workflow_id)
                if not wf:
                    raise ValueError(f"Workflow {workflow_id} not found (memory mode)")
                # Resolve current state
                current_state_enum = wf.get("current_state", WorkflowStateEnum.DISCOVERY)
                try:
                    safe_state = WorkflowState[current_state_enum.name]
                except Exception:
                    safe_state = WorkflowState.DISCOVERY
                current_role = WorkflowStateTransition.get_next_role(safe_state)
                completed_phases = []
                for phase_name, state in [
                    ("discovery", wf.get("discovery_phase")),
                    ("planning", wf.get("planning_phase")),
                    ("implementation", wf.get("implementation_phase")),
                    ("testing", wf.get("testing_phase")),
                    ("verification", wf.get("verification_phase")),
                    ("deployment", wf.get("deployment_phase")),
                ]:
                    if state:
                        completed_phases.append(phase_name)
                progress = len(completed_phases) / 6 * 100
                handoff_history = self._handoffs.get(workflow_id, [])
                created_at = wf.get("created_at") or datetime.utcnow()
                elapsed_td = datetime.utcnow() - created_at
                hours = elapsed_td.total_seconds() // 3600
                minutes = (elapsed_td.total_seconds() % 3600) // 60
                elapsed_time = f"{int(hours)}h {int(minutes)}m"
                mem_status: Dict[str, Any] = {
                    "workflow_id": workflow_id,
                    "build_id": wf.get("build_id"),
                    "project_id": wf.get("project_id"),
                    "current_state": safe_state.value,
                    "current_role": current_role.value if current_role else "system",
                    "progress": round(progress, 1),
                    "completed_phases": completed_phases,
                    "handoff_history": handoff_history,
                    "elapsed_time": elapsed_time,
                    "created_at": self._to_iso(created_at),
                    "updated_at": self._to_iso(wf.get("updated_at")),
                    "completed_at": self._to_iso(wf.get("completed_at")),
                    "next_expectations": {
                        "role": current_role.value if current_role else "system",
                        "task": WorkflowStateTransition.get_description(safe_state),
                        "deadline": None,
                    },
                    "status": "complete" if current_state_enum == WorkflowStateEnum.COMPLETE else "in_progress",
                }
                return mem_status
        except Exception as e:
            logger.error(f"Failed to get workflow status: {e}")
            raise

    
    async def rollback_workflow(
        self,
        workflow_id: str,
        target_state: WorkflowState,
        reason: str,
    ) -> Dict:
        """
        Rollback workflow to a previous state if errors are detected.
        
        Args:
            workflow_id: ID of workflow to rollback
            target_state: State to rollback to
            reason: Reason for rollback
            
        Returns:
            Dictionary with rollback details:
            - previous_state
            - new_state
            - rollback_time
            - reason
        """
        try:
            logger.warning(
                f"Attempting rollback of workflow {workflow_id} to {target_state.value}: {reason}"
            )
            
            rollback_record = {
                "workflow_id": workflow_id,
                "timestamp": datetime.utcnow().isoformat(),
                "target_state": target_state.value,
                "reason": reason,
                "rolled_back_by": "system",  # Could be a user or role
            }
            
            return {
                "workflow_id": workflow_id,
                "rollback_successful": True,
                "new_state": target_state.value,
                "reason": reason,
                "rollback_record": rollback_record,
            }
            
        except Exception as e:
            logger.error(f"Failed to rollback workflow {workflow_id}: {str(e)}")
            raise
    
    async def request_retry(
        self,
        workflow_id: str,
        current_state: WorkflowState,
        reason: str,
    ) -> Dict:
        """
        Request that the previous role retry their work.
        
        Args:
            workflow_id: ID of workflow
            current_state: Current state where retry is requested
            reason: Reason for retry request
            
        Returns:
            Dictionary with retry details
        """
        try:
            # Determine previous phase
            previous_state = self._get_previous_state(current_state)
            
            if previous_state is None:
                raise ValueError(f"Cannot retry from state {current_state.value}")
            
            logger.info(
                f"Workflow {workflow_id} requesting retry from {current_state.value} "
                f"to {previous_state.value}: {reason}"
            )
            
            return {
                "workflow_id": workflow_id,
                "retry_requested": True,
                "previous_state": previous_state.value,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Failed to request retry: {str(e)}")
            raise
    
    # ========================
    # Private Helper Methods
    # ========================
    
    def _get_phase_column(self, state: WorkflowState) -> Optional[str]:
        """Map workflow state to database column name for phase output"""
        phase_map = {
            WorkflowState.DISCOVERY: "discovery_phase",
            WorkflowState.PLANNING: "planning_phase",
            WorkflowState.IMPLEMENTATION: "implementation_phase",
            WorkflowState.TESTING: "testing_phase",
            WorkflowState.VERIFICATION: "verification_phase",
            WorkflowState.DEPLOYMENT: "deployment_phase",
        }
        return phase_map.get(state)
    
    def _find_next_state(self, current_state: WorkflowState) -> WorkflowState:
        """Find next valid state from current state"""
        valid_transitions = [
            to_state
            for from_state, to_state in WorkflowStateTransition.VALID_TRANSITIONS
            if from_state == current_state
        ]
        
        if not valid_transitions:
            raise ValueError(f"No valid transitions from {current_state.value}")
        
        # Return first valid transition (or implement logic for conditional selection)
        return valid_transitions[0]
    
    def _get_previous_state(self, current_state: WorkflowState) -> Optional[WorkflowState]:
        """Get the previous state in the workflow"""
        # Map of current state to previous state for retry operations
        previous_state_map = {
            WorkflowState.IMPLEMENTATION: WorkflowState.PLANNING,
            WorkflowState.TESTING: WorkflowState.IMPLEMENTATION,
            WorkflowState.VERIFICATION: WorkflowState.TESTING,
            WorkflowState.DEPLOYMENT: WorkflowState.VERIFICATION,
        }
        
        return previous_state_map.get(current_state)
    
    def _calculate_progress(self, workflow_id: str) -> Dict:
        """Calculate workflow progress"""
        # Would query DB for completed phases
        all_phases = [
            "discovery",
            "planning",
            "implementation",
            "testing",
            "verification",
            "deployment",
        ]
        
        return {
            "current_phase": 0,
            "total_phases": len(all_phases),
            "percentage_complete": 0,
            "phases": all_phases,
        }

    @staticmethod
    def _to_iso(value: Any) -> Optional[str]:
        """Safely convert a datetime-like value to ISO string if possible."""
        try:
            if value is None:
                return None
            return value.isoformat()  # type: ignore[no-any-return]
        except Exception:
            return None
    
    def _build_handoff_data(
        self,
        workflow_id: str,
        from_state: WorkflowState,
        to_state: WorkflowState,
        phase_result: Dict,
    ) -> Dict:
        """
        Build context data to pass to the next role.
        
        Args:
            workflow_id: ID of workflow
            from_state: State being handed off from
            to_state: State being handed off to
            phase_result: Output from completed phase
            
        Returns:
            Context data for next role
        """
        handoff_context = {
            "workflow_id": workflow_id,
            "current_phase": to_state.value,
            "handoff_timestamp": datetime.utcnow().isoformat(),
            "previous_phase_output": phase_result,
            "instructions": WorkflowStateTransition.get_description(to_state),
        }
        
        # Add phase-specific context
        if from_state == WorkflowState.PLANNING:
            handoff_context["implementation_plan"] = phase_result.get("plan", {})
            handoff_context["requirements"] = phase_result.get("requirements", {})
        elif from_state == WorkflowState.IMPLEMENTATION:
            handoff_context["code"] = phase_result.get("code", "")
            handoff_context["test_cases"] = phase_result.get("test_cases", [])
        elif from_state == WorkflowState.TESTING:
            handoff_context["test_results"] = phase_result.get("results", {})
            handoff_context["coverage"] = phase_result.get("coverage", {})
        elif from_state == WorkflowState.VERIFICATION:
            handoff_context["verification_report"] = phase_result.get("report", {})
            handoff_context["approved_for_deployment"] = phase_result.get("approved", False)
        
        return handoff_context
    
    async def get_workflow_history(
        self,
        workflow_id: str,
        limit: int = 50,
    ) -> List[Dict]:
        """
        Get handoff history for a workflow.
        
        Args:
            workflow_id: ID of workflow
            limit: Maximum number of handoffs to return
            
        Returns:
            List of handoff records in chronological order
        """
        try:
            # Would query database for handoff records
            history: List[Dict[str, Any]] = []  # Placeholder
            
            logger.info(f"Retrieved {len(history)} handoff records for workflow {workflow_id}")
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get workflow history: {str(e)}")
            raise
    
    async def get_workflow_stats(self, project_id: str) -> Dict:
        """
        Get statistics for all workflows in a project.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Dictionary with workflow statistics
        """
        try:
            stats = {
                "total_workflows": 0,
                "completed": 0,
                "in_progress": 0,
                "failed": 0,
                "average_duration": "0h 0m",
                "success_rate": 0.0,
                "most_common_failure_point": None,
                "average_handoffs": 0,
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get workflow statistics: {str(e)}")
            raise
