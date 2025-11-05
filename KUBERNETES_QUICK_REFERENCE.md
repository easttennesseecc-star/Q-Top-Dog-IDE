# 🚀 Top Dog Kubernetes - Quick Reference Commands

## ✅ Verify Deployment Status

```powershell
# Check all pods
kubectl get pods -n Top Dog -o wide

# Check backend specifically  
kubectl get pods -n Top Dog -l app=backend

# Check frontend specifically
kubectl get pods -n Top Dog -l app=frontend

# Get detailed pod info
kubectl describe pods -n Top Dog

# Check HPA (auto-scaling status)
kubectl get hpa -n Top Dog
```

## 📊 View Logs

```powershell
# Backend logs (latest pod)
kubectl logs -n Top Dog -l app=backend --tail=50

# Backend logs (specific pod)
kubectl logs -n Top Dog backend-PODNAME --tail=100

# Frontend logs
kubectl logs -n Top Dog -l app=frontend --tail=50

# Database logs
kubectl logs -n Top Dog postgres-0 --tail=50

# Follow logs in real-time
kubectl logs -n Top Dog -l app=backend -f
```

## 🧪 Test Health Endpoints

```powershell
# From inside a backend pod
kubectl exec -n Top Dog backend-PODNAME -- curl -s http://localhost:8000/health

# From another pod
kubectl exec -n Top Dog frontend-PODNAME -- curl -s http://backend:8000/health

# Port-forward and test locally
kubectl port-forward svc/backend 8000:8000 -n Top Dog
# Then in another terminal:
curl http://localhost:8000/health
```

## 🔄 Manage Deployments

```powershell
# Restart a deployment
kubectl rollout restart deployment/backend -n Top Dog

# Check rollout status
kubectl rollout status deployment/backend -n Top Dog -w

# View rollout history
kubectl rollout history deployment/backend -n Top Dog

# Undo last rollout
kubectl rollout undo deployment/backend -n Top Dog
```

## 🧹 Delete & Recreate

```powershell
# Force delete stuck pods
kubectl delete pods -n Top Dog -l app=backend --force --grace-period=0

# Delete entire deployment (keeps PVCs)
kubectl delete deployment backend -n Top Dog

# Delete everything in namespace (WARNING: removes ALL)
kubectl delete all -n Top Dog
```

## 📈 Scale Deployments

```powershell
# Manually scale backend to 5 replicas
kubectl scale deployment backend --replicas=5 -n Top Dog

# Check HPA (will override manual scaling)
kubectl get hpa -n Top Dog

# Delete HPA to allow manual scaling
kubectl delete hpa backend-hpa -n Top Dog
```

## 🔧 Edit Resources

```powershell
# Edit deployment manifest (opens editor)
kubectl edit deployment backend -n Top Dog

# Apply local manifest file
kubectl apply -f k8s/04-backend.yaml

# Diff local vs current
kubectl diff -f k8s/04-backend.yaml
```

## 🌐 Networking

```powershell
# Get service endpoints
kubectl get svc -n Top Dog

# Get ingress configuration
kubectl get ingress -n Top Dog

# Get LoadBalancer external IP
kubectl get svc -n ingress-nginx ingress-nginx

# Port-forward to backend
kubectl port-forward svc/backend 8000:8000 -n Top Dog

# Port-forward to frontend
kubectl port-forward svc/frontend 3000:3000 -n Top Dog

# Port-forward to postgres
kubectl port-forward svc/postgres 5432:5432 -n Top Dog
```

## 📋 Database Operations

```powershell
# Connect to postgres
kubectl port-forward svc/postgres 5432:5432 -n Top Dog
# Then from another terminal:
psql -h localhost -U postgres -d q_ide_dev

# Check PVC status
kubectl get pvc -n Top Dog

# Get PVC details
kubectl describe pvc postgres-storage-postgres-0 -n Top Dog
```

## 🔒 Security

```powershell
# Check secrets
kubectl get secrets -n Top Dog

# View secret (base64 decoded)
kubectl get secret ghcr-secret -n Top Dog -o jsonpath='{.data.\.dockerconfigjson}' | base64 -d

# Check RBAC
kubectl get rolebindings -n Top Dog
kubectl get clusterrolebindings | grep Top Dog
```

## 📊 Events & Debugging

```powershell
# Watch events in real-time
kubectl get events -n Top Dog -w

# Get events with details
kubectl describe events -n Top Dog

# Get pod description (shows events at bottom)
kubectl describe pod backend-PODNAME -n Top Dog
```

## 🔄 Image Management

```powershell
# Rebuild and push backend image
cd c:\Quellum-topdog-ide
docker build -t Top Dog-backend:v1.0.0 backend/
docker tag Top Dog-backend:v1.0.0 ghcr.io/easttennesseecc-star/Top Dog-backend:v1.0.0
docker push ghcr.io/easttennesseecc-star/Top Dog-backend:v1.0.0

# Force image pull on next deployment
kubectl patch deployment backend -n Top Dog -p "{\"spec\":{\"template\":{\"metadata\":{\"annotations\":{\"date\":\"`date +%s`\"}}}}}"

# Or just restart pods
kubectl delete pods -n Top Dog -l app=backend --force --grace-period=0
```

## 📊 Metrics & Performance

```powershell
# Get pod resource usage
kubectl top pods -n Top Dog

# Get node resource usage
kubectl top nodes

# Get HPA metrics
kubectl get hpa -n Top Dog -w
```

## 🚀 One-Liners

```powershell
# Full deployment check
kubectl get all -n Top Dog

# Everything with details
kubectl get all -n Top Dog -o wide

# Pod status summary
kubectl get pods -n Top Dog --no-headers | awk '{print $3}' | sort | uniq -c

# Quick health check
kubectl get pods -n Top Dog -l app=backend -o jsonpath='{.items[*].status.conditions[?(@.type=="Ready")].status}'

# Watch pod startup
kubectl get pods -n Top Dog -l app=backend -w
```

## 🎯 Common Troubleshooting

```powershell
# Pod won't start - check logs
kubectl logs -n Top Dog backend-PODNAME --previous

# Pod keeps restarting - check events
kubectl describe pod backend-PODNAME -n Top Dog

# CrashLoopBackOff - get full logs
kubectl logs -n Top Dog backend-PODNAME --all-containers=true

# Image pull failed - check pull secret
kubectl get secret ghcr-secret -n Top Dog -o yaml

# Network issues - test from pod
kubectl exec -n Top Dog backend-PODNAME -- ping postgres
kubectl exec -n Top Dog backend-PODNAME -- curl -v http://backend:8000/health

# DNS issues - check services
kubectl get svc -n Top Dog
kubectl exec -n Top Dog backend-PODNAME -- nslookup postgres
```

---

## Current Deployment Info

**LoadBalancer External IP**: `134.199.134.151`  
**Namespace**: `Top Dog`  
**Backend Image**: `ghcr.io/easttennesseecc-star/Top Dog-backend:v1.0.0`  
**Frontend Image**: `ghcr.io/easttennesseecc-star/Top Dog-frontend:v1.0.0`  
**Backend Service**: `backend:8000`  
**Frontend Service**: `frontend:3000`  
**Database Service**: `postgres:5432`  

---

**Last Updated**: November 1, 2025, 20:30 UTC
