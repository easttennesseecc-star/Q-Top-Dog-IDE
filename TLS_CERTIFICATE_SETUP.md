# 🔒 TLS Certificate Setup with Let's Encrypt

**Status**: Complete guide to set up HTTPS/SSL certificates automatically

---

## Overview

This guide sets up free, automatic HTTPS certificates using cert-manager and Let's Encrypt.

**Benefits**:
- ✅ Free SSL certificates
- ✅ Automatic renewal (every 90 days)
- ✅ Automatic injection into ingress
- ✅ Works with Kubernetes ingress controller

---

## Step 1: Install cert-manager

```bash
# Add Jetstack Helm repository
helm repo add jetstack https://charts.jetstack.io
helm repo update

# Create namespace for cert-manager
kubectl create namespace cert-manager

# Install CRDs
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.0/cert-manager.crds.yaml

# Install cert-manager via Helm
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --version v1.14.0
```

**Verify Installation**:
```bash
kubectl get pods --namespace cert-manager
# Should show 3 pods: cert-manager, cert-manager-webhook, cert-manager-cainjector
```

---

## Step 2: Create Let's Encrypt Issuers

Create ClusterIssuer for production certificates:

```bash
cat <<EOF | kubectl apply -f -
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
EOF
```

**Verify Issuers**:
```bash
kubectl get clusterissuer
# Should show: letsencrypt-prod, letsencrypt-staging
```

---

## Step 3: Update Ingress for HTTPS

Update your ingress to use TLS:

```bash
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: Top Dog-ingress
  namespace: Top Dog
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/proxy-body-size: 50m
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "600"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - Top Dog.com
    - www.Top Dog.com
    - api.Top Dog.com
    - topdog.com
    - www.topdog.com
    - quellum.com
    - www.quellum.com
    secretName: Top Dog-tls
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
  - host: topdog.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 3000
  - host: www.topdog.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 3000
  - host: quellum.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 3000
  - host: www.quellum.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 3000
EOF
```

---

## Step 4: Monitor Certificate Creation

cert-manager will automatically:
1. Create a Certificate resource
2. Request a certificate from Let's Encrypt
3. Solve the DNS challenge
4. Store the certificate in a Kubernetes Secret

**Check Certificate Status**:
```bash
# Watch certificate creation
kubectl get certificate -n Top Dog
kubectl describe certificate Top Dog-tls -n Top Dog

# Check Secret was created
kubectl get secret Top Dog-tls -n Top Dog
kubectl describe secret Top Dog-tls -n Top Dog

# View certificate details
kubectl get secret Top Dog-tls -n Top Dog -o jsonpath='{.data.tls\.crt}' | base64 --decode | openssl x509 -text -noout
```

**Expected Output**:
```
Certificate is issued and valid until ~90 days from now
Issuer: Let's Encrypt
Subject: Top Dog.com
```

---

## Step 5: Update DNS Records (If Not Already Done)

Ensure DNS points to your ingress:
```bash
# Create A records for these domains:
Top Dog.com           → 129.212.190.208
www.Top Dog.com       → 129.212.190.208
api.Top Dog.com       → 129.212.190.208
topdog.com          → 129.212.190.208
www.topdog.com      → 129.212.190.208
quellum.com         → 129.212.190.208
www.quellum.com     → 129.212.190.208
```

---

## Step 6: Test HTTPS Access

Once certificate is issued:

```bash
# Test your domains (will be HTTPS now)
curl https://Top Dog.com
curl https://www.Top Dog.com
curl https://api.Top Dog.com
curl https://topdog.com
curl https://quellum.com

# Check certificate is valid
openssl s_client -connect Top Dog.com:443

# Or open in browser:
https://Top Dog.com        # Should show no warnings
https://api.Top Dog.com    # Backend API
https://topdog.com       # Alias domain
https://quellum.com      # Company name
```

---

## Automatic Renewal

Let's Encrypt certificates expire after 90 days, but:

✅ **cert-manager automatically renews them** 30 days before expiration  
✅ **No action required from you**  
✅ **Renewal is seamless with no downtime**

Monitor renewal:
```bash
kubectl get certificaterequests -n Top Dog
kubectl logs -n cert-manager deployment/cert-manager --tail=20
```

---

## Troubleshooting

### Certificate Stuck in "Pending"
```bash
# Check what's wrong
kubectl describe certificate Top Dog-tls -n Top Dog

# Common issues:
# 1. DNS not resolving - make sure DNS is configured correctly
# 2. Firewall blocking port 80 - needed for HTTP-01 challenge
# 3. Ingress not ready - check ingress status

# Delete and recreate
kubectl delete certificate Top Dog-tls -n Top Dog
kubectl delete ingress Top Dog-ingress -n Top Dog
# Re-apply ingress YAML from Step 3
```

### "Error authorizing certificate"
- Make sure DNS is properly configured and resolving
- Let's Encrypt needs to access `http://Top Dog.com/.well-known/acme-challenge/`
- This requires port 80 to be open to the internet

### Check ACME challenge status
```bash
kubectl describe certificaterequest -n Top Dog
kubectl get challenges -n Top Dog
kubectl describe challenge -n Top Dog
```

---

## Upgrade HTTP to HTTPS

Add HTTP→HTTPS redirect:

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-configuration
  namespace: ingress-nginx
data:
  force-ssl-redirect: "true"
  ssl-protocols: "TLSv1.2 TLSv1.3"
  ssl-ciphers: "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256"
EOF
```

Now all HTTP requests automatically redirect to HTTPS.

---

## Certificate Rotation

To rotate/update certificates:
```bash
# Force immediate renewal (for testing)
kubectl delete certificate Top Dog-tls -n Top Dog

# New certificate will be automatically issued
kubectl get certificate -n Top Dog
```

---

## Monitoring Certificate Expiration

Create a reminder:
```bash
# Check when certificate expires
kubectl get certificate -n Top Dog -o jsonpath='{.items[0].status.notAfter}'

# Get next renewal date (30 days before expiry)
# Example: If not after is 2026-02-01, renewal at 2026-01-02
```

---

## Next Steps

- ✅ DNS configured (DNS_CONFIGURATION_PRODUCTION.md)
- ✅ TLS certificates set up
- ⏳ Set up monitoring: See MONITORING_SETUP.md
- ⏳ Configure backups: See POSTGRES_BACKUP_SETUP.md

---

**Your site is now HTTPS-secure and certificates auto-renew!**
