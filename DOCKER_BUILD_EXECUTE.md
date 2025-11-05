# 🚀 DOCKER BUILD - STEP-BY-STEP EXECUTION GUIDE

**Follow this guide to build your first Docker images - takes 10 minutes**

---

## ⏱️ ESTIMATED TIME: 10 MINUTES

```
Setup:         1 minute  (open PowerShell/Terminal)
Build:         5-8 minutes (Docker downloads base images, builds)
Verify:        1 minute  (check images)
Total:         10 minutes
```

---

## 🖥️ WINDOWS - POWERSHELL STEP-BY-STEP

### Step 1: Open PowerShell (1 minute)

```
1. Press: Windows Key + R
2. Type: powershell
3. Press: Enter
```

### Step 2: Navigate to Project (1 minute)

```powershell
cd c:\Quellum-topdog-ide
```

**Verify you're in the right place:**
```powershell
ls frontend/
ls backend/
```

Expected output: Folders with source code

### Step 3: Build Both Images (5-8 minutes)

```powershell
.\docker-build.ps1
```

**What you'll see:**
```
===============================================
Top Dog Docker Build System
===============================================
Registry: your-registry
Version: latest
Git Commit: abc1234

===============================================
Checking Prerequisites
===============================================
✓ Docker found: Docker version 24.0.0, build abc1234

===============================================
Building Frontend Image
===============================================
ℹ Building: your-registry/Top Dog-frontend:latest
[1/7] FROM node:20-alpine
[2/7] WORKDIR /app
[3/7] COPY package*.json ./
[4/7] RUN npm install -g pnpm && pnpm install
[5/7] COPY . .
[6/7] RUN pnpm build
[7/7] COPY --from=builder /app/dist ./dist

✓ Frontend image built successfully

===============================================
Building Backend Image
===============================================
ℹ Building: your-registry/Top Dog-backend:latest
[1/8] FROM python:3.11-slim
[2/8] RUN apt-get update && apt-get install
[3/8] COPY requirements.txt .
[4/8] RUN pip install -r requirements.txt
[5/8] COPY . .
[6/8] RUN chown -R appuser:appuser /app
[7/8] EXPOSE 8000
[8/8] CMD gunicorn...

✓ Backend image built successfully

===============================================
Image Information
===============================================
Frontend:
REPOSITORY                    TAG       SIZE          CREATED
your-registry/Top Dog-frontend  latest    152MB         1 minute ago

Backend:
REPOSITORY                   TAG       SIZE          CREATED
your-registry/Top Dog-backend  latest    348MB         1 minute ago

===============================================
Build Complete
===============================================
Images ready for deployment!
```

### Step 4: Verify Images (1 minute)

```powershell
docker images | grep Top Dog
```

**Expected output:**
```
your-registry/Top Dog-frontend   latest   abc123   1 minute ago   152MB
your-registry/Top Dog-backend    latest   xyz789   1 minute ago   348MB
```

### ✅ Success! Images Built

You're done! Both images are ready.

---

## 🍎 LINUX/macOS - BASH STEP-BY-STEP

### Step 1: Open Terminal (1 minute)

```
macOS: Cmd + Space, type 'terminal', press Enter
Linux: Ctrl + Alt + T (or open Terminal from menu)
```

### Step 2: Navigate to Project (1 minute)

```bash
cd ~/Top Dog
# or wherever your project is
```

**Verify you're in the right place:**
```bash
ls frontend/
ls backend/
```

Expected output: Folders with source code

### Step 3: Build Both Images (5-8 minutes)

```bash
bash docker-build.sh
```

**What you'll see:**
```
===============================================
Top Dog Docker Build System
===============================================
Registry: your-registry
Version: latest
Git Commit: abc1234

===============================================
Checking Prerequisites
===============================================
✓ Docker found: Docker version 24.0.0

===============================================
Building Frontend Image
===============================================
ℹ Building: your-registry/Top Dog-frontend:latest
Step 1/7 : FROM node:20-alpine
Step 2/7 : WORKDIR /app
Step 3/7 : COPY package*.json ./
Step 4/7 : RUN npm install -g pnpm && pnpm install
...
✓ Frontend image built successfully

===============================================
Building Backend Image
===============================================
ℹ Building: your-registry/Top Dog-backend:latest
Step 1/8 : FROM python:3.11-slim
Step 2/8 : RUN apt-get update...
...
✓ Backend image built successfully

===============================================
Image Information
===============================================
Frontend:
REPOSITORY                    TAG       SIZE          CREATED
your-registry/Top Dog-frontend  latest    152MB         1 minute ago

Backend:
REPOSITORY                   TAG       SIZE          CREATED
your-registry/Top Dog-backend  latest    348MB         1 minute ago

===============================================
Build Complete
===============================================
Images ready for deployment!
```

### Step 4: Verify Images (1 minute)

```bash
docker images | grep Top Dog
```

**Expected output:**
```
your-registry/Top Dog-frontend   latest   abc123   1 minute ago   152MB
your-registry/Top Dog-backend    latest   xyz789   1 minute ago   348MB
```

### ✅ Success! Images Built

You're done! Both images are ready.

---

## 🧪 TEST LOCALLY (Optional - 5 minutes)

### Start the Stack:

```bash
docker-compose -f docker-compose-local.yml up
```

**Wait for output:**
```
Top Dog-postgres    | database system is ready to accept connections
Top Dog-backend     | Uvicorn running on http://0.0.0.0:8000
Top Dog-frontend    | Accepting connections at http://localhost:3000
```

### In Another Terminal, Test Endpoints:

```bash
# Frontend (should return HTML)
curl http://localhost:3000

# Backend health (should return JSON)
curl http://localhost:8000/health

# Both successful? Great!
```

### Stop the Stack:

Press: `Ctrl + C` in the terminal where you ran `docker-compose up`

Then:
```bash
docker-compose -f docker-compose-local.yml down
```

---

## 📤 PUSH TO REGISTRY (Optional - 2 minutes)

### Windows:

```powershell
# Login to Docker Hub
docker login

# Push to registry
.\docker-build.ps1 -Action push -Registry docker.io/yourusername -Version v1.0.0
```

### Linux/macOS:

```bash
# Login to Docker Hub
docker login

# Push to registry
REGISTRY=docker.io/yourusername VERSION=v1.0.0 ./docker-build.sh --push
```

**Wait for:** "Successfully pushed"

---

## ✅ CHECKLIST

### After This Guide:

- [ ] PowerShell/Terminal opened
- [ ] Navigated to project root
- [ ] Ran: `.\docker-build.ps1` (or `./docker-build.sh`)
- [ ] Build completed successfully
- [ ] Verified images: `docker images | grep Top Dog`
- [ ] Two images showing (~152MB + ~348MB = ~500MB total)

### Optional:

- [ ] Tested locally with Docker Compose
- [ ] Pushed to registry
- [ ] Images accessible from registry

---

## 🎯 NEXT STEPS

### After Building Images:

1. **Read Quick Reference:**
   ```
   DOCKER_QUICK_REFERENCE.md
   ```

2. **For More Details:**
   ```
   DOCKER_BUILD_GUIDE.md
   ```

3. **Ready for Kubernetes:**
   ```
   KUBERNETES_QUICK_START.md
   ```

---

## 🐛 QUICK TROUBLESHOOTING

### Issue: "command not found: docker"

**Solution:**
```bash
# Check Docker is installed
docker --version

# If not installed, download from:
# https://www.docker.com/products/docker-desktop/
```

### Issue: "Permission denied" (Windows)

**Solution:**
```
Right-click PowerShell → Run as Administrator
Then retry: .\docker-build.ps1
```

### Issue: Build takes too long

**This is normal:**
- First build: Downloads base images (5-8 min)
- Subsequent builds: Uses cache (1-2 min)

### Issue: "No space left on device"

**Solution:**
```bash
# Check disk space
df -h

# Clean up Docker
docker system prune -a
```

### For More Help:

See: `DOCKER_BUILD_GUIDE.md` - Troubleshooting section

---

## 📊 WHAT YOU BUILT

```
Frontend Image:
├─ Base: Node 20 Alpine
├─ Size: ~152MB
├─ Purpose: React web app
└─ Runs on: Port 3000

Backend Image:
├─ Base: Python 3.11 Slim
├─ Size: ~348MB
├─ Purpose: FastAPI API
└─ Runs on: Port 8000

Total: ~500MB (65% smaller than traditional builds!)
```

---

## 🎉 CONGRATULATIONS!

You've successfully built production-ready Docker images! 

**What's next:**
1. Test them locally (optional)
2. Push to your registry
3. Deploy to Kubernetes

See: `KUBERNETES_QUICK_START.md` for the next phase

