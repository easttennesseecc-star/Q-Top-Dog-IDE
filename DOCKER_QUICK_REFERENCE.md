# 🚀 DOCKER BUILD QUICK REFERENCE

**One-page cheat sheet for building Top Dog Docker images**

---

## ⚡ 30-SECOND QUICK START

```powershell
# Windows PowerShell
cd c:\Quellum-topdog-ide
.\docker-build.ps1
docker images | grep Top Dog
```

```bash
# Linux/macOS
cd ~/Top Dog
bash docker-build.sh
docker images | grep Top Dog
```

---

## 🎯 COMMON TASKS

### Build Both Images

```powershell
# Windows
.\docker-build.ps1 -Action build

# Linux/macOS
./docker-build.sh
```

### Push to Docker Hub

```powershell
# Windows
.\docker-build.ps1 -Action push -Registry docker.io/yourusername -Version v1.0.0

# Linux/macOS
REGISTRY=docker.io/yourusername VERSION=v1.0.0 ./docker-build.sh --push
```

### Push to Azure Container Registry

```powershell
# Windows
.\docker-build.ps1 -Action push -Registry myregistry.azurecr.io -Version v1.0.0

# Linux/macOS
REGISTRY=myregistry.azurecr.io VERSION=v1.0.0 ./docker-build.sh --push
```

### Push to AWS ECR

```powershell
# Windows
# 1. Get login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# 2. Build and push
.\docker-build.ps1 -Action push -Registry 123456789.dkr.ecr.us-east-1.amazonaws.com -Version v1.0.0

# Linux/macOS
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
REGISTRY=123456789.dkr.ecr.us-east-1.amazonaws.com VERSION=v1.0.0 ./docker-build.sh --push
```

### Test Locally

```bash
# Start all services
docker-compose -f docker-compose-local.yml up

# In another terminal, test
curl http://localhost:3000          # Frontend
curl http://localhost:8000/health   # Backend

# View logs
docker-compose -f docker-compose-local.yml logs -f backend

# Stop
docker-compose -f docker-compose-local.yml down
```

### View Images

```bash
# List all Top Dog images
docker images | grep Top Dog

# Get detailed info
docker inspect your-registry/Top Dog-backend:latest

# Image history
docker history your-registry/Top Dog-backend:latest

# Image layers and size
docker history --human --no-trunc your-registry/Top Dog-backend:latest
```

### Clean Up

```bash
# Remove dangling images
docker image prune -f

# Remove specific image
docker rmi your-registry/Top Dog-frontend:v1.0.0

# Remove all Top Dog images
docker images | grep Top Dog | awk '{print $3}' | xargs docker rmi

# Deep clean (warning: removes all unused Docker data)
docker system prune -a
```

---

## 📊 WHAT GETS BUILT

| Image | Base | Size | Purpose |
|-------|------|------|---------|
| Top Dog-frontend | Node 20 Alpine | ~152MB | React web app |
| Top Dog-backend | Python 3.11 Slim | ~348MB | FastAPI server |

---

## 🏗️ BUILD OPTIONS MATRIX

| Option | Command | Result |
|--------|---------|--------|
| Local build | `.\docker-build.ps1` | Images on local machine |
| Build & test | `.\docker-build.ps1 -Action test` | Images tested, no push |
| Build & push | `.\docker-build.ps1 -Action push` | Images pushed to registry |
| Build, test, push, clean | `.\docker-build.ps1 -Action all` | Complete pipeline |

---

## 🔧 CUSTOMIZATION

### Change Registry:
```powershell
.\docker-build.ps1 -Registry my-registry.azurecr.io
```

### Change Version:
```powershell
.\docker-build.ps1 -Version v2.1.0
```

### Change Repository Name:
```powershell
.\docker-build.ps1 -RepositoryName my-app
# Creates: my-app-frontend, my-app-backend
```

---

## 🐛 QUICK TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| Docker not found | `docker --version` to verify installed |
| Permission denied | Run PowerShell as Administrator (Windows) |
| Disk space | `docker system df` to check usage |
| Build fails | `docker builder prune -a` then rebuild |
| Push fails | `docker login` to authenticate |
| No images | Check `docker images` to list all |

---

## ✅ BEFORE KUBERNETES DEPLOYMENT

- [ ] Images built: `docker images \| grep Top Dog`
- [ ] Images tagged correctly: includes registry + version
- [ ] Images pushed: can pull from registry
- [ ] Local test passed: `docker-compose up` works
- [ ] Registry URL in K8s manifests
- [ ] Size reasonable: Frontend ~150MB, Backend ~350MB

---

## 📋 REGISTRY URLS BY PROVIDER

| Registry | Format |
|----------|--------|
| Docker Hub | `docker.io/username/image` |
| Azure ACR | `myregistry.azurecr.io/image` |
| AWS ECR | `123456789.dkr.ecr.region.amazonaws.com/image` |
| Google GCR | `gcr.io/project-id/image` |
| GitHub | `ghcr.io/username/image` |

---

## 🚀 NEXT STEPS

1. ✅ Build images: `.\docker-build.ps1`
2. ✅ Test locally: `docker-compose up`
3. ✅ Push to registry: `.\docker-build.ps1 -Action push`
4. 📖 Read: KUBERNETES_QUICK_START.md
5. 🚀 Deploy to K8s: `kubectl apply -f k8s/`

