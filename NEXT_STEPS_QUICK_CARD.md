# 🚀 QUICK REFERENCE: DEPLOYMENT NEXT STEPS

**Status:** Images built ✅ | Manifests created ✅ | Blocked on API token ⏳

---

## ⏹️ WHAT'S BLOCKING PROGRESS

```
ERROR: 401 Unauthorized when pushing to registry
CAUSE: Previous DigitalOcean API token invalid/expired
FIX:   Generate new token (< 5 minutes)
```

---

## ✅ IMMEDIATE ACTION REQUIRED

### 1. Get New DigitalOcean API Token
```
👉 Go to: https://cloud.digitalocean.com/account/api/tokens
👉 Click "Generate New Token"
👉 Name: "Top Dog-Registry-Push"
👉 Permissions: "read & write"
👉 COPY IMMEDIATELY (only shown once!)
```

---

## 📋 THEN DO THIS (Copy & Paste)

### Push Images (After getting new token)
```powershell
$Token = "dop_v1_YOUR_NEW_TOKEN_HERE"
Write-Output $Token | docker login -u unused --password-stdin registry.digitalocean.com

docker push registry.digitalocean.com/Top Dog-registry/Top Dog-frontend:v1.0.0
docker push registry.digitalocean.com/Top Dog-registry/Top Dog-backend:v1.0.0

Write-Host "✅ Images pushed! Now update secrets file." -ForegroundColor Green
```

### Update Secrets
```powershell
# Open the secrets file
code k8s/02-secrets.yaml

# Replace these values with yours:
# - DATABASE_PASSWORD (create new secure password)
# - STRIPE_SECRET_KEY (from https://dashboard.stripe.com/apikeys)
# - STRIPE_WEBHOOK_SECRET (from Stripe webhooks)
# - STRIPE_PUBLISHABLE_KEY (from Stripe public keys)
# - STRIPE_PRICE_ID_* (from Stripe products page)
# - JWT_SECRET (generate with: openssl rand -base64 32)

# Save and close file (Ctrl+S, Ctrl+W)
```

### Deploy to Kubernetes
```powershell
# Go to project directory
cd C:\Quellum-topdog-ide

# Apply manifests in order
kubectl apply -f k8s/00-namespace.yaml
Start-Sleep -Seconds 3
kubectl apply -f k8s/01-configmap.yaml
kubectl apply -f k8s/02-secrets.yaml
kubectl apply -f k8s/03-postgresql.yaml

# Monitor database startup
kubectl get pods -n Top Dog -w

# Then deploy backend, frontend, ingress, certificates
kubectl apply -f k8s/04-backend.yaml
kubectl apply -f k8s/05-frontend.yaml
kubectl apply -f k8s/06-ingress.yaml
kubectl apply -f k8s/07-certificate.yaml

# Monitor deployment
kubectl get pods -n Top Dog -w
kubectl get ingress -n Top Dog -w

# Wait for ingress IP (should appear in 1-2 minutes)
kubectl get ingress -n Top Dog -o wide
```

### Update DNS (After ingress has IP)
```
Copy the ingress IP from above, then:

Go to your domain registrar and update:
  Top Dog.com           →  <ingress-ip>
  www.Top Dog.com       →  <ingress-ip>
  api.Top Dog.com       →  <ingress-ip>

Wait 5-30 minutes for DNS to propagate, then test:
  curl https://Top Dog.com
  curl https://api.Top Dog.com/health
```

---

## 📁 KEY FILES

```
/k8s/
├── 00-namespace.yaml       ← Create Top Dog namespace
├── 01-configmap.yaml       ← Environment variables
├── 02-secrets.yaml         ← ⚠️ EDIT WITH YOUR VALUES
├── 03-postgresql.yaml      ← Database
├── 04-backend.yaml         ← FastAPI backend
├── 05-frontend.yaml        ← React frontend
├── 06-ingress.yaml         ← Nginx router
└── 07-certificate.yaml     ← SSL certificates

Documentation:
├── KUBERNETES_DEPLOYMENT_READY.md     ← Full guide
├── DEPLOYMENT_STATUS_UPDATE.md        ← Status
└── DEPLOYMENT_COMPLETE_STATUS.md      ← Summary
```

---

## ⏱️ TIME ESTIMATE

```
1. Get new API token        ⏱️  2 min
2. Push images              ⏱️  3 min
3. Update secrets           ⏱️  3 min
4. Deploy to K8s            ⏱️ 25-30 min
5. Update DNS               ⏱️  5 min
6. DNS propagation          ⏱️  5-30 min
─────────────────────────────────────
TOTAL TO PRODUCTION:       ⏱️ 45-75 min
```

---

## ✅ VERIFY IT WORKED

```powershell
# After DNS propagates:
curl https://Top Dog.com
curl https://api.Top Dog.com/health
curl https://api.Top Dog.com/health

# Should return:
# {"status": "ok"} ✅

# Monitor logs:
kubectl logs -f deployment/backend -n Top Dog
kubectl logs -f deployment/frontend -n Top Dog
```

---

## 🆘 TROUBLESHOOTING

**Push fails with "401 Unauthorized"**
- New token invalid or expired
- Get another token from DigitalOcean dashboard

**Pods not starting**
- Check: `kubectl describe pod <name> -n Top Dog`
- Check logs: `kubectl logs <pod> -n Top Dog`

**Ingress not getting IP**
- Wait 1-2 more minutes
- Check: `kubectl describe ingress Top Dog-ingress -n Top Dog`

**DNS not resolving**
- Wait 5-30 minutes for propagation
- Verify DNS records entered correctly
- Use: `nslookup Top Dog.com`

---

**Current Status:** Ready to proceed with new API token ✅

Get token → Share token → Push images → Deploy → DONE! 🚀

