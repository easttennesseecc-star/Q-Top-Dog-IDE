# ✅ KUBERNETES DEPLOYMENT CHECKLIST

**DigitalOcean Kubernetes Cluster: do-atl1-top-dog-ide**  
**Cluster Status: ✅ VERIFIED**  
**Nodes: 3x Ready | Version: 1.33.1**

---

## 🎯 PRE-DEPLOYMENT CHECKLIST (Do This First)

### Infrastructure Requirements
- [x] Kubernetes cluster: `do-atl1-top-dog-ide` (verified)
- [x] 3 nodes running and healthy (verified)
- [x] kubectl client: v1.34.1 (verified)
- [ ] kubectl context set to: `do-atl1-top-dog-ide` (verify: `kubectl config current-context`)
- [ ] DigitalOcean Container Registry (DOCR) set up
- [ ] Docker images built and in registry

### Application Requirements
- [x] Docker images built locally:
  - [x] Frontend image: `docker images | grep Top Dog-frontend` (216MB)
  - [x] Backend image: `docker images | grep Top Dog-backend` (735MB)
- [x] Images size verified:
  - [x] Frontend: 216MB ✅
  - [x] Backend: 735MB ✅
- [ ] Images pushed to DigitalOcean Container Registry (DOCR) ← NEXT STEP

### Configuration Requirements
- [ ] Domain: `Top Dog.com` + `api.Top Dog.com` ready
- [ ] DNS records updated (see [DNS Setup](#dns-setup))
- [ ] SSL certificates configured (Let's Encrypt)
- [ ] Stripe API keys ready:
  - [ ] `STRIPE_SECRET_KEY` (sk_live_...)
  - [ ] `STRIPE_WEBHOOK_SECRET` (whsec_live_...)
  - [ ] `STRIPE_PUBLIC_KEY` (pk_live_...)
- [ ] PostgreSQL password generated and saved securely
- [ ] Environment variables documented

### Kubernetes Files Ready
- [ ] `k8s/00-namespace.yaml` (create Top Dog namespace)
- [ ] `k8s/01-configmap.yaml` (environment variables)
- [ ] `k8s/02-secrets.yaml` (API keys, passwords)
- [ ] `k8s/03-postgresql.yaml` (database deployment)
- [ ] `k8s/04-backend.yaml` (FastAPI deployment + HPA)
- [ ] `k8s/05-frontend.yaml` (React deployment + HPA)
- [ ] `k8s/06-ingress.yaml` (routing to domains)
- [ ] `k8s/07-certificate.yaml` (SSL/TLS)

---

## 📋 STEP-BY-STEP DEPLOYMENT

### Phase 1: Prepare (5 minutes)

```powershell
# Verify cluster connection
kubectl cluster-info
# Should show: Kubernetes control plane is running...

# Verify context
kubectl config current-context
# Should show: do-atl1-top-dog-ide

# Verify nodes
kubectl get nodes
# Should show: 3 nodes in Ready status

# Verify DOCR access
docker pull registry.digitalocean.com/your-project-name/Top Dog-frontend:v1.0.0
# Should succeed (or show image not found error only)
```

### Phase 2: Create Namespace (2 minutes)

```powershell
# Create namespace
kubectl create namespace Top Dog

# Verify namespace
kubectl get namespace Top Dog
# Should show: Top Dog  Active

# Set default namespace (optional, but recommended)
kubectl config set-context --current --namespace=Top Dog
```

### Phase 3: Configure Secrets & ConfigMaps (3 minutes)

#### Option A: Using kubectl commands (Quick, for testing)

```powershell
# ConfigMap - Non-sensitive configuration
kubectl create configmap Top Dog-config `
  --from-literal=ENVIRONMENT=production `
  --from-literal=FRONTEND_URL=https://Top Dog.com `
  --from-literal=BACKEND_URL=https://api.Top Dog.com `
  -n Top Dog

# Secrets - Sensitive data (USE STRONG VALUES!)
kubectl create secret generic Top Dog-secrets `
  --from-literal=DATABASE_PASSWORD='your-secure-password-32-chars-min' `
  --from-literal=STRIPE_SECRET_KEY='sk_live_your_actual_key' `
  --from-literal=STRIPE_WEBHOOK_SECRET='whsec_live_your_webhook_secret' `
  -n Top Dog

# Verify
kubectl get configmap -n Top Dog
kubectl get secrets -n Top Dog
```

#### Option B: Using YAML files (Recommended for production)

See: `k8s/01-configmap.yaml` and `k8s/02-secrets.yaml`

```powershell
# Create from files
kubectl apply -f k8s/01-configmap.yaml
kubectl apply -f k8s/02-secrets.yaml
```

### Phase 4: Deploy Database (5 minutes)

```powershell
# Deploy PostgreSQL
kubectl apply -f k8s/03-postgresql.yaml

# Watch database startup
kubectl get pods -n Top Dog
# Wait for: postgres-0 in Running status

# Wait for database to be ready (max 300 seconds)
kubectl wait --for=condition=ready pod -l app=postgres -n Top Dog --timeout=300s

# Verify database
kubectl logs -n Top Dog -l app=postgres --tail=20
```

### Phase 5: Deploy Backend (10 minutes)

```powershell
# Deploy backend
kubectl apply -f k8s/04-backend.yaml

# Watch deployment
kubectl get pods -n Top Dog

# Expected: 2 backend pods (deployment replicas)
# Status: ContainerCreating → Running

# Monitor startup (takes 3-5 minutes)
kubectl logs -n Top Dog -l app=backend --tail=50 -f

# Verify backend is ready
kubectl get deployment Top Dog-backend -n Top Dog
# Should show: DESIRED 2, CURRENT 2, READY 2
```

### Phase 6: Deploy Frontend (10 minutes)

```powershell
# Deploy frontend
kubectl apply -f k8s/05-frontend.yaml

# Watch deployment
kubectl get pods -n Top Dog

# Expected: 2 frontend pods (deployment replicas)
# Status: ContainerCreating → Running

# Monitor startup (takes 2-3 minutes)
kubectl logs -n Top Dog -l app=frontend --tail=50 -f

# Verify frontend is ready
kubectl get deployment Top Dog-frontend -n Top Dog
# Should show: DESIRED 2, CURRENT 2, READY 2
```

### Phase 7: Configure Ingress & SSL (10 minutes)

```powershell
# Deploy ingress (routes HTTP traffic)
kubectl apply -f k8s/06-ingress.yaml

# Deploy SSL certificate (Let's Encrypt)
kubectl apply -f k8s/07-certificate.yaml

# Watch certificate issuance (takes 1-5 minutes)
kubectl get certificate -n Top Dog
# Status should change from Pending → True

# Verify ingress is active
kubectl get ingress -n Top Dog
# Should show: CLASS ingress-nginx, HOSTS Top Dog.com/api.Top Dog.com, STATUS Active
```

### Phase 8: Configure DNS (2 minutes)

Update DNS records to point to DigitalOcean Kubernetes ingress:

```
Top Dog.com          CNAME  <ingress-ip-or-hostname>.ondigitalocean.app
api.Top Dog.com      CNAME  <ingress-ip-or-hostname>.ondigitalocean.app
```

Get ingress IP/hostname:

```powershell
kubectl get ingress -n Top Dog
# Look for INGRESS column value
```

---

## ✅ VERIFICATION CHECKLIST

### After Deployment

```powershell
# Get all resources
kubectl get all -n Top Dog

# Expected output should show:
# - 2 backend pods
# - 2 frontend pods
# - 1 postgres pod
# - 3 services (backend, frontend, postgres)
# - 1 ingress
# - 2 replica sets
# - 2 deployments
```

### Health Checks

```powershell
# 1. Verify all pods are running
kubectl get pods -n Top Dog
# All pods should have: READY 1/1, STATUS Running

# 2. Check pod events
kubectl describe pod <pod-name> -n Top Dog
# Look for: Status Phase: Running, No errors

# 3. Check service connectivity
kubectl get svc -n Top Dog
# All services should have: CLUSTER-IP and PORT(S)

# 4. Test backend health
kubectl exec -it <backend-pod-name> -n Top Dog -- curl http://localhost:8000/health
# Expected: {"status": "healthy"}

# 5. View logs
kubectl logs <pod-name> -n Top Dog
# Should show: Application started, listening on port...

# 6. Check ingress status
kubectl get ingress -n Top Dog -o wide
# Should show: Hosts listed, INGRESS IP/HOSTNAME, STATUS Active
```

### Network Connectivity Tests

```powershell
# 1. Test internal connectivity (backend to postgres)
kubectl exec -it <backend-pod-name> -n Top Dog -- psql -h postgres -U postgres -d Top Dog -c "SELECT 1"
# Expected: Successful connection

# 2. Test internal DNS
kubectl run -it --rm debug --image=busybox --restart=Never -n Top Dog -- nslookup Top Dog-backend
# Expected: NSLOOKUP successful, IP address returned

# 3. Test external access (after DNS update)
curl https://Top Dog.com
# Expected: HTTP 200, page loads

curl https://api.Top Dog.com/health
# Expected: {"status": "healthy"}
```

### Auto-Scaling Verification

```powershell
# Check HPA status
kubectl get hpa -n Top Dog
# Expected: 2 HPAs (backend + frontend), REFERENCE Deployment, TARGETS <current>/<target>

# Watch HPA during load test
kubectl get hpa -n Top Dog --watch
# Should show: REPLICAS scaling up as load increases

# View HPA details
kubectl describe hpa Top Dog-backend-hpa -n Top Dog
# Should show: Metrics, Current Replicas, Desired Replicas, Events
```

---

## 🔧 TROUBLESHOOTING

### Issue: Pods stuck in `Pending` status

```powershell
# Cause: Insufficient resources or image pull errors

# Check events
kubectl describe pod <pod-name> -n Top Dog

# Check node resources
kubectl top nodes

# Check if nodes have space
kubectl get nodes --resource-capacity
```

**Solution:**
- Scale up: Increase DO Kubernetes pool size
- Reduce: Lower resource requests in deployment YAML
- Image pull: Verify registry credentials in pull-secrets

### Issue: Pods in `CrashLoopBackOff`

```powershell
# Cause: Application crash or config error

# Check logs
kubectl logs <pod-name> -n Top Dog --previous
# Look for error messages in logs

# Check environment
kubectl exec <pod-name> -n Top Dog -- env | grep STRIPE
# Verify all env vars are set
```

**Solution:**
- Fix application error in code
- Verify secrets/configmaps are correct
- Check resource limits aren't too restrictive

### Issue: Ingress not routing traffic

```powershell
# Cause: DNS not updated, cert not ready, or ingress misconfigured

# Check cert status
kubectl describe certificate Top Dog-cert -n Top Dog
# Status should be: True, Reason: Ready

# Check ingress rules
kubectl get ingress -n Top Dog -o yaml
# Verify: hosts, backend service names, ports

# Test local DNS resolution
kubectl exec -it <any-pod> -n Top Dog -- nslookup Top Dog.com
# Should resolve to ingress IP
```

**Solution:**
- Wait for certificate (5-10 minutes)
- Update DNS records
- Verify ingress YAML rules

### Issue: Cannot connect to database

```powershell
# Cause: Database not ready, credentials wrong, or network issue

# Check postgres pod
kubectl get pod -n Top Dog -l app=postgres
# Must be in Running status

# Test database connection
kubectl exec -it <backend-pod> -n Top Dog -- psql -h postgres -U postgres -d postgres -c "SELECT 1"

# Check postgres logs
kubectl logs -n Top Dog -l app=postgres --tail=50

# Check service DNS
kubectl exec -it <backend-pod> -n Top Dog -- nslookup postgres
# Should resolve to service IP
```

**Solution:**
- Wait for database pod startup
- Verify DATABASE_PASSWORD secret is correct
- Check postgres service exists: `kubectl get svc postgres -n Top Dog`

---

## 📊 MONITORING & METRICS

### View Resource Usage

```powershell
# CPU and memory by node
kubectl top nodes

# CPU and memory by pod
kubectl top pods -n Top Dog

# Detailed pod metrics
kubectl describe node <node-name>
```

### View Events

```powershell
# Recent cluster events
kubectl get events -n Top Dog --sort-by='.lastTimestamp'

# Watch real-time events
kubectl get events -n Top Dog --watch
```

### Export Logs

```powershell
# Export backend logs
kubectl logs -n Top Dog -l app=backend > backend-logs.txt

# Export frontend logs
kubectl logs -n Top Dog -l app=frontend > frontend-logs.txt

# Stream logs in real-time
kubectl logs -n Top Dog -l app=backend -f
```

---

## 🚀 NEXT STEPS

### Immediately After Deployment

- [ ] Verify all services responding at their URLs
- [ ] Test Stripe webhook: `POST https://api.Top Dog.com/stripe/webhook`
- [ ] Test user signup/login flow
- [ ] Check metrics in DigitalOcean console

### First Week

- [ ] Monitor pods for stability (no crashes)
- [ ] Review logs for errors
- [ ] Test auto-scaling under load
- [ ] Verify backups are running

### Production Hardening

- [ ] Set up monitoring (Prometheus, Grafana)
- [ ] Configure alerts (PagerDuty, Slack)
- [ ] Set up log aggregation (Loki, CloudWatch)
- [ ] Regular security scans
- [ ] Backup strategy validation

---

## 📞 SUPPORT & DEBUGGING

### Useful Commands Reference

```powershell
# General info
kubectl cluster-info
kubectl get nodes
kubectl get events -n Top Dog

# Deployments
kubectl get deployments -n Top Dog
kubectl describe deployment Top Dog-backend -n Top Dog
kubectl logs -n Top Dog -l app=backend

# Pods
kubectl get pods -n Top Dog
kubectl exec -it <pod-name> -n Top Dog -- /bin/bash
kubectl port-forward <pod-name> 8000:8000 -n Top Dog

# Services
kubectl get svc -n Top Dog
kubectl describe svc Top Dog-backend -n Top Dog

# Ingress
kubectl get ingress -n Top Dog
kubectl describe ingress Top Dog-ingress -n Top Dog

# Delete/Cleanup
kubectl delete namespace Top Dog  # Deletes everything
kubectl delete pod <pod-name> -n Top Dog  # Restart pod
kubectl rollout restart deployment/Top Dog-backend -n Top Dog
```

### Emergency Recovery

```powershell
# View recent changes (last 5 actions)
kubectl rollout history deployment/Top Dog-backend -n Top Dog

# Rollback to previous version
kubectl rollout undo deployment/Top Dog-backend -n Top Dog

# Manually scale
kubectl scale deployment Top Dog-backend --replicas=4 -n Top Dog
```

---

## ✅ FINAL CHECKLIST

Before declaring production ready:

- [ ] All pods running and healthy
- [ ] Services accessible at their DNS names
- [ ] SSL certificates valid
- [ ] Database connected and migrated
- [ ] Stripe webhooks receiving events
- [ ] Auto-scaling responding to load
- [ ] Monitoring and logging active
- [ ] Backups configured
- [ ] Rollback procedure tested
- [ ] Team trained on kubectl commands

---

**Status: READY FOR DEPLOYMENT** ✅

**Current Cluster:** DigitalOcean `do-atl1-top-dog-ide`  
**Kubernetes Version:** 1.33.1  
**Nodes:** 3x Ready  
**Estimated Deployment Time:** 30-45 minutes  

**Next Action:** Follow "STEP-BY-STEP DEPLOYMENT" section above.

---
