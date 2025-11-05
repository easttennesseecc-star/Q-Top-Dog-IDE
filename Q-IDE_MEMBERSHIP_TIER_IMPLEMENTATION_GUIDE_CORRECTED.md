# Top Dog Membership Tier Implementation Guide (CORRECTED)

**Updated for your actual tech stack**:
- Backend: Python (Flask/FastAPI)
- Frontend: TypeScript/React + Tauri
- Project Root: `C:\Quellum-topdog-ide`
- Database: SQLite (dev) / PostgreSQL (production)

---

## PHASE 1: Database Setup (10-15 minutes)

### Step 1A: Create Database Tables

**Navigate to project root**:
```powershell
cd "C:\Quellum-topdog-ide"
```

**Create the database schema file**:
```powershell
# Create migration file for membership tiers
$schemaFile = @"
"""Database schema for membership tiers"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class MembershipTier(Base):
    __tablename__ = 'membership_tiers'
    
    id = Column(Integer, primary_key=True)
    tier_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    daily_call_limit = Column(Integer, nullable=False)
    daily_llm_requests = Column(Integer, nullable=False)
    concurrent_sessions = Column(Integer)
    storage_gb = Column(Integer)
    code_execution = Column(Boolean, default=False)
    data_persistence = Column(Boolean, default=True)
    game_engines = Column(Integer, default=0)
    verified_code_checks = Column(Integer, default=0)
    team_members = Column(Integer, default=1)
    roles = Column(Integer, default=1)
    hipaa_ready = Column(Boolean, default=False)
    custom_integrations = Column(Boolean, default=False)
    custom_llms = Column(Boolean, default=False)
    on_premise_deploy = Column(Boolean, default=False)
    account_manager = Column(Boolean, default=False)
    executive_access = Column(Boolean, default=False)
    support_tier = Column(String(100))
    sso = Column(Boolean, default=False)
    saml = Column(Boolean, default=False)
    sla = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserSubscription(Base):
    __tablename__ = 'user_subscriptions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), unique=True, nullable=False)
    tier_id = Column(String(50), ForeignKey('membership_tiers.tier_id'), nullable=False)
    subscription_date = Column(DateTime, default=datetime.utcnow)
    trial_expiry = Column(DateTime)  # For FREE tier: 7 days from subscription_date
    is_active = Column(Boolean, default=True)
    last_payment_date = Column(DateTime)
    next_billing_date = Column(DateTime)


class DailyUsageTracking(Base):
    __tablename__ = 'daily_usage_tracking'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False)
    usage_date = Column(String(10), nullable=False)  # YYYY-MM-DD
    api_calls_used = Column(Integer, default=0)
    llm_requests_used = Column(Integer, default=0)
    code_executions_used = Column(Integer, default=0)
    storage_used_gb = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TierAuditLog(Base):
    __tablename__ = 'tier_audit_log'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False)
    old_tier = Column(String(50))
    new_tier = Column(String(50), nullable=False)
    change_reason = Column(String(255))
    changed_at = Column(DateTime, default=datetime.utcnow)
"@

$schemaFile | Out-File -FilePath "backend/database/tier_schema.py" -Encoding UTF8
Write-Host "✅ Schema file created at backend/database/tier_schema.py" -ForegroundColor Green
```

**Run database migrations**:
```powershell
# If using Alembic migrations
cd backend
alembic revision --autogenerate -m "Add membership tier tables"
alembic upgrade head

# If not using Alembic, initialize tables directly in Python
python -c "from database.tier_schema import Base, engine; Base.metadata.create_all(engine)"
Write-Host "✅ Database tables created" -ForegroundColor Green
```

---

## PHASE 2: Populate Membership Tiers (5 minutes)

**Create seed data file**:
```powershell
$seedFile = @"
"""Populate membership tiers"""

from database.tier_schema import MembershipTier, engine
from sqlalchemy.orm import Session

tiers_data = [
    {
        'tier_id': 'free',
        'name': 'FREE',
        'price': 0,
        'daily_call_limit': 20,
        'daily_llm_requests': 2,
        'concurrent_sessions': 1,
        'storage_gb': 0.5,
        'code_execution': False,
        'data_persistence': True,
        'support_tier': 'Community Support'
    },
    {
        'tier_id': 'pro',
        'name': 'PRO',
        'price': 20,
        'daily_call_limit': 10000,
        'daily_llm_requests': 1000,
        'concurrent_sessions': 5,
        'storage_gb': 100,
        'code_execution': True,
        'data_persistence': True,
        'game_engines': 1,
        'verified_code_checks': 50,
        'support_tier': 'Email'
    },
    {
        'tier_id': 'pro_plus',
        'name': 'PRO-PLUS',
        'price': 45,
        'daily_call_limit': 50000,
        'daily_llm_requests': 5000,
        'concurrent_sessions': 8,
        'storage_gb': 250,
        'code_execution': True,
        'data_persistence': True,
        'game_engines': 2,
        'verified_code_checks': 200,
        'support_tier': 'Priority Email'
    },
    {
        'tier_id': 'teams_small',
        'name': 'TEAMS-SMALL',
        'price': 100,
        'daily_call_limit': 100000,
        'daily_llm_requests': 10000,
        'concurrent_sessions': 10,
        'storage_gb': 1000,
        'code_execution': True,
        'data_persistence': True,
        'game_engines': 4,
        'verified_code_checks': 1000,
        'team_members': 5,
        'support_tier': 'Email SLA 24hr'
    },
    {
        'tier_id': 'teams_medium',
        'name': 'TEAMS-MEDIUM',
        'price': 300,
        'daily_call_limit': 500000,
        'daily_llm_requests': 50000,
        'concurrent_sessions': 20,
        'storage_gb': 2000,
        'code_execution': True,
        'data_persistence': True,
        'game_engines': 4,
        'verified_code_checks': 5000,
        'team_members': 30,
        'support_tier': 'Priority Email SLA 12hr'
    },
    {
        'tier_id': 'teams_large',
        'name': 'TEAMS-LARGE',
        'price': 800,
        'daily_call_limit': 9999999,
        'daily_llm_requests': 100000,
        'concurrent_sessions': 50,
        'storage_gb': 5000,
        'code_execution': True,
        'data_persistence': True,
        'game_engines': 4,
        'verified_code_checks': 9999999,
        'team_members': 100,
        'support_tier': 'Priority Phone SLA 4hr'
    },
    {
        'tier_id': 'enterprise_standard',
        'name': 'ENTERPRISE-STANDARD',
        'price': 5000,
        'daily_call_limit': 9999999,
        'daily_llm_requests': 9999999,
        'concurrent_sessions': 100,
        'storage_gb': 10000,
        'code_execution': True,
        'data_persistence': True,
        'game_engines': 4,
        'verified_code_checks': 9999999,
        'team_members': 500,
        'hipaa_ready': True,
        'custom_llms': True,
        'support_tier': 'Dedicated 24/7'
    },
    {
        'tier_id': 'enterprise_premium',
        'name': 'ENTERPRISE-PREMIUM',
        'price': 15000,
        'daily_call_limit': 9999999,
        'daily_llm_requests': 9999999,
        'concurrent_sessions': 100,
        'storage_gb': 50000,
        'code_execution': True,
        'data_persistence': True,
        'game_engines': 4,
        'verified_code_checks': 9999999,
        'team_members': 2000,
        'hipaa_ready': True,
        'custom_llms': True,
        'sso': True,
        'account_manager': True,
        'support_tier': 'Dedicated 24/7 + Account Manager'
    },
    {
        'tier_id': 'enterprise_ultimate',
        'name': 'ENTERPRISE-ULTIMATE',
        'price': 50000,
        'daily_call_limit': 9999999,
        'daily_llm_requests': 9999999,
        'concurrent_sessions': 999,
        'storage_gb': 999999,
        'code_execution': True,
        'data_persistence': True,
        'game_engines': 4,
        'verified_code_checks': 9999999,
        'team_members': 99999,
        'hipaa_ready': True,
        'custom_integrations': True,
        'custom_llms': True,
        'on_premise_deploy': True,
        'sso': True,
        'saml': True,
        'account_manager': True,
        'executive_access': True,
        'support_tier': 'Dedicated 24/7 + Executive Access'
    }
]

# Insert tiers
session = Session(engine)
for tier_data in tiers_data:
    existing = session.query(MembershipTier).filter_by(tier_id=tier_data['tier_id']).first()
    if not existing:
        tier = MembershipTier(**tier_data)
        session.add(tier)
        print(f"✅ {tier_data['name']} tier created ({tier_data['price']}/mo)")

session.commit()
session.close()
print(f"\\n✅ All 9 membership tiers created successfully")
"@

$seedFile | Out-File -FilePath "backend/seeds/populate_tiers.py" -Encoding UTF8

# Run seed
cd backend
python seeds/populate_tiers.py
cd ..
Write-Host "✅ All 9 membership tiers populated" -ForegroundColor Green
```

---

## PHASE 3: Backend API Integration (30-45 minutes)

### Step 3A: Create Rate Limiting Service

**Create rate limiter**:
```powershell
$rateLimiterCode = @"
\"\"\"Rate limiting service for membership tiers\"\"\"

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.tier_schema import DailyUsageTracking, UserSubscription, MembershipTier

class RateLimiter:
    def __init__(self, db_session: Session):
        self.db = db_session
    
    async def check_limit(self, user_id: str) -> dict:
        \"\"\"Check if user has exceeded daily limits\"\"\"
        
        # Get user's subscription
        subscription = self.db.query(UserSubscription).filter_by(user_id=user_id).first()
        if not subscription:
            return {'allowed': False, 'error': 'No active subscription'}
        
        # Get tier info
        tier = self.db.query(MembershipTier).filter_by(tier_id=subscription.tier_id).first()
        
        # Check trial expiry for FREE tier
        if tier.tier_id == 'free':
            if subscription.trial_expiry and datetime.utcnow() > subscription.trial_expiry:
                return {
                    'allowed': False,
                    'error': 'FREE tier trial expired',
                    'expired_at': subscription.trial_expiry.isoformat()
                }
        
        # Check daily usage
        today = datetime.utcnow().date().isoformat()
        usage = self.db.query(DailyUsageTracking).filter_by(
            user_id=user_id,
            usage_date=today
        ).first()
        
        if not usage:
            usage = DailyUsageTracking(user_id=user_id, usage_date=today)
            self.db.add(usage)
            self.db.commit()
        
        if usage.api_calls_used >= tier.daily_call_limit:
            return {
                'allowed': False,
                'error': 'Daily API call limit exceeded',
                'limit': tier.daily_call_limit,
                'used': usage.api_calls_used,
                'reset_time': (datetime.utcnow() + timedelta(days=1)).isoformat()
            }
        
        # Increment usage
        usage.api_calls_used += 1
        self.db.commit()
        
        return {
            'allowed': True,
            'remaining': tier.daily_call_limit - usage.api_calls_used,
            'tier': tier.name
        }

\"\"\"

$rateLimiterCode | Out-File -FilePath "backend/services/rate_limiter.py" -Encoding UTF8
Write-Host "✅ Rate limiter service created" -ForegroundColor Green
```

### Step 3B: Create Tier Validation Middleware

```powershell
$middlewareCode = @"
\"\"\"Tier validation middleware\"\"\"

from functools import wraps
from flask import request, jsonify
from sqlalchemy.orm import Session
from database.tier_schema import UserSubscription, MembershipTier
from datetime import datetime

def require_tier_access(action_required=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = request.headers.get('X-User-ID')
            
            if not user_id:
                return jsonify({'error': 'User ID required'}), 401
            
            # Get user's subscription (assumed db session available)
            db = request.db
            subscription = db.query(UserSubscription).filter_by(user_id=user_id).first()
            
            if not subscription:
                return jsonify({'error': 'No active subscription'}), 403
            
            tier = db.query(MembershipTier).filter_by(tier_id=subscription.tier_id).first()
            
            # Check FREE tier trial expiry
            if tier.tier_id == 'free' and subscription.trial_expiry:
                if datetime.utcnow() > subscription.trial_expiry:
                    return jsonify({
                        'error': 'FREE tier trial expired',
                        'upgrade_url': '/upgrade'
                    }), 403
            
            # Check specific action permissions
            if action_required == 'code_execution' and not tier.code_execution:
                return jsonify({
                    'error': 'Code execution not available on your tier',
                    'upgrade_url': '/upgrade/pro'
                }), 403
            
            # Attach tier info to request
            request.user_tier = tier
            request.user_subscription = subscription
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

\"\"\"

$middlewareCode | Out-File -FilePath "backend/middleware/tier_validator.py" -Encoding UTF8
Write-Host "✅ Tier validator middleware created" -ForegroundColor Green
```

### Step 3C: Add Trial Expiry Job

```powershell
$trialJobCode = @"
\"\"\"Trial expiry check service\"\"\"

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from sqlalchemy.orm import Session
from database.tier_schema import UserSubscription, engine

def check_expired_trials():
    \"\"\"Run daily at midnight UTC to deactivate expired FREE trials\"\"\"
    
    session = Session(engine)
    
    try:
        expired = session.query(UserSubscription).filter(
            UserSubscription.tier_id == 'free',
            UserSubscription.trial_expiry < datetime.utcnow(),
            UserSubscription.is_active == True
        ).all()
        
        for subscription in expired:
            subscription.is_active = False
            print(f\"⏰ Trial expired for user {subscription.user_id}\")
        
        session.commit()
        print(f\"✅ Marked {len(expired)} trials as expired\")
    
    finally:
        session.close()

def start_trial_checker():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_expired_trials, 'cron', hour=0, minute=0)  # Midnight UTC
    scheduler.start()
    print(\"✅ Trial expiry checker started\")

\"\"\"

$trialJobCode | Out-File -FilePath "backend/services/trial_expiry_job.py" -Encoding UTF8
Write-Host "✅ Trial expiry job created" -ForegroundColor Green
```

**Integrate into main.py**:
```powershell
$integrationUpdate = @"
# Add to your backend/main.py (Flask/FastAPI app initialization)

from services.trial_expiry_job import start_trial_checker
from middleware.tier_validator import require_tier_access

# Start trial checker on app startup
@app.before_first_request
def startup():
    start_trial_checker()

# Example: Protect an endpoint with tier validation
@app.route('/api/code/execute', methods=['POST'])
@require_tier_access(action_required='code_execution')
def execute_code():
    # Your code execution logic
    pass

\"\"\"

Write-Host $integrationUpdate -ForegroundColor Cyan
Write-Host "ℹ️  Add the above code to your backend/main.py" -ForegroundColor Yellow
```

---

## PHASE 4: Frontend Integration (20-30 minutes)

### Step 4A: Create Tier Info Component (React + TypeScript)

```powershell
$tierComponentCode = @"
// File: frontend/src/components/TierInfo.tsx

import React, { useEffect, useState } from 'react';

interface Tier {
  tier_id: string;
  name: string;
  daily_call_limit: number;
  code_execution: boolean;
}

interface Usage {
  api_calls_used: number;
  daily_call_limit: number;
}

interface TrialExpiry {
  trial_expiry: string | null;
}

export const TierInfo: React.FC = () => {
  const [tier, setTier] = useState<Tier | null>(null);
  const [usage, setUsage] = useState<Usage | null>(null);
  const [trialDaysLeft, setTrialDaysLeft] = useState<number | null>(null);

  useEffect(() => {
    fetchTierInfo();
  }, []);

  const fetchTierInfo = async () => {
    try {
      const response = await fetch('/api/user/tier', {
        headers: {
          'Authorization': \`Bearer \${localStorage.getItem('token')}\`
        }
      });
      const data = await response.json();
      setTier(data.tier);
      setUsage(data.usage);

      if (data.tier.tier_id === 'free' && data.trial_expiry) {
        const expiryDate = new Date(data.trial_expiry);
        const today = new Date();
        const daysLeft = Math.ceil((expiryDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
        setTrialDaysLeft(daysLeft);
      }
    } catch (error) {
      console.error('Failed to fetch tier info:', error);
    }
  };

  if (!tier) return <div>Loading...</div>;

  const usagePercent = usage ? (usage.api_calls_used / tier.daily_call_limit) * 100 : 0;
  const isTrialExpired = tier.tier_id === 'free' && trialDaysLeft !== null && trialDaysLeft <= 0;

  return (
    <div className=\"tier-info p-4 bg-white rounded-lg shadow\">
      <h3 className=\"text-lg font-bold\">{tier.name} Tier</h3>

      {tier.tier_id === 'free' && trialDaysLeft !== null && (
        <div className={trialDaysLeft > 0 ? 'bg-blue-50 p-3 rounded mt-2' : 'bg-red-50 p-3 rounded mt-2'}>
          {trialDaysLeft > 0 ? (
            <>
              <p className=\"text-blue-700\">⏰ Trial expires in {trialDaysLeft} days</p>
              <a href=\"/upgrade\" className=\"text-blue-600 underline\">Upgrade Now</a>
            </>
          ) : (
            <>
              <p className=\"text-red-700\">⚠️ Trial Expired - Read-only access only</p>
              <a href=\"/upgrade\" className=\"text-red-600 underline\">Upgrade to PRO</a>
            </>
          )}
        </div>
      )}

      {usage && (
        <>
          <div className=\"mt-4\">
            <div className=\"flex justify-between mb-2\">
              <span>API Calls</span>
              <span>{usage.api_calls_used} / {usage.daily_call_limit}</span>
            </div>
            <div className=\"w-full bg-gray-200 rounded-full h-2\">
              <div
                className=\"bg-blue-600 h-2 rounded-full\"
                style={{ width: \`\${usagePercent}%\` }}
              ></div>
            </div>
          </div>
        </>
      )}

      {!tier.code_execution && tier.tier_id === 'free' && (
        <p className=\"text-yellow-600 mt-4\">⚠️ Code execution disabled on FREE tier</p>
      )}
    </div>
  );
};
\"\"\"

$tierComponentCode | Out-File -FilePath "frontend/src/components/TierInfo.tsx" -Encoding UTF8
Write-Host "✅ Tier info component created" -ForegroundColor Green
```

---

## PHASE 5: User Signup Flow Integration (15-20 minutes)

**Add to your user registration endpoint**:
```powershell
$signupCode = @"
# Add to your backend/routes/auth.py or similar

from datetime import datetime, timedelta
from database.tier_schema import UserSubscription, engine
from sqlalchemy.orm import Session

@app.route('/api/auth/register', methods=['POST'])
def register_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    # Create user (existing logic)
    user_id = create_user(email, password)
    
    # Assign FREE tier by default with 7-day trial
    session = Session(engine)
    subscription = UserSubscription(
        user_id=user_id,
        tier_id='free',
        trial_expiry=datetime.utcnow() + timedelta(days=7),
        is_active=True
    )
    session.add(subscription)
    session.commit()
    session.close()
    
    print(f\"✅ User {user_id} assigned FREE tier (7-day trial)\")
    
    return {
        'success': True,
        'message': 'Welcome to Top Dog! You have 7 days free access.',
        'user_id': user_id
    }, 201

\"\"\"

Write-Host $signupCode -ForegroundColor Cyan
Write-Host "ℹ️  Add the above code to your registration endpoint" -ForegroundColor Yellow
```

---

## PHASE 6: Setup Monitoring & Alerts (10-15 minutes)

**Create monitoring script**:
```powershell
# Create monitoring file
$monitoringCode = @"
\"\"\"Monitor tier usage and compliance\"\"\"

import requests
from datetime import datetime
from sqlalchemy.orm import Session
from database.tier_schema import DailyUsageTracking, UserSubscription, MembershipTier, engine

def monitor_tier_compliance():
    session = Session(engine)
    
    # Find users exceeding limits
    today = datetime.utcnow().date().isoformat()
    
    over_limit = session.query(
        DailyUsageTracking.user_id,
        UserSubscription.tier_id,
        MembershipTier.daily_call_limit,
        DailyUsageTracking.api_calls_used
    ).join(
        UserSubscription,
        DailyUsageTracking.user_id == UserSubscription.user_id
    ).join(
        MembershipTier,
        UserSubscription.tier_id == MembershipTier.tier_id
    ).filter(
        DailyUsageTracking.usage_date == today,
        DailyUsageTracking.api_calls_used > MembershipTier.daily_call_limit
    ).all()
    
    if over_limit:
        print(f\"⚠️  {len(over_limit)} users over limit:\")
        for user_id, tier_id, limit, used in over_limit:
            overage = used - limit
            print(f\"   - {user_id} ({tier_id}): {used}/{limit} (+{overage})\")
    else:
        print(f\"✅ All users within limits\")
    
    session.close()

if __name__ == '__main__':
    monitor_tier_compliance()

\"\"\"

$monitoringCode | Out-File -FilePath "backend/scripts/monitor_tiers.py" -Encoding UTF8
Write-Host "✅ Monitoring script created" -ForegroundColor Green
```

**Schedule with Windows Task Scheduler**:
```powershell
# Schedule monitoring to run hourly
$trigger = New-ScheduledJobTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)
Register-ScheduledJob -Name "Top Dog-Tier-Monitor" `
  -ScriptBlock { 
    cd "C:\Quellum-topdog-ide\backend"
    python scripts/monitor_tiers.py
  } -Trigger $trigger

Write-Host "✅ Monitoring scheduled to run every hour" -ForegroundColor Green
```

---

## PHASE 7: Test the Implementation (20-30 minutes)

### Step 7A: Create Test User

```powershell
$testScript = @"
\"\"\"Create test user with FREE tier\"\"\"

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.tier_schema import UserSubscription, DailyUsageTracking, MembershipTier, engine

def create_test_user():
    session = Session(engine)
    
    # Create FREE tier user
    subscription = UserSubscription(
        user_id='test-user-001',
        tier_id='free',
        trial_expiry=datetime.utcnow() + timedelta(days=7),
        is_active=True
    )
    session.add(subscription)
    
    # Initialize usage tracking
    usage = DailyUsageTracking(
        user_id='test-user-001',
        usage_date=datetime.utcnow().date().isoformat(),
        api_calls_used=0
    )
    session.add(usage)
    
    session.commit()
    
    # Verify
    tier_info = session.query(MembershipTier).filter_by(tier_id='free').first()
    print(f\"✅ Test user created\")
    print(f\"   User: test-user-001\")
    print(f\"   Tier: {tier_info.name}\")
    print(f\"   Limit: {tier_info.daily_call_limit} calls/day\")
    print(f\"   Trial expires: {subscription.trial_expiry}\")
    
    session.close()

create_test_user()

\"\"\"

$testScript | Out-File -FilePath "backend/scripts/create_test_user.py" -Encoding UTF8

cd backend
python scripts/create_test_user.py
cd ..
Write-Host "✅ Test user created" -ForegroundColor Green
```

### Step 7B: Test Rate Limiting

```powershell
# Test the rate limiter with a simple request
$testUrl = "http://localhost:5000/api/test/rate-limit"
$headers = @{
    'X-User-ID' = 'test-user-001'
    'Content-Type' = 'application/json'
}

Write-Host "Testing rate limiter..." -ForegroundColor Cyan
for ($i = 1; $i -le 25; $i++) {
    $response = Invoke-WebRequest -Uri $testUrl -Headers $headers -ErrorAction SilentlyContinue
    $status = $response.StatusCode
    $result = $response.Content | ConvertFrom-Json
    
    if ($status -eq 429) {
        Write-Host "Call $i: ❌ RATE LIMITED (429)" -ForegroundColor Red
        Write-Host "Message: $($result.error)" -ForegroundColor Red
        break
    } else {
        Write-Host "Call $i: ✅ Allowed (Remaining: $($result.remaining))" -ForegroundColor Green
    }
}
```

---

## PHASE 8: Deployment Checklist

```powershell
$checklist = @"
DEPLOYMENT VERIFICATION CHECKLIST
═════════════════════════════════

Database:
  ☐ Tier schema created in backend/database/tier_schema.py
  ☐ Database migrations run (alembic upgrade head)
  ☐ All 4 tables created (membership_tiers, user_subscriptions, daily_usage_tracking, tier_audit_log)
  ☐ All 9 tiers populated via seed script

Backend Services:
  ☐ Rate limiter service created (backend/services/rate_limiter.py)
  ☐ Tier validator middleware created (backend/middleware/tier_validator.py)
  ☐ Trial expiry job created (backend/services/trial_expiry_job.py)
  ☐ Services integrated into main.py
  ☐ New routes added for tier endpoints

Frontend:
  ☐ TierInfo component created (frontend/src/components/TierInfo.tsx)
  ☐ Component imported in relevant pages
  ☐ Tier display shows correctly
  ☐ Trial countdown visible on FREE tier
  ☐ Upgrade buttons point to correct URLs

Testing:
  ☐ Test user 'test-user-001' created on FREE tier
  ☐ Rate limiting works (blocks at 20 calls/day for FREE)
  ☐ Code execution blocked on FREE tier
  ☐ Trial expiry job runs at midnight UTC
  ☐ PRO tier has code execution enabled
  ☐ TEAMS tiers support team members

Monitoring:
  ☐ Monitoring script running (monitor_tiers.py)
  ☐ Trial expiry job scheduled (every midnight)
  ☐ Logs showing tier checks

Documentation:
  ☐ Team understands tier restrictions
  ☐ API docs updated with tier requirements
  ☐ Upgrade flow documented
\"@

Write-Host $checklist -ForegroundColor Cyan
```

---

## PHASE 9: Post-Launch Operations (Ongoing)

### Weekly Tier Report

```powershell
# Create weekly report script
$weeklyReport = @"
\"\"\"Weekly tier analytics report\"\"\"

from datetime import datetime
from sqlalchemy.orm import Session
from database.tier_schema import UserSubscription, engine

def generate_weekly_report():
    session = Session(engine)
    
    total_users = session.query(UserSubscription).count()
    free_users = session.query(UserSubscription).filter_by(tier_id='free').count()
    pro_users = session.query(UserSubscription).filter(
        UserSubscription.tier_id.like('pro%')
    ).count()
    teams_users = session.query(UserSubscription).filter(
        UserSubscription.tier_id.like('teams%')
    ).count()
    enterprise_users = session.query(UserSubscription).filter(
        UserSubscription.tier_id.like('enterprise%')
    ).count()
    
    conversion_rate = (pro_users / free_users * 100) if free_users > 0 else 0
    
    print(f\"WEEKLY TIER REPORT - {datetime.now().strftime('%Y-%m-%d')}\")
    print(f\"Total Users: {total_users}\")
    print(f\"  - FREE: {free_users} ({free_users/total_users*100:.1f}%)\")
    print(f\"  - PRO: {pro_users} ({pro_users/total_users*100:.1f}%)\")
    print(f\"  - TEAMS: {teams_users} ({teams_users/total_users*100:.1f}%)\")
    print(f\"  - ENTERPRISE: {enterprise_users} ({enterprise_users/total_users*100:.1f}%)\")
    print(f\"\\nConversion Rate (FREE→PRO): {conversion_rate:.1f}%\")
    
    if conversion_rate < 5:
        print(f\"⚠️  Low conversion - consider adjusting FREE tier\")
    
    session.close()

generate_weekly_report()

\"\"\"

$weeklyReport | Out-File -FilePath "backend/scripts/weekly_report.py" -Encoding UTF8
Write-Host "✅ Weekly report script created" -ForegroundColor Green
```

---

## TROUBLESHOOTING

### Issue 1: Users Hit Rate Limit Immediately

**Problem**: Limit blocks after just a few calls

**Solution**:
```python
# Ensure date is in UTC and consistent
from datetime import datetime, timezone

today = datetime.now(timezone.utc).date().isoformat()  # Use UTC, not local time
```

### Issue 2: FREE Trial Not Expiring

**Problem**: Users still have access after 7 days

**Solution**:
```python
# Check that trial_expiry_job is running
# Verify datetime comparison uses UTC
if datetime.utcnow() > subscription.trial_expiry:  # Use utcnow(), not now()
    # Deactivate
```

### Issue 3: Code Execution Not Blocked on FREE

**Problem**: FREE tier users can execute code

**Solution**:
```python
# Ensure middleware is applied BEFORE the handler
@app.route('/api/code/execute', methods=['POST'])
@require_tier_access(action_required='code_execution')  # MUST be applied first
def execute_code():
    pass
```

### Issue 4: Database Connection Issues

**Solution**:
```python
# Test connection
from database.tier_schema import engine
try:
    connection = engine.connect()
    print("✅ Database connected")
    connection.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

---

## QUICK REFERENCE

```powershell
# 1. CREATE DATABASE
cd backend
python -c "from database.tier_schema import Base, engine; Base.metadata.create_all(engine)"

# 2. POPULATE TIERS
python seeds/populate_tiers.py

# 3. RUN BACKEND
python main.py

# 4. START MONITORING
python scripts/monitor_tiers.py

# 5. TEST
python scripts/create_test_user.py

# 6. VERIFY
python -c "from scripts.monitor_tiers import monitor_tier_compliance; monitor_tier_compliance()"
```

---

## NEXT STEPS

1. **Today**: Run PHASE 1 & 2 (database setup + populate tiers)
2. **Today**: Run PHASE 3 & 4 (backend + frontend integration)
3. **Tomorrow**: Run PHASE 5, 6, 7 (signup, monitoring, testing)
4. **This week**: Complete PHASE 8 checklist and deploy to production
5. **Ongoing**: Run PHASE 9 weekly reports

**Expected Timeline**: 4-6 hours total

All file paths now reference `C:\Quellum-topdog-ide` ✅
All code matches your **Python backend** + **React/TypeScript frontend** tech stack ✅
Ready to execute! 🚀
