# ✅ DEPLOYMENT FINAL CHECKLIST

**Date:** November 1, 2025  
**Status:** 80% Complete - Ready for Final Push

---

## PHASE 1: BUILD & PREPARE ✅ COMPLETE

- [x] Build frontend image (216MB)
- [x] Build backend image (735MB)
- [x] Tag both images for registry
- [x] Fix all build issues (5 obstacles resolved)
- [x] Create k8s/ directory with 8 manifests
- [x] Verify Kubernetes cluster (3 nodes ready)
- [x] Verify ingress-nginx (ready)
- [x] Verify cert-manager (ready)
- [x] Verify block storage (ready)
- [x] Create comprehensive documentation

---

## PHASE 2: BLOCKED ⏳ WAITING FOR ACTION

### Task: Push Images to Registry
**Blocker:** DigitalOcean API token invalid (401 Unauthorized)

**What needs to happen:**
- [ ] Generate new DigitalOcean API token
  - Go to: https://cloud.digitalocean.com/account/api/tokens
  - Create token with "read & write" scope
  - **Copy immediately** (only shown once)
  
- [ ] Share token to proceed

**Time estimate:** 2-3 minutes

---

## PHASE 3: REGISTRY PUSH ⏳ READY AFTER API TOKEN

### Prerequisites
- [x] Images built and tagged locally
- [x] Registry URL configured (registry.digitalocean.com/Top Dog-registry/)
- [ ] Valid DigitalOcean API token ← WAITING

### Commands to Execute
```powershell
# Login
$Token = "YOUR_TOKEN_HERE"
Write-Output $Token | docker login -u unused --password-stdin registry.digitalocean.com

# Push frontend
docker push registry.digitalocean.com/Top Dog-registry/Top Dog-frontend:v1.0.0

# Push backend
docker push registry.digitalocean.com/Top Dog-registry/Top Dog-backend:v1.0.0

# Verify
docker pull registry.digitalocean.com/Top Dog-registry/Top Dog-frontend:v1.0.0
docker pull registry.digitalocean.com/Top Dog-registry/Top Dog-backend:v1.0.0
```

**Time estimate:** 3 minutes  
**Status:** Ready to execute

---

## PHASE 4: UPDATE SECRETS ⏳ READY AFTER PUSH

### File to Update
**File:** `k8s/02-secrets.yaml`

### Values to Replace
- [ ] `DATABASE_PASSWORD` - Secure password (32+ chars)
  - Example: `MyS3cur3Pas5w0rd!@#$%^&*()_+-=[]{}` 
  
- [ ] `STRIPE_SECRET_KEY` - From Stripe dashboard
  - Format: `sk_live_...`
  - Source: https://dashboard.stripe.com/apikeys
  
- [ ] `STRIPE_WEBHOOK_SECRET` - From Stripe webhooks
  - Format: `whsec_live_...`
  - Source: https://dashboard.stripe.com/webhooks
  
- [ ] `STRIPE_PUBLISHABLE_KEY` - From Stripe dashboard
  - Format: `pk_live_...`
  - Source: https://dashboard.stripe.com/apikeys
  
- [ ] `STRIPE_PRICE_ID_PRO` - From Stripe products
  - Format: `price_1P5Yz...`
  - Source: https://dashboard.stripe.com/products
  
- [ ] `STRIPE_PRICE_ID_TEAM` - From Stripe products
  - Format: `price_1P5Za...`
  
- [ ] `STRIPE_PRICE_ID_ENTERPRISE` - From Stripe products
  - Format: `price_1P5Zb...`
  
- [ ] `JWT_SECRET` - Random secure string
  - Generate: `openssl rand -base64 32`
  - Or create a secure random string

### How to Edit
```powershell
code k8s/02-secrets.yaml
# Replace values
# Save (Ctrl+S)
# Close (Ctrl+W)
```

**Time estimate:** 3 minutes  
**Status:** Ready to execute

---

## PHASE 5: KUBERNETES DEPLOYMENT ⏳ READY AFTER SECRETS

### Prerequisites
- [ ] Images pushed to registry
- [ ] Secrets file updated with real values
- [ ] Kubernetes cluster accessible
- [ ] kubectl configured

### Deployment Steps (In Order)

#### Step 1: Create Namespace
```powershell
kubectl apply -f k8s/00-namespace.yaml
kubectl get namespace Top Dog
```
- [ ] Namespace created successfully
- [ ] Status: Active

#### Step 2: Create ConfigMap
```powershell
kubectl apply -f k8s/01-configmap.yaml
kubectl get configmap -n Top Dog
```
- [ ] ConfigMap created
- [ ] Contains environment variables

#### Step 3: Create Secrets
```powershell
kubectl apply -f k8s/02-secrets.yaml
kubectl get secret -n Top Dog
```
- [ ] Secret created
- [ ] Values encrypted in etcd

#### Step 4: Deploy PostgreSQL
```powershell
kubectl apply -f k8s/03-postgresql.yaml
kubectl get pods -n Top Dog -w
# Wait for postgres pod to show "Running"
```
- [ ] Pod running
- [ ] PVC created (10GB)
- [ ] Service created

#### Step 5: Deploy Backend
```powershell
kubectl apply -f k8s/04-backend.yaml
kubectl get pods -n Top Dog -w
# Wait for backend pods to show "Running"
```
- [ ] Deployment created (2 replicas)
- [ ] Pods running
- [ ] Service created
- [ ] HPA created (scales 2-10)

#### Step 6: Deploy Frontend
```powershell
kubectl apply -f k8s/05-frontend.yaml
kubectl get pods -n Top Dog -w
# Wait for frontend pods to show "Running"
```
- [ ] Deployment created (2 replicas)
- [ ] Pods running
- [ ] Service created
- [ ] HPA created (scales 2-10)

#### Step 7: Deploy Ingress
```powershell
kubectl apply -f k8s/06-ingress.yaml
kubectl get ingress -n Top Dog -w
# Wait for IP to be assigned (1-2 minutes)
```
- [ ] Ingress created
- [ ] Has IP/hostname assigned
- [ ] Routes configured:
  - Top Dog.com → frontend:3000
  - api.Top Dog.com → backend:8000

#### Step 8: Deploy SSL Certificates
```powershell
kubectl apply -f k8s/07-certificate.yaml
kubectl get certificate -n Top Dog -w
# Wait for status "Ready"
```
- [ ] Certificate requested
- [ ] Status shows "Ready"
- [ ] TLS secret created

### Verification After Deployment
```powershell
# All pods running
kubectl get pods -n Top Dog
✓ postgres (1 pod)
✓ backend (2 pods)
✓ frontend (2 pods)

# All services active
kubectl get svc -n Top Dog
✓ postgres
✓ backend
✓ frontend

# All deployments ready
kubectl get deployment -n Top Dog
✓ backend (2/2)
✓ frontend (2/2)

# Ingress has IP
kubectl get ingress -n Top Dog
✓ Top Dog-ingress (has IP/hostname)

# Certificate ready
kubectl get certificate -n Top Dog
✓ Top Dog-cert (Ready)

# Auto-scaling active
kubectl get hpa -n Top Dog
✓ backend-hpa
✓ frontend-hpa
```

**Time estimate:** 25-30 minutes  
**Status:** Ready to execute

---

## PHASE 6: DNS CONFIGURATION ⏳ READY AFTER INGRESS IP

### Prerequisites
- [ ] Ingress has been assigned an IP/hostname
- [ ] Access to domain registrar

### Get Ingress IP
```powershell
kubectl get ingress -n Top Dog -o wide
# Copy the IP or hostname from INGRESS column
```

### Update DNS Records
At your domain registrar, create/update these records:

| Host | Type | Value |
|------|------|-------|
| Top Dog.com | A | `<ingress-ip>` |
| www.Top Dog.com | CNAME | Top Dog.com |
| api.Top Dog.com | A | `<ingress-ip>` |

- [ ] DNS records created
- [ ] TTL set to default or lower

### Verify DNS Propagation
```powershell
# Check multiple times (DNS propagates gradually)
nslookup Top Dog.com
nslookup www.Top Dog.com
nslookup api.Top Dog.com

# Should resolve to: <ingress-ip>
```

- [ ] Top Dog.com resolves
- [ ] www.Top Dog.com resolves
- [ ] api.Top Dog.com resolves

**Time estimate:** 5 minutes (DNS propagation: 5-30 minutes additional)  
**Status:** Ready to execute

---

## PHASE 7: VERIFICATION ⏳ READY AFTER DNS

### Test Endpoints
```powershell
# Wait for DNS to propagate (5-30 minutes)

# Test frontend (should load React app)
curl https://Top Dog.com
✓ Returns HTML content

# Test backend health (should return JSON)
curl https://api.Top Dog.com/health
✓ Returns: {"status": "ok"}

# Test API endpoint
curl -H "Content-Type: application/json" https://api.Top Dog.com/
✓ Returns JSON response

# Check HTTPS/SSL (should show valid cert)
curl -vI https://Top Dog.com
✓ SSL certificate valid (Let's Encrypt)
```

- [ ] Frontend loads (https://Top Dog.com)
- [ ] Backend health check passes (https://api.Top Dog.com/health)
- [ ] SSL certificate valid
- [ ] No 404 or 500 errors

### Check Logs
```powershell
# Backend logs (should show no errors)
kubectl logs -f deployment/backend -n Top Dog
✓ No ERROR or WARNING messages

# Frontend logs (should show no errors)
kubectl logs -f deployment/frontend -n Top Dog
✓ No ERROR messages

# Database logs (should show ready)
kubectl logs statefulset/postgres -n Top Dog
✓ "database system is ready to accept connections"
```

- [ ] Backend logs clean
- [ ] Frontend logs clean
- [ ] Database logs clean

### Monitor Resource Usage
```powershell
# Check CPU and memory
kubectl top pods -n Top Dog
kubectl top nodes

# Check auto-scaling
kubectl get hpa -n Top Dog
✓ Should show current replicas and targets
```

- [ ] CPU usage reasonable (< 80%)
- [ ] Memory usage reasonable (< 80%)
- [ ] HPA active and responding

### Final System Check
```powershell
# Get overall status
kubectl get all -n Top Dog

# Should show:
✓ 1 postgres pod Running
✓ 2 backend pods Running
✓ 2 frontend pods Running
✓ All services active
✓ Ingress with IP assigned
✓ Certificate Ready
✓ HPA scaling active
```

- [ ] All pods Running
- [ ] All services Active
- [ ] Ingress configured
- [ ] Certificate Ready
- [ ] HPA operational

**Time estimate:** 5 minutes  
**Status:** Ready to execute

---

## 🎯 FINAL COMPLETION CHECKLIST

**Infrastructure:**
- [x] Docker images built and tagged
- [x] Kubernetes manifests created
- [x] K8s cluster verified
- [x] ingress-nginx ready
- [x] cert-manager ready

**Deployment:**
- [ ] API token obtained (BLOCKER)
- [ ] Images pushed to registry (After token)
- [ ] Secrets updated (After push)
- [ ] K8s manifests applied (After secrets)
- [ ] DNS records updated (After ingress IP)
- [ ] Endpoints verified (After DNS propagates)

**Operations:**
- [ ] Pods running and healthy
- [ ] Services accessible
- [ ] SSL certificates valid
- [ ] Auto-scaling active
- [ ] Logs clean
- [ ] Monitoring configured

---

## ⏱️ REMAINING TIME

| Step | Time |
|------|------|
| Get API token | 2 min |
| Push images | 3 min |
| Update secrets | 3 min |
| Deploy K8s | 25-30 min |
| Update DNS | 5 min |
| DNS propagation | 5-30 min |
| Verify endpoints | 5 min |
| **TOTAL** | **~50-80 min** |

---

## 📞 READY TO PROCEED?

**Current Status:** 80% Complete | Ready for final steps

**Immediate Action:**
1. Get new DigitalOcean API token
2. Share token to continue

**Then Follow:** NEXT_STEPS_QUICK_CARD.md for copy-paste commands

---

**Let's ship this! 🚀**

