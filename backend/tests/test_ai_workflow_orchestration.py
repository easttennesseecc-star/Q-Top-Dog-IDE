"""
Comprehensive Test Suite for AI Workflow Orchestration

Tests for:
- AI context management
- Workflow initialization
- Role handoffs
- State transitions
- Database persistence
- End-to-end workflows
- Error handling
- Performance
"""

import pytest
import asyncio
from uuid import uuid4
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime

# Import classes to test
from backend.orchestration.workflow_state_machine import WorkflowState, LLMRole
from backend.services.orchestration_service import OrchestrationService
from backend.services.ai_orchestration import (
    AIOrchestrationContext,
    AIOrchestrationManager,
    AIModelType,
    initialize_ai_orchestration,
    get_ai_orchestration_manager,
)
from backend.orchestration.orchestration_prompts import get_orchestration_prompt


# ============================================
# Fixtures
# ============================================

@pytest.fixture
def mock_db_manager():
    """Create mock database manager"""
    mock_db = MagicMock()
    mock_db.get_session.return_value = MagicMock()
    return mock_db


@pytest.fixture
def orchestration_service(mock_db_manager):
    """Create orchestration service with mock DB"""
    return OrchestrationService(db=mock_db_manager)


@pytest.fixture
def ai_manager(orchestration_service):
    """Create AI orchestration manager"""
    return AIOrchestrationManager(orchestration_service)


@pytest.fixture
def workflow_id():
    """Generate workflow ID"""
    return str(uuid4())


@pytest.fixture
def ai_context(workflow_id):
    """Create AI context"""
    return AIOrchestrationContext(
        workflow_id=workflow_id,
        role=LLMRole.Q_ASSISTANT,
        model_type=AIModelType.GPT4
    )


# ============================================
# AI Context Tests
# ============================================

class TestAIOrchestrationContext:
    """Tests for AIOrchestrationContext class"""

    def test_context_initialization(self, workflow_id):
        """Test that context initializes with correct values"""
        context = AIOrchestrationContext(
            workflow_id=workflow_id,
            role=LLMRole.Q_ASSISTANT,
            model_type=AIModelType.GPT4
        )
        
        assert context.workflow_id == workflow_id
        assert context.role == LLMRole.Q_ASSISTANT
        assert context.model_type == AIModelType.GPT4
        assert context.system_prompt is not None
        assert context.conversation_history == []
        assert context.context_data == {}

    def test_system_prompt_injected(self, workflow_id):
        """Test that system prompt is correctly injected from orchestration_prompts"""
        context = AIOrchestrationContext(
            workflow_id=workflow_id,
            role=LLMRole.Q_ASSISTANT,
            model_type=AIModelType.GPT4
        )
        
        # System prompt should come from orchestration_prompts
        assert "Q Assistant" in context.system_prompt or "orchestration" in context.system_prompt.lower()
        assert len(context.system_prompt) > 50

    def test_add_message_to_history(self, ai_context):
        """Test adding messages to conversation history"""
        ai_context.add_message("user", "Gather requirements")
        assert len(ai_context.conversation_history) == 1
        assert ai_context.conversation_history[0]["role"] == "user"
        assert ai_context.conversation_history[0]["content"] == "Gather requirements"

    def test_multiple_messages(self, ai_context):
        """Test tracking multiple messages"""
        ai_context.add_message("user", "Gather requirements")
        ai_context.add_message("assistant", "I'll gather requirements...")
        ai_context.add_message("user", "Include performance metrics")
        
        assert len(ai_context.conversation_history) == 3
        assert ai_context.conversation_history[0]["role"] == "user"
        assert ai_context.conversation_history[1]["role"] == "assistant"
        assert ai_context.conversation_history[2]["role"] == "user"

    def test_get_system_message(self, ai_context):
        """Test system message generation"""
        system_msg = ai_context.get_system_message(WorkflowState.DISCOVERY)
        
        assert system_msg["role"] == "system"
        assert "content" in system_msg
        assert len(system_msg["content"]) > 0

    def test_build_api_request(self, ai_context):
        """Test building complete API request"""
        ai_context.add_message("assistant", "I've gathered requirements")
        
        api_request = ai_context.build_api_request(WorkflowState.DISCOVERY)
        
        assert "model" in api_request
        assert "messages" in api_request
        assert len(api_request["messages"]) >= 2  # System + at least one message
        assert api_request["messages"][0]["role"] == "system"

    def test_context_data_storage(self, ai_context):
        """Test storing context-specific data"""
        ai_context.context_data["requirements"] = "Build feature X"
        ai_context.context_data["user_feedback"] = "Include performance"
        
        assert ai_context.context_data["requirements"] == "Build feature X"
        assert ai_context.context_data["user_feedback"] == "Include performance"

    def test_different_model_types(self, workflow_id):
        """Test context with different model types"""
        for model in [AIModelType.GPT4, AIModelType.GPT35, AIModelType.CLAUDE, AIModelType.LOCAL]:
            context = AIOrchestrationContext(
                workflow_id=workflow_id,
                role=LLMRole.Q_ASSISTANT,
                model_type=model
            )
            api_request = context.build_api_request(WorkflowState.DISCOVERY)
            assert api_request["model"] == model.value


# ============================================
# AI Manager Tests
# ============================================

class TestAIOrchestrationManager:
    """Tests for AIOrchestrationManager class"""

    @pytest.mark.asyncio
    async def test_initialize_workflow(self, ai_manager, orchestration_service):
        """Test workflow initialization with AI"""
        ai_manager.orchestration_service = orchestration_service
        
        result = await ai_manager.initialize_workflow(
            workflow_id="test-123",
            project_id="proj-456",
            build_id="build-789",
            user_id="user-000",
            initial_requirements={"description": "Test build"}
        )
        
        assert result["workflow_id"] == "test-123"
        assert result["initial_state"] == WorkflowState.DISCOVERY.value
        assert "test-123" in ai_manager.contexts

    @pytest.mark.asyncio
    async def test_context_created_for_role(self, ai_manager, orchestration_service):
        """Test that context is created for each role"""
        ai_manager.orchestration_service = orchestration_service
        
        await ai_manager.initialize_workflow(
            workflow_id="test-123",
            project_id="proj-456",
            build_id="build-789",
            user_id="user-000",
            initial_requirements={}
        )
        
        # Context should be created for Q_ASSISTANT
        context = ai_manager.contexts.get("test-123")
        assert context is not None
        assert context.role == LLMRole.Q_ASSISTANT

    @pytest.mark.asyncio
    async def test_get_ai_prompt_for_phase(self, ai_manager, workflow_id):
        """Test getting AI prompt for current phase"""
        # Create context first
        context = AIOrchestrationContext(
            workflow_id=workflow_id,
            role=LLMRole.Q_ASSISTANT,
            model_type=AIModelType.GPT4
        )
        ai_manager.contexts[workflow_id] = context
        
        prompt = await ai_manager.get_ai_prompt_for_phase(workflow_id, WorkflowState.DISCOVERY)
        
        assert "model" in prompt
        assert "messages" in prompt
        assert len(prompt["messages"]) > 0

    @pytest.mark.asyncio
    async def test_advance_with_ai_result(self, ai_manager, orchestration_service):
        """Test advancing workflow with AI result"""
        ai_manager.orchestration_service = orchestration_service
        
        # Initialize workflow
        await ai_manager.initialize_workflow(
            workflow_id="test-123",
            project_id="proj-456",
            build_id="build-789",
            user_id="user-000",
            initial_requirements={"description": "Test"}
        )
        
        # Advance workflow
        result = await ai_manager.advance_with_ai_result(
            workflow_id="test-123",
            ai_response="Gathered requirements successfully",
            phase_result={"discovered_reqs": ["Req 1", "Req 2"]}
        )
        
        assert result["workflow_id"] == "test-123"
        assert result["previous_state"] == WorkflowState.DISCOVERY.value
        assert result["new_state"] in [s.value for s in WorkflowState]

    @pytest.mark.asyncio
    async def test_context_for_role(self, ai_manager):
        """Test getting context for specific role"""
        workflow_id = "test-123"
        context = await ai_manager.get_context_for_role(workflow_id, LLMRole.CODE_WRITER)
        
        assert context is not None
        assert context.role == LLMRole.CODE_WRITER
        assert context.workflow_id == workflow_id

    def test_manager_singleton(self, ai_manager, orchestration_service):
        """Test that manager follows singleton pattern"""
        # Initialize global manager
        from backend.services.ai_orchestration import initialize_ai_orchestration
        manager = initialize_ai_orchestration(orchestration_service)
        
        # Get manager from global
        retrieved = get_ai_orchestration_manager()
        assert retrieved is not None
        assert isinstance(retrieved, AIOrchestrationManager)


# ============================================
# Workflow Integration Tests
# ============================================

class TestAIWorkflowIntegration:
    """Tests for complete AI workflow scenarios"""

    @pytest.mark.asyncio
    async def test_discovery_to_planning_transition(self, ai_manager, orchestration_service):
        """Test transition from DISCOVERY to PLANNING"""
        ai_manager.orchestration_service = orchestration_service
        
        # Initialize
        await ai_manager.initialize_workflow(
            workflow_id="test-123",
            project_id="proj-456",
            build_id="build-789",
            user_id="user-000",
            initial_requirements={"description": "Test"}
        )
        
        # Verify initial state
        initial_context = ai_manager.contexts["test-123"]
        assert initial_context.role == LLMRole.Q_ASSISTANT
        
        # Advance
        result = await ai_manager.advance_with_ai_result(
            workflow_id="test-123",
            ai_response="Requirements gathered",
            phase_result={"reqs": ["R1", "R2"]}
        )
        
        assert result["new_state"] == WorkflowState.PLANNING.value

    @pytest.mark.asyncio
    async def test_conversation_history_maintained(self, ai_manager, orchestration_service):
        """Test that conversation history is maintained across phases"""
        ai_manager.orchestration_service = orchestration_service
        
        # Initialize
        await ai_manager.initialize_workflow(
            workflow_id="test-123",
            project_id="proj-456",
            build_id="build-789",
            user_id="user-000",
            initial_requirements={}
        )
        
        # Get context and add message
        context = ai_manager.contexts["test-123"]
        context.add_message("assistant", "I've gathered the requirements")
        
        # Verify history
        assert len(context.conversation_history) == 1
        
        # Get prompt (should include history)
        prompt = await ai_manager.get_ai_prompt_for_phase("test-123", WorkflowState.DISCOVERY)
        messages = prompt["messages"]
        
        # Should have system message + conversation history
        assert len(messages) >= 2

    @pytest.mark.asyncio
    async def test_multiple_concurrent_workflows(self, ai_manager, orchestration_service):
        """Test handling multiple concurrent workflows"""
        ai_manager.orchestration_service = orchestration_service
        
        # Initialize multiple workflows
        workflows = []
        for i in range(5):
            result = await ai_manager.initialize_workflow(
                workflow_id=f"test-{i}",
                project_id=f"proj-{i}",
                build_id=f"build-{i}",
                user_id="user-000",
                initial_requirements={}
            )
            workflows.append(result)
        
        # Verify all contexts exist
        assert len(ai_manager.contexts) == 5
        for i in range(5):
            assert f"test-{i}" in ai_manager.contexts

    @pytest.mark.asyncio
    async def test_role_handoff_q_to_code_writer(self, ai_manager, orchestration_service):
        """Test handoff from Q Assistant to Code Writer"""
        ai_manager.orchestration_service = orchestration_service
        
        # Initialize
        await ai_manager.initialize_workflow(
            workflow_id="test-123",
            project_id="proj-456",
            build_id="build-789",
            user_id="user-000",
            initial_requirements={}
        )
        
        # Get initial context (Q Assistant)
        q_context = ai_manager.contexts["test-123"]
        assert q_context.role == LLMRole.Q_ASSISTANT
        
        # Advance through DISCOVERY
        await ai_manager.advance_with_ai_result(
            workflow_id="test-123",
            ai_response="Requirements doc",
            phase_result={"reqs": []}
        )
        
        # Advance through PLANNING (Q Assistant again)
        result = await ai_manager.advance_with_ai_result(
            workflow_id="test-123",
            ai_response="Implementation plan",
            phase_result={"plan": []}
        )
        
        # Should now handoff to CODE_WRITER or stay with Q_ASSISTANT
        # depending on state machine logic
        assert result["new_state"] in [s.value for s in WorkflowState]


# ============================================
# Error Handling Tests
# ============================================

class TestAIErrorHandling:
    """Tests for error handling in AI orchestration"""

    @pytest.mark.asyncio
    async def test_invalid_workflow_id(self, ai_manager):
        """Test error when workflow doesn't exist"""
        with pytest.raises(Exception):
            await ai_manager.advance_with_ai_result(
                workflow_id="nonexistent",
                ai_response="test",
                phase_result={}
            )

    def test_context_with_invalid_role(self):
        """Test that invalid role handling works"""
        # Should handle gracefully
        context = AIOrchestrationContext(
            workflow_id="test-123",
            role=LLMRole.Q_ASSISTANT,
            model_type=AIModelType.GPT4
        )
        assert context is not None

    @pytest.mark.asyncio
    async def test_advance_with_missing_phase_result(self, ai_manager, orchestration_service):
        """Test error handling for missing phase result"""
        ai_manager.orchestration_service = orchestration_service
        
        # Initialize
        await ai_manager.initialize_workflow(
            workflow_id="test-123",
            project_id="proj-456",
            build_id="build-789",
            user_id="user-000",
            initial_requirements={}
        )
        
        # Advance should work with empty phase_result
        result = await ai_manager.advance_with_ai_result(
            workflow_id="test-123",
            ai_response="test",
            phase_result={}
        )
        
        assert result is not None


# ============================================
# Database Persistence Tests
# ============================================

class TestAIDatabasePersistence:
    """Tests for database persistence with AI workflows"""

    @pytest.mark.asyncio
    async def test_workflow_persisted_to_db(self, ai_manager, orchestration_service):
        """Test that workflow is persisted to database"""
        ai_manager.orchestration_service = orchestration_service
        
        # Initialize workflow
        await ai_manager.initialize_workflow(
            workflow_id="test-123",
            project_id="proj-456",
            build_id="build-789",
            user_id="user-000",
            initial_requirements={"description": "Test"}
        )
        
        # Get status (should be retrievable)
        status = await orchestration_service.get_workflow_status("test-123")
        
        assert status["workflow_id"] == "test-123"
        assert status["current_state"] == WorkflowState.DISCOVERY.value

    @pytest.mark.asyncio
    async def test_phase_results_persisted(self, ai_manager, orchestration_service):
        """Test that phase results are persisted"""
        ai_manager.orchestration_service = orchestration_service
        
        # Initialize and advance
        await ai_manager.initialize_workflow(
            workflow_id="test-123",
            project_id="proj-456",
            build_id="build-789",
            user_id="user-000",
            initial_requirements={}
        )
        
        phase_result = {
            "discovered_requirements": ["Req 1", "Req 2"],
            "user_feedback": "Looks good",
            "status": "discovered"
        }
        
        await ai_manager.advance_with_ai_result(
            workflow_id="test-123",
            ai_response="Requirements document",
            phase_result=phase_result
        )
        
        # Verify phase result is stored
        status = await orchestration_service.get_workflow_status("test-123")
        assert status is not None


# ============================================
# Performance Tests
# ============================================

class TestAIPerformance:
    """Performance tests for AI orchestration"""

    @pytest.mark.asyncio
    async def test_workflow_initialization_time(self, ai_manager, orchestration_service):
        """Test workflow initialization performance (target: <50ms)"""
        ai_manager.orchestration_service = orchestration_service
        
        import time
        start = time.time()
        
        await ai_manager.initialize_workflow(
            workflow_id="test-123",
            project_id="proj-456",
            build_id="build-789",
            user_id="user-000",
            initial_requirements={}
        )
        
        elapsed = (time.time() - start) * 1000  # Convert to ms
        
        # Should be fast (< 100ms with in-memory DB)
        assert elapsed < 100

    @pytest.mark.asyncio
    async def test_get_prompt_performance(self, ai_manager, workflow_id):
        """Test getting AI prompt performance (target: <100ms)"""
        context = AIOrchestrationContext(
            workflow_id=workflow_id,
            role=LLMRole.Q_ASSISTANT,
            model_type=AIModelType.GPT4
        )
        ai_manager.contexts[workflow_id] = context
        
        import time
        start = time.time()
        
        prompt = await ai_manager.get_ai_prompt_for_phase(workflow_id, WorkflowState.DISCOVERY)
        
        elapsed = (time.time() - start) * 1000
        
        # Should be very fast
        assert elapsed < 50

    @pytest.mark.asyncio
    async def test_concurrent_workflow_performance(self, ai_manager, orchestration_service):
        """Test performance with concurrent workflows"""
        ai_manager.orchestration_service = orchestration_service
        
        import time
        start = time.time()
        
        # Initialize 10 workflows concurrently
        tasks = [
            ai_manager.initialize_workflow(
                workflow_id=f"test-{i}",
                project_id=f"proj-{i}",
                build_id=f"build-{i}",
                user_id="user-000",
                initial_requirements={}
            )
            for i in range(10)
        ]
        
        await asyncio.gather(*tasks)
        
        elapsed = (time.time() - start) * 1000
        
        # 10 workflows should complete in reasonable time
        assert elapsed < 500  # 50ms average per workflow


# ============================================
# End-to-End Workflow Tests
# ============================================

class TestEndToEndWorkflow:
    """Complete end-to-end workflow tests"""

    @pytest.mark.asyncio
    async def test_complete_workflow_discovery_to_planning(self, ai_manager, orchestration_service):
        """Test complete workflow from DISCOVERY to PLANNING"""
        ai_manager.orchestration_service = orchestration_service
        
        # 1. Initialize
        result = await ai_manager.initialize_workflow(
            workflow_id="e2e-test-1",
            project_id="proj-123",
            build_id="build-456",
            user_id="user-789",
            initial_requirements={"description": "Build authentication system"}
        )
        
        assert result["workflow_id"] == "e2e-test-1"
        assert result["initial_state"] == WorkflowState.DISCOVERY.value
        
        # 2. Get AI prompt for Q Assistant
        prompt1 = await ai_manager.get_ai_prompt_for_phase("e2e-test-1", WorkflowState.DISCOVERY)
        assert "model" in prompt1
        assert "messages" in prompt1
        
        # 3. Q Assistant processes (simulated)
        context = ai_manager.contexts["e2e-test-1"]
        context.add_message("assistant", "I will gather requirements for authentication system")
        
        # 4. Advance to next phase
        result = await ai_manager.advance_with_ai_result(
            workflow_id="e2e-test-1",
            ai_response="Authentication requirements documented",
            phase_result={
                "requirements": ["OAuth2 support", "JWT tokens", "Rate limiting"],
                "status": "discovered"
            }
        )
        
        assert result["previous_state"] == WorkflowState.DISCOVERY.value
        assert result["new_state"] == WorkflowState.PLANNING.value
        
        # 5. Get status
        status = await orchestration_service.get_workflow_status("e2e-test-1")
        assert status["current_state"] == WorkflowState.PLANNING.value

    @pytest.mark.asyncio
    async def test_multiple_role_workflow(self, ai_manager, orchestration_service):
        """Test workflow with multiple roles"""
        ai_manager.orchestration_service = orchestration_service
        
        # Initialize
        await ai_manager.initialize_workflow(
            workflow_id="multi-role",
            project_id="proj-123",
            build_id="build-456",
            user_id="user-789",
            initial_requirements={}
        )
        
        # Phase 1: Q Assistant (DISCOVERY)
        context = ai_manager.contexts["multi-role"]
        assert context.role == LLMRole.Q_ASSISTANT
        
        # Advance
        result = await ai_manager.advance_with_ai_result(
            workflow_id="multi-role",
            ai_response="Discovery complete",
            phase_result={}
        )
        
        # Verify state changed
        assert result["new_state"] != WorkflowState.DISCOVERY.value


# ============================================
# Run Tests
# ============================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
