"""
Game Engine Integration Tests
Tests for multi-engine router, container manager, and API routes
"""

import pytest
import os
import json
from backend.services.game_engine_router import (
    MultiEngineRouter,
    GameEngine,
    EngineConfig,
)
from backend.services.game_container_manager import GameEngineContainerManager


class TestMultiEngineRouter:
    """Tests for MultiEngineRouter"""

    @pytest.fixture
    def router(self):
        """Create router instance"""
        return MultiEngineRouter()

    def test_register_construct3_project(self, router):
        """Test registering a Construct 3 project"""
        success = router.register_project(
            project_id="my-game-c3",
            engine=GameEngine.CONSTRUCT3,
            project_path="/path/to/game",
            version="1.0.0",
        )

        assert success is True
        assert "my-game-c3" in router.engine_configs
        assert router.engine_configs["my-game-c3"].engine == GameEngine.CONSTRUCT3

    def test_register_godot_project(self, router):
        """Test registering a Godot project"""
        success = router.register_project(
            project_id="my-godot-game",
            engine=GameEngine.GODOT,
            project_path="/path/to/godot",
        )

        assert success is True
        assert router.engine_configs["my-godot-game"].engine == GameEngine.GODOT

    def test_register_unity_project(self, router):
        """Test registering a Unity project"""
        success = router.register_project(
            project_id="my-unity-game",
            engine=GameEngine.UNITY,
            project_path="/path/to/unity",
        )

        assert success is True
        assert router.engine_configs["my-unity-game"].engine == GameEngine.UNITY

    def test_register_unreal_project(self, router):
        """Test registering an Unreal project"""
        success = router.register_project(
            project_id="my-unreal-game",
            engine=GameEngine.UNREAL,
            project_path="/path/to/unreal",
        )

        assert success is True
        assert router.engine_configs["my-unreal-game"].engine == GameEngine.UNREAL

    def test_get_construct3_completions(self, router):
        """Test getting Construct 3 completions"""
        router.register_project(
            project_id="c3-project",
            engine=GameEngine.CONSTRUCT3,
            project_path="/path",
        )

        completions = router.get_completions(
            project_id="c3-project",
            file_path="main.js",
            line=0,
            column=0,
        )

        assert len(completions) > 0
        assert any(c["label"] == "On Start" for c in completions)

    def test_get_godot_completions(self, router):
        """Test getting Godot completions"""
        router.register_project(
            project_id="godot-project",
            engine=GameEngine.GODOT,
            project_path="/path",
        )

        completions = router.get_completions(
            project_id="godot-project",
            file_path="main.gd",
            line=0,
            column=0,
        )

        assert len(completions) > 0
        assert any(c["label"] == "_ready" for c in completions)

    def test_get_unity_completions(self, router):
        """Test getting Unity completions"""
        router.register_project(
            project_id="unity-project",
            engine=GameEngine.UNITY,
            project_path="/path",
        )

        completions = router.get_completions(
            project_id="unity-project",
            file_path="Main.cs",
            line=0,
            column=0,
        )

        assert len(completions) > 0
        assert any(c["label"] == "Update" for c in completions)

    def test_get_unreal_completions(self, router):
        """Test getting Unreal completions"""
        router.register_project(
            project_id="unreal-project",
            engine=GameEngine.UNREAL,
            project_path="/path",
        )

        completions = router.get_completions(
            project_id="unreal-project",
            file_path="Main.cpp",
            line=0,
            column=0,
        )

        assert len(completions) > 0
        assert any(c["label"] == "BeginPlay" for c in completions)

    def test_switch_engine(self, router):
        """Test switching active engine"""
        router.register_project(
            project_id="project1",
            engine=GameEngine.GODOT,
            project_path="/path1",
        )
        router.register_project(
            project_id="project2",
            engine=GameEngine.UNITY,
            project_path="/path2",
        )

        assert router.get_active_engine() == "unity"

        success = router.switch_engine("project1")
        assert success is True
        assert router.get_active_engine() == "godot"

    def test_list_projects(self, router):
        """Test listing projects"""
        router.register_project(
            project_id="project1",
            engine=GameEngine.GODOT,
            project_path="/path1",
        )
        router.register_project(
            project_id="project2",
            engine=GameEngine.UNITY,
            project_path="/path2",
        )

        projects = router.list_projects()
        assert len(projects) == 2
        assert any(p["project_id"] == "project1" for p in projects)
        assert any(p["project_id"] == "project2" for p in projects)

    def test_get_hover_info(self, router):
        """Test getting hover information"""
        router.register_project(
            project_id="project",
            engine=GameEngine.GODOT,
            project_path="/path",
        )

        hover = router.get_hover_info(
            project_id="project",
            file_path="main.gd",
            line=0,
            column=0,
        )

        assert hover is not None
        assert "content" in hover

    def test_get_diagnostics(self, router):
        """Test getting diagnostics"""
        router.register_project(
            project_id="project",
            engine=GameEngine.UNITY,
            project_path="/path",
        )

        diagnostics = router.get_diagnostics(
            project_id="project",
            file_path="Main.cs",
        )

        assert isinstance(diagnostics, list)

    def test_invalid_project_id(self, router):
        """Test accessing invalid project"""
        completions = router.get_completions(
            project_id="nonexistent",
            file_path="file.js",
            line=0,
            column=0,
        )

        assert completions == []


class TestGameEngineContainerManager:
    """Tests for GameEngineContainerManager"""

    @pytest.fixture
    def manager(self):
        """Create manager instance"""
        return GameEngineContainerManager()

    def test_docker_check(self, manager):
        """Test Docker availability check"""
        # Should not crash, just log if Docker unavailable
        assert isinstance(manager.docker_available, bool)

    def test_list_containers_empty(self, manager):
        """Test listing containers when none exist"""
        containers = manager.list_containers()
        assert containers == []

    def test_get_container_port(self, manager):
        """Test getting container port"""
        # No containers, should return None
        port = manager.get_container_port("nonexistent", "preview")
        assert port is None

    def test_container_start_requires_docker(self, manager):
        """Test that container start requires Docker"""
        if not manager.docker_available:
            status = manager.start_godot_container(
                project_id="test-project",
                project_path="/path/to/project",
            )
            assert status is None


class TestEngineLanguageServers:
    """Tests for Language Server routing"""

    @pytest.fixture
    def router(self):
        return MultiEngineRouter()

    def test_construct3_language_servers(self, router):
        """Test Construct 3 language server list"""
        assert GameEngine.CONSTRUCT3 in router.language_servers
        assert "typescript" in router.language_servers[GameEngine.CONSTRUCT3]

    def test_godot_language_servers(self, router):
        """Test Godot language server list"""
        assert GameEngine.GODOT in router.language_servers
        assert "gdscript" in router.language_servers[GameEngine.GODOT]

    def test_unity_language_servers(self, router):
        """Test Unity language server list"""
        assert GameEngine.UNITY in router.language_servers
        assert "csharp" in router.language_servers[GameEngine.UNITY]

    def test_unreal_language_servers(self, router):
        """Test Unreal language server list"""
        assert GameEngine.UNREAL in router.language_servers
        assert "cpp" in router.language_servers[GameEngine.UNREAL]


# ==================== PERFORMANCE TESTS ====================


class TestPerformance:
    """Performance tests for game engine integration"""

    @pytest.fixture
    def router(self):
        return MultiEngineRouter()

    def test_completion_response_time(self, router):
        """Test that completions respond within 50ms"""
        import time

        router.register_project(
            project_id="perf-test",
            engine=GameEngine.UNITY,
            project_path="/path",
        )

        start = time.time()
        completions = router.get_completions(
            project_id="perf-test",
            file_path="Main.cs",
            line=0,
            column=0,
        )
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert elapsed < 50, f"Completions took {elapsed}ms, target is <50ms"
        assert len(completions) > 0

    def test_multiple_projects_performance(self, router):
        """Test performance with multiple projects"""
        import time

        # Register 10 projects
        for i in range(10):
            router.register_project(
                project_id=f"project-{i}",
                engine=GameEngine.UNITY if i % 2 == 0 else GameEngine.GODOT,
                project_path=f"/path/{i}",
            )

        start = time.time()
        # Get completions for each
        for i in range(10):
            completions = router.get_completions(
                project_id=f"project-{i}",
                file_path="file.cs",
                line=0,
                column=0,
            )
            assert len(completions) > 0

        elapsed = (time.time() - start) * 1000
        avg_time = elapsed / 10

        assert avg_time < 50, f"Average completion time {avg_time}ms exceeds 50ms"
