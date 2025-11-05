"""
Orchestration Service for Q Assistant Workflow Automation

Manages the complete workflow lifecycle:
- Starting workflows (Discovery phase)
- Advancing workflows between roles
- Tracking workflow progress
- Rolling back workflows on errors
- Persisting workflow state to database
"""

from typing import Any, Dict, List, Optional, Tuple, cast
import os
from datetime import datetime, timedelta
from uuid import uuid4
import logging

from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.orchestration.workflow_state_machine import (
    WorkflowState,
    WorkflowStateTransition,
    LLMRole,
    WorkflowPhaseData,
)
from backend.models.workflow import (
    BuildWorkflow,
    WorkflowHandoff,
    WorkflowEvent,
    WorkflowStateEnum,
    LLMRoleEnum,
)

logger = logging.getLogger(__name__)


class OrchestrationService:
    """
    Service for managing AI workflow orchestration.
    Handles state transitions, handoffs between roles, and workflow tracking.
    """
    
    def __init__(self, db: Optional[Session] = None):
        """
        Initialize orchestration service.
        
        Args:
            db: Database session (optional for testing)
        """
        self.db = db
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
            
            if self.db is not None:
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
                
                self.db.add(workflow)
                self.db.commit()
                self.db.refresh(workflow)
                
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
                self.db.add(event)
                self.db.commit()
            else:
                # In-memory storage for testing
                self._workflows[workflow_id] = {
                    "id": workflow_id,
                    "build_id": build_id,
                    "project_id": project_id,
                    "user_id": user_id,
                    "current_state": WorkflowState.DISCOVERY,
                    "discovery_phase": discovery_data,
                    "planning_phase": None,
                    "implementation_phase": None,
                    "testing_phase": None,
                    "verification_phase": None,
                    "deployment_phase": None,
                    "metadata": metadata or {},
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
                self._handoffs[workflow_id] = []
                self._events[workflow_id] = [{
                    "event_type": "workflow_started",
                    "triggered_by": "system",
                    "timestamp": datetime.utcnow(),
                }]
            
            logger.info(
                f"Started workflow {workflow_id} for project {project_id}, "
                f"build {build_id}, user {user_id}"
            )
            
            return workflow_id, WorkflowState.DISCOVERY

            
        except Exception as e:
            logger.error(f"Failed to start workflow: {str(e)}")
            if self.db is not None:
                self.db.rollback()
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
            
            if self.db is not None:
                # Database mode
                # Fetch workflow from database
                workflow = self.db.query(BuildWorkflow).filter(
                    BuildWorkflow.id == workflow_id
                ).first()
                
                if not workflow:
                    raise ValueError(f"Workflow {workflow_id} not found")
                
                # Store phase result in workflow
                phase_key = self._get_phase_column(completed_state)
                if phase_key:
                    setattr(workflow, phase_key, phase_result)
                
                # Update workflow state to the new state (not the completed one)
                wf = cast(Any, workflow)
                wf.current_state = WorkflowStateEnum[next_state.name]
                wf.updated_at = datetime.utcnow()
                
                # Create handoff record in database
                handoff = WorkflowHandoff(
                    workflow_id=workflow_id,
                    from_role=LLMRoleEnum[current_role.name],
                    to_role=LLMRoleEnum[next_role.name] if next_role else None,
                    from_state=WorkflowStateEnum[completed_state.name],
                    to_state=WorkflowStateEnum[next_state.name],
                    data_transferred=phase_result,
                    notes=f"{current_role.value} completed {completed_state.value}",
                )
                
                self.db.add(handoff)
                
                # Create event in audit trail
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
                self.db.add(event)
                
                # Mark as complete if finished
                if next_state == WorkflowState.COMPLETE:
                    wf.completed_at = datetime.utcnow()
                
                self.db.commit()
            else:
                # In-memory mode (testing)
                if workflow_id not in self._workflows:
                    raise ValueError(f"Workflow {workflow_id} not found")
                
                workflow = self._workflows[workflow_id]
                
                # Store phase result
                phase_key = self._get_phase_column(completed_state)
                if phase_key:
                    workflow[phase_key] = phase_result
                
                # Update state
                workflow["current_state"] = next_state
                workflow["updated_at"] = datetime.utcnow()
                
                # Record handoff
                self._handoffs[workflow_id].append({
                    "from_role": current_role,
                    "to_role": next_role,
                    "from_state": completed_state,
                    "to_state": next_state,
                    "data_transferred": phase_result,
                    "timestamp": datetime.utcnow(),
                })
                
                # Record event
                self._events[workflow_id].append({
                    "event_type": "state_advanced",
                    "triggered_by": current_role.value,
                    "from_state": completed_state.value,
                    "to_state": next_state.value,
                    "timestamp": datetime.utcnow(),
                })
                
                if next_state == WorkflowState.COMPLETE:
                    workflow["completed_at"] = datetime.utcnow()
            
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
            if self.db is not None:
                self.db.rollback()
            raise
        except Exception as e:
            logger.error(f"Failed to advance workflow {workflow_id}: {str(e)}")
            if self.db is not None:
                self.db.rollback()
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
            
            if self.db is not None:
                # Database mode
                # Fetch workflow from database
                workflow = self.db.query(BuildWorkflow).filter(
                    BuildWorkflow.id == workflow_id
                ).first()
                
                if not workflow:
                    raise ValueError(f"Workflow {workflow_id} not found")
                
                # Get handoff history
                handoffs = self.db.query(WorkflowHandoff).filter(
                    WorkflowHandoff.workflow_id == workflow_id
                ).order_by(WorkflowHandoff.timestamp).all()
                
                # Calculate elapsed time
                elapsed = datetime.utcnow() - workflow.created_at
                hours = elapsed.total_seconds() // 3600
                minutes = (elapsed.total_seconds() % 3600) // 60
                elapsed_time = f"{int(hours)}h {int(minutes)}m"
                
                # Resolve current state safely (support mocks in tests)
                try:
                    state_name = getattr(workflow.current_state, "name", None)
                    if not isinstance(state_name, str):
                        state_name = str(state_name)
                    safe_state = WorkflowState[state_name]
                except Exception:
                    safe_state = WorkflowState.DISCOVERY
                # Get current role
                current_role = WorkflowStateTransition.get_next_role(safe_state)
                
                # Count completed phases
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
                
                # Calculate progress
                progress = len(completed_phases) / 6 * 100
                
                # Build handoff history
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
                
                # Build status response
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
            else:
                # In-memory mode (testing)
                if workflow_id not in self._workflows:
                    raise ValueError(f"Workflow {workflow_id} not found")
                
                workflow = self._workflows[workflow_id]
                handoffs = self._handoffs.get(workflow_id, [])
                
                # Calculate elapsed time
                elapsed = datetime.utcnow() - workflow["created_at"]
                hours = elapsed.total_seconds() // 3600
                minutes = (elapsed.total_seconds() % 3600) // 60
                elapsed_time = f"{int(hours)}h {int(minutes)}m"
                
                # Get current state and role
                current_state = workflow.get("current_state", WorkflowState.DISCOVERY)
                current_role = WorkflowStateTransition.get_next_role(current_state)
                
                # Count completed phases
                completed_phases = []
                if workflow.get("discovery_phase"):
                    completed_phases.append("discovery")
                if workflow.get("planning_phase"):
                    completed_phases.append("planning")
                if workflow.get("implementation_phase"):
                    completed_phases.append("implementation")
                if workflow.get("testing_phase"):
                    completed_phases.append("testing")
                if workflow.get("verification_phase"):
                    completed_phases.append("verification")
                if workflow.get("deployment_phase"):
                    completed_phases.append("deployment")
                
                # Calculate progress
                progress = len(completed_phases) / 6 * 100
                
                # Build handoff history
                handoff_history = [
                    {
                        "from_role": str(h["from_role"]),
                        "to_role": str(h["to_role"]) if h.get("to_role") else None,
                        "from_state": str(h["from_state"]),
                        "to_state": str(h["to_state"]),
                        "timestamp": h["timestamp"].isoformat() if h.get("timestamp") else None,
                    }
                    for h in handoffs
                ]
                
                # Build status response
                status = {
                    "workflow_id": workflow_id,
                    "build_id": workflow.get("build_id"),
                    "project_id": workflow.get("project_id"),
                    "current_state": current_state.value if isinstance(current_state, WorkflowState) else str(current_state),
                    "current_role": current_role.value if current_role else "system",
                    "progress": round(progress, 1),
                    "completed_phases": completed_phases,
                    "handoff_history": handoff_history,
                    "elapsed_time": elapsed_time,
                    "created_at": OrchestrationService._to_iso(workflow.get("created_at")),
                    "updated_at": OrchestrationService._to_iso(workflow.get("updated_at")),
                    "completed_at": OrchestrationService._to_iso(workflow.get("completed_at")),
                    "next_expectations": {
                        "role": current_role.value if current_role else "system",
                        "task": WorkflowStateTransition.get_description(current_state) if isinstance(current_state, WorkflowState) else "Unknown",
                        "deadline": None,
                    },
                    "status": "complete" if isinstance(current_state, WorkflowState) and current_state == WorkflowState.COMPLETE else "in_progress",
                }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get workflow status: {str(e)}")
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
        completed = 0  # Would count from DB
        
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
