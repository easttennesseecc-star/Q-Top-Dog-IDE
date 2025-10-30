"""
Unit and Integration Tests for Q Assistant Orchestration

Tests the complete workflow state machine, orchestration service,
and API endpoints.
"""

import pytest
import asyncio
from uuid import uuid4
from datetime import datetime

from backend.orchestration.workflow_state_machine import (
    WorkflowState,
    LLMRole,
    WorkflowStateTransition,
    WorkflowPhaseData,
)
from backend.services.orchestration_service import OrchestrationService


class TestWorkflowStateMachine:
    """Test workflow state machine transitions"""
    
    def test_valid_transition_discovery_to_planning(self):
        """Test valid transition from discovery to planning"""
        assert WorkflowStateTransition.is_valid_transition(
            WorkflowState.DISCOVERY,
            WorkflowState.PLANNING
        )
    
    def test_valid_transition_planning_to_handoff(self):
        """Test valid transition from planning to handoff to coder"""
        assert WorkflowStateTransition.is_valid_transition(
            WorkflowState.PLANNING,
            WorkflowState.HANDOFF_TO_CODER
        )
    
    def test_valid_transition_implementation_to_handoff_tester(self):
        """Test valid transition from implementation to handoff to tester"""
        assert WorkflowStateTransition.is_valid_transition(
            WorkflowState.IMPLEMENTATION,
            WorkflowState.HANDOFF_TO_TESTER
        )
    
    def test_valid_transition_testing_to_verification(self):
        """Test valid transition from testing to verification"""
        assert WorkflowStateTransition.is_valid_transition(
            WorkflowState.TESTING,
            WorkflowState.HANDOFF_TO_VERIFIER
        )
    
    def test_invalid_transition_discovery_to_deployment(self):
        """Test invalid transition from discovery to deployment (skipping phases)"""
        assert not WorkflowStateTransition.is_valid_transition(
            WorkflowState.DISCOVERY,
            WorkflowState.DEPLOYMENT
        )
    
    def test_invalid_transition_same_state(self):
        """Test that transitioning to same state is invalid"""
        assert not WorkflowStateTransition.is_valid_transition(
            WorkflowState.DISCOVERY,
            WorkflowState.DISCOVERY
        )
    
    def test_retry_testing_to_implementation(self):
        """Test retry transition from testing back to implementation"""
        assert WorkflowStateTransition.is_valid_transition(
            WorkflowState.TESTING,
            WorkflowState.IMPLEMENTATION
        )
    
    def test_retry_verification_to_implementation(self):
        """Test retry transition from verification back to implementation"""
        assert WorkflowStateTransition.is_valid_transition(
            WorkflowState.VERIFICATION,
            WorkflowState.IMPLEMENTATION
        )
    
    def test_get_next_role_from_planning(self):
        """Test that next role after planning is code writer"""
        next_role = WorkflowStateTransition.get_next_role(WorkflowState.HANDOFF_TO_CODER)
        assert next_role == LLMRole.CODE_WRITER
    
    def test_get_next_role_from_implementation(self):
        """Test that next role after implementation is test auditor"""
        next_role = WorkflowStateTransition.get_next_role(WorkflowState.HANDOFF_TO_TESTER)
        assert next_role == LLMRole.TEST_AUDITOR
    
    def test_get_next_role_from_testing(self):
        """Test that next role after testing is verification overseer"""
        next_role = WorkflowStateTransition.get_next_role(WorkflowState.HANDOFF_TO_VERIFIER)
        assert next_role == LLMRole.VERIFICATION_OVERSEER
    
    def test_get_next_role_from_deployment(self):
        """Test that next role after deployment is release manager"""
        next_role = WorkflowStateTransition.get_next_role(WorkflowState.HANDOFF_TO_RELEASER)
        assert next_role == LLMRole.RELEASE_MANAGER
    
    def test_get_description_for_state(self):
        """Test getting human-readable description for state"""
        desc = WorkflowStateTransition.get_description(WorkflowState.IMPLEMENTATION)
        assert "Code Writer" in desc
        assert "implementing" in desc.lower()
    
    def test_state_to_role_mapping(self):
        """Test that states map to correct roles"""
        assert WorkflowStateTransition.STATE_TO_ROLE[WorkflowState.DISCOVERY] == LLMRole.Q_ASSISTANT
        assert WorkflowStateTransition.STATE_TO_ROLE[WorkflowState.IMPLEMENTATION] == LLMRole.CODE_WRITER
        assert WorkflowStateTransition.STATE_TO_ROLE[WorkflowState.TESTING] == LLMRole.TEST_AUDITOR


class TestWorkflowPhaseData:
    """Test workflow phase data storage"""
    
    def test_set_and_get_discovery_data(self):
        """Test setting and retrieving discovery phase data"""
        phase_data = WorkflowPhaseData()
        discovery_info = {"requirements": ["feature 1", "feature 2"]}
        
        phase_data.set_phase_data(WorkflowState.DISCOVERY, discovery_info)
        
        assert phase_data.get_phase_data(WorkflowState.DISCOVERY) == discovery_info
    
    def test_set_and_get_implementation_data(self):
        """Test setting and retrieving implementation phase data"""
        phase_data = WorkflowPhaseData()
        impl_info = {"code": "def hello(): pass"}
        
        phase_data.set_phase_data(WorkflowState.IMPLEMENTATION, impl_info)
        
        assert phase_data.get_phase_data(WorkflowState.IMPLEMENTATION) == impl_info
    
    def test_to_dict_converts_all_phases(self):
        """Test converting all phase data to dictionary"""
        phase_data = WorkflowPhaseData()
        phase_data.set_phase_data(WorkflowState.DISCOVERY, {"req": 1})
        phase_data.set_phase_data(WorkflowState.IMPLEMENTATION, {"code": "x"})
        
        data_dict = phase_data.to_dict()
        
        assert data_dict["discovery"] == {"req": 1}
        assert data_dict["implementation"] == {"code": "x"}
        assert data_dict["planning"] is None


class TestOrchestrationService:
    """Test orchestration service"""
    
    @pytest.mark.asyncio
    async def test_start_workflow_returns_workflow_id(self):
        """Test starting workflow returns valid workflow ID"""
        service = OrchestrationService(db=None)
        
        workflow_id, initial_state = await service.start_workflow(
            project_id="proj-123",
            build_id="build-456",
            user_id="user-789",
            initial_requirements={"feature": "test"},
        )
        
        assert workflow_id is not None
        assert len(workflow_id) == 36  # UUID length
        assert initial_state == WorkflowState.DISCOVERY
    
    @pytest.mark.asyncio
    async def test_start_workflow_initial_state_discovery(self):
        """Test that starting workflow begins in discovery state"""
        service = OrchestrationService(db=None)
        
        _, initial_state = await service.start_workflow(
            project_id="proj-123",
            build_id="build-456",
            user_id="user-789",
            initial_requirements={},
        )
        
        assert initial_state == WorkflowState.DISCOVERY
    
    @pytest.mark.asyncio
    async def test_advance_workflow_planning_to_handoff(self):
        """Test advancing workflow from planning to handoff to coder"""
        service = OrchestrationService(db=None)
        
        # First start a workflow
        workflow_id, _ = await service.start_workflow(
            project_id="proj-123",
            build_id="build-456",
            user_id="user-789",
            initial_requirements={},
        )
        
        # Now advance it from planning to handoff
        result = await service.advance_workflow(
            workflow_id=workflow_id,
            current_role=LLMRole.Q_ASSISTANT,
            completed_state=WorkflowState.PLANNING,
            phase_result={"plan": "implement feature X"},
        )
        
        assert result["workflow_id"] == workflow_id
        assert result["previous_state"] == WorkflowState.PLANNING.value
        assert result["new_state"] == WorkflowState.HANDOFF_TO_CODER.value
        assert result["next_role"] == LLMRole.CODE_WRITER.value
        assert result["is_complete"] is False
    
    @pytest.mark.asyncio
    async def test_advance_workflow_deployment_to_complete(self):
        """Test advancing workflow from deployment to complete"""
        service = OrchestrationService(db=None)
        
        # First start a workflow
        workflow_id, _ = await service.start_workflow(
            project_id="proj-123",
            build_id="build-456",
            user_id="user-789",
            initial_requirements={},
        )
        
        result = await service.advance_workflow(
            workflow_id=workflow_id,
            current_role=LLMRole.RELEASE_MANAGER,
            completed_state=WorkflowState.DEPLOYMENT,
            phase_result={"deployed": True},
        )
        
        assert result["new_state"] == WorkflowState.COMPLETE.value
        assert result["is_complete"] is True
        assert result["next_role"] is None
    
    @pytest.mark.asyncio
    async def test_advance_workflow_invalid_transition_raises_error(self):
        """Test that invalid transition raises error"""
        service = OrchestrationService(db=None)
        
        workflow_id = str(uuid4())
        
        with pytest.raises(ValueError):
            await service.advance_workflow(
                workflow_id=workflow_id,
                current_role=LLMRole.Q_ASSISTANT,
                completed_state=WorkflowState.DISCOVERY,
                phase_result={},
                next_state=WorkflowState.DEPLOYMENT,  # Invalid skip
            )
    
    @pytest.mark.asyncio
    async def test_get_workflow_status_returns_status(self):
        """Test getting workflow status"""
        service = OrchestrationService(db=None)
        
        # First start a workflow
        workflow_id, _ = await service.start_workflow(
            project_id="proj-123",
            build_id="build-456",
            user_id="user-789",
            initial_requirements={},
        )
        
        status = await service.get_workflow_status(workflow_id)
        
        assert status["workflow_id"] == workflow_id
        assert "current_state" in status
        assert "current_role" in status
        assert "progress" in status
    
    @pytest.mark.asyncio
    async def test_request_retry_from_testing(self):
        """Test requesting retry from testing state"""
        service = OrchestrationService(db=None)
        
        workflow_id = str(uuid4())
        result = await service.request_retry(
            workflow_id=workflow_id,
            current_state=WorkflowState.TESTING,
            reason="Tests failing",
        )
        
        assert result["workflow_id"] == workflow_id
        assert result["retry_requested"] is True
        assert result["previous_state"] == WorkflowState.IMPLEMENTATION.value
        assert "Tests failing" in result["reason"]
    
    @pytest.mark.asyncio
    async def test_rollback_workflow(self):
        """Test rolling back workflow to previous state"""
        service = OrchestrationService(db=None)
        
        workflow_id = str(uuid4())
        result = await service.rollback_workflow(
            workflow_id=workflow_id,
            target_state=WorkflowState.IMPLEMENTATION,
            reason="Critical bug found",
        )
        
        assert result["workflow_id"] == workflow_id
        assert result["rollback_successful"] is True
        assert result["new_state"] == WorkflowState.IMPLEMENTATION.value
        assert "Critical bug found" in result["reason"]


class TestWorkflowIntegration:
    """Integration tests for complete workflow"""
    
    @pytest.mark.asyncio
    async def test_complete_workflow_discovery_to_implementation(self):
        """Test workflow progression from discovery through implementation"""
        service = OrchestrationService(db=None)
        
        # Start workflow
        workflow_id, initial_state = await service.start_workflow(
            project_id="proj-123",
            build_id="build-456",
            user_id="user-789",
            initial_requirements={"build": "feature X"},
        )
        
        assert initial_state == WorkflowState.DISCOVERY
        
        # Advance to planning
        result1 = await service.advance_workflow(
            workflow_id=workflow_id,
            current_role=LLMRole.Q_ASSISTANT,
            completed_state=WorkflowState.DISCOVERY,
            phase_result={"extracted": "requirements"},
        )
        
        assert result1["new_state"] == WorkflowState.PLANNING.value
        assert result1["next_role"] == LLMRole.Q_ASSISTANT.value
        
        # Advance to handoff to coder
        result2 = await service.advance_workflow(
            workflow_id=workflow_id,
            current_role=LLMRole.Q_ASSISTANT,
            completed_state=WorkflowState.PLANNING,
            phase_result={"plan": "detailed plan"},
        )
        
        assert result2["new_state"] == WorkflowState.HANDOFF_TO_CODER.value
        assert result2["next_role"] == LLMRole.CODE_WRITER.value
        
        # Advance to implementation
        result3 = await service.advance_workflow(
            workflow_id=workflow_id,
            current_role=LLMRole.CODE_WRITER,
            completed_state=WorkflowState.HANDOFF_TO_CODER,
            phase_result={},
        )
        
        assert result3["new_state"] == WorkflowState.IMPLEMENTATION.value
        assert result3["next_role"] == LLMRole.CODE_WRITER.value
    
    @pytest.mark.asyncio
    async def test_workflow_with_retry_loop(self):
        """Test workflow with retry loop (code fails tests, retries)"""
        service = OrchestrationService(db=None)
        
        # Start workflow first
        workflow_id, _ = await service.start_workflow(
            project_id="proj-123",
            build_id="build-456",
            user_id="user-789",
            initial_requirements={},
        )
        
        # Code Writer completes implementation
        impl_result = await service.advance_workflow(
            workflow_id=workflow_id,
            current_role=LLMRole.CODE_WRITER,
            completed_state=WorkflowState.IMPLEMENTATION,
            phase_result={"code": "initial code"},
        )
        
        assert impl_result["new_state"] == WorkflowState.HANDOFF_TO_TESTER.value
        
        # Test Auditor finds issues and requests retry
        retry_result = await service.request_retry(
            workflow_id=workflow_id,
            current_state=WorkflowState.TESTING,
            reason="Test coverage too low",
        )
        
        assert retry_result["retry_requested"] is True
        assert retry_result["previous_state"] == WorkflowState.IMPLEMENTATION.value
        
        # Code Writer retries implementation
        retry_impl = await service.advance_workflow(
            workflow_id=workflow_id,
            current_role=LLMRole.CODE_WRITER,
            completed_state=WorkflowState.IMPLEMENTATION,
            phase_result={"code": "improved code with tests"},
        )
        
        assert retry_impl["new_state"] == WorkflowState.HANDOFF_TO_TESTER.value


# ================================
# Run tests
# ================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
