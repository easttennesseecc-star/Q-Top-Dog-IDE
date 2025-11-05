# 🔒 TLS Certificate Setup Guide - Let's Encrypt & cert-manager

**Status**: Production-ready HTTPS setup  
**Certificate Authority**: Let's Encrypt (FREE)  
**Auto-Renewal**: Yes (automatic 90-day renewal)

---

## ✅ Step 1: Install cert-manager

### 1.1 Add Helm Repository

```powershell
helm repo add jetstack https://charts.jetstack.io
helm repo update
```

### 1.2 Create cert-manager Namespace

```bash
kubectl create namespace cert-manager
```

### 1.3 Install cert-manager

```bash
helm install cert-manager jetstack/cert-manager `
  --namespace cert-manager `
  --version v1.13.2 `
  --set installCRDs=true `
  --set global.leaderElection.namespace=cert-manager
```

### 1.4 Verify Installation

```bash
kubectl get pods -n cert-manager
# Should show 3 pods: cert-manager, cert-manager-webhook, cert-manager-cainjector
# All should be Running
```

---

## ✅ Step 2: Create Let's Encrypt ClusterIssuer

### 2.1 Create ClusterIssuer Manifest

Create file: `k8s/07-cert-manager-issuer.yaml`

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@Top Dog.com  # CHANGE THIS TO YOUR EMAIL
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx

---
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
spec:
  acme:
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    email: admin@Top Dog.com  # CHANGE THIS TO YOUR EMAIL
    privateKeySecretRef:
      name: letsencrypt-staging
    solvers:
    - http01:
        ingress:
          class: nginx
```

### 2.2 Apply the Issuer

```bash
kubectl apply -f k8s/07-cert-manager-issuer.yaml

# Verify
kubectl get clusterissuer
# Should show both letsencrypt-prod and letsencrypt-staging as True/Ready
```

---

## ✅ Step 3: Update Ingress for HTTPS

### 3.1 Update Ingress Configuration

Edit file: `k8s/06-ingress-simple.yaml`

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
  namespace: Top Dog
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"  # ADD THIS LINE
    nginx.ingress.kubernetes.io/ssl-redirect: "true"    # ADD THIS LINE
spec:
  ingressClassName: nginx
  tls:  # ADD THIS ENTIRE SECTION
  - hosts:
    - Top Dog.com
    - www.Top Dog.com
    secretName: Top Dog-tls
  - hosts:
    - api.Top Dog.com
    secretName: api-Top Dog-tls
  rules:
  - host: Top Dog.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 3000
  - host: www.Top Dog.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 3000
  - host: api.Top Dog.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 8000
```

### 3.2 Apply Updated Ingress

```bash
kubectl apply -f k8s/06-ingress-simple.yaml

# Verify
kubectl get ingress -n Top Dog -o wide
kubectl describe ingress nginx-ingress -n Top Dog
```

---

## ✅ Step 4: Monitor Certificate Generation

### 4.1 Check Certificate Status

```bash
# View certificates
kubectl get certificate -n Top Dog

# Get detailed status
kubectl describe certificate Top Dog-tls -n Top Dog
kubectl describe certificate api-Top Dog-tls -n Top Dog

# Check cert-manager logs for troubleshooting
kubectl logs -n cert-manager -l app=cert-manager --tail=50
```

### 4.2 Expected Output

```
NAME             READY  SECRET           AGE
Top Dog-tls        True   Top Dog-tls        2m
api-Top Dog-tls    True   api-Top Dog-tls    2m
```

### 4.3 Monitor Challenges

```bash
# Watch ACME challenges (should complete within 1 minute)
kubectl get challenges -n Top Dog --watch
```

---

## 🧪 Step 5: Verification

### 5.1 Test HTTPS Access

```powershell
# Test with PowerShell
$url = "https://Top Dog.com"
try {
    $response = Invoke-WebRequest -Uri $url -SkipCertificateCheck
    Write-Host "✅ HTTPS working: $url"
    Write-Host "Status Code: $($response.StatusCode)"
} catch {
    Write-Host "❌ HTTPS failed: $_"
}

# Test all domains
foreach ($domain in @("Top Dog.com", "www.Top Dog.com", "api.Top Dog.com")) {
    $url = "https://$domain"
    Write-Host "Testing $url..."
    Invoke-WebRequest -Uri $url -SkipCertificateCheck | Select-Object StatusCode, StatusDescription
}
```

### 5.2 Check Certificate Details

```bash
# View certificate details
kubectl get secret Top Dog-tls -n Top Dog -o yaml | grep tls.crt | awk '{print $2}' | base64 -d | openssl x509 -text -noout

# Check expiration
openssl x509 -in <(kubectl get secret Top Dog-tls -n Top Dog -o jsonpath='{.data.tls\.crt}' | base64 -d) -noout -dates
```

### 5.3 Test from Outside Cluster

```powershell
# Force HTTP redirect test
curl -L -I http://Top Dog.com
# Should show redirect to https://

# Final HTTPS test
curl -I https://Top Dog.com
# Should show 200 OK
```

---

## ⚙️ Advanced Configuration

### Auto-Renewal Configuration

Certificates are automatically renewed 30 days before expiration. To verify:

```bash
# Check cert-manager controller logs for renewal activity
kubectl logs -n cert-manager -l app=cert-manager --tail=100 | grep -i "renew\|issuing"

# Monitor certificate age
kubectl get certificate -n Top Dog -o wide
# Certificates show Age - automatically renewed when needed
```

### Wildcard Certificates (Optional)

If you need `*.Top Dog.com`, use DNS validation:

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: wildcard-Top Dog
  namespace: Top Dog
spec:
  secretName: wildcard-Top Dog-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
  - "*.Top Dog.com"
  - "Top Dog.com"
```

---

## 🔧 Troubleshooting

### Certificate Not Issuing

```bash
# 1. Check certificate status
kubectl describe certificate Top Dog-tls -n Top Dog
# Look for "Status" and "Conditions"

# 2. Check challenges
kubectl get challenges -n Top Dog
kubectl describe challenge -n Top Dog <challenge-name>

# 3. Check cert-manager logs
kubectl logs -n cert-manager -l app=cert-manager | grep -i "error\|failed"

# 4. Verify ingress is ready
kubectl get ingress -n Top Dog
# Must show an IP address in INGRESS column
```

### Challenges Not Completing

```bash
# Check HTTP challenge validation
kubectl describe challenge -n Top Dog <name>

# Verify ingress controller is accessible
kubectl port-forward svc/nginx-ingress -n Top Dog 80:80
curl -I http://localhost/.well-known/acme-challenge/test
```

### Certificate Expired

```bash
# Force renewal
kubectl delete certificate Top Dog-tls -n Top Dog
kubectl apply -f k8s/06-ingress-simple.yaml
# New certificate will be issued immediately
```

---

## 📋 Deployment Checklist

- [ ] cert-manager installed and running (3 pods in cert-manager namespace)
- [ ] ClusterIssuers created (letsencrypt-prod and letsencrypt-staging)
- [ ] Ingress updated with TLS and cert-manager annotation
- [ ] Certificates issued (Ready: True)
- [ ] https://Top Dog.com responds with 200
- [ ] https://api.Top Dog.com responds with 200
- [ ] HTTP redirects to HTTPS
- [ ] Certificate details show correct domains
- [ ] No errors in cert-manager logs

---

## ✅ Success Criteria

```
✅ curl https://Top Dog.com returns 200
✅ curl https://api.Top Dog.com/health returns {"status":"ok"}
✅ Certificate is valid for: Top Dog.com, www.Top Dog.com, api.Top Dog.com
✅ Certificate auto-renews before expiration
✅ HTTP traffic redirects to HTTPS
✅ No security warnings in browser
✅ Cert-manager shows 0 errors in logs
```

---

## 📚 Quick Reference

```bash
# Install all components
helm repo add jetstack https://charts.jetstack.io
helm install cert-manager jetstack/cert-manager -n cert-manager --create-namespace --set installCRDs=true
kubectl apply -f k8s/07-cert-manager-issuer.yaml
kubectl apply -f k8s/06-ingress-simple.yaml

# Monitor status
kubectl get certificate -n Top Dog
kubectl get challenges -n Top Dog

# View logs
kubectl logs -n cert-manager -l app=cert-manager -f

# Restart cert-manager if needed
kubectl rollout restart deployment/cert-manager -n cert-manager
```

---

**Status**: 🟡 Ready for Installation  
**Complexity**: ⭐⭐ Medium (15-20 minutes)  
**Impact**: Critical for secure HTTPS access  
**Maintenance**: Automatic (no manual renewal needed)
