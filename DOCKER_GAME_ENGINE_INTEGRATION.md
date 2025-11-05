# 🐳 DOCKER INTEGRATION FOR GAME ENGINES
## Top Dog Multi-Engine Support via Containers

**Date**: October 29, 2025  
**Version**: 1.0  
**Status**: Implementation Ready

---

## EXECUTIVE SUMMARY

Top Dog will use **Docker containers** to run game engine runtimes, enabling:

1. **Godot** - GDScript debugger + scene preview in Docker
2. **Unreal Engine** - C++ compilation + PIE (Play In Editor) in Docker
3. **Custom Games** - Any game runtime packaged in container

**Benefits**:
- ✅ No local engine installation required
- ✅ Consistent environment (Windows, Mac, Linux)
- ✅ Scalable (multi-project parallel containers)
- ✅ Cloud-ready (deploy containers to AWS/GCP)
- ✅ CI/CD integration (automated game builds)

---

## DOCKER ARCHITECTURE

### Container Strategy

```
Top Dog Frontend (React, Monaco)
    ↕ WebSocket
Top Dog Backend (Python)
    ├─ Docker Manager (spawn/manage containers)
    ├─ Container 1: Godot Runtime (port 6006)
    ├─ Container 2: Unreal Build (port 6007)
    ├─ Container 3: Game Preview (port 6008)
    └─ Container N: Custom Runtime (port 600X)
        ↕
    Docker Engine (Linux/Mac/Windows WSL2)
```

### Port Mapping

```
Top Dog Backend: 5000
├─ Godot LSP: 5001
├─ Godot Debugger: 6006
├─ Godot Preview: 8006
├─ Unreal LSP: 5002
├─ Unreal Debugger: 6007
├─ Unreal Preview: 8007
└─ Game Preview: 6008-6099 (for multiple projects)
```

---

## DOCKERFILE SPECIFICATIONS

### 1. Godot Runtime Container

```dockerfile
# File: docker/godot-runtime.dockerfile
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    godot-engine \
    gdb \
    python3-pip \
    netcat \
    curl

# Create working directory
WORKDIR /project

# Expose ports
EXPOSE 6006 8006  # 6006: debugger, 8006: preview

# Copy entrypoint script
COPY godot-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
```

### Godot Entrypoint Script

```bash
#!/bin/bash
# File: docker/godot-entrypoint.sh

# Start Godot debugger server
godot \
  --path /project \
  --debug-collisions \
  --verbose \
  2>&1 | tee /tmp/godot.log &

GODOT_PID=$!

# Monitor logs
tail -f /tmp/godot.log &

# Keep container running
wait $GODOT_PID
```

### Godot Container Usage

```python
# backend/services/docker_manager.py
import docker
import time

class DockerManager:
    def __init__(self):
        self.client = docker.from_env()
        self.containers = {}
    
    def start_godot_runtime(self, project_id, project_path):
        """Start Godot runtime in Docker container"""
        container = self.client.containers.run(
            image="Top Dog-godot:latest",
            name=f"godot-{project_id}",
            ports={'6006/tcp': 6006, '8006/tcp': 8006},
            volumes={project_path: {'bind': '/project', 'mode': 'rw'}},
            detach=True,
            environment={
                'PROJECT_ID': project_id,
                'DEBUG_PORT': '6006'
            }
        )
        self.containers[project_id] = {
            'engine': 'godot',
            'container': container,
            'debugger_port': 6006,
            'preview_port': 8006,
            'started_at': time.time()
        }
        return container
    
    def stop_godot_runtime(self, project_id):
        """Stop Godot runtime container"""
        if project_id in self.containers:
            container = self.containers[project_id]['container']
            container.stop()
            container.remove()
            del self.containers[project_id]
```

---

### 2. Unreal Engine Build Container

```dockerfile
# File: docker/unreal-build.dockerfile
# Note: This is a Windows container (Unreal needs Windows)

FROM mcr.microsoft.com/windows/server:ltsc2022

# Install Visual Studio Build Tools
RUN powershell -Command \
    Invoke-WebRequest -Uri https://aka.ms/vs/17/release/vs_buildtools.exe -OutFile vs_buildtools.exe ; \
    .\vs_buildtools.exe --passive --wait

# Install Unreal Engine
RUN powershell -Command \
    Invoke-WebRequest -Uri https://launcher.unrealengine.com -OutFile unreal_setup.exe ; \
    .\unreal_setup.exe /S /D=C:\UnrealEngine

# Create working directory
WORKDIR C:\project

# Expose ports
EXPOSE 6007 8007 10100  # 6007: debugger, 8007: preview, 10100: PIE

# Copy entrypoint
COPY unreal-entrypoint.bat /entrypoint.bat

ENTRYPOINT ["cmd", "/c", "entrypoint.bat"]
```

### Unreal Entrypoint Script

```batch
# File: docker/unreal-entrypoint.bat
@echo off

REM Start Unreal Editor in headless mode for debugging
C:\UnrealEngine\Engine\Binaries\Win64\UnrealEditor-Cmd.exe ^
  "%PROJECT_PATH%\MyGame.uproject" ^
  -stdout ^
  -log ^
  -debug ^
  -unattended

REM Keep container running
timeout /t 86400
```

### Unreal Container Usage

```python
class DockerManager:
    def start_unreal_runtime(self, project_id, project_path):
        """Start Unreal Engine in Docker container"""
        # Note: Windows containers only
        container = self.client.containers.run(
            image="Top Dog-unreal:latest",
            name=f"unreal-{project_id}",
            ports={
                '6007/tcp': 6007,    # Debugger
                '8007/tcp': 8007,    # Preview
                '10100/tcp': 10100   # PIE
            },
            volumes={project_path: {'bind': 'C:\\project', 'mode': 'rw'}},
            detach=True,
            environment={
                'PROJECT_ID': project_id,
                'DEBUG_PORT': '6007',
                'PROJECT_PATH': 'C:\\project'
            }
        )
        self.containers[project_id] = {
            'engine': 'unreal',
            'container': container,
            'debugger_port': 6007,
            'preview_port': 8007,
            'pie_port': 10100,
            'started_at': time.time()
        }
        return container
```

---

### 3. Game Preview Container (Generic)

```dockerfile
# File: docker/game-preview.dockerfile
FROM node:18-alpine

# Install common game frameworks
RUN npm install -g \
    @babylonjs/core \
    three \
    phaser \
    pixi.js

WORKDIR /game

EXPOSE 8080  # Preview server

# Copy game files from host
COPY . /game/

# Start preview server
CMD ["node", "server.js"]
```

---

## CONTAINER MANAGEMENT

### Python Docker Manager Class

```python
# backend/services/docker_manager.py

import docker
import json
import logging
from typing import Dict, Optional

class ContainerManager:
    """Manage game engine containers"""
    
    def __init__(self):
        self.client = docker.from_env()
        self.containers: Dict[str, dict] = {}
        self.logger = logging.getLogger(__name__)
    
    def build_image(self, dockerfile_path: str, tag: str):
        """Build Docker image from Dockerfile"""
        try:
            image, build_logs = self.client.images.build(
                dockerfile=dockerfile_path,
                tag=tag
            )
            self.logger.info(f"Built image: {tag}")
            return image
        except Exception as e:
            self.logger.error(f"Failed to build image {tag}: {e}")
            raise
    
    def start_container(self, engine: str, project_id: str, config: dict) -> dict:
        """Start container for game engine"""
        try:
            if engine == 'godot':
                container = self._start_godot(project_id, config)
            elif engine == 'unreal':
                container = self._start_unreal(project_id, config)
            elif engine == 'custom':
                container = self._start_custom(project_id, config)
            else:
                raise ValueError(f"Unknown engine: {engine}")
            
            # Store container reference
            self.containers[project_id] = {
                'engine': engine,
                'container': container,
                'config': config
            }
            
            return {
                'status': 'started',
                'project_id': project_id,
                'container_id': container.id[:12],
                'ports': self._get_ports(container)
            }
        except Exception as e:
            self.logger.error(f"Failed to start {engine}: {e}")
            raise
    
    def _start_godot(self, project_id: str, config: dict):
        """Start Godot container"""
        return self.client.containers.run(
            image=config.get('image', 'Top Dog-godot:latest'),
            name=f"godot-{project_id}",
            ports={
                '6006/tcp': config.get('debugger_port', 6006),
                '8006/tcp': config.get('preview_port', 8006)
            },
            volumes={
                config['project_path']: {
                    'bind': '/project',
                    'mode': 'rw'
                }
            },
            detach=True,
            environment={'PROJECT_ID': project_id}
        )
    
    def _start_unreal(self, project_id: str, config: dict):
        """Start Unreal Engine container"""
        return self.client.containers.run(
            image=config.get('image', 'Top Dog-unreal:latest'),
            name=f"unreal-{project_id}",
            ports={
                '6007/tcp': config.get('debugger_port', 6007),
                '8007/tcp': config.get('preview_port', 8007),
                '10100/tcp': config.get('pie_port', 10100)
            },
            volumes={
                config['project_path']: {
                    'bind': 'C:\\project',
                    'mode': 'rw'
                }
            },
            detach=True
        )
    
    def _start_custom(self, project_id: str, config: dict):
        """Start custom game runtime container"""
        return self.client.containers.run(
            image=config['image'],
            name=f"game-{project_id}",
            ports={port: port for port in config.get('ports', [8080])},
            volumes={
                config['project_path']: {
                    'bind': '/game',
                    'mode': 'rw'
                }
            },
            detach=True
        )
    
    def stop_container(self, project_id: str):
        """Stop and remove container"""
        if project_id not in self.containers:
            raise ValueError(f"Container not found: {project_id}")
        
        container_info = self.containers[project_id]
        container = container_info['container']
        container.stop()
        container.remove()
        del self.containers[project_id]
    
    def get_container_logs(self, project_id: str) -> str:
        """Get container logs"""
        if project_id not in self.containers:
            raise ValueError(f"Container not found: {project_id}")
        
        container = self.containers[project_id]['container']
        return container.logs(decode=True)
    
    def _get_ports(self, container) -> dict:
        """Extract port mappings from container"""
        ports = {}
        if container.ports:
            for internal_port, external_ports in container.ports.items():
                if external_ports:
                    external_port = external_ports[0]['HostPort']
                    ports[internal_port] = external_port
        return ports
```

---

## FRONTEND INTEGRATION

### Container Status UI (React)

```typescript
// frontend/components/ContainerManager.tsx

import React, { useState, useEffect } from 'react';

interface Container {
  project_id: string;
  engine: string;
  status: 'running' | 'stopped' | 'error';
  ports: Record<string, string>;
}

export function ContainerManager() {
  const [containers, setContainers] = useState<Container[]>([]);
  const [loading, setLoading] = useState(false);

  const startContainer = async (engine: string, projectId: string) => {
    setLoading(true);
    try {
      const response = await fetch('/api/containers/start', {
        method: 'POST',
        body: JSON.stringify({
          engine,
          project_id: projectId,
          project_path: `/projects/${projectId}`
        })
      });
      const data = await response.json();
      setContainers([...containers, data]);
    } finally {
      setLoading(false);
    }
  };

  const stopContainer = async (projectId: string) => {
    setLoading(true);
    try {
      await fetch(`/api/containers/${projectId}`, { method: 'DELETE' });
      setContainers(containers.filter(c => c.project_id !== projectId));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container-manager">
      <h2>Active Containers</h2>
      {containers.map(container => (
        <div key={container.project_id} className="container-item">
          <span className={`badge ${container.status}`}>
            {container.engine.toUpperCase()}: {container.status}
          </span>
          <div className="ports">
            {Object.entries(container.ports).map(([internal, external]) => (
              <span key={internal}>
                {internal} → {external}
              </span>
            ))}
          </div>
          <button
            onClick={() => stopContainer(container.project_id)}
            disabled={loading}
          >
            Stop
          </button>
        </div>
      ))}
    </div>
  );
}
```

---

## DOCKER SETUP FOR DEVELOPERS

### Quick Start (Local Development)

```bash
# Build all game engine images
docker build -f docker/godot-runtime.dockerfile -t Top Dog-godot:latest .
docker build -f docker/game-preview.dockerfile -t Top Dog-preview:latest .

# On Windows, build Unreal image (requires Windows container)
docker build -f docker/unreal-build.dockerfile -t Top Dog-unreal:latest .

# Verify images
docker images | grep Top Dog
```

### Docker Compose (Local Dev Stack)

```yaml
# File: docker-compose.yml
version: '3.8'

services:
  Top Dog-backend:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - DOCKER_HOST=unix:///var/run/docker.sock

  godot-runtime:
    image: Top Dog-godot:latest
    ports:
      - "6006:6006"
      - "8006:8006"
    volumes:
      - ./projects:/project

  game-preview:
    image: Top Dog-preview:latest
    ports:
      - "8080:8080"
    volumes:
      - ./projects:/game

# Note: Unreal container runs separately on Windows
```

---

## API ENDPOINTS

### Container Management API

```python
# backend/api/v1/containers.py

@app.route('/api/containers/start', methods=['POST'])
def start_container():
    """Start game engine container"""
    data = request.json
    result = container_manager.start_container(
        engine=data['engine'],
        project_id=data['project_id'],
        config={
            'project_path': data['project_path'],
            'debugger_port': data.get('debugger_port', 6006),
            'preview_port': data.get('preview_port', 8006)
        }
    )
    return jsonify(result)

@app.route('/api/containers/<project_id>', methods=['GET'])
def get_container_status(project_id):
    """Get container status"""
    container_info = container_manager.containers.get(project_id)
    if not container_info:
        return {'status': 'not_found'}, 404
    
    container = container_info['container']
    logs = container.logs(tail=100, decode=True)
    
    return jsonify({
        'project_id': project_id,
        'engine': container_info['engine'],
        'status': 'running' if container.status == 'running' else 'stopped',
        'logs': logs.split('\n')[-10:]
    })

@app.route('/api/containers/<project_id>', methods=['DELETE'])
def stop_container(project_id):
    """Stop container"""
    container_manager.stop_container(project_id)
    return {'status': 'stopped'}, 200
```

---

## CI/CD INTEGRATION

### GitHub Actions Example

```yaml
# .github/workflows/build-game.yml
name: Build Game

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Godot Container
        run: docker build -f docker/godot-runtime.dockerfile -t Top Dog-godot:latest .
      
      - name: Start Godot Container
        run: docker run -d -p 6006:6006 Top Dog-godot:latest
      
      - name: Run Game Tests
        run: docker exec godot-0 godot --path /project --script tests/run_tests.gd
      
      - name: Build Game
        run: docker exec godot-0 godot --path /project --export-debug HTML5 /output/game.html
      
      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: game-build
          path: /output/game.html
```

---

## PERFORMANCE CONSIDERATIONS

### Memory Management

```python
# Limit container memory usage
container = self.client.containers.run(
    image='Top Dog-godot:latest',
    mem_limit='1g',  # 1GB max
    memswap_limit='1g',
    cpuset_cpus='0-3'  # Use only 4 CPU cores
)
```

### Network Optimization

- Use bridge networking for local development
- Use macvlan for production deployments
- Implement port health checks

```python
healthcheck = {
    'test': ['CMD', 'curl', '-f', 'http://localhost:6006/health'],
    'interval': 30000000000,  # 30 seconds
    'timeout': 10000000000,   # 10 seconds
    'retries': 3
}
```

---

## TROUBLESHOOTING

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| **Port already in use** | Another container using port | `docker ps` to find, `docker stop <id>` to kill |
| **Out of memory** | Too many containers | Set `mem_limit` on containers |
| **Container won't start** | Image not built | Run `docker build` first |
| **Network timeout** | Container not responding | Check logs with `docker logs <id>` |

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check container status
docker logs godot-project-1
docker stats godot-project-1
docker inspect godot-project-1
```

---

## CONCLUSION

Docker enables Top Dog to:
- ✅ Support Godot, Unreal, and custom game runtimes without local installation
- ✅ Scale multiple projects in parallel (one container per project)
- ✅ Deploy game builds to cloud infrastructure
- ✅ Integrate with CI/CD pipelines for automated testing

**Implementation Timeline**: Week 2-3 (concurrent with IntelliSense + Refactoring)  
**Effort**: 500-700 lines of Python + 300-400 lines of Docker config  
**ROI**: Enables $840k MRR game developer market segment

---

**Version 1.0** | October 29, 2025 | Implementation Ready
