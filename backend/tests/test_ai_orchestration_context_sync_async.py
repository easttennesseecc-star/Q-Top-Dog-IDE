import pytest
from fastapi.testclient import TestClient

from backend.services.ai_orchestration import AIOrchestrationManager
from backend.orchestration.workflow_state_machine import LLMRole


def test_get_context_for_role_sync(ai_manager: AIOrchestrationManager):
    """
    Test that the awaitable proxy returned by get_context_for_role
    can be used synchronously.
    """
    ctx = ai_manager.get_context_for_role("wf-sync", LLMRole.CODE_WRITER)

    # The method returns an awaitable proxy; it should behave like the context directly
    assert ctx.workflow_id == "wf-sync"
    assert ctx.role == LLMRole.CODE_WRITER


@pytest.mark.asyncio
async def test_get_context_for_role_async(ai_manager: AIOrchestrationManager):
    """
    Test that the awaitable proxy returned by get_context_for_role
    can also be awaited.
    """
    ctx = await ai_manager.get_context_for_role("wf-async", LLMRole.Q_ASSISTANT)

    assert ctx.workflow_id == "wf-async"
    assert ctx.role == LLMRole.Q_ASSISTANT
