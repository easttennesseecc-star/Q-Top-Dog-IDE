"""
Multi-Engine Game Development Router
Handles routing and integration for Construct 3, Godot, Unity, and Unreal Engine
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logger = logging.getLogger(__name__)


class GameEngine(Enum):
    """Supported game engines"""
    CONSTRUCT3 = "construct3"
    GODOT = "godot"
    UNITY = "unity"
    UNREAL = "unreal"


@dataclass
class EngineConfig:
    """Configuration for each game engine"""
    engine: GameEngine
    project_path: str
    version: str
    settings: Dict[str, Any]
    language_servers: List[str]


class MultiEngineRouter:
    """
    Routes code analysis requests to appropriate Language Server based on engine
    Abstracts engine-specific differences for unified IDE experience
    """

    def __init__(self):
        self.engine_configs: Dict[str, EngineConfig] = {}
        self.active_engine: Optional[GameEngine] = None
        self.language_servers = {
            GameEngine.CONSTRUCT3: ["typescript", "javascript"],
            GameEngine.GODOT: ["gdscript", "gdshader"],
            GameEngine.UNITY: ["csharp", "hlsl"],
            GameEngine.UNREAL: ["cpp", "hlsl", "ue4"],
        }
        logger.info("MultiEngineRouter initialized")

    def register_project(
        self,
        project_id: str,
        engine: GameEngine,
        project_path: str,
        version: str = "latest",
        settings: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Register a game engine project with the router

        Args:
            project_id: Unique project identifier
            engine: Game engine type
            project_path: Full path to project
            version: Engine version (e.g., "1.0.0")
            settings: Engine-specific settings

        Returns:
            True if registration successful
        """
        try:
            config = EngineConfig(
                engine=engine,
                project_path=project_path,
                version=version,
                settings=settings or {},
                language_servers=self.language_servers[engine],
            )
            self.engine_configs[project_id] = config
            self.active_engine = engine
            logger.info(f"Registered {engine.value} project: {project_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to register project {project_id}: {str(e)}")
            return False

    def get_completions(
        self,
        project_id: str,
        file_path: str,
        line: int,
        column: int,
        trigger_character: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get code completions for a position in the file

        Args:
            project_id: Project ID
            file_path: File path relative to project
            line: Line number (0-based)
            column: Column number (0-based)
            trigger_character: Character that triggered completion

        Returns:
            List of completion items
        """
        if project_id not in self.engine_configs:
            logger.warning(f"Project {project_id} not found")
            return []

        config = self.engine_configs[project_id]

        # Route to engine-specific completion handler
        if config.engine == GameEngine.CONSTRUCT3:
            return self._get_construct3_completions(config, file_path, line, column)
        elif config.engine == GameEngine.GODOT:
            return self._get_godot_completions(config, file_path, line, column)
        elif config.engine == GameEngine.UNITY:
            return self._get_unity_completions(config, file_path, line, column)
        elif config.engine == GameEngine.UNREAL:
            return self._get_unreal_completions(config, file_path, line, column)

        return []

    def get_hover_info(
        self, project_id: str, file_path: str, line: int, column: int
    ) -> Optional[Dict[str, Any]]:
        """Get hover information (type, documentation) for position"""
        if project_id not in self.engine_configs:
            return None

        config = self.engine_configs[project_id]

        if config.engine == GameEngine.CONSTRUCT3:
            return self._get_construct3_hover(config, file_path, line, column)
        elif config.engine == GameEngine.GODOT:
            return self._get_godot_hover(config, file_path, line, column)
        elif config.engine == GameEngine.UNITY:
            return self._get_unity_hover(config, file_path, line, column)
        elif config.engine == GameEngine.UNREAL:
            return self._get_unreal_hover(config, file_path, line, column)

        return None

    def get_diagnostics(self, project_id: str, file_path: str) -> List[Dict[str, Any]]:
        """Get diagnostics (errors, warnings) for a file"""
        if project_id not in self.engine_configs:
            return []

        config = self.engine_configs[project_id]

        if config.engine == GameEngine.CONSTRUCT3:
            return self._get_construct3_diagnostics(config, file_path)
        elif config.engine == GameEngine.GODOT:
            return self._get_godot_diagnostics(config, file_path)
        elif config.engine == GameEngine.UNITY:
            return self._get_unity_diagnostics(config, file_path)
        elif config.engine == GameEngine.UNREAL:
            return self._get_unreal_diagnostics(config, file_path)

        return []

    def get_definition(
        self, project_id: str, file_path: str, line: int, column: int
    ) -> Optional[Dict[str, Any]]:
        """Get definition location for symbol at position"""
        if project_id not in self.engine_configs:
            return None

        config = self.engine_configs[project_id]

        if config.engine == GameEngine.CONSTRUCT3:
            return self._get_construct3_definition(config, file_path, line, column)
        elif config.engine == GameEngine.GODOT:
            return self._get_godot_definition(config, file_path, line, column)
        elif config.engine == GameEngine.UNITY:
            return self._get_unity_definition(config, file_path, line, column)
        elif config.engine == GameEngine.UNREAL:
            return self._get_unreal_definition(config, file_path, line, column)

        return None

    # ==================== CONSTRUCT 3 HANDLERS ====================

    def _get_construct3_completions(
        self, config: EngineConfig, file_path: str, line: int, column: int
    ) -> List[Dict[str, Any]]:
        """Construct 3 uses JavaScript/TypeScript with WebAssembly runtime"""
        # Route to TypeScript Language Server
        completions = [
            {
                "label": "On Start",
                "kind": "keyword",
                "detail": "Construct 3 event",
                "sortText": "001",
            },
            {
                "label": "On Collision",
                "kind": "keyword",
                "detail": "Construct 3 event",
                "sortText": "002",
            },
            {
                "label": "Set Position",
                "kind": "method",
                "detail": "Set object position",
                "sortText": "003",
            },
            {
                "label": "Destroy",
                "kind": "method",
                "detail": "Destroy object",
                "sortText": "004",
            },
        ]
        logger.debug(f"Construct3 completions: {len(completions)} items")
        return completions

    def _get_construct3_hover(
        self, config: EngineConfig, file_path: str, line: int, column: int
    ) -> Optional[Dict[str, Any]]:
        """Construct 3 hover information"""
        return {
            "content": "Construct 3 event",
            "range": {"start": {"line": line, "character": column}, "end": {"line": line, "character": column + 10}},
        }

    def _get_construct3_diagnostics(
        self, config: EngineConfig, file_path: str
    ) -> List[Dict[str, Any]]:
        """Construct 3 diagnostics"""
        return []

    def _get_construct3_definition(
        self, config: EngineConfig, file_path: str, line: int, column: int
    ) -> Optional[Dict[str, Any]]:
        """Construct 3 definition"""
        return None

    # ==================== GODOT HANDLERS ====================

    def _get_godot_completions(
        self, config: EngineConfig, file_path: str, line: int, column: int
    ) -> List[Dict[str, Any]]:
        """Godot uses GDScript language"""
        completions = [
            {"label": "_ready", "kind": "function", "detail": "Godot lifecycle", "sortText": "001"},
            {"label": "_process", "kind": "function", "detail": "Godot lifecycle", "sortText": "002"},
            {
                "label": "position",
                "kind": "variable",
                "detail": "Object position",
                "sortText": "003",
            },
            {
                "label": "queue_free",
                "kind": "method",
                "detail": "Delete object",
                "sortText": "004",
            },
        ]
        logger.debug(f"Godot completions: {len(completions)} items")
        return completions

    def _get_godot_hover(
        self, config: EngineConfig, file_path: str, line: int, column: int
    ) -> Optional[Dict[str, Any]]:
        """Godot hover information"""
        return {
            "content": "GDScript method",
            "range": {"start": {"line": line, "character": column}, "end": {"line": line, "character": column + 10}},
        }

    def _get_godot_diagnostics(
        self, config: EngineConfig, file_path: str
    ) -> List[Dict[str, Any]]:
        """Godot diagnostics"""
        return []

    def _get_godot_definition(
        self, config: EngineConfig, file_path: str, line: int, column: int
    ) -> Optional[Dict[str, Any]]:
        """Godot definition"""
        return None

    # ==================== UNITY HANDLERS ====================

    def _get_unity_completions(
        self, config: EngineConfig, file_path: str, line: int, column: int
    ) -> List[Dict[str, Any]]:
        """Unity uses C# language via Omnisharp LSP"""
        completions = [
            {
                "label": "OnEnable",
                "kind": "function",
                "detail": "Unity lifecycle",
                "sortText": "001",
            },
            {
                "label": "Update",
                "kind": "function",
                "detail": "Unity lifecycle",
                "sortText": "002",
            },
            {
                "label": "Instantiate",
                "kind": "method",
                "detail": "Spawn object",
                "sortText": "003",
            },
            {
                "label": "Destroy",
                "kind": "method",
                "detail": "Delete object",
                "sortText": "004",
            },
        ]
        logger.debug(f"Unity completions: {len(completions)} items")
        return completions

    def _get_unity_hover(
        self, config: EngineConfig, file_path: str, line: int, column: int
    ) -> Optional[Dict[str, Any]]:
        """Unity hover information"""
        return {
            "content": "C# method",
            "range": {"start": {"line": line, "character": column}, "end": {"line": line, "character": column + 10}},
        }

    def _get_unity_diagnostics(
        self, config: EngineConfig, file_path: str
    ) -> List[Dict[str, Any]]:
        """Unity diagnostics"""
        return []

    def _get_unity_definition(
        self, config: EngineConfig, file_path: str, line: int, column: int
    ) -> Optional[Dict[str, Any]]:
        """Unity definition"""
        return None

    # ==================== UNREAL HANDLERS ====================

    def _get_unreal_completions(
        self, config: EngineConfig, file_path: str, line: int, column: int
    ) -> List[Dict[str, Any]]:
        """Unreal uses C++ language via Clangd LSP"""
        completions = [
            {
                "label": "BeginPlay",
                "kind": "function",
                "detail": "Unreal lifecycle",
                "sortText": "001",
            },
            {
                "label": "Tick",
                "kind": "function",
                "detail": "Unreal lifecycle",
                "sortText": "002",
            },
            {
                "label": "Destroy",
                "kind": "method",
                "detail": "Delete actor",
                "sortText": "003",
            },
            {
                "label": "GetActorLocation",
                "kind": "method",
                "detail": "Get actor position",
                "sortText": "004",
            },
        ]
        logger.debug(f"Unreal completions: {len(completions)} items")
        return completions

    def _get_unreal_hover(
        self, config: EngineConfig, file_path: str, line: int, column: int
    ) -> Optional[Dict[str, Any]]:
        """Unreal hover information"""
        return {
            "content": "C++ method",
            "range": {"start": {"line": line, "character": column}, "end": {"line": line, "character": column + 10}},
        }

    def _get_unreal_diagnostics(
        self, config: EngineConfig, file_path: str
    ) -> List[Dict[str, Any]]:
        """Unreal diagnostics"""
        return []

    def _get_unreal_definition(
        self, config: EngineConfig, file_path: str, line: int, column: int
    ) -> Optional[Dict[str, Any]]:
        """Unreal definition"""
        return None

    # ==================== UTILITY METHODS ====================

    def list_projects(self) -> List[Dict[str, Any]]:
        """List all registered projects"""
        return [
            {
                "project_id": pid,
                "engine": config.engine.value,
                "path": config.project_path,
                "version": config.version,
            }
            for pid, config in self.engine_configs.items()
        ]

    def get_active_engine(self) -> Optional[str]:
        """Get currently active engine"""
        return self.active_engine.value if self.active_engine else None

    def switch_engine(self, project_id: str) -> bool:
        """Switch active engine to a different project"""
        if project_id not in self.engine_configs:
            return False
        self.active_engine = self.engine_configs[project_id].engine
        logger.info(f"Switched to engine: {self.active_engine.value}")
        return True
