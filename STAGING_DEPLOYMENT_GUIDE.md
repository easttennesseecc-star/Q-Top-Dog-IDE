# Staging Deployment Guide

## Status: ✅ Ready for Staging Deployment

**Completed:**
- ✅ All 31 AI Marketplace tests passing (100%)
- ✅ All 17 Monitoring tests passing (100%)
- ✅ Comprehensive monitoring system with 15+ endpoints
- ✅ Health checks (liveness, readiness, full health)
- ✅ Performance metrics and error tracking
- ✅ Alert system with automatic thresholds

---

## Pre-Deployment Checklist

### Infrastructure Preparation
- [ ] Choose hosting platform (Heroku, AWS, DigitalOcean, or Railway)
- [ ] Set up PostgreSQL database
- [ ] Configure environment variables
- [ ] Set up domain/SSL certificates
- [ ] Configure firewall rules

### Code Preparation
- [ ] All tests passing locally (✅ 48/48 tests passing)
- [ ] Code review completed
- [ ] Security review completed
- [ ] Dependencies locked in requirements.txt (✅)
- [ ] Environment configuration in .env template

### Monitoring Setup
- [ ] Monitoring endpoints configured
- [ ] Health checks operational
- [ ] Logging configured
- [ ] Alerts configured
- [ ] Dashboard accessible

### Documentation
- [ ] README with deployment instructions
- [ ] API documentation generated
- [ ] Runbooks created for common issues
- [ ] Incident response plan ready

---

## Deployment Options

### Option 1: Heroku (Recommended - Easiest)

**Timeline:** ~1 hour  
**Cost:** Free tier available, $7+/month for production

#### Steps:

1. **Install Heroku CLI**
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   heroku login
   ```

2. **Create Heroku App**
   ```bash
   heroku create your-app-name
   heroku addons:create heroku-postgresql:standard-0
   ```

3. **Deploy Code**
   ```bash
   git push heroku main
   ```

4. **Configure Environment**
   ```bash
   heroku config:set ENVIRONMENT=production
   heroku config:set DEBUG=false
   heroku config:set DATABASE_URL=<postgres_url>
   ```

5. **Run Migrations**
   ```bash
   heroku run python migrate.py
   ```

6. **View Logs**
   ```bash
   heroku logs --tail
   ```

7. **Access Application**
   ```
   https://your-app-name.herokuapp.com
   https://your-app-name.herokuapp.com/api/monitoring/health
   https://your-app-name.herokuapp.com/api/monitoring/status
   ```

### Option 2: DigitalOcean (Recommended - More Control)

**Timeline:** ~2 hours  
**Cost:** $5-20/month for app platform

#### Steps:

1. **Create App on App Platform**
   - Connect GitHub repository
   - Set build command: `pip install -r requirements.txt`
   - Set run command: `uvicorn main:app --host 0.0.0.0 --port 8080`

2. **Configure Database**
   - Create managed PostgreSQL database
   - Add connection string to environment

3. **Deploy**
   - Push to GitHub
   - DigitalOcean auto-deploys

4. **Configure Domain**
   - Point domain to DigitalOcean
   - Enable HTTPS

### Option 3: AWS (Most Powerful)

**Timeline:** ~3-4 hours  
**Cost:** $20-50+/month

#### Steps:

1. **Set up EC2 Instance**
   ```bash
   # Ubuntu 22.04 LTS
   # t3.small or larger
   ```

2. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install python3.11 python3-pip postgresql
   pip install -r requirements.txt
   ```

3. **Run Application**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 main:app
   ```

4. **Configure RDS Database**
   - Create managed PostgreSQL instance
   - Update connection string

5. **Set up Load Balancer**
   - Create Application Load Balancer
   - Configure health check: `/api/monitoring/health/live`

---

## Deployment Validation

### Step 1: Verify Health Checks

```bash
# Liveness probe (service is running)
curl https://your-domain.com/api/monitoring/health/live
# Expected: {"status": "alive", "timestamp": "..."}

# Readiness probe (ready for traffic)
curl https://your-domain.com/api/monitoring/health/ready
# Expected: {"status": "ready", "ready": true, ...}

# Full health check
curl https://your-domain.com/api/monitoring/health
# Expected: Comprehensive health status
```

### Step 2: Verify API Endpoints

```bash
# Status page (HTML)
curl https://your-domain.com/api/monitoring/status

# Performance metrics
curl https://your-domain.com/api/monitoring/metrics/performance

# System dashboard
curl https://your-domain.com/api/monitoring/dashboard/json
```

### Step 3: Verify Marketplace Functionality

```bash
# Create test user and verify flow
curl -X POST https://your-domain.com/api/users/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"password123"}'

# List models
curl https://your-domain.com/api/models

# Search models
curl "https://your-domain.com/api/models/search?query=code%20generation"
```

### Step 4: Verify Database

```bash
# Connect to database
psql $DATABASE_URL

# Check tables
\dt

# Verify data
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM models;
SELECT COUNT(*) FROM api_keys;
```

---

## Monitoring Setup for Staging

### 1. **Configure Alerts**

Add to environment:
```env
ALERT_EMAIL_RECIPIENTS=team@example.com
ALERT_SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
ALERT_ON_ERROR_RATE=0.05
ALERT_ON_RESPONSE_TIME=2.0
```

### 2. **Set Up Error Tracking (Optional)**

Use Sentry for enhanced error tracking:

```bash
pip install sentry-sdk
```

Add to code:
```python
import sentry_sdk

sentry_sdk.init(
    dsn="https://your-key@sentry.io/your-project",
    environment="staging"
)
```

### 3. **Configure Logging**

Logs are written to:
- `logs/marketplace.log` - All application logs
- `logs/alerts.log` - Alert history

### 4. **Set Up Monitoring Dashboard**

Access at: `https://your-domain.com/api/monitoring/status`

Available metrics:
- System health status
- Error rate and trend
- Performance statistics (p95, p99)
- Recent errors and alerts
- Event tracking by category

---

## Load Testing Before Go-Live

### 1. **Install Load Testing Tool**

```bash
pip install locust
```

### 2. **Create Load Test**

```python
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 5)
    
    @task
    def search_models(self):
        self.client.get("/api/models/search?query=code")
    
    @task
    def get_recommendations(self):
        self.client.post("/api/recommendations", json={
            "query": "debug code",
            "complexity": "medium"
        })
```

### 3. **Run Load Test**

```bash
locust -f load_test.py --host https://your-domain.com --users 100 --spawn-rate 10
```

### 4. **Monitor Results**

Check monitoring dashboard:
- Monitor p95/p99 response times
- Watch for error spikes
- Verify database connection pool
- Check alert triggers

---

## Common Issues & Solutions

### Issue: Slow Database Queries

**Solution:**
1. Check performance metrics: `/api/monitoring/metrics/performance`
2. Review slow query logs in PostgreSQL
3. Add database indexes
4. Scale up database instance

### Issue: Memory Leaks

**Solution:**
1. Monitor memory usage in hosting platform
2. Set up alerts for high memory
3. Configure process restart policies
4. Use memory profiling tools

### Issue: High Error Rate

**Solution:**
1. Check recent errors: `/api/monitoring/errors/recent`
2. Review application logs: `logs/marketplace.log`
3. Check database connectivity
4. Verify API key configuration

### Issue: Certificate Issues

**Solution:**
1. Use Let's Encrypt (free)
2. Set up auto-renewal
3. For Heroku: Use Heroku's free SSL
4. For DigitalOcean: Use managed certificates

---

## Rollback Plan

If deployment has critical issues:

### Heroku Rollback
```bash
heroku releases
heroku rollback v123
```

### DigitalOcean Rollback
- Use GitHub deployment history
- Redeploy previous commit

### AWS Rollback
- Use AMI snapshots
- Switch load balancer to previous version

---

## Post-Deployment Tasks

### Day 1
- ✅ Monitor system health continuously
- ✅ Check error logs for any issues
- ✅ Verify all API endpoints responding
- ✅ Test complete user flow (signup → search → use)
- ✅ Confirm monitoring alerts working

### Day 2-7 (Staging Week)
- ✅ Run load tests
- ✅ Test edge cases and error scenarios
- ✅ Verify performance under load
- ✅ Collect feedback from team
- ✅ Make any necessary optimizations

### Week 2
- ✅ Plan production deployment
- ✅ Set up beta user recruitment
- ✅ Prepare launch announcement
- ✅ Create go-live runbook

---

## Database Migration

### Automated Migration

```bash
cd backend
python migrate.py
```

This will:
1. Create all 10 tables
2. Create 3 views for reporting
3. Create 2 procedures for common operations
4. Set up proper indexes
5. Configure constraints

### Verification

```bash
psql $DATABASE_URL
\dt  # List tables
\dv  # List views
\dp  # List privileges
```

---

## Performance Targets for Staging

Ensure these before go-live:

| Metric | Target | Current |
|--------|--------|---------|
| P95 Response Time | < 500ms | Testing |
| P99 Response Time | < 1000ms | Testing |
| Error Rate | < 0.5% | Testing |
| Availability | > 99.5% | Testing |
| DB Connection Pool | < 10 connections | Testing |
| Memory Usage | < 256MB | Testing |

---

## Success Criteria

Staging deployment is successful when:

✅ All health checks passing  
✅ All API endpoints responding  
✅ Performance within targets  
✅ Error rate < 0.5%  
✅ Monitoring alerts functional  
✅ Database migration successful  
✅ Team verified workflow end-to-end  

---

## Next Steps

### Immediate (Today)
1. Choose hosting platform
2. Create staging account/instance
3. Deploy code
4. Run validation checks
5. Monitor for 24 hours

### Short-term (This Week)
1. Load testing
2. Security review
3. Team feedback
4. Optimization if needed

### Long-term (Before Production)
1. Beta user recruitment
2. Production deployment
3. Go-live announcement
4. Customer support readiness

---

## Support & Monitoring

**During Staging:**
- Monitor: `https://your-domain.com/api/monitoring/status`
- Logs: Available in hosting platform dashboard
- Alerts: Will trigger at configured thresholds

**Need Help?**
1. Check `/api/monitoring/errors/recent` for errors
2. Review `logs/marketplace.log` for details
3. Check monitoring dashboard for health status
4. Review deployment guide section for your platform

---

**Status**: Ready for staging deployment  
**Next Task**: Choose hosting and deploy  
**Estimated Time**: 1-2 hours  
**Go-Live Target**: After 1 week of successful staging
