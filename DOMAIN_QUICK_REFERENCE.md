# 🌐 DOMAIN QUICK REFERENCE

## Your Domain Portfolio

```
OWNED TODAY
✅ quellum.net       (Corporate info)

PURCHASING NOW
🛒 Top Dog.com        (Primary product)
🛒 Top Dog.net        (Backup/redundancy)
```

---

## DNS RECORDS TO CREATE

### For Top Dog.com (Primary Domain)

```
TYPE    NAME               POINTS TO              TTL
──────  ─────────────────  ──────────────────────────────  ─────
A       @                  YOUR_SERVER_IP                 300
A       www                YOUR_SERVER_IP                 300
CNAME   api                Top Dog.com                      300
CNAME   docs               Top Dog.com                      300
CNAME   downloads          Top Dog.com                      300
CNAME   status             Top Dog.com                      300
```

### For Top Dog.net (Backup Domain)

```
TYPE    NAME    POINTS TO           TTL
──────  ──────  ────────────────────────────  ─────
CNAME   @       Top Dog.com                     300
CNAME   www     Top Dog.com                     300
CNAME   api     api.Top Dog.com                 300
```

### For quellum.net (Company Site)

```
TYPE    NAME     POINTS TO           TTL
──────  ───────  ────────────────────────────  ─────
A       www      YOUR_COMPANY_SERVER_IP       300
CNAME   product  Top Dog.com                    300
```

---

## DOMAIN ROUTING

```
User visits:              Gets redirected to:
──────────────────────────────────────────────────
Top Dog.com              → Frontend (www)
www.Top Dog.com          → Frontend (www)
api.Top Dog.com          → Backend API
docs.Top Dog.com         → Documentation
downloads.Top Dog.com    → Downloads
status.Top Dog.com       → Status page

Top Dog.net              → Top Dog.com (redirect)
www.Top Dog.net          → Top Dog.com (redirect)

quellum.net/product    → Top Dog.com (redirect)
```

---

## DEPLOYMENT TIMELINE

### Day 1: Purchase & DNS Setup
```
Time    Action
─────────────────────────────────────────────
10:00   Purchase Top Dog.com
10:05   Purchase Top Dog.net
10:10   Update DNS records at registrar
10:15   Wait for DNS propagation (24-48 hrs)
```

### Day 2-3: Server Setup
```
Time    Action
─────────────────────────────────────────────
Setup DigitalOcean droplet
Deploy application code
Install PostgreSQL
Configure environment variables
```

### Day 3: SSL & Nginx
```
Time    Action
─────────────────────────────────────────────
Install Let's Encrypt SSL (for all domains)
Configure Nginx reverse proxy
Setup auto-renewal
Test all domains (HTTPS)
```

### Day 4: Go Live
```
Time    Action
─────────────────────────────────────────────
Switch Stripe to production keys
Test payments with real card
Monitor logs
🎉 LAUNCH
```

---

## CRITICAL REMINDERS

🔴 **BEFORE YOU PURCHASE:**
- [ ] Decide which registrar (Namecheap vs GoDaddy)
- [ ] Have your DigitalOcean account ready
- [ ] Know your server IP address (from DigitalOcean)
- [ ] Have your Stripe production keys ready

🟡 **AFTER PURCHASE:**
- [ ] Point nameservers to DigitalOcean immediately
- [ ] DNS takes 24-48 hours to propagate
- [ ] SSL certificate creation waits for DNS
- [ ] Don't switch Stripe to live until tested

🟢 **LAUNCH CHECKLIST:**
- [ ] All domains resolve to correct servers
- [ ] SSL certificates valid on all domains
- [ ] Backend API responding at api.Top Dog.com
- [ ] Frontend loads at Top Dog.com
- [ ] Payments process successfully
- [ ] Stripe webhooks firing correctly
- [ ] Database backups working
- [ ] Logs being recorded

---

## QUICK COMMANDS

```bash
# Check domain DNS
nslookup Top Dog.com

# Test SSL certificate
curl -vI https://Top Dog.com

# Test API endpoint
curl https://api.Top Dog.com/health

# Check Nginx config
nginx -t

# Monitor backend logs
tail -f /var/www/Top Dog/backend/logs/app.log

# Restart backend
systemctl restart Top Dog-backend

# Check certificate expiry
certbot certificates
```

---

## COST SUMMARY

```
Category                  Cost/Year    Cost/Month
──────────────────────────────────────────────────
Domains (Top Dog.com, net)   $25         $2.08
Server (DigitalOcean)     $144        $12.00
SSL (Let's Encrypt)         $0         $0.00
──────────────────────────────────────────────────
TOTAL                     $169        $14.08

+ Stripe fees: 2.9% + $0.30 per transaction
+ Optional: Backups, CDN, Monitoring
```

---

## WHERE TO BUY DOMAINS

### Recommended Registrars:
1. **Namecheap** (Cheapest)
   - Top Dog.com: ~$8.99/year
   - Support: Good
   - WHOIS privacy: Included

2. **GoDaddy** (Popular)
   - Top Dog.com: ~$14.99/year
   - Support: Excellent
   - WHOIS privacy: Extra cost

3. **Hover** (Best support)
   - Top Dog.com: ~$12.99/year
   - Support: Best in class
   - WHOIS privacy: Included

**I recommend Namecheap** - cheapest and solid support.

---

## DOMAIN CHECKLIST

### Before Purchase:
- [ ] .com domain short and memorable?
- [ ] .net domain same or different strategy?
- [ ] Quellum.net integration plan clear?
- [ ] Budget approved? (~$170/year)

### After Purchase:
- [ ] Domains added to your account?
- [ ] Nameservers changed to DigitalOcean?
- [ ] DNS records created?
- [ ] Waiting for propagation?

### Before Deployment:
- [ ] DigitalOcean droplet created?
- [ ] SSL certificates ready?
- [ ] Nginx configured?
- [ ] Backend running?

### Before Launch:
- [ ] Stripe switched to production?
- [ ] All domains resolve correctly?
- [ ] HTTPS working on all domains?
- [ ] Payments tested?
- [ ] Webhooks verified?

---

## NEXT ACTIONS

### ✅ Today:
1. Purchase Top Dog.com and Top Dog.net
2. Update nameservers to DigitalOcean

### ✅ Tomorrow:
3. Create DNS records
4. Wait for propagation

### ✅ Next 2 Days:
5. Deploy to DigitalOcean
6. Configure SSL
7. Test everything

### ✅ Before Launch:
8. Switch Stripe to production
9. Final testing
10. 🎉 Go live!

---

**Questions?** I'm here to help with every step!

