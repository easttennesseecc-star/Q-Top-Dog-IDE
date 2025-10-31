# Q-IDE Membership Tiers & Pricing Model

## MAIN MEMBERSHIP TIERS

### TIER 1: FREE

**Daily API Call Limits:**
- 20 API calls/day (trial only)
- 2 LLM requests/day (very limited)
- 1 concurrent session
- Community support only
- **Auto-expires after 7 days**

**Features:**
- Core IDE access (VS Code base - read-only features)
- 2 LLM models available (basic GPT, Claude Light)
- No code execution (read-only IDE)
- No game engine access
- No media synthesis
- 512MB storage (limited)
- Public sharing only
- Watermark on all exports: "Made with Q-IDE Free Trial"
- 5 minute max session length
- Data saved (no loss of progress) - BUT read-only after 7 days

**Code:**
```powershell
$tier = @{
    Name = "FREE"
    Price = 0
    DailyCallLimit = 20
    LLMRequests = 2
    ConcurrentSessions = 1
    SessionLength = "5 minutes"
    Storage = "512MB"
    ExpiresAfter = "7 days"
    CodeExecution = $false
    DataPersistence = $true
    ReadOnlyAfter = "7 days"
    Support = "Community"
    Watermark = "Made with Q-IDE Free Trial"
}
```

---

### TIER 2: PRO

**Daily API Call Limits:**
- 10,000 API calls/day
- 1,000 LLM requests/day
- 5 concurrent sessions
- Email support

**Features:**
- Full IDE access
- All 53 LLM models
- 1 game engine (choose: Construct 3, Godot, Unity, Unreal)
- Basic media synthesis (DALL-E 3 only)
- 100GB storage
- Private repos (up to 5)
- Verified code (Overwatch) - limited (50 checks/day)

**Code:**
```powershell
$tier = @{
    Name = "PRO"
    Price = 20
    DailyCallLimit = 10000
    LLMRequests = 1000
    ConcurrentSessions = 5
    Storage = "100GB"
    GameEngines = 1
    MediaSynthesis = "DALL-E 3"
    VerifiedCodeChecks = 50
    Support = "Email"
}
```

---

### TIER 3: TEAMS

**Daily API Call Limits:**
- 100,000 API calls/day
- 10,000 LLM requests/day
- 10 concurrent sessions per user
- 5 team members included
- Priority email support

**Features:**
- Everything in PRO
- All 4 game engines
- All media synthesis (DALL-E 3, Midjourney, Runway)
- 1TB storage
- Unlimited private repos
- Verified code (Overwatch) - 1,000 checks/day
- Team collaboration features
- Role-based access control (5 roles)
- Team billing
- SSO (Single Sign-On)

**Code:**
```powershell
$tier = @{
    Name = "TEAMS"
    Price = 100
    DailyCallLimit = 100000
    LLMRequests = 10000
    ConcurrentSessions = 10
    TeamMembers = 5
    Storage = "1TB"
    GameEngines = 4
    MediaSynthesis = "All"
    VerifiedCodeChecks = 1000
    Roles = 5
    Support = "Priority Email"
}
```

---

### TIER 4: ENTERPRISE

**Daily API Call Limits:**
- Unlimited API calls
- Unlimited LLM requests
- 50+ concurrent sessions
- 100+ users included
- Dedicated support & SLAs

**Features:**
- Everything in TEAMS
- Unlimited storage
- Custom integrations
- Advanced RBAC (8+ roles)
- HIPAA compliance ready
- Verified code (Overwatch) - unlimited checks
- Dedicated account manager
- SLA: 99.99% uptime
- On-premise deployment option
- Custom LLM models
- Advanced security (encryption, audit logs)
- Custom branding

**Code:**
```powershell
$tier = @{
    Name = "ENTERPRISE"
    Price = "Custom"
    DailyCallLimit = "Unlimited"
    LLMRequests = "Unlimited"
    ConcurrentSessions = 50
    Users = 100
    Storage = "Unlimited"
    VerifiedCodeChecks = "Unlimited"
    HIPAAReady = $true
    Support = "Dedicated 24/7"
    SLA = "99.99%"
}
```

---

## COMPLETE TIER COMPARISON TABLE

```
Feature                    | FREE    | PRO        | TEAMS       | ENTERPRISE
================================================================
Price/Month                | $0      | $20        | $100        | Custom
Duration                   | 7 days  | Unlimited  | Unlimited   | Unlimited
Daily API Calls            | 20      | 10,000     | 100,000     | Unlimited
Daily LLM Requests         | 2       | 1,000      | 10,000      | Unlimited
Concurrent Sessions        | 1       | 5          | 10          | 50+
Session Length             | 5 min   | Unlimited  | Unlimited   | Unlimited
Storage                    | 512MB   | 100GB      | 1TB         | Unlimited
Data Persistence           | ❌      | ✅         | ✅          | ✅
Code Execution             | ❌      | ✅         | ✅          | ✅
Team Members               | N/A     | N/A        | 5           | 100+
Private Repos              | 0       | 5          | Unlimited   | Unlimited
Game Engines               | 0       | 1          | 4           | 4
Media Synthesis            | None    | DALL-E 3   | All         | All
Verified Code (Overwatch)  | 0       | 50/day     | 1,000/day   | Unlimited
Roles/Permissions          | 1       | 3          | 5           | 8+
Watermark on Exports       | ✅      | ❌         | ❌          | ❌
HIPAA Ready                | ❌      | ❌         | ❌          | ✅
Custom Integrations        | ❌      | ❌         | ❌          | ✅
On-Premise Deploy          | ❌      | ❌         | ❌          | ✅
Support                    | Community| Email      | Priority    | Dedicated 24/7
SLA                        | None    | None       | 99.9%       | 99.99%
```

---

## SUB-TIERS WITHIN EACH MAIN TIER

### FREE TIER SUB-DIVISIONS

**Free-Basic** (Absolute minimum)
```powershell
$subTier = @{
    Name = "Free-Basic"
    DailyCallLimit = 50
    LLMRequests = 5
    Storage = "512MB"
    Support = "Community Forum Only"
}
```

**Free-Extended** (After free trial)
```powershell
$subTier = @{
    Name = "Free-Extended"
    DailyCallLimit = 100
    LLMRequests = 10
    Storage = "1GB"
    Support = "Community + Chat"
}
```

---

### PRO TIER SUB-DIVISIONS

**Pro-Starter** (Individual developers)
```powershell
$subTier = @{
    Name = "Pro-Starter"
    Price = 20
    DailyCallLimit = 10000
    LLMRequests = 1000
    ConcurrentSessions = 5
    Storage = "100GB"
    GameEngines = 1
    VerifiedCodeChecks = 50
}
```

**Pro-Plus** (Freelancers/Small teams 2-3 people)
```powershell
$subTier = @{
    Name = "Pro-Plus"
    Price = 45
    DailyCallLimit = 50000
    LLMRequests = 5000
    ConcurrentSessions = 8
    Storage = "250GB"
    GameEngines = 2
    VerifiedCodeChecks = 200
    Support = "Priority Email"
}
```

---

### TEAMS TIER SUB-DIVISIONS

**Teams-Small** (5-10 people)
```powershell
$subTier = @{
    Name = "Teams-Small"
    Price = 100
    TeamMembers = 5
    DailyCallLimit = 100000
    LLMRequests = 10000
    VerifiedCodeChecks = 1000
    Support = "Email SLA 24hr"
}
```

**Teams-Medium** (11-30 people)
```powershell
$subTier = @{
    Name = "Teams-Medium"
    Price = 300
    TeamMembers = 30
    DailyCallLimit = 500000
    LLMRequests = 50000
    VerifiedCodeChecks = 5000
    Support = "Priority Email SLA 12hr"
}
```

**Teams-Large** (31-100 people)
```powershell
$subTier = @{
    Name = "Teams-Large"
    Price = 800
    TeamMembers = 100
    DailyCallLimit = "Unlimited"
    LLMRequests = 100000
    VerifiedCodeChecks = "Unlimited"
    Support = "Priority + Phone SLA 4hr"
}
```

---

### ENTERPRISE TIER SUB-DIVISIONS

**Enterprise-Standard** (100-500 users)
```powershell
$subTier = @{
    Name = "Enterprise-Standard"
    Price = 5000
    Users = 500
    DailyCallLimit = "Unlimited"
    VerifiedCodeChecks = "Unlimited"
    Support = "Dedicated 24/7"
    SLA = "99.9%"
}
```

**Enterprise-Premium** (500-2000 users)
```powershell
$subTier = @{
    Name = "Enterprise-Premium"
    Price = 15000
    Users = 2000
    DailyCallLimit = "Unlimited"
    VerifiedCodeChecks = "Unlimited"
    HIPAAReady = $true
    Support = "Dedicated 24/7 + Account Manager"
    SLA = "99.95%"
}
```

**Enterprise-Ultimate** (2000+ users)
```powershell
$subTier = @{
    Name = "Enterprise-Ultimate"
    Price = 50000
    Users = "Unlimited"
    DailyCallLimit = "Unlimited"
    VerifiedCodeChecks = "Unlimited"
    HIPAAReady = $true
    OnPremise = $true
    CustomLLMs = $true
    Support = "Dedicated 24/7 + Executive Access"
    SLA = "99.99%"
}
```

---

## DAILY CALL LIMITS - WHAT COUNTS?

### API Calls Include:
- Each IDE operation (save, compile, run)
- Each LLM inference request
- Each code verification check (Overwatch)
- Each file upload/download
- Each media generation request
- Each database query
- Each game engine asset load

### Daily Limits Reset:
- UTC midnight (00:00 UTC)
- User timezone option in Enterprise tier

### What Happens When Limit Exceeded:
```powershell
# FREE tier
if ($dailyCallsUsed -gt 100) {
    Write-Host "Free tier daily limit reached" -ForegroundColor Red
    Write-Host "Upgrade to Pro for more calls" -ForegroundColor Yellow
    $APIBlocked = $true
}

# PRO tier
if ($dailyCallsUsed -gt 10000) {
    Write-Host "Pro tier daily limit reached" -ForegroundColor Red
    Write-Host "Usage will resume at UTC midnight" -ForegroundColor Yellow
}

# ENTERPRISE tier
if ($dailyCallsUsed -gt 999999999) {
    Write-Host "Unlimited tier - no limits" -ForegroundColor Green
}
```

---

## OVERAGE PRICING (Optional)

```powershell
# For PRO tier when limit exceeded
$overagePerCall = 0.001  # $0.001 per API call
$overagePerLLM = 0.01    # $0.01 per LLM request

# For TEAMS tier when limit exceeded
$overagePerCall = 0.0005  # $0.0005 per API call
$overagePerLLM = 0.005    # $0.005 per LLM request

# Monthly overage cap (won't go higher)
$monthlyOverageCap = 500  # Max $500/month in overages
```

---

## UPGRADE PATH

```
FREE ──→ PRO-Starter ──→ PRO-Plus ──→ TEAMS-Small ──→ TEAMS-Medium ──→ TEAMS-Large ──→ ENTERPRISE
```

---

## SUMMARY

| Tier | Price | Call Limit | Duration | Run Code? |
|------|-------|-----------|----------|-----------|
| FREE | $0 | 20/day | 7 days | ❌ No |
| PRO | $20/mo | 10k/day | Unlimited | ✅ Yes |
| TEAMS | $100/mo | 100k/day | Unlimited | ✅ Yes |
| ENTERPRISE | Custom | Unlimited | Unlimited | ✅ Yes |

**Key Strategy:**
- ✅ FREE is a **TRIAL**, not a functional tier
- ✅ 20 calls/day forces upgrade to PRO ($20)
- ✅ 7-day expiration creates urgency
- ✅ No code execution = can't build anything meaningful
- ✅ Watermark reminds them it's trial version
- ✅ Competitive advantage: Users see Q-IDE is SO much better than free tools, they'll pay
- ✅ Everyone who wants to actually USE Q-IDE upgrades to PRO ($20/mo minimum)
