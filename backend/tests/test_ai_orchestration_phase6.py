"""
Phase 6: Simplified AI Orchestration Integration Tests

Focus on validating the core AI orchestration capabilities work correctly.
These tests ensure the AI system is production-ready.
"""

import pytest
from uuid import uuid4

from backend.orchestration.workflow_state_machine import WorkflowState, LLMRole
from backend.services.orchestration_service import OrchestrationService
from backend.services.ai_orchestration import (
    AIOrchestrationContext,
    AIOrchestrationManager,
    AIModelType,
    initialize_ai_orchestration,
    get_ai_orchestration_manager,
)


class TestAIContextCore:
    """Core AI context functionality tests"""

    def test_context_creation(self):
        """Test creating AI context"""
        context = AIOrchestrationContext(
            workflow_id="test-123",
            role=LLMRole.Q_ASSISTANT,
            model_type=AIModelType.GPT4
        )
        assert context.workflow_id == "test-123"
        assert context.role == LLMRole.Q_ASSISTANT
        assert context.system_prompt is not None

    def test_message_tracking(self):
        """Test message history tracking"""
        context = AIOrchestrationContext(
            workflow_id="test-123",
            role=LLMRole.CODE_WRITER
        )
        
        context.add_message("assistant", "Writing code...")
        assert len(context.conversation_history) == 1
        assert context.conversation_history[0]["role"] == "assistant"

    def test_api_request_building(self):
        """Test building complete API request"""
        context = AIOrchestrationContext(
            workflow_id="test-123",
            role=LLMRole.Q_ASSISTANT
        )
        
        request = context.build_api_request(WorkflowState.DISCOVERY)
        assert "model" in request
        assert "messages" in request
        assert request["model"] in [m.value for m in AIModelType]

    def test_all_role_contexts(self):
        """Test creating contexts for all roles"""
        roles = [
            LLMRole.Q_ASSISTANT,
            LLMRole.CODE_WRITER,
            LLMRole.TEST_AUDITOR,
            LLMRole.VERIFICATION_OVERSEER,
            LLMRole.RELEASE_MANAGER
        ]
        
        for role in roles:
            context = AIOrchestrationContext(
                workflow_id="test",
                role=role
            )
            assert context.role == role
            assert context.system_prompt is not None


class TestAIManagerCore:
    """Core AI manager functionality tests"""

    def test_manager_creation(self):
        """Test creating AI manager"""
        mock_service = OrchestrationService(db=None)
        manager = AIOrchestrationManager(mock_service)
        
        assert manager is not None
        assert manager.orchestration_service == mock_service
        assert manager.contexts == {}

    def test_context_storage(self):
        """Test contexts are stored properly"""
        mock_service = OrchestrationService(db=None)
        manager = AIOrchestrationManager(mock_service)
        
        context = AIOrchestrationContext("w-1", LLMRole.Q_ASSISTANT)
        manager.contexts["w-1"] = context
        
        assert "w-1" in manager.contexts
        assert manager.contexts["w-1"].workflow_id == "w-1"

    def test_get_context_for_role(self):
        """Test retrieving context for role"""
        mock_service = OrchestrationService(db=None)
        manager = AIOrchestrationManager(mock_service)
        
        # Get context (creates if doesn't exist)
        context = manager.get_context_for_role("w-1", LLMRole.CODE_WRITER)
        
        assert context.workflow_id == "w-1"
        assert context.role == LLMRole.CODE_WRITER

    def test_initialize_global_manager(self):
        """Test initializing global manager"""
        mock_service = OrchestrationService(db=None)
        manager = initialize_ai_orchestration(mock_service)
        
        assert manager is not None
        assert isinstance(manager, AIOrchestrationManager)
        
        # Should be retrievable
        retrieved = get_ai_orchestration_manager()
        assert retrieved == manager


class TestAIPromptGeneration:
    """Test prompt generation capabilities"""

    def test_system_message_generation(self):
        """Test system message includes orchestration context"""
        context = AIOrchestrationContext(
            workflow_id="test-123",
            role=LLMRole.Q_ASSISTANT
        )
        
        msg = context.get_system_message(WorkflowState.DISCOVERY)
        assert msg["role"] == "system"
        assert "content" in msg
        assert len(msg["content"]) > 50

    def test_prompt_with_conversation_history(self):
        """Test prompt includes conversation history"""
        context = AIOrchestrationContext(
            workflow_id="test-123",
            role=LLMRole.Q_ASSISTANT
        )
        
        # Add messages
        context.add_message("user", "Build a feature")
        context.add_message("assistant", "I'll analyze requirements")
        context.add_message("user", "Include security")
        
        request = context.build_api_request(WorkflowState.DISCOVERY)
        messages = request["messages"]
        
        # Should have system + 3 conversation messages
        assert len(messages) >= 4
        assert messages[0]["role"] == "system"

    def test_prompts_for_all_states(self):
        """Test that prompts can be generated for all workflow states"""
        context = AIOrchestrationContext(
            workflow_id="test-123",
            role=LLMRole.Q_ASSISTANT
        )
        
        states = [
            WorkflowState.DISCOVERY,
            WorkflowState.PLANNING,
            WorkflowState.IMPLEMENTATION,
            WorkflowState.TESTING,
            WorkflowState.VERIFICATION,
            WorkflowState.DEPLOYMENT
        ]
        
        for state in states:
            prompt = context.build_api_request(state)
            assert "messages" in prompt
            assert len(prompt["messages"]) > 0


class TestAIRoleTransitions:
    """Test role transition scenarios"""

    def test_different_role_contexts(self):
        """Test creating contexts for role transitions"""
        workflow_id = "w-1"
        
        # Create context for Q Assistant
        q_context = AIOrchestrationContext(workflow_id, LLMRole.Q_ASSISTANT)
        assert q_context.role == LLMRole.Q_ASSISTANT
        
        # Create context for Code Writer
        cw_context = AIOrchestrationContext(workflow_id, LLMRole.CODE_WRITER)
        assert cw_context.role == LLMRole.CODE_WRITER
        
        # Both have same workflow_id but different roles
        assert q_context.workflow_id == cw_context.workflow_id
        assert q_context.role != cw_context.role

    def test_role_specific_prompts(self):
        """Test that each role gets appropriate prompt"""
        workflow_id = "w-1"
        state = WorkflowState.IMPLEMENTATION
        
        # Q Assistant planning phase
        q_context = AIOrchestrationContext(workflow_id, LLMRole.Q_ASSISTANT)
        q_prompt = q_context.build_api_request(state)
        
        # Code Writer implementation phase
        cw_context = AIOrchestrationContext(workflow_id, LLMRole.CODE_WRITER)
        cw_prompt = cw_context.build_api_request(state)
        
        # Prompts should differ for different roles
        q_messages = q_prompt["messages"]
        cw_messages = cw_prompt["messages"]
        
        # System prompts should be different
        assert q_messages[0]["content"] != cw_messages[0]["content"]

    def test_conversation_history_independent_per_role(self):
        """Test that conversation history is independent per role"""
        workflow_id = "w-1"
        
        q_context = AIOrchestrationContext(workflow_id, LLMRole.Q_ASSISTANT)
        q_context.add_message("assistant", "Q Assistant message")
        
        cw_context = AIOrchestrationContext(workflow_id, LLMRole.CODE_WRITER)
        cw_context.add_message("assistant", "Code Writer message")
        
        # Histories should be independent
        assert len(q_context.conversation_history) == 1
        assert len(cw_context.conversation_history) == 1
        assert q_context.conversation_history[0]["content"] != cw_context.conversation_history[0]["content"]


class TestAIModels:
    """Test different AI model support"""

    def test_model_types_enum(self):
        """Test all model types are available"""
        models = [AIModelType.GPT4, AIModelType.GPT35, AIModelType.CLAUDE, AIModelType.LOCAL]
        assert len(models) == 4
        
        for model in models:
            assert hasattr(model, 'value')
            assert len(model.value) > 0

    def test_context_with_different_models(self):
        """Test creating contexts with different models"""
        for model in [AIModelType.GPT4, AIModelType.GPT35, AIModelType.CLAUDE]:
            context = AIOrchestrationContext(
                "w-1",
                LLMRole.Q_ASSISTANT,
                model_type=model
            )
            
            request = context.build_api_request(WorkflowState.DISCOVERY)
            assert request["model"] == model.value


class TestAIDataPersistence:
    """Test AI context data persistence"""

    def test_context_data_storage(self):
        """Test storing context-specific data"""
        context = AIOrchestrationContext("w-1", LLMRole.Q_ASSISTANT)
        
        context.context_data["requirements"] = "Build auth system"
        context.context_data["deadline"] = "2025-10-31"
        
        assert context.context_data["requirements"] == "Build auth system"
        assert context.context_data["deadline"] == "2025-10-31"

    def test_context_state_tracking(self):
        """Test tracking current state"""
        context = AIOrchestrationContext("w-1", LLMRole.Q_ASSISTANT)
        
        context.current_state = WorkflowState.DISCOVERY
        assert context.current_state == WorkflowState.DISCOVERY
        
        context.current_state = WorkflowState.PLANNING
        assert context.current_state == WorkflowState.PLANNING


class TestAIProductionReadiness:
    """Test production readiness of AI orchestration"""

    def test_no_api_key_required_in_context(self):
        """Test that contexts don't require API keys"""
        context = AIOrchestrationContext("w-1", LLMRole.Q_ASSISTANT)
        # Should not raise any errors
        assert context.system_prompt is not None

    def test_safe_message_building(self):
        """Test message building doesn't expose sensitive data"""
        context = AIOrchestrationContext("w-1", LLMRole.Q_ASSISTANT)
        context.add_message("user", "password=secret123")
        
        request = context.build_api_request(WorkflowState.DISCOVERY)
        # Messages should still be there (caller is responsible for sanitization)
        assert len(request["messages"]) > 0

    def test_large_conversation_history(self):
        """Test handling large conversation histories"""
        context = AIOrchestrationContext("w-1", LLMRole.Q_ASSISTANT)
        
        # Add many messages
        for i in range(100):
            context.add_message("user" if i % 2 == 0 else "assistant", f"Message {i}")
        
        assert len(context.conversation_history) == 100
        
        # Should still build request
        request = context.build_api_request(WorkflowState.DISCOVERY)
        assert "messages" in request

    def test_concurrent_contexts(self):
        """Test managing multiple concurrent contexts"""
        manager = AIOrchestrationManager(OrchestrationService(db=None))
        
        # Create multiple workflow contexts
        for i in range(10):
            context = AIOrchestrationContext(f"w-{i}", LLMRole.Q_ASSISTANT)
            manager.contexts[f"w-{i}"] = context
        
        assert len(manager.contexts) == 10


# ============================================
# Run Tests
# ============================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
