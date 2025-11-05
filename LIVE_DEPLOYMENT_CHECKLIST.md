# 🔧 LIVE DEPLOYMENT FIX CHECKLIST
## Follow These Steps IN YOUR DigitalOcean Dashboard RIGHT NOW

---

## ✅ STEP 1: Find Your App

**In DigitalOcean Dashboard:**
1. Click **Apps Platform** (left sidebar)
2. Look for app named:
   - `Top Dog-production` OR
   - `quellum-topdog-ai` OR
   - `Top Dog` OR similar
3. **REPORT BACK**: What app name do you see?

---

## ✅ STEP 2: Check App Status

**Look at the top of the app page:**
- 🟢 **ACTIVE** = Good! Go to STEP 3
- 🔴 **ERROR** = Problem! Go to STEP 2B
- 🟡 **DEPLOYING** = Wait, come back in 2 min
- ⏸️ **INACTIVE** = App is paused, click **Resume**

### If ERROR (STEP 2B):
1. Scroll down to **Logs** tab
2. Copy the ERROR message you see
3. **REPORT BACK**: What's the exact error?

---

## ✅ STEP 3: Check Domains & SSL

**Still in the app page:**
1. Click **Settings** tab (top)
2. Scroll to **Domains** section
3. You should see:
   - ☑️ `Top Dog.com` (PRIMARY)
   - ☑️ `www.Top Dog.com` (ALIAS)

**Check SSL Status:**
- 🔒 **HTTPS (green lock)** = Good! Go to STEP 4
- ⚠️ **WARNING (yellow)** = SSL issue
- ❌ **ERROR (red)** = Certificate broken

### If SSL Problem:
1. Find the domain row
2. Click the **...** (three dots) menu
3. Select **Renew Certificate** OR **Force HTTPS**
4. Wait 2-3 minutes
5. Refresh the page
6. Should show 🔒 HTTPS now

**REPORT BACK**: Is SSL showing green 🔒 now?

---

## ✅ STEP 4: Verify Environment Variables

**Still in Settings:**
1. Click **Environment** section
2. Verify these are set (should be VISIBLE):

```
ENVIRONMENT=production        ← Should say "production" NOT "development"
DEBUG=false                   ← Should be "false" NOT "true"
BACKEND_URL=https://Top Dog.com  (or https://api.Top Dog.com)
FRONTEND_URL=https://Top Dog.com
STRIPE_SECRET_KEY=sk_live_... ← Must start with "sk_live_" NOT "sk_test_"
STRIPE_PUBLISHABLE_KEY=pk_live_... ← Must start with "pk_live_" NOT "pk_test_"
```

### Missing or Wrong Variables?
1. Click **Edit** button
2. Add/fix the variable
3. Click **Save**
4. The app will automatically redeploy
5. Wait for deployment to finish

**REPORT BACK**: Are all environment variables correct?

---

## ✅ STEP 5: Check Services Status

**Still in app page:**
1. Click **Deployments** tab
2. Look at the most recent deployment
3. You should see TWO services:
   - **backend-api** → Status: ✅ RUNNING
   - **frontend-web** → Status: ✅ RUNNING

### If Either Shows ERROR:
1. Click on the service name
2. Check the logs for error message
3. Common issues:
   - **"502 Bad Gateway"** = Backend crashed
   - **"404 Not Found"** = Frontend bundle missing
   - **"Connection timeout"** = Database not accessible

**REPORT BACK**: What's the status of both services?

---

## ✅ STEP 6: Redeploy If Needed

**If you changed any environment variables OR there's an error:**

1. Click **Actions** button (top right)
2. Select **Redeploy**
3. Click **Redeploy** to confirm
4. Watch the deployment progress in **Deployments** tab
5. Should take 3-5 minutes

**While deploying, you'll see:**
```
⏳ Queued
⏳ Building
⏳ Building backend...
⏳ Building frontend...
⏳ Deploying backend...
⏳ Deploying frontend...
✅ Deployment successful
```

**REPORT BACK**: Did deployment succeed or fail?

---

## ✅ STEP 7: Test Backend Health

**Once deployment is ACTIVE:**

1. Open a new browser tab
2. Go to: `https://Top Dog.com/health`
3. You should see JSON response:
```json
{
  "status": "ok",
  "message": "Backend is running"
}
```

### If you get:
- ✅ **200 OK** = Backend working!
- ❌ **502 Bad Gateway** = Backend crashed
- ❌ **503 Service Unavailable** = Deployment not done
- ❌ **Connection refused** = Domain not resolving

**REPORT BACK**: What HTTP status do you get?

---

## ✅ STEP 8: Test Frontend Loading

1. Go to: `https://Top Dog.com/`
2. You should see the TopDog IDE landing page loading
3. Check browser console (F12 → Console tab)
4. Should be NO red errors

### If you see errors:
1. Check what the error says
2. Common ones:
   - **"CORS error"** = Update CORS_ORIGINS environment variable
   - **"404 not found /assets/..."** = Frontend build incomplete
   - **"Cannot connect to API"** = Backend URL wrong in environment

**REPORT BACK**: Does the page load? Any errors in console?

---

## ✅ STEP 9: Final Checks

Once everything loads:

1. ✅ Can you see the landing page?
2. ✅ Does it say "TopDog IDE"?
3. ✅ Can you click "Sign Up"?
4. ✅ Does sign-up form appear?
5. ✅ Can you see pricing tiers?

**REPORT BACK**: What can you see working?

---

## 🚨 If ANYTHING Fails

**For EACH problem:**
1. Check the **Logs** tab
2. Copy the error message exactly
3. Report it back with the step number

**Example:**
```
STEP 5 FAILED:
Service: backend-api
Error: "ModuleNotFoundError: No module named 'fastapi'"
```

---

## Quick Summary

| Step | What to Do | ✅ Success = |
|------|-----------|------------|
| 1 | Find app | You see app name |
| 2 | Check status | Shows 🟢 ACTIVE |
| 3 | Check SSL | Shows 🔒 HTTPS |
| 4 | Verify env vars | All production values set |
| 5 | Check services | backend-api ✅ + frontend-web ✅ |
| 6 | Redeploy if needed | Shows "Deployment successful" |
| 7 | Test /health | Returns 200 OK |
| 8 | Test landing page | Page loads, no errors |
| 9 | Final verification | Can see landing page, sign-up works |

---

**Start with STEP 1 and report back what you find!**
