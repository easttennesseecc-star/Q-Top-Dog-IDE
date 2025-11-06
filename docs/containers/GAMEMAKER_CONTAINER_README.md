# GameMaker Container — Quick Start (Scaffold)

Goal: Launch a GameMaker project in a Windows container (requires license + installer).

Prerequisites
- Docker Desktop with Windows containers enabled
- Valid GameMaker license
- Silent installer URL or a mounted installer path
- Environment variables:
  - GM_SILENT_INSTALLER_URL (or provide in config.installer_url)
  - GM_LICENSE (or provide in config.license)

Start container (scaffold)
- API: POST /api/v1/game-engine/containers/start
- Body:
  {
    "project_id": "my-gamemaker-project",
    "engine": "gamemaker",
    "project_path": "C:/path/to/your/gm-project",
    "config": { "installer_url": "https://.../GameMakerInstaller.exe", "license": "LICENSE-KEY" }
  }

Notes
- The current image is a scaffold; integrate your silent install steps in the Dockerfile as needed.
- Returns a helpful error if prerequisites are missing.

Stop container
- API: DELETE /api/v1/game-engine/containers/{project_id}

Helpful links
- GameMaker download/licensing: https://gamemaker.io/en
- Windows containers: https://learn.microsoft.com/windows/containers/
- Docker Desktop: https://www.docker.com/products/docker-desktop/
