# Top Dog Membership Tier Implementation Guide

Complete walkthrough for implementing membership tier restrictions, rate limiting, and monetization on your Top Dog backend.

---

## PHASE 1: Database Setup (10-15 minutes)

### Step 1A: Create Database Tables

**Open a NEW PowerShell window** (Right-click Desktop → PowerShell)

```powershell
# Navigate to your project directory
cd "C:\Quellum-topdog-ide"

# Check if you have SQL Server or using another database
# This example assumes SQL Server. Adjust if using PostgreSQL, MySQL, MongoDB, etc.
```

**Run this SQL command** (Connect to your database first):

```sql
-- Create membership_tiers table
CREATE TABLE membership_tiers (
    id INT PRIMARY KEY IDENTITY(1,1),
    tier_id NVARCHAR(50) UNIQUE NOT NULL,
    name NVARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    daily_call_limit INT NOT NULL,
    daily_llm_requests INT NOT NULL,
    concurrent_sessions INT NOT NULL,
    storage_gb INT NOT NULL,
    code_execution BIT NOT NULL,
    data_persistence BIT NOT NULL,
    game_engines INT,
    verified_code_checks INT,
    team_members INT,
    roles INT,
    hipaa_ready BIT,
    custom_integrations BIT,
    custom_llms BIT,
    on_premise_deploy BIT,
    account_manager BIT,
    executive_access BIT,
    support_tier NVARCHAR(100),
    sso BIT,
    saml BIT,
    sla NVARCHAR(20),
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()
);

-- Create user_subscriptions table (tracks which tier each user is on)
CREATE TABLE user_subscriptions (
    id INT PRIMARY KEY IDENTITY(1,1),
    user_id NVARCHAR(255) UNIQUE NOT NULL,
    tier_id NVARCHAR(50) NOT NULL,
    subscription_date DATETIME DEFAULT GETDATE(),
    trial_expiry DATETIME NULL,  -- For FREE tier: 7 days from subscription_date
    is_active BIT DEFAULT 1,
    last_payment_date DATETIME NULL,
    next_billing_date DATETIME NULL,
    FOREIGN KEY (tier_id) REFERENCES membership_tiers(tier_id)
);

-- Create daily_usage_tracking table (tracks API calls per user per day)
CREATE TABLE daily_usage_tracking (
    id INT PRIMARY KEY IDENTITY(1,1),
    user_id NVARCHAR(255) NOT NULL,
    usage_date DATE NOT NULL,
    api_calls_used INT DEFAULT 0,
    llm_requests_used INT DEFAULT 0,
    code_executions_used INT DEFAULT 0,
    storage_used_gb DECIMAL(10,2) DEFAULT 0,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE(),
    UNIQUE(user_id, usage_date)
);

-- Create tier_audit_log table (track tier changes for compliance)
CREATE TABLE tier_audit_log (
    id INT PRIMARY KEY IDENTITY(1,1),
    user_id NVARCHAR(255) NOT NULL,
    old_tier NVARCHAR(50),
    new_tier NVARCHAR(50) NOT NULL,
    change_reason NVARCHAR(255),
    changed_at DATETIME DEFAULT GETDATE()
);
```

**Expected Result**: ✅ 4 tables created successfully

---

## PHASE 2: Populate Membership Tiers (5 minutes)

**Still in the same PowerShell window**, run the SQL INSERT command:

```sql
-- Insert all 9 membership tiers
INSERT INTO membership_tiers (tier_id, name, price, daily_call_limit, daily_llm_requests, concurrent_sessions, storage_gb, code_execution, data_persistence, game_engines, verified_code_checks, team_members, roles, support_tier) VALUES
('free', 'FREE', 0, 20, 2, 1, 0.5, 0, 1, 0, 0, 1, 1, 'Community Support'),
('pro', 'PRO', 20, 10000, 1000, 5, 100, 1, 1, 1, 50, 1, 1, 'Email'),
('pro_plus', 'PRO-PLUS', 45, 50000, 5000, 8, 250, 1, 1, 2, 200, 1, 1, 'Priority Email'),
('teams_small', 'TEAMS-SMALL', 100, 100000, 10000, 10, 1000, 1, 1, 4, 1000, 5, 5, 'Email SLA 24hr'),
('teams_medium', 'TEAMS-MEDIUM', 300, 500000, 50000, 20, 2000, 1, 1, 4, 5000, 30, 5, 'Priority Email SLA 12hr'),
('teams_large', 'TEAMS-LARGE', 800, 9999999, 100000, 50, 5000, 1, 1, 4, 9999999, 100, 8, 'Priority Phone SLA 4hr'),
('enterprise_standard', 'ENTERPRISE-STANDARD', 5000, 9999999, 9999999, 100, 10000, 1, 1, 4, 9999999, 500, 8, 'Dedicated 24/7'),
('enterprise_premium', 'ENTERPRISE-PREMIUM', 15000, 9999999, 9999999, 100, 50000, 1, 1, 4, 9999999, 2000, 8, 'Dedicated 24/7 + Account Manager'),
('enterprise_ultimate', 'ENTERPRISE-ULTIMATE', 50000, 9999999, 9999999, 999, 999999, 1, 1, 4, 9999999, 99999, 999, 'Dedicated 24/7 + Executive Access');

-- Verify insertion
SELECT * FROM membership_tiers;
```

**Expected Result**: 9 rows inserted, 9 rows displayed ✅

---

## PHASE 3: Backend API Integration (30-45 minutes)

### Step 3A: Create Rate Limiting Middleware

**Open a NEW PowerShell window** for code editing:

```powershell
# Create the rate limiting service file
# If using Node.js/Express backend:

$rateLimiterCode = @"
// File: services/rateLimiter.js

const redis = require('redis');
const client = redis.createClient();

async function checkRateLimit(userId, tierLimits) {
    const today = new Date().toISOString().split('T')[0];
    const key = `usage:\${userId}:\${today}`;
    
    try {
        const currentUsage = await client.get(key);
        const used = currentUsage ? parseInt(currentUsage) : 0;
        
        if (used >= tierLimits.daily_call_limit) {
            return {
                allowed: false,
                message: 'Daily API call limit exceeded',
                limit: tierLimits.daily_call_limit,
                used: used,
                resetTime: new Date(today).getTime() + (24 * 60 * 60 * 1000)
            };
        }
        
        // Increment counter
        await client.incr(key);
        await client.expire(key, 86400); // Expire after 24 hours
        
        return {
            allowed: true,
            remaining: tierLimits.daily_call_limit - used - 1
        };
    } catch (error) {
        console.error('Rate limiter error:', error);
        return { allowed: false, error: 'Rate limiter check failed' };
    }
}

module.exports = { checkRateLimit };
"@

# Write to file (adjust path to your backend)
$rateLimiterCode | Out-File -FilePath "C:\path\to\your\backend\services\rateLimiter.js" -Encoding UTF8
Write-Host "Rate limiter service created" -ForegroundColor Green
```

### Step 3B: Create Tier Validation Middleware

```powershell
# File: middleware/tierValidator.js

$tierValidatorCode = @"
// Middleware to check tier restrictions

async function validateTierAccess(req, res, next) {
    const userId = req.user.id;
    
    try {
        // Get user's current tier
        const subscription = await db.query(
            'SELECT us.tier_id, mt.* FROM user_subscriptions us ' +
            'JOIN membership_tiers mt ON us.tier_id = mt.tier_id ' +
            'WHERE us.user_id = @userId',
            { userId }
        );
        
        if (!subscription) {
            return res.status(403).json({ error: 'No active subscription' });
        }
        
        // Check if FREE tier trial has expired
        if (subscription.tier_id === 'free') {
            const trialExpiry = new Date(subscription.trial_expiry);
            if (new Date() > trialExpiry) {
                return res.status(403).json({
                    error: 'FREE tier trial expired',
                    message: 'Upgrade to PRO to continue',
                    expiredAt: trialExpiry
                });
            }
        }
        
        // Check code execution permission for FREE tier
        if (req.body.action === 'code_execution' && !subscription.code_execution) {
            return res.status(403).json({
                error: 'Code execution not available on FREE tier',
                upgradeUrl: '/upgrade/pro'
            });
        }
        
        // Attach tier info to request
        req.userTier = subscription;
        next();
    } catch (error) {
        res.status(500).json({ error: 'Tier validation failed' });
    }
}

module.exports = { validateTierAccess };
"@

$tierValidatorCode | Out-File -FilePath "C:\path\to\your\backend\middleware\tierValidator.js" -Encoding UTF8
Write-Host "Tier validator middleware created" -ForegroundColor Green
```

### Step 3C: Create Trial Expiry Check Service

```powershell
# File: services/trialExpiryService.js

$trialExpiryCode = @"
// Check and deactivate expired FREE trials

const schedule = require('node-schedule');

// Run daily at midnight UTC
const job = schedule.scheduleJob('0 0 * * *', async () => {
    console.log('Running trial expiry check...');
    
    try {
        const expiredTrials = await db.query(
            'SELECT user_id, tier_id FROM user_subscriptions ' +
            'WHERE tier_id = \'free\' AND trial_expiry < NOW() AND is_active = 1'
        );
        
        for (const trial of expiredTrials) {
            // Mark as expired (read-only access allowed)
            await db.query(
                'UPDATE user_subscriptions SET is_active = 0 WHERE user_id = @userId',
                { userId: trial.user_id }
            );
            
            // Log to audit
            await db.query(
                'INSERT INTO tier_audit_log (user_id, old_tier, new_tier, change_reason) ' +
                'VALUES (@userId, \'free\', \'free\', \'trial_expired\')',
                { userId: trial.user_id }
            );
            
            // Send email notification
            await sendEmail(trial.user_id, {
                subject: 'Your Top Dog FREE trial has expired',
                template: 'trial-expired',
                upgradeUrl: 'https://Top Dog.com/upgrade'
            });
        }
        
        console.log(`Marked \${expiredTrials.length} trials as expired`);
    } catch (error) {
        console.error('Trial expiry check failed:', error);
    }
});

module.exports = { job };
"@

$trialExpiryCode | Out-File -FilePath "C:\path\to\your\backend\services\trialExpiryService.js" -Encoding UTF8
Write-Host "Trial expiry service created" -ForegroundColor Green
```

---

## PHASE 4: Frontend Integration (20-30 minutes)

### Step 4A: Create Tier Display Component

```powershell
# File: components/TierBadge.jsx

$tierComponentCode = @"
// React component to display tier info

import React, { useState, useEffect } from 'react';

export default function TierInfo() {
    const [userTier, setUserTier] = useState(null);
    const [usage, setUsage] = useState(null);
    
    useEffect(() => {
        fetchUserTierInfo();
    }, []);
    
    async function fetchUserTierInfo() {
        try {
            const response = await fetch('/api/user/tier', {
                headers: { 'Authorization': \`Bearer \${localStorage.token}\` }
            });
            const data = await response.json();
            setUserTier(data.tier);
            setUsage(data.dailyUsage);
        } catch (error) {
            console.error('Failed to fetch tier info:', error);
        }
    }
    
    if (!userTier) return <div>Loading...</div>;
    
    const usagePercent = (usage.api_calls_used / userTier.daily_call_limit) * 100;
    const trialDaysLeft = userTier.tier_id === 'free' 
        ? Math.ceil((new Date(userTier.trial_expiry) - new Date()) / (1000 * 60 * 60 * 24))
        : null;
    
    return (
        <div className="tier-info">
            <h3>{userTier.name} Tier</h3>
            
            {userTier.tier_id === 'free' && trialDaysLeft > 0 && (
                <div className="trial-warning">
                    Trial expires in {trialDaysLeft} days
                    <a href="/upgrade">Upgrade Now</a>
                </div>
            )}
            
            {userTier.tier_id === 'free' && trialDaysLeft <= 0 && (
                <div className="trial-expired">
                    Trial Expired - Read-only access only
                    <a href="/upgrade">Upgrade to PRO</a>
                </div>
            )}
            
            <div className="usage-bar">
                <div className="usage-fill" style={{width: \`\${usagePercent}%\`}}></div>
            </div>
            <p>{usage.api_calls_used} / {userTier.daily_call_limit} API calls used today</p>
            
            {!userTier.code_execution && userTier.tier_id === 'free' && (
                <p className="limitation">
                    ⚠️ Code execution disabled on FREE tier
                </p>
            )}
        </div>
    );
}
"@

$tierComponentCode | Out-File -FilePath "C:\path\to\your\frontend\components\TierInfo.jsx" -Encoding UTF8
Write-Host "Tier info component created" -ForegroundColor Green
```

---

## PHASE 5: User Signup Flow Integration (15-20 minutes)

### Step 5A: Assign DEFAULT Tier on Signup

**Add this to your registration endpoint:**

```powershell
# File: routes/auth.js (Node.js example)

$signupCode = @"
// When new user registers, assign FREE tier by default

router.post('/register', async (req, res) => {
    const { email, password, username } = req.body;
    
    try {
        // Create user
        const userId = await createUser(email, username, password);
        
        // Assign FREE tier by default
        await db.query(
            'INSERT INTO user_subscriptions (user_id, tier_id, trial_expiry, is_active) ' +
            'VALUES (@userId, \'free\', DATEADD(day, 7, GETDATE()), 1)',
            { userId }
        );
        
        // Log tier assignment
        await db.query(
            'INSERT INTO tier_audit_log (user_id, new_tier, change_reason) ' +
            'VALUES (@userId, \'free\', \'initial_signup\')',
            { userId }
        );
        
        // Send welcome email
        await sendWelcomeEmail(email, {
            trialDays: 7,
            upgradeUrl: 'https://Top Dog.com/upgrade/pro'
        });
        
        res.json({ 
            success: true, 
            message: 'Welcome to Top Dog! You have 7 days free access.',
            userId 
        });
    } catch (error) {
        res.status(500).json({ error: 'Registration failed' });
    }
});
"@

Write-Host "Add this code to your signup endpoint" -ForegroundColor Yellow
Write-Host $signupCode
```

---

## PHASE 6: Setup Monitoring & Alerts (10-15 minutes)

### Step 6A: Create Usage Monitoring Script

```powershell
# File: scripts/monitorUsage.ps1

$monitoringScript = @"
# Monitor user tier compliance

# Run every hour
\$job = Register-ScheduledJob -Name "Top Dog-Tier-Monitor" -ScriptBlock {
    
    \$connString = "Server=YOUR_SERVER;Database=Q_IDE;User Id=sa;Password=YOUR_PASSWORD"
    \$connection = New-Object System.Data.SqlClient.SqlConnection(\$connString)
    \$connection.Open()
    
    # Check for over-limit users
    \$query = @"
        SELECT TOP 10
            us.user_id,
            us.tier_id,
            mt.daily_call_limit,
            dut.api_calls_used,
            (dut.api_calls_used - mt.daily_call_limit) as overage
        FROM daily_usage_tracking dut
        JOIN user_subscriptions us ON dut.user_id = us.user_id
        JOIN membership_tiers mt ON us.tier_id = mt.tier_id
        WHERE dut.usage_date = CAST(GETDATE() as DATE)
        AND dut.api_calls_used > mt.daily_call_limit
        ORDER BY overage DESC
"@
    
    \$command = New-Object System.Data.SqlClient.SqlCommand(\$query, \$connection)
    \$reader = \$command.ExecuteReader()
    
    \$overLimitUsers = @()
    while (\$reader.Read()) {
        \$overLimitUsers += @{
            user_id = \$reader["user_id"]
            tier = \$reader["tier_id"]
            overage = \$reader["overage"]
        }
    }
    
    \$connection.Close()
    
    # Alert if users over limit
    if (\$overLimitUsers.Count -gt 0) {
        Write-Host "⚠️  \$(\$overLimitUsers.Count) users over daily limit" -ForegroundColor Red
        \$overLimitUsers | ForEach-Object {
            Write-Host "  - User: \$(\$_.user_id) | Tier: \$(\$_.tier) | Overage: \$(\$_.overage) calls"
        }
    } else {
        Write-Host "✅ All users within limits" -ForegroundColor Green
    }
    
} -Trigger (New-JobTrigger -AtStartup) -RunAs32

Write-Host "Monitoring job scheduled" -ForegroundColor Green
"@

$monitoringScript | Out-File -FilePath "C:\Quellum-topdog-ide\scripts\monitorUsage.ps1" -Encoding UTF8
Write-Host "Usage monitoring script created" -ForegroundColor Green
```

---

## PHASE 7: Test the Implementation (20-30 minutes)

### Step 7A: Create Test User with FREE Tier

```powershell
# Open PowerShell and connect to database

$testUserScript = @"
# Test user creation script

# 1. Create test user
INSERT INTO user_subscriptions (user_id, tier_id, trial_expiry, is_active) 
VALUES ('test-user-001', 'free', DATEADD(day, 7, GETDATE()), 1)

# 2. Verify insertion
SELECT * FROM user_subscriptions WHERE user_id = 'test-user-001'

# 3. Initialize daily usage tracking
INSERT INTO daily_usage_tracking (user_id, usage_date, api_calls_used) 
VALUES ('test-user-001', CAST(GETDATE() as DATE), 0)

# 4. Test rate limit check
SELECT 
    CAST(GETDATE() as DATE) as today,
    us.user_id,
    mt.daily_call_limit,
    ISNULL(dut.api_calls_used, 0) as used,
    mt.daily_call_limit - ISNULL(dut.api_calls_used, 0) as remaining
FROM user_subscriptions us
JOIN membership_tiers mt ON us.tier_id = mt.tier_id
LEFT JOIN daily_usage_tracking dut ON us.user_id = dut.user_id 
    AND dut.usage_date = CAST(GETDATE() as DATE)
WHERE us.user_id = 'test-user-001'
"@

Write-Host "Test user creation SQL commands:" -ForegroundColor Cyan
Write-Host $testUserScript
```

### Step 7B: Test API Rate Limiting

```powershell
# Test the rate limiter with a curl request

$testUrl = "http://localhost:3000/api/code/execute"
$headers = @{
    "Authorization" = "Bearer YOUR_TEST_TOKEN"
    "Content-Type" = "application/json"
}

$body = @{
    code = "console.log('Hello World');"
    language = "javascript"
} | ConvertTo-Json

# First call should succeed
$response1 = Invoke-WebRequest -Uri $testUrl -Method POST -Headers $headers -Body $body
Write-Host "Call 1: $($response1.StatusCode) - $(($response1.Content | ConvertFrom-Json).remaining) calls remaining" -ForegroundColor Green

# Run 20 more calls to test limit (FREE tier = 20 calls/day)
for ($i = 1; $i -le 20; $i++) {
    $response = Invoke-WebRequest -Uri $testUrl -Method POST -Headers $headers -Body $body -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 429) {
        Write-Host "Call $(($i+1)): RATE LIMITED (429) ✅ Limit working!" -ForegroundColor Yellow
        break
    }
}

Write-Host "Rate limiting test complete"
```

---

## PHASE 8: Deployment Checklist

### Before Going Live

```powershell
# Final verification checklist

$checklist = @"
DEPLOYMENT VERIFICATION CHECKLIST
═════════════════════════════════

Database:
  ☐ membership_tiers table created with 9 tiers
  ☐ user_subscriptions table created
  ☐ daily_usage_tracking table created
  ☐ tier_audit_log table created
  ☐ All 9 tiers inserted into membership_tiers

Backend Services:
  ☐ Rate limiting middleware deployed
  ☐ Tier validator middleware deployed
  ☐ Trial expiry check service running
  ☐ Usage tracking logging enabled
  ☐ All environment variables set (.env file)

Frontend:
  ☐ Tier info component displaying correctly
  ☐ Trial countdown shows on FREE tier
  ☐ "Upgrade" button visible when tier is limited
  ☐ Usage bar shows API call consumption

Testing:
  ☐ Test user on FREE tier can use for 7 days
  ☐ Test user gets error on code execution (FREE tier)
  ☐ Test user hits rate limit at 20 calls
  ☐ Tier expiry job removes access after 7 days
  ☐ PRO tier users get unlimited code execution
  ☐ TEAMS users can add multiple team members

Monitoring:
  ☐ Usage monitoring script running
  ☐ Trial expiry job scheduled
  ☐ Alert system configured
  ☐ Logs being written to proper location

Documentation:
  ☐ Team trained on tier restrictions
  ☐ Support docs updated
  ☐ API documentation shows tier requirements
  ☐ Upgrade flow documented for users
"@

Write-Host $checklist -ForegroundColor Cyan
```

---

## PHASE 9: Post-Launch Operations (Ongoing)

### Monitor & Adjust

```powershell
# Weekly monitoring PowerShell script

$weeklyReport = @"
# Weekly Tier Report - Every Monday 9 AM

\$params = @{
    ConnectionString = "YOUR_CONNECTION_STRING"
    Query = @"
        SELECT 
            COUNT(*) as total_users,
            SUM(CASE WHEN tier_id = 'free' THEN 1 ELSE 0 END) as free_users,
            SUM(CASE WHEN tier_id LIKE 'pro%' THEN 1 ELSE 0 END) as pro_users,
            SUM(CASE WHEN tier_id LIKE 'teams%' THEN 1 ELSE 0 END) as teams_users,
            SUM(CASE WHEN tier_id LIKE 'enterprise%' THEN 1 ELSE 0 END) as enterprise_users,
            SUM(CASE WHEN tier_id = 'free' AND DATEDIFF(day, trial_expiry, GETDATE()) > 0 THEN 1 ELSE 0 END) as expired_trials
        FROM user_subscriptions
"@
}

\$result = Invoke-Sqlcmd @params

Write-Host "WEEKLY TIER REPORT" -ForegroundColor Cyan
Write-Host "Total Users: \$(\$result.total_users)"
Write-Host "  - FREE: \$(\$result.free_users)"
Write-Host "  - PRO: \$(\$result.pro_users)"
Write-Host "  - TEAMS: \$(\$result.teams_users)"
Write-Host "  - ENTERPRISE: \$(\$result.enterprise_users)"
Write-Host "  - Expired Trials: \$(\$result.expired_trials)"

# Calculate conversion rate
\$conversionRate = (\$result.pro_users / \$result.free_users) * 100
Write-Host "Conversion Rate (FREE→PRO): \$(\$conversionRate)%" -ForegroundColor Yellow

# Alert if conversion is below 5%
if (\$conversionRate -lt 5) {
    Write-Host "⚠️  Low conversion rate - consider FREE tier adjustments" -ForegroundColor Red
}
"@

Write-Host "Weekly monitoring report configured"
```

---

## TROUBLESHOOTING & COMMON ISSUES

### Issue 1: Users Hitting Rate Limit Immediately

**Problem**: Users report hitting daily limit within minutes
**Solution**:
```powershell
# Check if usage is being reset properly
SELECT * FROM daily_usage_tracking WHERE user_id = 'test-user-001' ORDER BY usage_date DESC

# If old dates exist, they're not resetting
# Fix: Ensure your API resets counters at midnight UTC
# Add to your rate limiter:
# const today = new Date().toISOString().split('T')[0]  # UTC date only
```

### Issue 2: FREE Tier Users Can Still Execute Code

**Problem**: FREE tier users running code despite code_execution = 0
**Solution**:
```powershell
# Verify middleware is applied to code execution endpoint
# Check your Express/API routes:

# BEFORE (wrong):
app.post('/api/code/execute', codeExecutor);

# AFTER (correct):
app.post('/api/code/execute', tierValidator, codeExecutor);

# Ensure tierValidator is BEFORE the executor
```

### Issue 3: Trial Expiry Job Not Running

**Problem**: Users still have access after 7 days
**Solution**:
```powershell
# Check if scheduled job is running
Get-ScheduledJob -Name "Top Dog-Trial-Expiry" | Get-ScheduledJobOption

# If not running, restart:
Stop-ScheduledJob -Name "Top Dog-Trial-Expiry"
Remove-ScheduledJob -Name "Top Dog-Trial-Expiry"

# Re-register the job
Register-ScheduledJob -Name "Top Dog-Trial-Expiry" -ScriptBlock { ... } -Trigger (New-JobTrigger -Daily -At 00:00)

# Verify it's running
Get-ScheduledJob -Name "Top Dog-Trial-Expiry"
```

### Issue 4: Database Connection String Issues

**Problem**: "Cannot connect to database"
**Solution**:
```powershell
# Test your connection string
$connString = "Server=YOUR_SERVER;Database=YOUR_DB;User Id=sa;Password=YOUR_PASSWORD"

$connection = New-Object System.Data.SqlClient.SqlConnection($connString)
try {
    $connection.Open()
    Write-Host "✅ Connection successful" -ForegroundColor Green
    $connection.Close()
} catch {
    Write-Host "❌ Connection failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Common issues:
# - Wrong server name (use: localhost\SQLEXPRESS for local)
# - Wrong password
# - Firewall blocking connection
# - SQL Server not running
```

---

## QUICK REFERENCE: Commands Summary

```powershell
# 1. START HERE - Create database tables
# Run SQL section in PHASE 2

# 2. Insert all tiers
# Run SQL INSERT in PHASE 2

# 3. Create backend services
# Copy code from PHASE 3 into your backend

# 4. Create frontend component
# Copy code from PHASE 4 into your frontend

# 5. Add signup flow
# Update registration endpoint (PHASE 5)

# 6. Setup monitoring
# Copy monitoring script and schedule it

# 7. Test everything
# Run test scripts in PHASE 7

# 8. Deploy
# Follow checklist in PHASE 8

# 9. Monitor ongoing
# Run weekly report script
```

---

## NEXT STEPS

1. **Immediately**: Complete PHASE 1 & 2 (database setup)
2. **Today**: Complete PHASE 3 & 4 (backend/frontend integration)
3. **Tomorrow**: Complete PHASE 5, 6, 7 (signup, monitoring, testing)
4. **This week**: Go through PHASE 8 checklist and deploy
5. **Ongoing**: Run PHASE 9 monitoring weekly

**Expected Timeline**: 4-6 hours total setup time

**Need Help?**
- Database issues → Check connection string + SQL syntax
- Rate limiting not working → Verify Redis is running + middleware is applied
- Trial not expiring → Check scheduled job is running + database trigger logic
- API returning wrong tier info → Verify user_subscriptions table has correct tier_id values

