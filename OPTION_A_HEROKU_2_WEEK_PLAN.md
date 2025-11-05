# 🚀 OPTION A: Heroku MVP Launch - 2 Week Execution Plan

**Decision Made**: Heroku (simplest, fastest)  
**Timeline**: 2 weeks (10 working days)  
**Team**: 1-2 people  
**Cost**: $50-100/month  
**Outcome**: Live MVP with real users

---

## Executive Overview

You're going to **deploy Top Dog to production in 2 weeks** using Heroku. This is the fastest path to real users and real feedback.

### What You'll Have After 2 Weeks
✅ Live URL that users can visit  
✅ Real database persisting data  
✅ OAuth login working  
✅ Full feature set available  
✅ Basic monitoring  
✅ Production-grade security (basic level)  

### What You're NOT Doing (Save for Later)
❌ Advanced Kubernetes clustering  
❌ Complex auto-scaling  
❌ Enterprise monitoring  
❌ Advanced disaster recovery  

These can all be added in Month 2 if needed.

---

## Week 1: Deploy to Heroku (Days 1-5)

### Day 1: Preparation & Setup (8 hours)

#### Morning (4 hours): Docker Preparation

```
TASKS:
1. Review backend code structure
   ├─ Check main.py entry point ✓
   ├─ Check requirements.txt ✓
   └─ Identify environment variables needed

2. Create backend/Dockerfile
   └─ Multi-stage build
   └─ Python 3.11 slim image
   └─ Install dependencies
   └─ Run port 8000

3. Create backend/.dockerignore
   └─ Exclude __pycache__
   └─ Exclude .venv
   └─ Exclude *.pyc
   └─ Exclude .env

TIME: 4 hours
BLOCKER: None
OUTPUT: Working backend Dockerfile
```

**Action Items:**
- [ ] Create `backend/Dockerfile`
- [ ] Create `backend/.dockerignore`
- [ ] Test build locally: `docker build -t Top Dog-backend .`

**Dockerfile Template** (save as `backend/Dockerfile`):
```dockerfile
# Multi-stage build
FROM python:3.11-slim as builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Set environment
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["python", "main.py"]
```

#### Afternoon (4 hours): Frontend Docker

```
TASKS:
1. Review frontend structure
   ├─ Check package.json ✓
   ├─ Check build command ✓
   └─ Identify environment variables

2. Create frontend/Dockerfile
   └─ Node.js build stage
   └─ Production serve stage
   └─ Run port 3000

3. Create frontend/.dockerignore
   └─ Exclude node_modules
   └─ Exclude build
   └─ Exclude .env

TIME: 4 hours
BLOCKER: None
OUTPUT: Working frontend Dockerfile
```

**Action Items:**
- [ ] Create `frontend/Dockerfile`
- [ ] Create `frontend/.dockerignore`
- [ ] Test build locally: `docker build -t Top Dog-frontend .`

**Dockerfile Template** (save as `frontend/Dockerfile`):
```dockerfile
# Build stage
FROM node:18-alpine as builder

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install

COPY . .
RUN pnpm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

RUN npm install -g serve

COPY --from=builder /app/dist ./dist

ENV PORT=3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["serve", "-s", "dist", "-l", "3000"]
```

**Day 1 Completion Checklist:**
- [ ] backend/Dockerfile created and tested
- [ ] frontend/Dockerfile created and tested
- [ ] Both build successfully locally
- [ ] Both run successfully locally
- [ ] Environment variables identified

---

### Day 2: Heroku Setup (8 hours)

#### Morning (4 hours): Create Heroku Account & Apps

```
TASKS:
1. Sign up for Heroku
   └─ Go to heroku.com
   └─ Create free account
   └─ Verify email
   └─ Install Heroku CLI

2. Create 2 Heroku apps
   └─ heroku create Top Dog-backend
   └─ heroku create Top Dog-frontend
   └─ Note the generated URLs

3. Add PostgreSQL addon to backend app
   └─ heroku addons:create heroku-postgresql:hobby-dev
   └─ This gives you a free database

TIME: 4 hours
BLOCKER: Need email verification
OUTPUT: 2 Heroku apps + database
```

**Command Reference:**
```bash
# Install Heroku CLI (if not already)
npm install -g heroku

# Login to Heroku
heroku login

# Create apps
heroku create Top Dog-backend
heroku create Top Dog-frontend

# Add PostgreSQL to backend
heroku addons:create heroku-postgresql:hobby-dev --app Top Dog-backend

# Get database URL
heroku config:get DATABASE_URL --app Top Dog-backend
```

**Action Items:**
- [ ] Create Heroku account
- [ ] Install Heroku CLI
- [ ] Create Top Dog-backend app
- [ ] Create Top Dog-frontend app
- [ ] Add PostgreSQL database
- [ ] Note all 3 URLs (backend, frontend, database)

#### Afternoon (4 hours): Configure Environment Variables

```
TASKS:
1. Get database URL from Heroku
   └─ DATABASE_URL will be created automatically

2. Set environment variables for backend
   └─ DATABASE_URL (from addon)
   └─ LLM_API_KEYS (from your config)
   └─ OAUTH_CLIENT_ID
   └─ OAUTH_CLIENT_SECRET
   └─ FRONTEND_URL (the frontend Heroku URL)

3. Set environment variables for frontend
   └─ VITE_API_URL (the backend Heroku URL)

TIME: 4 hours
BLOCKER: Need to gather all API keys
OUTPUT: All env vars configured
```

**Command Reference:**
```bash
# View current config
heroku config --app Top Dog-backend

# Set a variable
heroku config:set DATABASE_URL="..." --app Top Dog-backend

# Set multiple variables at once
heroku config:set \
  FRONTEND_URL="https://Top Dog-frontend.herokuapp.com" \
  LLM_API_KEY="your-key" \
  OAUTH_CLIENT_ID="your-id" \
  OAUTH_CLIENT_SECRET="your-secret" \
  --app Top Dog-backend

# For frontend
heroku config:set \
  VITE_API_URL="https://Top Dog-backend.herokuapp.com" \
  --app Top Dog-frontend
```

**Action Items:**
- [ ] Gather all API keys and secrets
- [ ] Set backend environment variables
- [ ] Set frontend environment variables
- [ ] Verify with `heroku config`

**Day 2 Completion Checklist:**
- [ ] Heroku accounts created
- [ ] 2 apps created
- [ ] PostgreSQL database added
- [ ] All environment variables set
- [ ] Ready to deploy

---

### Day 3-4: Deploy Backend (16 hours)

#### Day 3 (8 hours): Backend Deployment

```
TASKS:
1. Push code to Heroku
   └─ heroku git:remote -a Top Dog-backend
   └─ git push heroku main

2. Monitor deployment
   └─ heroku logs --tail --app Top Dog-backend
   └─ Watch for errors
   └─ Fix if needed

3. Verify health endpoint
   └─ curl https://Top Dog-backend.herokuapp.com/health
   └─ Should return 200 OK

4. Check database connection
   └─ heroku logs --app Top Dog-backend
   └─ Look for "Database connected"

TIME: 8 hours (mostly waiting for build)
BLOCKER: Build failures need debugging
OUTPUT: Backend running on Heroku
```

**Command Reference:**
```bash
# Connect Heroku remote
cd backend
heroku git:remote -a Top Dog-backend

# Deploy
git push heroku main

# Watch logs
heroku logs --tail --app Top Dog-backend

# Test health endpoint
curl https://Top Dog-backend.herokuapp.com/health

# If deployment fails, check:
heroku logs --app Top Dog-backend | tail -50
```

**Troubleshooting:**
- **Build fails**: Check `heroku logs`, look for missing dependencies
- **Port error**: Ensure main.py reads PORT environment variable
- **Database error**: Check DATABASE_URL is set correctly
- **404 on health**: May be building, wait 2-3 minutes

**Action Items:**
- [ ] Deploy backend to Heroku
- [ ] Check logs for errors
- [ ] Health endpoint responds (200 OK)
- [ ] Database connected
- [ ] Backend URL working

#### Day 4 (8 hours): Test Backend

```
TASKS:
1. Test API endpoints
   ├─ GET /health → 200 OK
   ├─ POST /api/auth/login → Works
   ├─ GET /api/projects → Works
   └─ POST /api/chat → Works

2. Test OAuth flow
   ├─ Click login button
   ├─ Redirect to GitHub/Google
   ├─ Login works
   ├─ Redirects back

3. Test database
   ├─ Create project via UI
   ├─ Check data persists
   ├─ Refresh page, data still there

4. Monitor for errors
   ├─ Check heroku logs for warnings
   ├─ Fix any critical issues
   └─ Document all for Week 2

TIME: 8 hours
BLOCKER: OAuth redirect URLs need updating
OUTPUT: Backend fully tested
```

**OAuth Configuration Update Needed:**
```
GitHub OAuth:
  - Redirect URL: https://Top Dog-backend.herokuapp.com/oauth/callback/github

Google OAuth:
  - Redirect URL: https://Top Dog-backend.herokuapp.com/oauth/callback/google
```

**Update in:**
- GitHub Developer Settings
- Google Cloud Console

**Action Items:**
- [ ] Update OAuth redirect URLs
- [ ] Test all API endpoints
- [ ] Test OAuth login flow
- [ ] Test database persistence
- [ ] Review logs for warnings
- [ ] Document any issues

**Day 3-4 Completion Checklist:**
- [ ] Backend deployed to Heroku
- [ ] All health checks passing
- [ ] OAuth working
- [ ] Database persisting data
- [ ] Logs show no critical errors

---

### Day 5: Deploy Frontend (8 hours)

#### Deploy Frontend

```
TASKS:
1. Deploy frontend to Heroku
   └─ cd frontend
   └─ heroku git:remote -a Top Dog-frontend
   └─ git push heroku main

2. Monitor deployment
   └─ heroku logs --tail --app Top Dog-frontend
   └─ Watch for build success

3. Verify frontend loads
   └─ Open https://Top Dog-frontend.herokuapp.com
   └─ Should see login screen
   └─ No console errors

4. Test full flow
   ├─ Login with OAuth
   ├─ Create a project
   ├─ Use LLM features
   ├─ Verify everything works

5. Check logs
   └─ heroku logs --app Top Dog-frontend
   └─ heroku logs --app Top Dog-backend
   └─ No critical errors

TIME: 8 hours
BLOCKER: CORS or API connection issues
OUTPUT: Full stack live
```

**Command Reference:**
```bash
# Navigate to frontend
cd frontend

# Connect Heroku remote
heroku git:remote -a Top Dog-frontend

# Deploy
git push heroku main

# Watch logs
heroku logs --tail --app Top Dog-frontend

# Test the URL
# Open: https://Top Dog-frontend.herokuapp.com
```

**Troubleshooting:**
- **Blank page**: Check browser console, look for errors
- **Can't connect to API**: Check VITE_API_URL is correct
- **CORS errors**: May need to update CORS settings in backend
- **OAuth redirect fails**: Check redirect URLs are updated

**Action Items:**
- [ ] Deploy frontend to Heroku
- [ ] Frontend loads successfully
- [ ] Can login with OAuth
- [ ] Can create projects
- [ ] LLM features work
- [ ] No critical console errors

**Day 5 Completion Checklist:**
- [ ] Frontend deployed
- [ ] UI loads correctly
- [ ] All features working
- [ ] OAuth flow complete
- [ ] Full user journey works
- [ ] Ready for Week 2

**END OF WEEK 1: MVP LIVE! 🎉**

---

## Week 2: Security & Hardening (Days 6-10)

### Day 6: Secrets Management (8 hours)

#### Audit Secrets

```
TASKS:
1. Find all hardcoded secrets in code
   ├─ Search for "key" in backend
   ├─ Search for "secret" in frontend
   ├─ Search for "password"
   └─ Document findings

2. Remove from .env files
   ├─ Delete any .env files with secrets
   ├─ Update .gitignore
   ├─ Ensure no secrets in git history

3. Move to Heroku Config Vars
   └─ All secrets → heroku config:set
   └─ Verify no secrets visible

TIME: 8 hours
BLOCKER: Need to identify all secrets
OUTPUT: All secrets secured
```

**Action Items:**
- [ ] Audit code for hardcoded secrets
- [ ] Remove from codebase
- [ ] Ensure in Heroku Config Vars
- [ ] Verify not in git history

### Day 7-8: Security Headers & Rate Limiting (16 hours)

#### Configure Security

```
TASKS:
1. Add security headers (backend)
   ├─ X-Frame-Options: SAMEORIGIN
   ├─ X-Content-Type-Options: nosniff
   ├─ Strict-Transport-Security: max-age=31536000
   └─ Content-Security-Policy headers

2. Implement rate limiting
   ├─ Rate limit API endpoints
   ├─ 100 requests/minute per IP
   ├─ Return 429 when exceeded

3. Update CORS
   ├─ Remove wildcard (*)
   ├─ Specify exact frontend URL
   └─ Test from frontend

TIME: 16 hours
BLOCKER: Backend coding needed
OUTPUT: Hardened API
```

**Action Items:**
- [ ] Add security headers
- [ ] Implement rate limiting
- [ ] Update CORS settings
- [ ] Test with frontend
- [ ] Verify no breaking changes

### Day 9: HTTPS & Compliance (8 hours)

#### Verify Security

```
TASKS:
1. Verify HTTPS
   ├─ Heroku provides free SSL
   ├─ All traffic is HTTPS
   ├─ HTTP redirects to HTTPS

2. Check SSL certificate
   ├─ Visit https://www.ssllabs.com
   ├─ Test your Heroku URL
   ├─ Aim for A rating

3. Compliance check
   ├─ Create privacy policy
   ├─ Create terms of service
   ├─ Document GDPR compliance

TIME: 8 hours
BLOCKER: None (Heroku handles most)
OUTPUT: A+ SSL rating
```

**Action Items:**
- [ ] Verify HTTPS working
- [ ] Test with SSL Labs
- [ ] Create privacy policy
- [ ] Create terms of service
- [ ] Document compliance

### Day 10: Final Testing & Validation (8 hours)

#### Production Smoke Tests

```
TASKS:
1. User signup flow
   ├─ New user can sign up
   ├─ Email verification (if applicable)
   ├─ Account created

2. OAuth flow
   ├─ Login with GitHub
   ├─ Login with Google
   ├─ All working

3. Core features
   ├─ Create project
   ├─ Use LLM chat
   ├─ Save work
   ├─ Everything persists

4. Performance
   ├─ Check response times
   ├─ Check no 500 errors
   ├─ Monitor Heroku logs

5. Cross-browser
   ├─ Chrome ✓
   ├─ Firefox ✓
   ├─ Safari ✓
   ├─ Mobile ✓

TIME: 8 hours
BLOCKER: None
OUTPUT: Ready to announce
```

**Action Items:**
- [ ] Test new user signup
- [ ] Test OAuth flows
- [ ] Test all core features
- [ ] Test on multiple browsers
- [ ] Check performance
- [ ] Verify logs clean

**END OF WEEK 2: PRODUCTION READY! ✅**

---

## Heroku Dashboard Monitoring (Quick & Easy)

Once deployed, you can monitor right from Heroku dashboard:

```
HEROKU DASHBOARD
├─ Dyno status (is it running?)
├─ Recent logs (any errors?)
├─ Add-ons status (is database running?)
├─ Metrics (CPU, memory usage)
└─ Activity (deployment history)
```

**Free Monitoring Includes:**
- ✅ Logs (50 most recent entries)
- ✅ Dyno status
- ✅ Error tracking (basic)
- ✅ CPU/memory graphs

---

## Post-Launch: Your First Week as "Live"

### Immediately After Launch
```
WEEK 1 TASKS:
├─ Share URL with beta testers
├─ Monitor Heroku logs 24/7
├─ Watch for error spikes
├─ Respond quickly to issues
└─ Gather user feedback
```

### Success Metrics After 2 Weeks
```
YOU'LL KNOW YOU'RE SUCCESSFUL IF:
✅ Backend responding to all requests
✅ Database persisting data
✅ OAuth login working
✅ No 500 errors in logs
✅ <1 second response times
✅ First users testing it
```

---

## Common Issues & Quick Fixes

### Issue: "Application Error"
**Solution**: 
```bash
heroku logs --app Top Dog-backend
# Look for the error, fix it locally, push again
git push heroku main
```

### Issue: Can't Connect to Database
**Solution**:
```bash
# Verify DATABASE_URL is set
heroku config:get DATABASE_URL --app Top Dog-backend

# If not set, add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev --app Top Dog-backend
```

### Issue: CORS Errors
**Solution**:
```python
# In backend main.py, update CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://Top Dog-frontend.herokuapp.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Frontend Shows Blank Page
**Solution**:
```bash
# Check browser console for errors
# Ensure VITE_API_URL is correct
heroku config --app Top Dog-frontend | grep VITE_API_URL

# Should be: https://Top Dog-backend.herokuapp.com
```

---

## Budget: $50-100/Month

```
Heroku Costs:
├─ Dyno (backend): $25/month
├─ Dyno (frontend): $25/month
├─ PostgreSQL Database: $9/month
└─ Total: $59/month

Optional Add-ons:
├─ Scheduler (cron jobs): $10/month
├─ Redis cache: $15/month (optional)
└─ Enhanced logging: $50/month (optional)

For MVP, you only need: $59/month
```

---

## Timeline Summary

```
DAY 1: Docker setup (8 hours)
DAY 2: Heroku setup (8 hours)
DAY 3-4: Deploy backend (16 hours)
DAY 5: Deploy frontend (8 hours)
──────────────────────────
WEEK 1: 40 hours → MVP LIVE ✅

DAY 6: Secrets management (8 hours)
DAY 7-8: Security hardening (16 hours)
DAY 9: HTTPS & compliance (8 hours)
DAY 10: Final testing (8 hours)
──────────────────────────
WEEK 2: 40 hours → PRODUCTION READY ✅

Total: 80 hours for 1 person
```

---

## Success Criteria

### After Week 1
- ✅ Live URL accessible
- ✅ All features working
- ✅ Users can sign up and login
- ✅ Data persists in database

### After Week 2
- ✅ All secrets secured
- ✅ Security headers active
- ✅ HTTPS enforced
- ✅ No critical errors
- ✅ Ready for real users

---

## Next: Week 3+ (Scale & Improve)

After you launch, you can optionally add:

**Week 3+:**
- Add monitoring (DataDog, Sentry)
- Set up error tracking
- Performance optimization
- Backup procedures
- Analytics

But these are NOT required for MVP launch.

---

## Your Starting Point Tomorrow

**Tomorrow morning, start with Day 1:**

1. Create `backend/Dockerfile`
2. Create `frontend/Dockerfile`
3. Test both build locally
4. Move forward to Day 2

**You've got this!** 🚀

---

**Timeline**: 2 weeks  
**Effort**: 80 hours (1 person)  
**Cost**: $59/month  
**Outcome**: MVP live with real users  
**Next**: Gather feedback and improve

**Let's ship Top Dog!** 🌍

