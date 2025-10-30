"""
Docker Container Manager for Game Engines
Manages Godot and Unreal Engine Docker containers for cloud-based game development
"""

import os
import json
import logging
import subprocess
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)


@dataclass
class ContainerStatus:
    """Status information for a running container"""
    container_id: str
    project_id: str
    engine: str
    status: str  # 'running', 'stopped', 'error'
    created_at: str
    port_mapping: Dict[str, int]
    logs: str = ""


class GameEngineContainerManager:
    """
    Manages Docker containers for game engines
    Handles startup, shutdown, logging, and port mapping
    """

    def __init__(self):
        self.containers: Dict[str, ContainerStatus] = {}
        self.docker_available = self._check_docker()
        logger.info(f"Docker available: {self.docker_available}")

    def _check_docker(self) -> bool:
        """Check if Docker is installed and running"""
        try:
            subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                check=True,
                timeout=5,
            )
            return True
        except Exception as e:
            logger.warning(f"Docker not available: {str(e)}")
            return False

    def start_godot_container(
        self, project_id: str, project_path: str, config: Optional[Dict[str, Any]] = None
    ) -> Optional[ContainerStatus]:
        """
        Start a Godot Engine container

        Args:
            project_id: Unique project ID
            project_path: Path to Godot project on host
            config: Optional configuration (e.g., godot version, export settings)

        Returns:
            ContainerStatus if successful, None otherwise
        """
        if not self.docker_available:
            logger.error("Docker not available, cannot start Godot container")
            return None

        try:
            container_id = str(uuid.uuid4())[:8]
            config = config or {}
            godot_version = config.get("version", "4.2")

            # Port mapping
            debug_port = 6006  # GDScript debugger
            preview_port = 8006  # Game preview server
            host_debug_port = 6006 + hash(project_id) % 1000
            host_preview_port = 8006 + hash(project_id) % 1000

            # Build Dockerfile (in-memory)
            dockerfile = f"""
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \\
    godot-engine \\
    gdb \\
    python3 \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /project
VOLUME ["/project"]

EXPOSE {debug_port} {preview_port}

CMD ["godot", "--headless", "--debug-server", "0.0.0.0:{debug_port}"]
            """

            # Create temporary Dockerfile
            temp_dir = Path("/tmp") / f"godot_{container_id}"
            temp_dir.mkdir(exist_ok=True)
            dockerfile_path = temp_dir / "Dockerfile"
            dockerfile_path.write_text(dockerfile)

            # Build image
            image_tag = f"q-ide-godot-{container_id}"
            build_cmd = [
                "docker",
                "build",
                "-t",
                image_tag,
                str(temp_dir),
            ]

            logger.info(f"Building Godot image: {image_tag}")
            subprocess.run(build_cmd, check=True, capture_output=True)

            # Run container
            run_cmd = [
                "docker",
                "run",
                "-d",
                "--name",
                f"godot-{container_id}",
                "-v",
                f"{project_path}:/project",
                "-p",
                f"{host_debug_port}:{debug_port}",
                "-p",
                f"{host_preview_port}:{preview_port}",
                image_tag,
            ]

            logger.info(f"Starting Godot container: godot-{container_id}")
            result = subprocess.run(run_cmd, check=True, capture_output=True, text=True)

            # Create status object
            status = ContainerStatus(
                container_id=container_id,
                project_id=project_id,
                engine="godot",
                status="running",
                created_at=datetime.now().isoformat(),
                port_mapping={
                    "debug": host_debug_port,
                    "preview": host_preview_port,
                },
            )

            self.containers[project_id] = status
            logger.info(f"Godot container started: {container_id}")
            return status

        except Exception as e:
            logger.error(f"Failed to start Godot container: {str(e)}")
            return None

    def start_unreal_container(
        self, project_id: str, project_path: str, config: Optional[Dict[str, Any]] = None
    ) -> Optional[ContainerStatus]:
        """
        Start an Unreal Engine container

        Args:
            project_id: Unique project ID
            project_path: Path to Unreal project on host
            config: Optional configuration (e.g., UE version, build settings)

        Returns:
            ContainerStatus if successful, None otherwise
        """
        if not self.docker_available:
            logger.error("Docker not available, cannot start Unreal container")
            return None

        try:
            container_id = str(uuid.uuid4())[:8]
            config = config or {}
            ue_version = config.get("version", "5.3")

            # Port mapping
            debug_port = 6007
            preview_port = 8007
            pie_port = 10100  # Play In Editor
            host_debug_port = 6007 + hash(project_id) % 1000
            host_preview_port = 8007 + hash(project_id) % 1000
            host_pie_port = 10100 + hash(project_id) % 1000

            # Build Dockerfile
            dockerfile = f"""
FROM mcr.microsoft.com/windows/servercore:ltsc2022
RUN powershell -Command \\
    Invoke-WebRequest -Uri 'https://www.unrealengine.com/download' -OutFile 'ue_installer.exe' ; \\
    .\\ue_installer.exe /S

WORKDIR /project
VOLUME ["C:/project"]

EXPOSE {debug_port} {preview_port} {pie_port}

CMD ["cmd.exe", "/c", "C:\\UnrealEngine\\Engine\\Binaries\\Win64\\UnrealEditor-Cmd.exe", "C:\\project\\project.uproject", "-server", "-log"]
            """

            # Create temporary Dockerfile
            temp_dir = Path("/tmp") / f"unreal_{container_id}"
            temp_dir.mkdir(exist_ok=True)
            dockerfile_path = temp_dir / "Dockerfile"
            dockerfile_path.write_text(dockerfile)

            # Build image
            image_tag = f"q-ide-unreal-{container_id}"
            build_cmd = [
                "docker",
                "build",
                "-t",
                image_tag,
                str(temp_dir),
            ]

            logger.info(f"Building Unreal image: {image_tag}")
            subprocess.run(build_cmd, check=True, capture_output=True)

            # Run container
            run_cmd = [
                "docker",
                "run",
                "-d",
                "--name",
                f"unreal-{container_id}",
                "-v",
                f"{project_path}:C:\\project",
                "-p",
                f"{host_debug_port}:{debug_port}",
                "-p",
                f"{host_preview_port}:{preview_port}",
                "-p",
                f"{host_pie_port}:{pie_port}",
                image_tag,
            ]

            logger.info(f"Starting Unreal container: unreal-{container_id}")
            result = subprocess.run(run_cmd, check=True, capture_output=True, text=True)

            # Create status object
            status = ContainerStatus(
                container_id=container_id,
                project_id=project_id,
                engine="unreal",
                status="running",
                created_at=datetime.now().isoformat(),
                port_mapping={
                    "debug": host_debug_port,
                    "preview": host_preview_port,
                    "pie": host_pie_port,
                },
            )

            self.containers[project_id] = status
            logger.info(f"Unreal container started: {container_id}")
            return status

        except Exception as e:
            logger.error(f"Failed to start Unreal container: {str(e)}")
            return None

    def stop_container(self, project_id: str) -> bool:
        """Stop and remove a container"""
        if project_id not in self.containers:
            logger.warning(f"Container for project {project_id} not found")
            return False

        try:
            status = self.containers[project_id]
            container_name = f"{status.engine}-{status.container_id}"

            # Stop container
            stop_cmd = ["docker", "stop", container_name]
            subprocess.run(stop_cmd, check=True, capture_output=True)

            # Remove container
            rm_cmd = ["docker", "rm", container_name]
            subprocess.run(rm_cmd, check=True, capture_output=True)

            del self.containers[project_id]
            logger.info(f"Container stopped and removed: {container_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to stop container: {str(e)}")
            return False

    def get_container_status(self, project_id: str) -> Optional[ContainerStatus]:
        """Get current status of a container"""
        if project_id not in self.containers:
            return None

        status = self.containers[project_id]

        try:
            # Check if container is still running
            inspect_cmd = [
                "docker",
                "inspect",
                f"{status.engine}-{status.container_id}",
            ]
            result = subprocess.run(inspect_cmd, capture_output=True, text=True)

            if result.returncode == 0:
                status.status = "running"
            else:
                status.status = "stopped"
        except Exception as e:
            logger.warning(f"Failed to check container status: {str(e)}")
            status.status = "error"

        return status

    def get_container_logs(self, project_id: str, tail: int = 100) -> Optional[str]:
        """Get logs from a container"""
        if project_id not in self.containers:
            return None

        try:
            status = self.containers[project_id]
            logs_cmd = [
                "docker",
                "logs",
                "--tail",
                str(tail),
                f"{status.engine}-{status.container_id}",
            ]

            result = subprocess.run(logs_cmd, capture_output=True, text=True)
            return result.stdout

        except Exception as e:
            logger.error(f"Failed to get container logs: {str(e)}")
            return None

    def list_containers(self) -> List[Dict[str, Any]]:
        """List all managed containers"""
        return [asdict(status) for status in self.containers.values()]

    def get_container_port(self, project_id: str, port_type: str = "preview") -> Optional[int]:
        """
        Get mapped port for a container

        Args:
            project_id: Project ID
            port_type: 'debug', 'preview', or 'pie' for Unreal

        Returns:
            Host port number or None
        """
        if project_id not in self.containers:
            return None

        status = self.containers[project_id]
        return status.port_mapping.get(port_type)
