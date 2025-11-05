# 🌐 DNS Configuration Guide - Top Dog Kubernetes

**LoadBalancer IP**: `134.199.134.151`  
**Domains**: Top Dog.com, www.Top Dog.com, api.Top Dog.com

---

## ✅ Option 1: Using DigitalOcean DNS (Recommended)

### Step 1: Create DigitalOcean DNS Zone

1. Go to DigitalOcean Control Panel → Manage → Domains
2. Click "Add Domain"
3. Enter `Top Dog.com` and select your project
4. DigitalOcean will provide nameservers

### Step 2: Add DNS Records in DigitalOcean

Once the domain is registered in DO, add these records:

```
Type    | Name      | Value               | TTL
--------|-----------|---------------------|-------
A       | @         | 134.199.134.151    | 300
A       | www       | 134.199.134.151    | 300
A       | api       | 134.199.134.151    | 300
```

**PowerShell Command** (if using DigitalOcean CLI):
```powershell
# Requires: doctl installed and authenticated

# Create DNS zone
doctl compute domain create Top Dog.com

# Add A records
doctl compute domain records create Top Dog.com --record-type A --record-name "@" --record-data "134.199.134.151" --record-ttl 300
doctl compute domain records create Top Dog.com --record-type A --record-name "www" --record-data "134.199.134.151" --record-ttl 300
doctl compute domain records create Top Dog.com --record-type A --record-name "api" --record-data "134.199.134.151" --record-ttl 300

# Verify
doctl compute domain records list Top Dog.com
```

### Step 3: Update Domain Registrar (If External)

If your domain registrar is external (GoDaddy, Namecheap, etc.):

1. Go to your registrar's control panel
2. Find "Nameservers" or "DNS Settings"
3. Update to DigitalOcean nameservers:
   - `ns1.digitalocean.com`
   - `ns2.digitalocean.com`
   - `ns3.digitalocean.com`

---

## ⚙️ Option 2: External Registrar (GoDaddy, Namecheap, etc.)

### GoDaddy Example:

1. Log in to GoDaddy control panel
2. Go to Domains → Select Top Dog.com
3. Click "DNS" tab
4. Find "A Records" section
5. Update/Add records:

| Name | Points To | TTL |
|------|-----------|-----|
| @ | 134.199.134.151 | 1800 |
| www | 134.199.134.151 | 1800 |
| api | 134.199.134.151 | 1800 |

---

## 🧪 Verification Steps

### 1. Verify DNS Resolution

```powershell
# Test DNS resolution
nslookup Top Dog.com
nslookup www.Top Dog.com
nslookup api.Top Dog.com

# Should all return: 134.199.134.151

# Alternative (works on all platforms)
Resolve-DnsName Top Dog.com
Resolve-DnsName api.Top Dog.com
```

### 2. Verify HTTP Access

```powershell
# Test frontend
curl http://Top Dog.com
curl http://www.Top Dog.com

# Test backend API
curl http://api.Top Dog.com/health

# Test via direct IP (should still work)
curl http://134.199.134.151
```

### 3. Check Ingress Configuration

```bash
kubectl get ingress -n Top Dog -o wide
kubectl describe ingress nginx-ingress -n Top Dog
```

Expected output should show:
```
Rules:
  Host              | Path | Backends
  Top Dog.com         | /    | frontend:3000
  www.Top Dog.com     | /    | frontend:3000
  api.Top Dog.com     | /    | backend:8000
```

---

## ⏱️ Propagation Timeline

- **Immediate**: Direct IP access (http://134.199.134.151) ✅
- **Within 5 minutes**: DNS should resolve (with TTL 300)
- **Within 30 minutes**: Full global propagation
- **Within 2 hours**: Complete propagation across all ISPs

---

## 🔧 Troubleshooting

### DNS Not Resolving

```powershell
# Clear local DNS cache (Windows)
Clear-DnsClientCache

# Flush DNS (alternative)
ipconfig /flushdns

# Wait and retry
Start-Sleep -Seconds 30
nslookup Top Dog.com
```

### Check Nameserver Status

```powershell
nslookup -type=NS Top Dog.com
# Should show DigitalOcean nameservers if using DO DNS
```

### Verify LoadBalancer is Ready

```bash
kubectl get svc -n Top Dog -l app=frontend
# Should show EXTERNAL-IP: 134.199.134.151
```

### Check Ingress is Routing

```bash
# Test from inside cluster
kubectl exec -n Top Dog frontend-PODNAME -- curl http://Top Dog.com

# Test from outside
curl -v http://Top Dog.com
# Should see successful response
```

---

## 📋 DNS Record Summary

Once complete, you should have:

```
Domain: Top Dog.com
├── @ (root)      → 134.199.134.151 → Frontend (Top Dog.com, www.Top Dog.com)
├── www           → 134.199.134.151 → Frontend
└── api           → 134.199.134.151 → Backend API

All records pointing to DigitalOcean LoadBalancer
```

---

## ✅ Success Criteria

- [ ] `nslookup Top Dog.com` returns 134.199.134.151
- [ ] `nslookup www.Top Dog.com` returns 134.199.134.151
- [ ] `nslookup api.Top Dog.com` returns 134.199.134.151
- [ ] `curl http://Top Dog.com` shows frontend
- [ ] `curl http://api.Top Dog.com/health` returns {"status":"ok"}
- [ ] WHOIS shows correct nameservers (if using DO)
- [ ] Global DNS checker shows all IPs correct

---

**Status**: 🟡 Awaiting DNS Configuration  
**Complexity**: ⭐ Low (5-10 minutes)  
**Impact**: Critical for public access
