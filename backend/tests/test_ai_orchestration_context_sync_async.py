import pytest

from backend.services.ai_orchestration import AIOrchestrationManager
from backend.services.orchestration_service import OrchestrationService
from backend.orchestration.workflow_state_machine import LLMRole


def test_get_context_for_role_sync():
    service = OrchestrationService(db=None)
    manager = AIOrchestrationManager(service)

    ctx = manager.get_context_for_role("wf-sync", LLMRole.CODE_WRITER)

    # The method returns an awaitable proxy; it should behave like the context directly
    assert ctx.workflow_id == "wf-sync"
    assert ctx.role == LLMRole.CODE_WRITER


@pytest.mark.asyncio
async def test_get_context_for_role_async():
    service = OrchestrationService(db=None)
    manager = AIOrchestrationManager(service)

    ctx = await manager.get_context_for_role("wf-async", LLMRole.Q_ASSISTANT)

    assert ctx.workflow_id == "wf-async"
    assert ctx.role == LLMRole.Q_ASSISTANT
