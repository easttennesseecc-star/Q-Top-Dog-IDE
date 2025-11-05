# ⚡ KUBERNETES DEPLOYMENT QUICK-START (FOR AUTO-SCALING)

**Your 3-Step Journey from Code to Enterprise Production**

---

## 🚀 STEP 1: PREPARE DOCKER IMAGES (1 hour)

### Command Checklist:

```bash
# 1. Build frontend image
cd frontend
docker build -t your-registry/Top Dog-frontend:v1.0.0 .
docker push your-registry/Top Dog-frontend:v1.0.0

# 2. Build backend image
cd ../backend
docker build -t your-registry/Top Dog-backend:v1.0.0 .
docker push your-registry/Top Dog-backend:v1.0.0

# 3. Verify images
docker images | grep Top Dog
```

**Result:** Two images in your registry, ready to deploy ✅

---

## 🎯 STEP 2: DEPLOY TO KUBERNETES (2 hours)

### Sequential Deployment:

```bash
# 1. Create namespace
kubectl create namespace Top Dog

# 2. Create ConfigMap (edit values first!)
kubectl create configmap Top Dog-config \
  --from-literal=ENVIRONMENT=production \
  --from-literal=FRONTEND_URL=https://Top Dog.com \
  --from-literal=BACKEND_URL=https://api.Top Dog.com \
  -n Top Dog

# 3. Create Secrets (CRITICAL: Use sealed-secrets in production!)
kubectl create secret generic Top Dog-secrets \
  --from-literal=DATABASE_PASSWORD='<your-secure-password>' \
  --from-literal=STRIPE_SECRET_KEY='sk_live_<your-key>' \
  --from-literal=STRIPE_WEBHOOK_SECRET='whsec_live_<your-secret>' \
  -n Top Dog

# 4. Deploy PostgreSQL
kubectl apply -f k8s/03-postgresql.yaml

# 5. Wait for database (5 min)
kubectl wait --for=condition=ready pod -l app=postgres -n Top Dog --timeout=300s

# 6. Deploy backend with auto-scaling
kubectl apply -f k8s/04-backend.yaml

# 7. Deploy frontend with auto-scaling
kubectl apply -f k8s/05-frontend.yaml

# 8. Deploy ingress and SSL
kubectl apply -f k8s/06-ingress.yaml
kubectl apply -f k8s/07-certificate.yaml

# 9. Verify everything
kubectl get all -n Top Dog
```

**Expected Output:**
```
✅ 2 backend pods running
✅ 2 frontend pods running
✅ 1 postgres pod running
✅ 3 services created
✅ 1 ingress with SSL
```

---

## 📊 STEP 3: VERIFY & MONITOR (30 min)

### Health Checks:

```bash
# Check all pods are running
kubectl get pods -n Top Dog
# Expected: All READY 1/1, STATUS Running

# Check services
kubectl get svc -n Top Dog
# Expected: 3 services, all have CLUSTER-IP

# Check ingress
kubectl get ingress -n Top Dog
# Expected: All hosts listed, STATUS: Active

# Check certificates
kubectl get certificate -n Top Dog
# Expected: READY True

# Check HPA
kubectl get hpa -n Top Dog
# Expected: Both HPAs showing replicas

# View logs
kubectl logs -f deployment/Top Dog-backend -n Top Dog
# Expected: No errors, health checks passing
```

### Test Application:

```bash
# Once DNS is updated to point to cluster:
curl https://Top Dog.com
# Expected: HTML response from frontend

curl https://api.Top Dog.com/health
# Expected: {"status": "healthy"}

# Test database connection
kubectl exec -it postgres-0 -n Top Dog -- \
  psql -U qide_user -d qide_prod -c "SELECT 1"
# Expected: Returns 1
```

---

## 🎬 TRAFFIC SPIKE TEST (Auto-Scaling Verification)

### Load Test Command:

```bash
# Install ab tool
sudo apt-get install apache2-utils

# Run load test (10k requests, 100 concurrent)
ab -n 10000 -c 100 https://Top Dog.com

# In another terminal, watch pods scale:
watch -n 2 'kubectl get pods -n Top Dog && echo "---" && kubectl get hpa -n Top Dog'
```

### Expected Behavior:

```
BEFORE LOAD:
├─ 2 backend pods @ 10% CPU
├─ 2 frontend pods @ 5% CPU
└─ Response time: 50ms

DURING LOAD (30 seconds):
├─ 2 → 4 → 6 pods automatically added
├─ CPU normalized to ~70-75%
├─ Response time: 100-200ms
└─ Zero errors

AFTER LOAD:
├─ Pods scale back down
├─ CPU drops below 70%
├─ Stabilizes to 2-4 pods
└─ Ready for next spike
```

---

## 🔄 CONTINUOUS UPDATES (Zero Downtime)

### Deploy New Version:

```bash
# 1. Build and push new image
docker build -t your-registry/Top Dog-backend:v1.0.1 backend/
docker push your-registry/Top Dog-backend:v1.0.1

# 2. Update deployment
kubectl set image deployment/Top Dog-backend \
  backend=your-registry/Top Dog-backend:v1.0.1 \
  -n Top Dog --record

# 3. Monitor rollout
kubectl rollout status deployment/Top Dog-backend -n Top Dog

# 4. If needed, rollback
kubectl rollout undo deployment/Top Dog-backend -n Top Dog
```

**Result:** Users don't notice any downtime! ✅

---

## 📈 SCALING REFERENCE

### Current Configuration:

```yaml
Backend:
├─ Min replicas: 2
├─ Max replicas: 10
├─ CPU threshold: 75%
├─ Memory threshold: 80%
└─ Scale time: 15 seconds

Frontend:
├─ Min replicas: 2
├─ Max replicas: 10
├─ CPU threshold: 70%
├─ Memory threshold: 80%
└─ Scale time: 15 seconds
```

### Adjust Scaling (Optional):

```bash
# Increase max replicas for backend
kubectl patch hpa Top Dog-backend-hpa -n Top Dog \
  -p '{"spec":{"maxReplicas":20}}'

# Adjust CPU threshold
kubectl patch hpa Top Dog-backend-hpa -n Top Dog \
  --type='json' \
  -p='[{"op": "replace", "path": "/spec/metrics/0/resource/target/averageUtilization", "value":80}]'

# View current settings
kubectl get hpa Top Dog-backend-hpa -n Top Dog -o yaml
```

---

## 💾 BACKUP DATABASE

### Create Backup:

```bash
# Backup to file
kubectl exec postgres-0 -n Top Dog -- \
  pg_dump -U qide_user qide_prod > backup-$(date +%Y%m%d-%H%M%S).sql

# Verify backup
ls -lh backup-*.sql

# Test restore (to test database)
kubectl exec -it postgres-0 -n Top Dog -- \
  createdb -U qide_user qide_prod_test

kubectl exec postgres-0 -n Top Dog -- \
  psql -U qide_user qide_prod_test < backup-20251101-120000.sql
```

### Restore Database:

```bash
# WARNING: This will overwrite existing data!
kubectl exec postgres-0 -n Top Dog -- \
  psql -U qide_user qide_prod < backup-20251101-120000.sql
```

---

## 🚨 EMERGENCY TROUBLESHOOTING

### Issue: Pods not starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n Top Dog

# Check logs
kubectl logs <pod-name> -n Top Dog

# Common fixes
# 1. Check image availability
kubectl get events -n Top Dog --sort-by='.lastTimestamp'

# 2. Check resource availability
kubectl top nodes

# 3. Check PVC status
kubectl get pvc -n Top Dog
```

### Issue: Application not responding

```bash
# Check services
kubectl get svc -n Top Dog

# Check endpoints
kubectl get endpoints -n Top Dog

# Check ingress
kubectl describe ingress Top Dog-ingress -n Top Dog

# Test from inside cluster
kubectl exec -it deployment/Top Dog-backend -n Top Dog -- \
  curl http://localhost:8000/health
```

### Issue: Database connection failing

```bash
# Check database pod
kubectl get pod postgres-0 -n Top Dog

# Check logs
kubectl logs postgres-0 -n Top Dog

# Verify credentials
kubectl get secret Top Dog-secrets -n Top Dog -o yaml

# Test connection
kubectl exec postgres-0 -n Top Dog -- \
  psql -U qide_user -d qide_prod -c "SELECT 1"
```

---

## 📊 MONITORING DASHBOARD

### View Real-Time Metrics:

```bash
# CPU and memory usage per pod
kubectl top pods -n Top Dog

# Node resource usage
kubectl top nodes

# Watch pod scaling
watch kubectl get pods -n Top Dog

# Watch HPA status
watch kubectl get hpa -n Top Dog

# Stream logs from all backend pods
kubectl logs -f deployment/Top Dog-backend -n Top Dog --all-containers
```

### Setup Prometheus (Advanced):

```bash
# Install kube-prometheus-stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace

# Access Grafana
kubectl port-forward -n monitoring svc/kube-prometheus-grafana 3000:80
# Open: http://localhost:3000
# Login: admin / prom-operator
```

---

## 🎯 COST OPTIMIZATION

### Monitor Resource Usage:

```bash
# Total requests/CPU/Memory
kubectl top pods -n Top Dog --containers

# Identify resource hogs
kubectl top pods -n Top Dog --sort-by=memory

# Check if scaling is working
kubectl get hpa -n Top Dog --watch
```

### Right-size Resources:

```bash
# If CPU is under 30% consistently, reduce requests
kubectl patch deployment Top Dog-backend -n Top Dog \
  -p '{"spec":{"template":{"spec":{"containers":[{"name":"backend","resources":{"requests":{"cpu":"250m"}}}]}}}}'

# If memory spikes, increase limits
kubectl patch deployment Top Dog-backend -n Top Dog \
  -p '{"spec":{"template":{"spec":{"containers":[{"name":"backend","resources":{"limits":{"memory":"2Gi"}}}]}}}}'
```

---

## 📋 DAILY CHECKLIST

### Daily Tasks:

- [ ] Check pod status: `kubectl get pods -n Top Dog`
- [ ] Review logs for errors: `kubectl logs -f deployment/Top Dog-backend -n Top Dog`
- [ ] Monitor resource usage: `kubectl top pods -n Top Dog`
- [ ] Check certificate expiry: `kubectl get certificate -n Top Dog`
- [ ] Verify ingress health: `kubectl describe ingress -n Top Dog`
- [ ] Test health endpoints: `curl https://api.Top Dog.com/health`

### Weekly Tasks:

- [ ] Review HPA metrics: `kubectl get hpa -n Top Dog`
- [ ] Check database backups
- [ ] Review Prometheus metrics
- [ ] Update Docker images if needed
- [ ] Test failover procedures

### Monthly Tasks:

- [ ] Review and adjust resource limits
- [ ] Test disaster recovery
- [ ] Update Kubernetes version (if available)
- [ ] Review security policies
- [ ] Optimize costs

---

## 🎉 SUCCESS INDICATORS

### Your System is Working When:

✅ All pods READY 1/1 and STATUS Running  
✅ Ingress shows all hosts Active  
✅ Certificates show READY True  
✅ HPA metrics updating  
✅ Health endpoints responding  
✅ Database queries completing  
✅ Logs showing normal operations  
✅ Load test shows scaling behavior  
✅ Zero 5xx errors in logs  
✅ Response times under 500ms  

---

## 📚 KEY REFERENCES

| Command | Purpose |
|---------|---------|
| `kubectl get all -n Top Dog` | See everything |
| `kubectl logs -f POD_NAME -n Top Dog` | Stream logs |
| `kubectl describe pod POD_NAME -n Top Dog` | Debug pod |
| `kubectl exec -it POD_NAME -n Top Dog -- bash` | Access pod shell |
| `kubectl port-forward svc/SERVICE 8000:8000 -n Top Dog` | Local access |
| `kubectl set image deployment/NAME IMAGE` | Update version |
| `kubectl scale deployment NAME --replicas=5 -n Top Dog` | Manual scale |
| `kubectl delete pod POD_NAME -n Top Dog` | Force restart |

---

## 🚀 YOU'RE LIVE!

With Kubernetes auto-scaling, you're now:
- ✅ Handling unlimited traffic spikes
- ✅ Running zero-downtime deployments
- ✅ Getting enterprise-grade reliability
- ✅ Paying only for what you use
- ✅ Ready to scale to millions of users

**Congratulations! Top Dog is now production-ready at enterprise scale!** 🎉

