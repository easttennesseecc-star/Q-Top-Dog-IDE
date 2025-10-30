"""
Game Engine API Routes
Exposes game engine functionality via REST API
"""

from flask import Blueprint, request, jsonify
import logging
from typing import Dict, Any, Optional

from backend.services.game_engine_router import (
    MultiEngineRouter,
    GameEngine,
)
from backend.services.game_container_manager import GameEngineContainerManager

# Initialize services
engine_router = MultiEngineRouter()
container_manager = GameEngineContainerManager()

# Create blueprint
game_engine_bp = Blueprint("game_engine", __name__, url_prefix="/api/v1/game-engine")

logger = logging.getLogger(__name__)


# ==================== PROJECT ENDPOINTS ====================


@game_engine_bp.route("/projects", methods=["GET"])
def list_projects():
    """List all registered game engine projects"""
    try:
        projects = engine_router.list_projects()
        return jsonify({"success": True, "projects": projects}), 200
    except Exception as e:
        logger.error(f"Error listing projects: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@game_engine_bp.route("/projects", methods=["POST"])
def register_project():
    """Register a new game engine project"""
    try:
        data = request.json
        engine_name = data.get("engine")
        project_id = data.get("project_id")
        project_path = data.get("project_path")
        version = data.get("version", "latest")
        settings = data.get("settings", {})

        # Validate engine
        try:
            engine = GameEngine[engine_name.upper()]
        except KeyError:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Unknown engine: {engine_name}. Supported: construct3, godot, unity, unreal",
                    }
                ),
                400,
            )

        # Register project
        success = engine_router.register_project(
            project_id=project_id,
            engine=engine,
            project_path=project_path,
            version=version,
            settings=settings,
        )

        if success:
            return (
                jsonify(
                    {
                        "success": True,
                        "message": f"Project {project_id} registered with {engine_name} engine",
                        "project_id": project_id,
                    }
                ),
                201,
            )
        else:
            return (
                jsonify({"success": False, "error": "Failed to register project"}),
                400,
            )

    except Exception as e:
        logger.error(f"Error registering project: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@game_engine_bp.route("/projects/<project_id>/switch", methods=["POST"])
def switch_project(project_id: str):
    """Switch to a different project"""
    try:
        success = engine_router.switch_engine(project_id)

        if success:
            active_engine = engine_router.get_active_engine()
            return (
                jsonify(
                    {
                        "success": True,
                        "message": f"Switched to project {project_id}",
                        "active_engine": active_engine,
                    }
                ),
                200,
            )
        else:
            return (
                jsonify({"success": False, "error": f"Project {project_id} not found"}),
                404,
            )

    except Exception as e:
        logger.error(f"Error switching project: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== CODE INTELLIGENCE ENDPOINTS ====================


@game_engine_bp.route("/projects/<project_id>/completions", methods=["POST"])
def get_completions(project_id: str):
    """Get code completions for a position"""
    try:
        data = request.json
        file_path = data.get("file_path")
        line = data.get("line")
        column = data.get("column")
        trigger_character = data.get("trigger_character")

        completions = engine_router.get_completions(
            project_id=project_id,
            file_path=file_path,
            line=line,
            column=column,
            trigger_character=trigger_character,
        )

        return jsonify({"success": True, "completions": completions}), 200

    except Exception as e:
        logger.error(f"Error getting completions: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@game_engine_bp.route("/projects/<project_id>/hover", methods=["POST"])
def get_hover(project_id: str):
    """Get hover information for a position"""
    try:
        data = request.json
        file_path = data.get("file_path")
        line = data.get("line")
        column = data.get("column")

        hover_info = engine_router.get_hover_info(
            project_id=project_id,
            file_path=file_path,
            line=line,
            column=column,
        )

        if hover_info:
            return jsonify({"success": True, "hover": hover_info}), 200
        else:
            return jsonify({"success": True, "hover": None}), 200

    except Exception as e:
        logger.error(f"Error getting hover info: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@game_engine_bp.route("/projects/<project_id>/diagnostics", methods=["POST"])
def get_diagnostics(project_id: str):
    """Get diagnostics (errors, warnings) for a file"""
    try:
        data = request.json
        file_path = data.get("file_path")

        diagnostics = engine_router.get_diagnostics(
            project_id=project_id,
            file_path=file_path,
        )

        return jsonify({"success": True, "diagnostics": diagnostics}), 200

    except Exception as e:
        logger.error(f"Error getting diagnostics: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@game_engine_bp.route("/projects/<project_id>/definition", methods=["POST"])
def get_definition(project_id: str):
    """Get definition location for a symbol"""
    try:
        data = request.json
        file_path = data.get("file_path")
        line = data.get("line")
        column = data.get("column")

        definition = engine_router.get_definition(
            project_id=project_id,
            file_path=file_path,
            line=line,
            column=column,
        )

        if definition:
            return jsonify({"success": True, "definition": definition}), 200
        else:
            return jsonify({"success": True, "definition": None}), 200

    except Exception as e:
        logger.error(f"Error getting definition: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== CONTAINER ENDPOINTS ====================


@game_engine_bp.route("/containers", methods=["GET"])
def list_containers():
    """List all running game engine containers"""
    try:
        containers = container_manager.list_containers()
        return jsonify({"success": True, "containers": containers}), 200
    except Exception as e:
        logger.error(f"Error listing containers: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@game_engine_bp.route("/containers/start", methods=["POST"])
def start_container():
    """Start a game engine container (Godot or Unreal)"""
    try:
        data = request.json
        project_id = data.get("project_id")
        engine = data.get("engine")
        project_path = data.get("project_path")
        config = data.get("config", {})

        if engine.lower() == "godot":
            status = container_manager.start_godot_container(
                project_id=project_id,
                project_path=project_path,
                config=config,
            )
        elif engine.lower() == "unreal":
            status = container_manager.start_unreal_container(
                project_id=project_id,
                project_path=project_path,
                config=config,
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Engine {engine} does not support containers",
                    }
                ),
                400,
            )

        if status:
            return (
                jsonify(
                    {
                        "success": True,
                        "message": f"Container started for {engine}",
                        "container": {
                            "project_id": status.project_id,
                            "engine": status.engine,
                            "container_id": status.container_id,
                            "status": status.status,
                            "port_mapping": status.port_mapping,
                        },
                    }
                ),
                201,
            )
        else:
            return (
                jsonify({"success": False, "error": "Failed to start container"}),
                500,
            )

    except Exception as e:
        logger.error(f"Error starting container: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@game_engine_bp.route("/containers/<project_id>", methods=["GET"])
def get_container_status(project_id: str):
    """Get status of a container"""
    try:
        status = container_manager.get_container_status(project_id)

        if status:
            return (
                jsonify(
                    {
                        "success": True,
                        "container": {
                            "project_id": status.project_id,
                            "engine": status.engine,
                            "container_id": status.container_id,
                            "status": status.status,
                            "port_mapping": status.port_mapping,
                            "created_at": status.created_at,
                        },
                    }
                ),
                200,
            )
        else:
            return (
                jsonify({"success": False, "error": f"Container not found"}),
                404,
            )

    except Exception as e:
        logger.error(f"Error getting container status: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@game_engine_bp.route("/containers/<project_id>/logs", methods=["GET"])
def get_container_logs(project_id: str):
    """Get container logs"""
    try:
        tail = request.args.get("tail", 100, type=int)
        logs = container_manager.get_container_logs(project_id, tail=tail)

        if logs is not None:
            return jsonify({"success": True, "logs": logs}), 200
        else:
            return (
                jsonify({"success": False, "error": f"Container not found"}),
                404,
            )

    except Exception as e:
        logger.error(f"Error getting logs: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@game_engine_bp.route("/containers/<project_id>", methods=["DELETE"])
def stop_container(project_id: str):
    """Stop and remove a container"""
    try:
        success = container_manager.stop_container(project_id)

        if success:
            return (
                jsonify(
                    {
                        "success": True,
                        "message": f"Container stopped for project {project_id}",
                    }
                ),
                200,
            )
        else:
            return (
                jsonify({"success": False, "error": f"Container not found"}),
                404,
            )

    except Exception as e:
        logger.error(f"Error stopping container: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@game_engine_bp.route("/health", methods=["GET"])
def health_check():
    """Health check for game engine services"""
    return (
        jsonify(
            {
                "success": True,
                "docker_available": container_manager.docker_available,
                "active_containers": len(container_manager.containers),
                "registered_projects": len(engine_router.engine_configs),
            }
        ),
        200,
    )
