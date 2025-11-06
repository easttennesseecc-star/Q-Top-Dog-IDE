import os
import pytest

from backend.services.game_container_manager import GameEngineContainerManager
from backend.services.game_engine_router import MultiEngineRouter, GameEngine


def test_router_register_construct3():
    router = MultiEngineRouter()
    ok = router.register_project(
        project_id="proj-c3",
        engine=GameEngine.CONSTRUCT3,
        project_path="C:/projects/c3",
        version="r382",
        settings={},
    )
    assert ok is True
    assert router.get_active_engine() == GameEngine.CONSTRUCT3.value


def test_construct3_container_graceful_without_docker(monkeypatch):
    mgr = GameEngineContainerManager()
    # Force docker unavailable to avoid running any commands in CI
    mgr.docker_available = False
    status = mgr.start_construct3_container(
        project_id="proj-c3",
        project_path="C:/projects/c3",
        config={},
    )
    assert status is None


def test_gamemaker_requires_prereqs(monkeypatch):
    mgr = GameEngineContainerManager()
    mgr.docker_available = False
    # Even if docker were available, missing envs should lead to None
    status = mgr.start_gamemaker_container(
        project_id="proj-gm",
        project_path="C:/projects/gm",
        config={},
    )
    assert status is None
