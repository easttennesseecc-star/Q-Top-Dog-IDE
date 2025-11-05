# 🌐 DOMAIN DEPLOYMENT STRATEGY

## Your Domain Portfolio

```
✅ quellum.net        (Already owned)
🔄 Top Dog.com         (About to purchase)
🔄 Top Dog.net         (About to purchase)
```

---

## 📋 RECOMMENDED DOMAIN ARCHITECTURE

### Domain Strategy
```
Primary Domain:       Top Dog.com
├─ www.Top Dog.com    → Main application
├─ api.Top Dog.com    → Backend API
├─ docs.Top Dog.com   → Documentation
├─ status.Top Dog.com → Status page
└─ downloads.Top Dog.com → MSI downloads

Secondary Domain:    Top Dog.net
├─ Redirects to Top Dog.com
└─ Backup/failover option

Corporate Domain:    quellum.net
├─ company.quellum.net → Company info
├─ blog.quellum.net    → Blog posts
├─ careers.quellum.net → Job listings
└─ Can link to Top Dog.com for product
```

---

## 🎯 THREE DEPLOYMENT OPTIONS

### Option A: Unified Approach (Recommended)
- **Top Dog.com**: Your main product
- **Top Dog.net**: Backup/alias for Top Dog.com
- **quellum.net**: Corporate information & company site
- **Link**: quellum.net → Top Dog.com for product access

**Pros:**
- Clear separation (product vs. company)
- Professional brand hierarchy
- All domains serve a purpose
- Easy to explain to users

**Cons:**
- Requires managing 3+ domains
- More DNS records
- Slightly more complex

---

### Option B: Product-First Approach
- **Top Dog.com**: Everything (primary)
- **Top Dog.net**: Redirect to Top Dog.com
- **quellum.net**: Unused (or light landing page)

**Pros:**
- Simpler to manage
- All focus on Top Dog brand
- Easier DNS setup

**Cons:**
- Top Dog.net and quellum.net not leveraged
- Less brand separation

---

### Option C: Synergy Approach
- **Top Dog.com**: Product (www.Top Dog.com, api.Top Dog.com, etc.)
- **Top Dog.net**: Exact same copy (redundancy/SEO)
- **quellum.net**: Parent company/marketing site

**Pros:**
- Maximum brand presence
- SEO benefits (multiple domains)
- Professional company structure

**Cons:**
- Most complex to manage
- Duplicate content SEO issues (need canonicals)
- Most expensive

---

## 🚀 STEP-BY-STEP DEPLOYMENT (Option A - Recommended)

### Phase 1: Purchase & DNS Setup (1 hour)

#### 1.1 Purchase Domains
```
1. Go to: namecheap.com or godaddy.com
2. Search: Top Dog.com → Purchase
3. Search: Top Dog.net → Purchase
4. Review: quellum.net already owned ✓
```

#### 1.2 Create DNS Records for Top Dog.com

**In your domain registrar (Namecheap/GoDaddy):**

```
Record Type | Name              | Value
-----------|-------------------|----------------------------------
A          | @                 | [YOUR_SERVER_IP]
CNAME      | www               | @
CNAME      | api               | @
CNAME      | docs              | @
CNAME      | downloads         | @
CNAME      | status            | @
MX         | @                 | mail.example.com (if email needed)
TXT        | @                 | v=spf1 include:sendgrid.net ~all
```

**Example with DigitalOcean:**
```
Domain: Top Dog.com
Nameservers: 
  ns1.digitalocean.com
  ns2.digitalocean.com
  ns3.digitalocean.com
```

#### 1.3 Create DNS Records for Top Dog.net

```
Record Type | Name    | Value
-----------|---------|----------------------------------
CNAME      | @       | Top Dog.com
CNAME      | www     | Top Dog.com
CNAME      | api     | api.Top Dog.com
```

**Result**: Top Dog.net redirects to Top Dog.com ✓

#### 1.4 Update quellum.net

```
Record Type | Name    | Value
-----------|---------|----------------------------------
A          | www     | [COMPANY_SERVER_IP]
CNAME      | product | Top Dog.com
```

**Result**: quellum.net is company info, product link goes to Top Dog.com ✓

---

### Phase 2: Cloud Server Setup (2 hours)

#### 2.1 Create DigitalOcean Droplet

```bash
# Recommended specs for Top Dog
OS: Ubuntu 22.04 LTS
CPU: 2 vCPU
RAM: 4 GB
Storage: 80 GB SSD
Cost: ~$12/month
```

#### 2.2 Configure Server

```bash
# SSH into your server
ssh root@your_server_ip

# Update system
apt update && apt upgrade -y

# Install required tools
apt install -y nodejs npm python3.11 python3-pip git nginx postgresql

# Create app directory
mkdir -p /var/www/Top Dog
cd /var/www/Top Dog

# Clone your repo
git clone https://github.com/easttennesseecc-star/Q-Top-Dog-IDE.git .
```

#### 2.3 Install Application

```bash
# Backend setup
cd backend
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
npm run build

# Return to root
cd ..
```

#### 2.4 Configure Environment

```bash
# Create .env file with production keys
cat > backend/.env << EOF
# Production Environment
ENVIRONMENT=production

# URLs
FRONTEND_URL=https://Top Dog.com
BACKEND_URL=https://api.Top Dog.com
CORS_ORIGINS=https://Top Dog.com,https://www.Top Dog.com,https://Top Dog.net

# Stripe Production Keys
STRIPE_PUBLIC_KEY=pk_live_YOUR_PRODUCTION_KEY_HERE
STRIPE_SECRET_KEY=sk_live_YOUR_PRODUCTION_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET_HERE

# Database
DATABASE_URL=postgresql://user:password@localhost/qide_production

# LLM Config
GITHUB_COPILOT_API_KEY=your_api_key_here
GOOGLE_GEMINI_API_KEY=your_api_key_here
EOF
```

#### 2.5 Setup PostgreSQL Database

```bash
# Create database
sudo -u postgres psql << EOF
CREATE DATABASE qide_production;
CREATE USER qide_user WITH PASSWORD 'strong_password_here';
GRANT ALL PRIVILEGES ON DATABASE qide_production TO qide_user;
EOF

# Migrate database
cd /var/www/Top Dog/backend
python migrate.py
```

---

### Phase 3: SSL & Nginx Setup (1 hour)

#### 3.1 Install SSL Certificates (Let's Encrypt)

```bash
# Install Certbot
apt install -y certbot python3-certbot-nginx

# Create certificates for all subdomains
certbot certonly --nginx \
  -d Top Dog.com \
  -d www.Top Dog.com \
  -d api.Top Dog.com \
  -d docs.Top Dog.com \
  -d downloads.Top Dog.com \
  -d status.Top Dog.com
```

#### 3.2 Configure Nginx

```bash
# Create Nginx config
cat > /etc/nginx/sites-available/Top Dog << 'EOF'
# Frontend (www.Top Dog.com)
server {
    listen 443 ssl http2;
    server_name Top Dog.com www.Top Dog.com;
    
    ssl_certificate /etc/letsencrypt/live/Top Dog.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/Top Dog.com/privkey.pem;
    
    root /var/www/Top Dog/frontend/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# API (api.Top Dog.com)
server {
    listen 443 ssl http2;
    server_name api.Top Dog.com;
    
    ssl_certificate /etc/letsencrypt/live/Top Dog.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/Top Dog.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
        proxy_connect_timeout 60s;
    }
}

# HTTP Redirect
server {
    listen 80;
    server_name Top Dog.com www.Top Dog.com api.Top Dog.com docs.Top Dog.com downloads.Top Dog.com;
    return 301 https://$server_name$request_uri;
}

# Top Dog.net redirect
server {
    listen 443 ssl http2;
    server_name Top Dog.net www.Top Dog.net;
    
    ssl_certificate /etc/letsencrypt/live/Top Dog.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/Top Dog.com/privkey.pem;
    
    return 301 https://Top Dog.com$request_uri;
}
EOF

# Enable config
ln -s /etc/nginx/sites-available/Top Dog /etc/nginx/sites-enabled/Top Dog
rm /etc/nginx/sites-enabled/default 2>/dev/null

# Test and restart
nginx -t
systemctl restart nginx
```

#### 3.3 Setup Auto-Renewal

```bash
# Certbot auto-renewal
systemctl enable certbot.timer
systemctl start certbot.timer

# Verify
systemctl status certbot.timer
```

---

### Phase 4: Application Deployment (30 mins)

#### 4.1 Setup Backend Service

```bash
# Create systemd service
cat > /etc/systemd/system/Top Dog-backend.service << EOF
[Unit]
Description=Top Dog Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/Top Dog/backend
Environment="PATH=/var/www/Top Dog/backend/venv/bin"
ExecStart=/var/www/Top Dog/backend/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create venv
cd /var/www/Top Dog/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Enable and start
systemctl daemon-reload
systemctl enable Top Dog-backend
systemctl start Top Dog-backend
systemctl status Top Dog-backend
```

#### 4.2 Setup Log Rotation

```bash
# Configure log rotation
cat > /etc/logrotate.d/Top Dog << EOF
/var/www/Top Dog/backend/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
EOF
```

---

### Phase 5: Update Stripe Webhooks (10 mins)

#### 5.1 Switch Stripe to Production

```bash
# In Stripe Dashboard:
# 1. Switch from Test Mode to Live Mode
# 2. Get LIVE API keys
#    - pk_live_... (publishable key)
#    - sk_live_... (secret key)
# 3. Create webhook endpoint:
#    URL: https://api.Top Dog.com/api/billing/webhook
#    Events: (same as before)
#       - customer.subscription.created
#       - customer.subscription.updated
#       - customer.subscription.deleted
#       - invoice.payment_succeeded
#       - invoice.payment_failed
# 4. Copy webhook signing secret (whsec_live_...)
```

#### 5.2 Update .env with Production Keys

```bash
# Edit backend/.env
STRIPE_PUBLIC_KEY=pk_live_YOUR_PRODUCTION_KEY_HERE
STRIPE_SECRET_KEY=sk_live_YOUR_PRODUCTION_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_live_YOUR_WEBHOOK_SECRET_HERE
```

#### 5.3 Restart Backend

```bash
systemctl restart Top Dog-backend
```

---

### Phase 6: Testing (30 mins)

#### 6.1 Test All Domains

```bash
# Test www.Top Dog.com
curl -I https://www.Top Dog.com
# Expected: 200 OK

# Test api.Top Dog.com
curl -I https://api.Top Dog.com/health
# Expected: 200 OK

# Test Top Dog.net redirect
curl -I https://Top Dog.net
# Expected: 301 redirect to Top Dog.com
```

#### 6.2 Test SSL Certificates

```bash
# Check certificate validity
curl -vI https://Top Dog.com 2>&1 | grep certificate

# Should show: "certificate verify ok"
```

#### 6.3 Test Payment Processing

1. Open https://Top Dog.com in browser
2. Go to Pricing page
3. Select a paid tier
4. Use test card (if in test mode still):
   ```
   Card: 4242 4242 4242 4242
   Expires: 12/25
   CVC: 123
   ```
5. Verify payment processes
6. Check Stripe Dashboard shows transaction

#### 6.4 Monitor Logs

```bash
# Watch backend logs
tail -f /var/www/Top Dog/backend/logs/app.log

# Watch error logs
tail -f /var/www/Top Dog/backend/logs/error.log

# Search for errors
grep ERROR /var/www/Top Dog/backend/logs/*.log
```

---

## 📊 FINAL ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER BROWSERS                              │
└────────────┬────────────────────────────────────────────────────┘
             │
    ┌────────┴────────┬────────────┬────────────┐
    │                 │            │            │
    v                 v            v            v
Top Dog.com      Top Dog.net      docs.Top Dog.com downloads.Top Dog.com
(primary)      (redirect)     (static)       (files)
    │                 │
    └─────────┬───────┘
              │
              v
    ┌─────────────────────────┐
    │   NGINX Reverse Proxy   │
    │  (SSL Termination)      │
    └─────────┬───────────────┘
              │
      ┌───────┴────────┐
      │                │
      v                v
Frontend          Backend
(Next.js)         (FastAPI)
:3000             :8000
      │                │
      └───────┬────────┘
              │
              v
    ┌─────────────────────────┐
    │   PostgreSQL Database   │
    │   (User data, subs)     │
    └─────────────────────────┘
              │
              v
    ┌─────────────────────────┐
    │   Stripe (Production)   │
    │   (Payment processing)  │
    └─────────────────────────┘
```

---

## 💰 COST BREAKDOWN

| Item | Cost | Notes |
|------|------|-------|
| **Top Dog.com** | $15/year | Registrar fee |
| **Top Dog.net** | $10/year | Registrar fee |
| **quellum.net** | $10/year | Already owned |
| **DigitalOcean Droplet** | $12/month | 2 vCPU, 4GB RAM |
| **PostgreSQL Database** | FREE | On same droplet |
| **SSL Certificate** | FREE | Let's Encrypt |
| **Stripe** | 2.9% + $0.30 | Per transaction |
| **Bandwidth** | Included | First 1TB free |
| **Backups** | $1-2/month | Optional |
| **CDN** (optional) | $0-20/month | For faster loading |
| **Monitoring** (optional) | $0-10/month | Uptime monitoring |
| **Email** (optional) | $0-5/month | Transactional email |
| **TOTAL (basic)** | ~$180/year | Very affordable |

---

## 🔐 SECURITY CHECKLIST

- [ ] SSL certificates installed (https on all domains)
- [ ] Firewall configured (ufw)
- [ ] SSH key-based auth only (no passwords)
- [ ] Fail2ban installed (brute force protection)
- [ ] Rate limiting on API endpoints
- [ ] CORS configured correctly
- [ ] Database backups automated (daily)
- [ ] Stripe production keys secured in .env
- [ ] Regular security updates (apt upgrade weekly)
- [ ] Monitoring alerts setup (uptime, errors)

---

## 📱 MOBILE APP CONFIGURATION

```env
# For your mobile app to connect:
API_BASE_URL=https://api.Top Dog.com
STRIPE_PUBLIC_KEY=pk_live_YOUR_KEY_HERE
```

---

## 🎯 NEXT STEPS

### This Week:
1. [ ] Purchase Top Dog.com
2. [ ] Purchase Top Dog.net
3. [ ] Point nameservers to DigitalOcean

### Next Week:
4. [ ] Create DigitalOcean droplet
5. [ ] Deploy application
6. [ ] Setup SSL certificates
7. [ ] Test all domains

### Before Launch:
8. [ ] Switch Stripe to production
9. [ ] Test payment processing
10. [ ] Monitor logs and performance
11. [ ] **🎉 LAUNCH!**

---

## 📞 SUPPORT RESOURCES

**Registrar Support:**
- Namecheap: https://www.namecheap.com/support
- GoDaddy: https://www.godaddy.com/help

**DigitalOcean:**
- Documentation: https://docs.digitalocean.com
- Community: https://www.digitalocean.com/community

**Let's Encrypt:**
- Certbot: https://certbot.eff.org

**Nginx:**
- Documentation: https://nginx.org/en/docs

---

## 🚀 Ready to Deploy?

Once you have the three domains purchased, I can:
1. ✅ Create detailed DNS records for your registrar
2. ✅ Provide exact DigitalOcean setup steps
3. ✅ Help with SSL certificate setup
4. ✅ Configure everything for production
5. ✅ Test the entire system end-to-end

**Just let me know when you're ready!** 🎉

