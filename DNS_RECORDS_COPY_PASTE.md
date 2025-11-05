# 📋 DNS RECORDS - COPY & PASTE READY

**Keep this file handy when setting up DNS!**

---

## ℹ️ BEFORE YOU START

You'll need:
- [ ] Your DigitalOcean server IP address (e.g., `123.45.67.89`)
- [ ] Access to your domain registrar (Namecheap, GoDaddy, etc.)
- [ ] These DNS records ready to paste

---

## 🎯 STEP 1: Get Your Server IP

**After creating DigitalOcean droplet:**

```
Go to: DigitalOcean Dashboard
  → Droplets
  → Your Top Dog Droplet
  → Copy IPv4 address (looks like: 123.45.67.89)

Save it here: MY_SERVER_IP = ___________________
```

---

## 🔧 STEP 2: Create DNS Records

### A. For Top Dog.com (Primary Domain)

**In your registrar (e.g., Namecheap, GoDaddy):**

1. Go to: DNS Management for Top Dog.com
2. Add these records:

```
┌─────────────────────────────────────────────────────────────┐
│ Type: A                                                     │
│ Name: @ (or leave blank)                                   │
│ Value: YOUR_DIGITALOCEAN_SERVER_IP                         │
│ TTL: 300 (or auto)                                         │
│ [SAVE]                                                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Type: CNAME                                                 │
│ Name: www                                                   │
│ Value: Top Dog.com                                           │
│ TTL: 300 (or auto)                                         │
│ [SAVE]                                                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Type: CNAME                                                 │
│ Name: api                                                   │
│ Value: Top Dog.com                                           │
│ TTL: 300 (or auto)                                         │
│ [SAVE]                                                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Type: CNAME                                                 │
│ Name: docs                                                  │
│ Value: Top Dog.com                                           │
│ TTL: 300 (or auto)                                         │
│ [SAVE]                                                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Type: CNAME                                                 │
│ Name: downloads                                             │
│ Value: Top Dog.com                                           │
│ TTL: 300 (or auto)                                         │
│ [SAVE]                                                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Type: CNAME                                                 │
│ Name: status                                                │
│ Value: Top Dog.com                                           │
│ TTL: 300 (or auto)                                         │
│ [SAVE]                                                      │
└─────────────────────────────────────────────────────────────┘
```

✅ **Result:** 6 records for Top Dog.com

---

### B. For Top Dog.net (Backup Domain)

**In your registrar:**

1. Go to: DNS Management for Top Dog.net
2. Add these records:

```
┌─────────────────────────────────────────────────────────────┐
│ Type: CNAME                                                 │
│ Name: @ (or leave blank)                                   │
│ Value: Top Dog.com                                           │
│ TTL: 300 (or auto)                                         │
│ [SAVE]                                                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Type: CNAME                                                 │
│ Name: www                                                   │
│ Value: Top Dog.com                                           │
│ TTL: 300 (or auto)                                         │
│ [SAVE]                                                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Type: CNAME                                                 │
│ Name: api                                                   │
│ Value: api.Top Dog.com                                       │
│ TTL: 300 (or auto)                                         │
│ [SAVE]                                                      │
└─────────────────────────────────────────────────────────────┘
```

✅ **Result:** 3 records for Top Dog.net (all redirect to Top Dog.com)

---

### C. For quellum.net (Optional - Company Info)

**In your registrar:**

1. Go to: DNS Management for quellum.net
2. Add this record:

```
┌─────────────────────────────────────────────────────────────┐
│ Type: CNAME                                                 │
│ Name: product                                               │
│ Value: Top Dog.com                                           │
│ TTL: 300 (or auto)                                         │
│ [SAVE]                                                      │
└─────────────────────────────────────────────────────────────┘
```

**Result:** Users who go to quellum.net/product get redirected to Top Dog.com

✅ **Total Records Created:** 10

---

## ✅ VERIFICATION

### Verify DNS is working (run these in terminal):

```powershell
# Check Top Dog.com
nslookup Top Dog.com
# Should show: YOUR_DIGITALOCEAN_SERVER_IP

# Check www
nslookup www.Top Dog.com
# Should show: YOUR_DIGITALOCEAN_SERVER_IP

# Check api
nslookup api.Top Dog.com
# Should show: YOUR_DIGITALOCEAN_SERVER_IP

# Check Top Dog.net redirect
nslookup Top Dog.net
# Should show: points to Top Dog.com

# Check quellum.net
nslookup product.quellum.net
# Should show: points to Top Dog.com
```

---

## 🔄 DNS PROPAGATION

After adding records:

- ⏱️ **Immediate:** Some regions see updates
- ⏱️ **5 minutes:** Most regions see updates
- ⏱️ **24 hours:** All regions should see updates
- ⏱️ **48 hours:** Guaranteed all regions updated

**During this time:**
- SSL certificates may not work yet
- Domain may not resolve
- Just wait! Don't change anything.

**Check propagation status:**
- https://www.whatsmydns.net/?type=A&q=Top Dog.com

---

## 🔐 HTTPS/SSL (After DNS Propagates)

Once DNS is working, create SSL certificates:

```bash
# SSH into your server
ssh root@YOUR_SERVER_IP

# Install Certbot
apt install -y certbot python3-certbot-nginx

# Create certificates for all domains
certbot certonly --nginx \
  -d Top Dog.com \
  -d www.Top Dog.com \
  -d api.Top Dog.com \
  -d docs.Top Dog.com \
  -d downloads.Top Dog.com \
  -d status.Top Dog.com

# You'll be asked for email, agree to terms, etc.
# Certificates will be created automatically
```

---

## 🧪 FINAL TESTING

After everything is set up:

```bash
# Test HTTPS on main domain
curl -vI https://Top Dog.com

# Should show:
# ✓ SSL certificate verified
# ✓ HTTP/2 200 OK

# Test API
curl https://api.Top Dog.com/health

# Should show:
# {"status": "healthy"}

# Test redirect
curl -I https://Top Dog.net
# Should show: 301 redirect to Top Dog.com
```

---

## 📝 QUICK CHECKLIST

### DNS Setup:
- [ ] Purchased Top Dog.com
- [ ] Purchased Top Dog.net
- [ ] Have DigitalOcean server IP
- [ ] Created 6 records for Top Dog.com
- [ ] Created 3 records for Top Dog.net
- [ ] Created 1 record for quellum.net
- [ ] Waited 24 hours for propagation
- [ ] Verified with `nslookup` commands

### SSL Setup:
- [ ] DNS propagation confirmed
- [ ] Installed Certbot
- [ ] Created certificates for all domains
- [ ] Nginx configured with SSL
- [ ] Verified https:// works

### Pre-Launch:
- [ ] All domains resolve correctly
- [ ] SSL certificates valid
- [ ] API responding at api.Top Dog.com
- [ ] Frontend loading at Top Dog.com
- [ ] Stripe webhooks pointing to api.Top Dog.com
- [ ] Payments tested

---

## 💡 TIPS

**Common mistakes to avoid:**
1. ❌ Don't forget TTL (leave at 300)
2. ❌ Don't use www in the @ record
3. ❌ Don't forget the subdomain names (api, www, etc.)
4. ❌ Don't rush - wait for DNS to propagate
5. ❌ Don't use old IP addresses (get fresh one)

**If something doesn't work:**
1. Wait 24 hours (DNS is slow)
2. Clear your browser cache (Ctrl+Shift+Delete)
3. Try different browser
4. Check registrar didn't make typos
5. Verify IP address is correct

---

## 📞 SUPPORT

If you get stuck:

**Namecheap:**
- https://www.namecheap.com/support/

**GoDaddy:**
- https://www.godaddy.com/help

**DigitalOcean:**
- https://docs.digitalocean.com/products/networking/dns/

**Let me know if you need help!** 🚀

