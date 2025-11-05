# 🔧 IMMEDIATE ACTION REQUIRED - DigitalOcean Deployment Fix

## Current Problem
- **Top Dog.com**: SSL/TLS connection errors
- **topdog-ide.com**: Domain doesn't resolve  
- **Status**: Deployment broken - product not accessible

---

## Step-by-Step Fix (30-60 minutes)

### STEP 1: Access DigitalOcean Dashboard
1. Go to: https://cloud.digitalocean.com/
2. Log in with your credentials
3. Look for "Apps Platform" in left sidebar

### STEP 2: Find the App
Look for an app named:
- `Top Dog-production` OR
- `quellum-topdog-ai` OR  
- Similar name with "Top Dog" or "topdog"

### STEP 3: Check App Status
1. Click on the app
2. Look for status indicator:
   - 🟢 **ACTIVE** = Good, move to Step 5
   - 🔴 **ERROR** = Problem, move to Step 4
   - 🟡 **DEPLOYING** = Wait for it to finish

### STEP 4: If App is in ERROR
1. Click **Settings** tab
2. Look for recent error messages in **Logs**
3. Common issues:
   - **"Build failed"** = Code/dependency issue
   - **"Health check failed"** = App crashing
   - **"Connection refused"** = Database not connected
4. Click **Redeploy** button to try again

### STEP 5: If App is ACTIVE but Domain Not Responding

#### A. Verify SSL Certificate
1. Go to **Settings** → **Domains**
2. Look for domain entries:
   - `Top Dog.com` (PRIMARY)
   - `www.Top Dog.com` (ALIAS)
3. Check if HTTPS shows 🔒 (locked) or ⚠️ (warning)
4. If warning: Click **Renew Certificate** or **Force HTTPS**

#### B. Verify DNS Records
1. Still in **Domains** section
2. Check the **Name Servers** DigitalOcean assigned
3. Must be something like:
   ```
   ns1.digitalocean.com
   ns2.digitalocean.com
   ns3.digitalocean.com
   ```
4. Go to domain registrar (GoDaddy, Namecheap, etc.)
5. Update domain nameservers to match DigitalOcean's

#### C. Check Environment Variables
1. Go to **Settings** → **Environment**
2. Verify these are set:
   ```
   ENVIRONMENT=production
   DEBUG=false
   BACKEND_URL=https://Top Dog.com  (or https://api.Top Dog.com)
   FRONTEND_URL=https://Top Dog.com
   STRIPE_SECRET_KEY=sk_live_...  (NOT test key!)
   STRIPE_PUBLISHABLE_KEY=pk_live_...  (NOT test key!)
   ```
3. If any missing: Add them
4. Click **Save and Redeploy**

### STEP 6: Monitor Redeployment
1. After saving, watch the **Logs** tab
2. Should see:
   ```
   ✓ Backend service deploying
   ✓ Frontend service deploying
   ✓ Database ready
   ✓ All health checks passing
   ```
3. Takes 2-5 minutes typically
4. When done, status should show 🟢 ACTIVE

### STEP 7: Test the Deployment

Once ACTIVE, test from local command line:

```powershell
# Test DNS
nslookup Top Dog.com

# Test SSL
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
Invoke-WebRequest -Uri "https://Top Dog.com" -MaximumRedirection 2

# Should get 200 OK
```

### STEP 8: If Still Not Working

Check **App Logs** for specific errors:

**Common Errors & Fixes:**

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: No module named 'fastapi'` | Backend dependencies not installed. Redeploy. |
| `Database connection refused` | Check DATABASE_URL env var. Verify managed DB is active. |
| `SSL certificate not found` | Let's Encrypt failed. Click "Force HTTPS" and wait. |
| `Stripe API key invalid` | Update STRIPE_SECRET_KEY to live key (starts with `sk_live_`) |
| `CORS error in console` | Update CORS_ORIGINS in environment to include domain |

---

## Quick Checklist

```
☐ DigitalOcean app is in ACTIVE state
☐ Top Dog.com DNS resolves to DigitalOcean IP
☐ HTTPS certificate is valid (no SSL errors)
☐ Environment variables are set for production
☐ Database connection working
☐ Backend health check passing (/health returns 200)
☐ Frontend loads without 502/503 errors
☐ Can access https://Top Dog.com in browser
☐ Sign-up page loads
☐ Free trial can be started
```

---

## If It's Still Broken - Advanced Debugging

1. **Get app ID**:
   - Go to DigitalOcean dashboard
   - Click app → URL shows: `https://cloud.digitalocean.com/apps/{APP_ID}`
   - Copy the APP_ID

2. **Use doctl CLI** (if installed):
   ```powershell
   doctl auth init  # Log in
   doctl apps list  # Show all apps
   doctl apps describe {APP_ID}  # Get details
   doctl apps logs {APP_ID} --app  # Show logs
   doctl apps create-deployment {APP_ID} --wait  # Force redeploy
   ```

3. **Check GitHub Actions**:
   - Go to https://github.com/easttennesseecc-star/Q-Top-Dog-IDE
   - Click **Actions** tab
   - Look for most recent deploy
   - If it shows ❌ red X = GitHub Actions failed
   - Check what the error was

---

## Support & Next Steps

Once deployed and working:

1. ✅ Open https://Top Dog.com in browser
2. ✅ Sign up for free trial
3. ✅ Test LLM model selection
4. ✅ Test game engine selection
5. ✅ Test Stripe billing
6. ✅ Test pair programming with another user
7. ✅ Monitor for 1 hour to ensure stability

---

**Status**: Deployment needs intervention - app may be down or misconfigured  
**Time to fix**: 15-60 minutes depending on root cause  
**You need**: DigitalOcean account access + git push access
