# 🚀 KUBERNETES DEPLOYMENT GUIDE

**Status:** K8s manifests created and ready for deployment  
**Cluster:** do-atl1-top-dog-ide (3 nodes, v1.33.1)  
**Namespace:** Top Dog (production)

---

## 📋 Files Created

```
k8s/
├── 00-namespace.yaml          ✅ Namespace (Top Dog)
├── 01-configmap.yaml          ✅ Configuration (non-sensitive)
├── 02-secrets.yaml            ⚠️  SECRETS - NEEDS VALUES (see below)
├── 03-postgresql.yaml         ✅ Database (StatefulSet + PVC)
├── 04-backend.yaml            ✅ FastAPI (Deployment + HPA)
├── 05-frontend.yaml           ✅ React (Deployment + HPA)
├── 06-ingress.yaml            ✅ Ingress (nginx + TLS)
└── 07-certificate.yaml        ✅ SSL/TLS (Let's Encrypt)
```

---

## ⚠️ CRITICAL: Update secrets BEFORE deploying

Edit `k8s/02-secrets.yaml` and replace ALL `CHANGE_ME_*` values:

```yaml
# Required database password
DATABASE_PASSWORD: "your-secure-password-here-32-chars-min"

# Required Stripe keys (get from https://dashboard.stripe.com/apikeys)
STRIPE_SECRET_KEY: "sk_live_YOUR_SECRET_KEY_HERE"
STRIPE_WEBHOOK_SECRET: "whsec_live_YOUR_WEBHOOK_SECRET_HERE"
STRIPE_PUBLISHABLE_KEY: "pk_live_YOUR_PUBLIC_KEY_HERE"

# Stripe Price IDs (from Stripe Products page)
STRIPE_PRICE_ID_PRO: "price_1P5Yz..."
STRIPE_PRICE_ID_TEAM: "price_1P5Za..."
STRIPE_PRICE_ID_ENTERPRISE: "price_1P5Zb..."

# JWT Secret (generate: openssl rand -base64 32)
JWT_SECRET: "your-random-jwt-secret-here"

# Optional LLM keys (if using AI features)
OPENAI_API_KEY: "sk-..." or leave as CHANGE_ME
ANTHROPIC_API_KEY: "sk-..." or leave as CHANGE_ME
GOOGLE_API_KEY: "..." or leave as CHANGE_ME
```

---

## 🔐 Prerequisites Before Deployment

Before running `kubectl apply`, ensure you have:

- [ ] **Docker images pushed to registry** ← WAITING ON: New DigitalOcean API token
  - [ ] `registry.digitalocean.com/Top Dog-registry/Top Dog-frontend:v1.0.0`
  - [ ] `registry.digitalocean.com/Top Dog-registry/Top Dog-backend:v1.0.0`

- [ ] **Secrets updated in `k8s/02-secrets.yaml`**
  - [ ] DATABASE_PASSWORD (32+ characters, secure)
  - [ ] STRIPE_SECRET_KEY (sk_live_...)
  - [ ] STRIPE_WEBHOOK_SECRET (whsec_live_...)
  - [ ] STRIPE_PUBLISHABLE_KEY (pk_live_...)
  - [ ] STRIPE_PRICE_IDs (from Stripe dashboard)
  - [ ] JWT_SECRET (random, 32+ characters)

- [ ] **Kubernetes cluster verified**
  ```powershell
  kubectl cluster-info
  kubectl get nodes
  # Should show: 3 nodes in Ready status
  ```

- [ ] **ingress-nginx controller installed**
  ```powershell
  kubectl get ns | Select-String ingress-nginx
  # Should show: ingress-nginx namespace
  ```

- [ ] **cert-manager installed** (for SSL certificates)
  ```powershell
  kubectl get ns | Select-String cert-manager
  # Should show: cert-manager namespace
  ```

- [ ] **DigitalOcean block storage configured**
  ```powershell
  kubectl get storageclass
  # Should show: do-block-storage
  ```

---

## 🚀 DEPLOYMENT STEPS

### Step 1: Verify Prerequisites

```powershell
# Check K8s connection
kubectl cluster-info

# Check nodes
kubectl get nodes

# Verify namespaces
kubectl get ns | Select-String "ingress-nginx|cert-manager"
```

### Step 2: Update Secrets File

Edit `k8s/02-secrets.yaml` with your actual values:

```powershell
# Open the file
code k8s/02-secrets.yaml

# Replace all CHANGE_ME_ values with your actual credentials
```

### Step 3: Create Namespace

```powershell
kubectl apply -f k8s/00-namespace.yaml

# Verify
kubectl get namespace Top Dog
```

### Step 4: Create ConfigMap

```powershell
kubectl apply -f k8s/01-configmap.yaml

# Verify
kubectl get configmap -n Top Dog
kubectl describe configmap Top Dog-config -n Top Dog
```

### Step 5: Create Secrets

```powershell
kubectl apply -f k8s/02-secrets.yaml

# Verify
kubectl get secret -n Top Dog
kubectl describe secret Top Dog-secrets -n Top Dog
# NOTE: Values are hidden (stored encrypted in etcd)
```

### Step 6: Deploy PostgreSQL

```powershell
kubectl apply -f k8s/03-postgresql.yaml

# Monitor startup
kubectl get pods -n Top Dog
kubectl logs -f deployment/postgres -n Top Dog

# Wait until: postgres pods show "Running" (may take 1-2 minutes)
```

### Step 7: Deploy Backend

```powershell
kubectl apply -f k8s/04-backend.yaml

# Monitor startup
kubectl get pods -n Top Dog -l app=backend
kubectl logs -f deployment/backend -n Top Dog

# Check health endpoint (once running)
kubectl port-forward svc/backend 8000:8000 -n Top Dog
# Then: curl http://localhost:8000/health
```

### Step 8: Deploy Frontend

```powershell
kubectl apply -f k8s/05-frontend.yaml

# Monitor startup
kubectl get pods -n Top Dog -l app=frontend
kubectl logs -f deployment/frontend -n Top Dog

# Check health endpoint (once running)
kubectl port-forward svc/frontend 3000:3000 -n Top Dog
# Then: curl http://localhost:3000
```

### Step 9: Deploy Ingress

```powershell
kubectl apply -f k8s/06-ingress.yaml

# Verify ingress created
kubectl get ingress -n Top Dog
kubectl describe ingress Top Dog-ingress -n Top Dog

# Watch for ingress IP (may take 1-2 minutes)
kubectl get ingress -n Top Dog -w
```

### Step 10: Deploy SSL Certificates

```powershell
kubectl apply -f k8s/07-certificate.yaml

# Monitor certificate issuance
kubectl get certificate -n Top Dog
kubectl describe certificate Top Dog-cert -n Top Dog

# Watch for "Ready" status (may take 1-2 minutes)
kubectl get certificate -n Top Dog -w
```

---

## ✅ VERIFICATION CHECKLIST

After deployment, verify everything is working:

```powershell
# 1. Check all namespaces are created
kubectl get namespace | Select-String Top Dog

# 2. Check all pods are running
kubectl get pods -n Top Dog
# Expected: postgres, backend (2), frontend (2) all "Running"

# 3. Check services
kubectl get svc -n Top Dog
# Expected: backend, frontend, postgres

# 4. Check deployments
kubectl get deployment -n Top Dog
# Expected: backend, frontend (all should show "2/2 Ready")

# 5. Check ingress
kubectl get ingress -n Top Dog
# Expected: Top Dog-ingress with ingress IP/hostname

# 6. Check certificates
kubectl get certificate -n Top Dog
# Expected: Top Dog-cert with "Ready" status

# 7. Check HPA status
kubectl get hpa -n Top Dog
# Expected: backend-hpa, frontend-hpa both scaling properly

# 8. Test backend health
kubectl port-forward svc/backend 8000:8000 -n Top Dog &
curl http://localhost:8000/health
# Expected: {"status": "ok"}

# 9. Test frontend
kubectl port-forward svc/frontend 3000:3000 -n Top Dog &
curl http://localhost:3000
# Expected: HTML content (React app)

# 10. Get ingress IP
kubectl get ingress -n Top Dog -o wide
# Expected: Shows IP or hostname
```

---

## 📊 Monitoring Commands

```powershell
# Watch all resources
kubectl get all -n Top Dog -w

# View logs
kubectl logs -f deployment/backend -n Top Dog
kubectl logs -f deployment/frontend -n Top Dog
kubectl logs -f statefulset/postgres -n Top Dog

# Check resource usage
kubectl top nodes
kubectl top pods -n Top Dog

# View events
kubectl get events -n Top Dog --sort-by='.lastTimestamp'

# Port forward for local testing
kubectl port-forward svc/backend 8000:8000 -n Top Dog
kubectl port-forward svc/frontend 3000:3000 -n Top Dog
kubectl port-forward svc/postgres 5432:5432 -n Top Dog
```

---

## 🔧 Troubleshooting

### Pods not starting
```powershell
# Check pod status
kubectl describe pod <pod-name> -n Top Dog

# Check logs for errors
kubectl logs <pod-name> -n Top Dog
kubectl logs <pod-name> -n Top Dog --previous
```

### ImagePullBackOff error
- Images not pushed to registry yet
- Or registry credentials not configured
- Run: `kubectl get secrets -n Top Dog` to verify registry secret

### Ingress not getting IP
- Wait 1-2 minutes for cloud provider to assign IP
- Check ingress controller logs: `kubectl logs -f deployment/ingress-nginx-controller -n ingress-nginx`

### Certificate not issuing
- Check cert-manager logs: `kubectl logs -f deployment/cert-manager -n cert-manager`
- Ensure email in certificate is valid: admin@Top Dog.com
- Wait up to 5 minutes for Let's Encrypt validation

---

## 🌐 DNS Configuration (After Ingress Ready)

Once ingress has an IP address:

1. Get ingress IP:
```powershell
kubectl get ingress -n Top Dog -o wide
# Note the IP or hostname
```

2. Update DNS records (at your registrar):
```
Top Dog.com          → <ingress-ip>
www.Top Dog.com      → <ingress-ip>
api.Top Dog.com      → <ingress-ip>
```

3. Verify DNS:
```powershell
nslookup Top Dog.com
nslookup api.Top Dog.com
```

4. Test endpoints:
```powershell
curl https://Top Dog.com
curl https://api.Top Dog.com/health
```

---

## 📈 Auto-scaling Configuration

Both backend and frontend have HPA configured:

**Backend HPA:**
- Min replicas: 2
- Max replicas: 10
- Scales on: CPU > 70% or Memory > 80%
- Scale-up: Add 1-2 pods per 30 seconds
- Scale-down: Remove 50% of excess pods per 60 seconds

**Frontend HPA:**
- Min replicas: 2
- Max replicas: 10
- Scales on: CPU > 70% or Memory > 80%
- Scale-up: Add 1-2 pods per 30 seconds
- Scale-down: Remove 50% of excess pods per 60 seconds

Monitor autoscaling:
```powershell
kubectl get hpa -n Top Dog -w
kubectl describe hpa backend-hpa -n Top Dog
```

---

## 🚨 Emergency Procedures

### Scale down to zero (disable service)
```powershell
kubectl scale deployment backend --replicas=0 -n Top Dog
kubectl scale deployment frontend --replicas=0 -n Top Dog
```

### Scale back up
```powershell
kubectl scale deployment backend --replicas=2 -n Top Dog
kubectl scale deployment frontend --replicas=2 -n Top Dog
```

### Restart a deployment
```powershell
kubectl rollout restart deployment/backend -n Top Dog
kubectl rollout restart deployment/frontend -n Top Dog
```

### Delete entire namespace (CAREFUL!)
```powershell
kubectl delete namespace Top Dog
# This deletes everything in Top Dog namespace
```

---

## 📞 Next Steps

1. **Get new DigitalOcean API token** (current one invalid)
2. **Push images to registry** (docker push commands)
3. **Update secrets** in `k8s/02-secrets.yaml`
4. **Deploy to Kubernetes** (kubectl apply commands above)
5. **Configure DNS** (point domains to ingress IP)
6. **Verify production** (test endpoints, monitoring)

---

**Ready to deploy!** Follow the steps above in order.

