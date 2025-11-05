# 🌐 DNS Configuration Guide for Top Dog

**Status**: How to configure real DNS for production use

---

## Option 1: DigitalOcean DNS (Recommended if using DigitalOcean)

### Step 1: Get Your Domain Registered
- Purchase domain at GoDaddy, NameCheap, Google Domains, or your registrar
- Examples: `Top Dog.com`, `topdog.io`, `quellum.app`

### Step 2: Set Up DigitalOcean DNS

#### 2a. Add Domain to DigitalOcean
```bash
# Via CLI
doctl compute domain create Top Dog.com

# Or via DigitalOcean Dashboard:
# 1. Go to Networking > Domains
# 2. Click "Add Domain"
# 3. Enter your domain name
# 4. Select your project
# 5. Click "Add Domain"
```

#### 2b. Change Nameservers at Your Registrar
Point your domain registrar to DigitalOcean's nameservers:
```
ns1.digitalocean.com
ns2.digitalocean.com
ns3.digitalocean.com
```

**Time to take effect**: 24-48 hours (sometimes faster)

#### 2c: Create DNS Records in DigitalOcean

```bash
# A Records pointing to Ingress IP
doctl compute domain records create Top Dog.com --record-type A --record-name "@" --record-data 129.212.190.208
doctl compute domain records create Top Dog.com --record-type A --record-name "www" --record-data 129.212.190.208
doctl compute domain records create Top Dog.com --record-type A --record-name "api" --record-data 129.212.190.208

# OR via Dashboard:
# In DigitalOcean Dashboard > Networking > Domains > Top Dog.com
# Click "Create Record"
# Type: A
# Hostname: @ (for root), www, api
# Directs to: 129.212.190.208
```

### Step 3: Verify DNS Resolution

```bash
# Test from command line
nslookup Top Dog.com
nslookup www.Top Dog.com
nslookup api.Top Dog.com

# Should show: 129.212.190.208
```

---

## Option 2: Alternative DNS Providers

### Cloudflare (Free)
```
1. Add domain to Cloudflare
2. Update nameservers at registrar to Cloudflare
3. In Cloudflare Dashboard:
   - Type: A
   - Name: Top Dog.com
   - IPv4: 129.212.190.208
   - Proxy: DNS only (gray cloud)
4. Wait 24-48 hours for propagation
```

### Google Domains
```
1. Go to DNS settings
2. Add custom nameservers (DigitalOcean's) OR
3. Add A records directly:
   - Host: @, www, api
   - Points to: 129.212.190.208
```

---

## Kubernetes Ingress Configuration

Your ingress is already configured to respond to these domains:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: Top Dog-ingress
  namespace: Top Dog
spec:
  ingressClassName: nginx
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

---

## Testing DNS Configuration

Once DNS is configured:

```bash
# Test in your browser
http://Top Dog.com          # Frontend
http://www.Top Dog.com      # Frontend (alias)
http://api.Top Dog.com      # Backend API

# Command line tests
curl http://Top Dog.com
curl http://api.Top Dog.com/health
```

---

## Multiple Domain Variants

You can also add these A records for variations:

```
topdog.com          → 129.212.190.208
www.topdog.com      → 129.212.190.208
quellum.com         → 129.212.190.208
www.quellum.com     → 129.212.190.208
```

Update your ingress rules to include these hostnames.

---

## Troubleshooting

### DNS not resolving?
```bash
# Clear your local DNS cache (Windows)
ipconfig /flushdns

# Check DNS propagation
nslookup Top Dog.com
# Should show: 129.212.190.208

# If still not working:
# 1. Wait 24-48 hours for nameserver propagation
# 2. Verify A record is created in your DNS provider
# 3. Verify Ingress IP is correct: 129.212.190.208
```

### Getting "ERR_CONNECTION_TIMED_OUT"?
```bash
# Make sure:
# 1. DNS is configured (see above)
# 2. Ingress controller is running
kubectl get pods -n ingress-nginx

# 3. Ingress has address assigned
kubectl get ingress -n Top Dog -o wide

# 4. Backend services are running
kubectl get svc -n Top Dog
```

---

## Next Step: HTTPS/TLS

Once DNS is working, set up HTTPS with Let's Encrypt (see TLS_CERTIFICATE_SETUP.md)
