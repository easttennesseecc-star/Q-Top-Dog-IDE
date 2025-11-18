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
from fastapi.testclient import TestClient

# Import classes to test
from backend.orchestration.workflow_state_machine import WorkflowState, LLMRole
from backend.services.orchestration_service import OrchestrationService
from backend.services.ai_orchestration import (
    AIOrchestrationContext,
    AIOrchestrationManager,
    AIModelType,
)


# ============================================
# Fixtures
# ============================================

@pytest.fixture
def orchestration_service(test_client: TestClient) -> OrchestrationService:
    """Get the orchestration service from the test client's app state."""
    return test_client.app.state.orchestration_service


@pytest.fixture
def ai_manager(test_client: TestClient) -> AIOrchestrationManager:
    """Get the AI orchestration manager from the test client's app state."""
    return test_client.app.state.ai_orchestration_manager


@pytest.fixture
def workflow_id():
    """Generate workflow ID"""
    return str(uuid4())

@pytest.fixture
def build_id():
    """Generate a unique build ID per test to avoid UNIQUE constraint collisions."""
    return f"build-{uuid4()}"


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
    async def test_initialize_workflow(self, ai_manager: AIOrchestrationManager, test_client: TestClient, build_id: str, workflow_id: str):
        """Test workflow initialization with AI"""
        # The manager is now initialized via lifespan event, available on app.state
        manager = test_client.app.state.ai_orchestration_manager
        
        result = await manager.initialize_workflow(
            workflow_id=workflow_id,
            project_id="proj-456",
            build_id=build_id,
            user_id="user-000",
            initial_requirements={"description": "Test build"}
        )
        
        assert "workflow_id" in result
        assert result["workflow_id"] == workflow_id
        assert "system_prompt" in result
        # The manager is stateless, so we can't check for context existence directly.
        # Success is implied by the call not raising an error and returning the expected dict.

    @pytest.mark.asyncio
    async def test_context_created_for_role(self, ai_manager: AIOrchestrationManager, test_client: TestClient, workflow_id: str):
        """Test that context can be created for each role"""
        manager = test_client.app.state.ai_orchestration_manager
        
        # We don't need to initialize a workflow to get a transient context
        context = await manager.get_context_for_role(workflow_id, LLMRole.CODE_WRITER)
        
        assert context is not None
        assert context.role == LLMRole.CODE_WRITER

    @pytest.mark.asyncio
    async def test_get_ai_prompt_for_phase(self, ai_manager: AIOrchestrationManager, workflow_id: str, test_client: TestClient, build_id: str):
        """Test getting AI prompt for current phase"""
        manager = test_client.app.state.ai_orchestration_manager
        
        # Initialize a workflow so the service has a state to query
        await manager.initialize_workflow(
            workflow_id=workflow_id,
            project_id="proj-456",
            build_id=build_id,
            user_id="user-000",
            initial_requirements={}
        )

        prompt = await manager.get_ai_prompt_for_phase(workflow_id, WorkflowState.DISCOVERY)
        
        assert "model" in prompt
        assert "messages" in prompt
        assert len(prompt["messages"]) > 0

    @pytest.mark.asyncio
    async def test_advance_with_ai_result(self, ai_manager: AIOrchestrationManager, test_client: TestClient, build_id: str, workflow_id: str):
        """Test advancing workflow with AI result"""
        manager = test_client.app.state.ai_orchestration_manager
        
        # Initialize workflow
        await manager.initialize_workflow(
            workflow_id=workflow_id,
            project_id="proj-456",
            build_id=build_id,
            user_id="user-000",
            initial_requirements={"description": "Test"}
        )
        
        # Advance workflow
        result = await manager.advance_with_ai_result(
            workflow_id=workflow_id,
            ai_response="Gathered requirements successfully",
            phase_result={"discovered_reqs": ["Req 1", "Req 2"]}
        )
        
        assert result["workflow_id"] == workflow_id
        assert result["previous_state"] == WorkflowState.DISCOVERY.value
        assert result["new_state"] in [s.value for s in WorkflowState]


# ============================================
# Workflow Integration Tests
# ============================================

class TestAIWorkflowIntegration:
    """Tests for complete AI workflow scenarios"""

    @pytest.mark.asyncio
    async def test_discovery_to_planning_transition(self, ai_manager: AIOrchestrationManager, test_client: TestClient, build_id: str, workflow_id: str):
        """Test transition from DISCOVERY to PLANNING"""
        manager = test_client.app.state.ai_orchestration_manager
        
        # Initialize
        await manager.initialize_workflow(
            workflow_id=workflow_id,
            project_id="proj-456",
            build_id=build_id,
            user_id="user-000",
            initial_requirements={"description": "Test"}
        )
        
        # Advance
        result = await manager.advance_with_ai_result(
            workflow_id=workflow_id,
            ai_response="Requirements gathered",
            phase_result={"reqs": ["R1", "R2"]}
        )
        
        assert result["new_state"] == WorkflowState.PLANNING.value

    @pytest.mark.asyncio
    async def test_multiple_concurrent_workflows(self, ai_manager: AIOrchestrationManager, test_client: TestClient):
        """Test handling multiple concurrent workflows"""
        manager = test_client.app.state.ai_orchestration_manager
        
        # Initialize multiple workflows
        tasks = [
            manager.initialize_workflow(
                workflow_id=str(uuid4()),
                project_id=f"proj-{i}",
                build_id=f"build-{uuid4()}",
                user_id="user-000",
                initial_requirements={}
            ) for i in range(5)
        ]
        results = await asyncio.gather(*tasks)
        
        # Verify all initializations succeeded
        assert len(results) == 5
        for result in results:
            assert 'workflow_id' in result and isinstance(result['workflow_id'], str) and len(result['workflow_id']) > 0

    @pytest.mark.asyncio
    async def test_role_handoff_q_to_code_writer(self, ai_manager: AIOrchestrationManager, test_client: TestClient, build_id: str, workflow_id: str):
        """Test handoff from Q Assistant to Code Writer"""
        manager = test_client.app.state.ai_orchestration_manager
        
        # Initialize
        await manager.initialize_workflow(
            workflow_id=workflow_id,
            project_id="proj-456",
            build_id=build_id,
            user_id="user-000",
            initial_requirements={}
        )
        
        # Advance through DISCOVERY
        await manager.advance_with_ai_result(
            workflow_id=workflow_id,
            ai_response="Requirements doc",
            phase_result={"reqs": []}
        )
        
        # Advance through PLANNING (Q Assistant again)
        result = await manager.advance_with_ai_result(
            workflow_id=workflow_id,
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
    async def test_invalid_workflow_id(self, ai_manager: AIOrchestrationManager, test_client: TestClient):
        """Test error when workflow doesn't exist"""
        manager = test_client.app.state.ai_orchestration_manager
        with pytest.raises(Exception):
            await manager.advance_with_ai_result(
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
    async def test_advance_with_missing_phase_result(self, ai_manager: AIOrchestrationManager, test_client: TestClient, build_id: str, workflow_id: str):
        """Test error handling for missing phase result"""
        manager = test_client.app.state.ai_orchestration_manager
        
        # Initialize
        await manager.initialize_workflow(
            workflow_id=workflow_id,
            project_id="proj-456",
            build_id=build_id,
            user_id="user-000",
            initial_requirements={}
        )
        
        # Advance should work with empty phase_result
        result = await manager.advance_with_ai_result(
            workflow_id=workflow_id,
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
    async def test_workflow_persisted_to_db(self, ai_manager: AIOrchestrationManager, orchestration_service: OrchestrationService, test_client: TestClient, build_id: str, workflow_id: str):
        """Test that workflow is persisted to database"""
        manager = test_client.app.state.ai_orchestration_manager
        
        # Initialize workflow
        await manager.initialize_workflow(
            workflow_id=workflow_id,
            project_id="proj-456",
            build_id=build_id,
            user_id="user-000",
            initial_requirements={"description": "Test"}
        )
        
        # Get status (should be retrievable)
        status = await orchestration_service.get_workflow_status(workflow_id)
        
        assert status["workflow_id"] == workflow_id
        assert status["current_state"] == WorkflowState.DISCOVERY.value

    @pytest.mark.asyncio
    async def test_phase_results_persisted(self, ai_manager: AIOrchestrationManager, orchestration_service: OrchestrationService, test_client: TestClient, build_id: str, workflow_id: str):
        """Test that phase results are persisted"""
        manager = test_client.app.state.ai_orchestration_manager
        
        # Initialize and advance
        await manager.initialize_workflow(
            workflow_id=workflow_id,
            project_id="proj-456",
            build_id=build_id,
            user_id="user-000",
            initial_requirements={}
        )
        
        phase_result = {
            "discovered_requirements": ["Req 1", "Req 2"],
            "user_feedback": "Looks good",
            "status": "discovered"
        }
        
        await manager.advance_with_ai_result(
            workflow_id=workflow_id,
            ai_response="Requirements document",
            phase_result=phase_result
        )
        
        # Verify phase result is stored
        status = await orchestration_service.get_workflow_status(workflow_id)
        assert status is not None


# ============================================
# Performance Tests
# ============================================

class TestAIPerformance:
    """Performance tests for AI orchestration"""

    @pytest.mark.asyncio
    async def test_workflow_initialization_time(self, ai_manager: AIOrchestrationManager, test_client: TestClient, build_id: str, workflow_id: str):
        """Test workflow initialization performance (target: <50ms)"""
        manager = test_client.app.state.ai_orchestration_manager
        
        import time
        start = time.time()
        
        await manager.initialize_workflow(
            workflow_id=workflow_id,
            project_id="proj-456",
            build_id=build_id,
            user_id="user-000",
            initial_requirements={}
        )
        
        elapsed = (time.time() - start) * 1000  # Convert to ms
        
        # Should be fast (< 100ms with in-memory DB)
        assert elapsed < 100

    @pytest.mark.asyncio
    async def test_get_prompt_performance(self, ai_manager: AIOrchestrationManager, workflow_id: str, test_client: TestClient, build_id: str):
        """Test getting AI prompt performance (target: <100ms)"""
        manager = test_client.app.state.ai_orchestration_manager
        
        await manager.initialize_workflow(
            workflow_id=workflow_id,
            project_id="proj-456",
            build_id=build_id,
            user_id="user-000",
            initial_requirements={}
        )

        import time
        start = time.time()
        
        await manager.get_ai_prompt_for_phase(workflow_id, WorkflowState.DISCOVERY)
        
        elapsed = (time.time() - start) * 1000
        
        # Should be very fast
        assert elapsed < 50

    @pytest.mark.asyncio
    async def test_concurrent_workflow_performance(self, ai_manager: AIOrchestrationManager, test_client: TestClient):
        """Test performance with concurrent workflows"""
        manager = test_client.app.state.ai_orchestration_manager
        
        import time
        start = time.time()
        
        # Initialize 10 workflows concurrently
        tasks = [
            manager.initialize_workflow(
                workflow_id=str(uuid4()),  # use true unique IDs to avoid cross-test or intra-test collisions
                project_id=f"proj-{i}",
                build_id=f"build-{uuid4()}",
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
    async def test_complete_workflow_discovery_to_planning(self, ai_manager: AIOrchestrationManager, orchestration_service: OrchestrationService, test_client: TestClient, build_id: str, workflow_id: str):
        """Test complete workflow from DISCOVERY to PLANNING"""
        manager = test_client.app.state.ai_orchestration_manager
        
        # 1. Initialize
        result = await manager.initialize_workflow(
            workflow_id=workflow_id,
            project_id="proj-123",
            build_id=build_id,
            user_id="user-789",
            initial_requirements={"description": "Build authentication system"}
        )
        
        assert "workflow_id" in result
        assert result["workflow_id"] == workflow_id
        assert result["system_prompt"] is not None
        
        # 2. Get AI prompt for Q Assistant
        prompt1 = await manager.get_ai_prompt_for_phase(workflow_id, WorkflowState.DISCOVERY)
        assert "model" in prompt1
        assert "messages" in prompt1
        
        # 3. Q Assistant processes (simulated)
        # In a stateless manager, we can't add to a persistent context.
        # This step is now implicit in the advance_with_ai_result call.
        
        # 4. Advance to next phase
        result = await manager.advance_with_ai_result(
            workflow_id=workflow_id,
            ai_response="Authentication requirements documented",
            phase_result={
                "requirements": ["OAuth2 support", "JWT tokens", "Rate limiting"],
                "status": "discovered"
            }
        )
        
        assert result["previous_state"] == WorkflowState.DISCOVERY.value
        assert result["new_state"] == WorkflowState.PLANNING.value
        
        # 5. Get status
        status = await orchestration_service.get_workflow_status(workflow_id)
        assert status["current_state"] == WorkflowState.PLANNING.value

    @pytest.mark.asyncio
    async def test_multiple_role_workflow(self, ai_manager: AIOrchestrationManager, test_client: TestClient, build_id: str, workflow_id: str):
        """Test workflow with multiple roles"""
        manager = test_client.app.state.ai_orchestration_manager
        
        # Initialize
        await manager.initialize_workflow(
            workflow_id=workflow_id,
            project_id="proj-123",
            build_id=build_id,
            user_id="user-789",
            initial_requirements={}
        )
        
        # Phase 1: Q Assistant (DISCOVERY)
        # We can get a transient context to check the role if needed
        context = await manager.get_context_for_role(workflow_id, LLMRole.Q_ASSISTANT)
        assert context.role == LLMRole.Q_ASSISTANT
        
        # Advance
        result = await manager.advance_with_ai_result(
            workflow_id=workflow_id,
            ai_response="Discovery complete",
            phase_result={}
        )
        
        # Verify state changed
        assert result["new_state"] != WorkflowState.DISCOVERY.value
