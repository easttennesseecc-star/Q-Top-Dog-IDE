# Construct 3 Container — Quick Start

Goal: Preview your Construct 3 export in seconds via a container.

Prerequisites
- Docker Desktop installed and running
- A Construct 3 project exported to HTML5 (folder on your machine)

Start container
- API: POST /api/v1/game-engine/containers/start
- Body:
  {
    "project_id": "my-construct3-game",
    "engine": "construct3",
    "project_path": "C:/path/to/your/c3-export",
    "config": { "preview_port": 8080 }
  }

What happens
- A Node http-server container serves your exported folder read-only
- The API returns the mapped host port; open http://localhost:<port>

Stop container
- API: DELETE /api/v1/game-engine/containers/{project_id}

Helpful links
- Construct 3 export: https://www.construct.net/en/make-games/manuals/construct-3/exporting
- Docker Desktop: https://www.docker.com/products/docker-desktop/
