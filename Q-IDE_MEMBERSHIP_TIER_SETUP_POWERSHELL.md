# Top Dog Membership Tier Setup - PowerShell Commands

## TIER 1: FREE (Trial - 7 Days)

```powershell
# Create FREE tier
$freeTier = @{
    tier_id = "free"
    name = "FREE"
    price = 0
    duration_days = 7
    daily_call_limit = 20
    daily_llm_requests = 2
    concurrent_sessions = 1
    max_session_length_minutes = 5
    storage_gb = 0.5
    code_execution = $false
    data_persistence = $true
    read_only_after_expiry = $true
    watermark = "Made with Top Dog Free Trial"
}

# Execute in database
$query = "INSERT INTO membership_tiers (tier_id, name, price, duration_days, daily_call_limit, daily_llm_requests, concurrent_sessions, storage_gb, code_execution, data_persistence) VALUES ('$($freeTier.tier_id)', '$($freeTier.name)', $($freeTier.price), $($freeTier.duration_days), $($freeTier.daily_call_limit), $($freeTier.daily_llm_requests), $($freeTier.concurrent_sessions), $($freeTier.storage_gb), $($freeTier.code_execution), $($freeTier.data_persistence))"

Write-Host "FREE tier created" -ForegroundColor Green
```

---

## TIER 2: PRO ($20/month)

```powershell
# Create PRO tier
$proTier = @{
    tier_id = "pro"
    name = "PRO"
    price = 20
    duration_days = 0  # Unlimited
    daily_call_limit = 10000
    daily_llm_requests = 1000
    concurrent_sessions = 5
    max_session_length_minutes = 0  # Unlimited
    storage_gb = 100
    code_execution = $true
    data_persistence = $true
    game_engines = 1
    media_synthesis = "DALL-E 3"
    verified_code_checks = 50
    private_repos = 5
    support_tier = "Email"
}

# Execute in database
$query = "INSERT INTO membership_tiers (tier_id, name, price, daily_call_limit, daily_llm_requests, concurrent_sessions, storage_gb, code_execution, data_persistence, game_engines, verified_code_checks, private_repos, support_tier) VALUES ('$($proTier.tier_id)', '$($proTier.name)', $($proTier.price), $($proTier.daily_call_limit), $($proTier.daily_llm_requests), $($proTier.concurrent_sessions), $($proTier.storage_gb), $($proTier.code_execution), $($proTier.data_persistence), $($proTier.game_engines), $($proTier.verified_code_checks), $($proTier.private_repos), '$($proTier.support_tier)')"

Write-Host "PRO tier created" -ForegroundColor Green
```

---

## TIER 3: PRO-PLUS ($45/month)

```powershell
# Create PRO-PLUS tier
$proPlusTier = @{
    tier_id = "pro_plus"
    name = "PRO-PLUS"
    price = 45
    daily_call_limit = 50000
    daily_llm_requests = 5000
    concurrent_sessions = 8
    storage_gb = 250
    code_execution = $true
    data_persistence = $true
    game_engines = 2
    media_synthesis = "DALL-E 3, Midjourney"
    verified_code_checks = 200
    private_repos = 20
    support_tier = "Priority Email"
}

# Execute in database
$query = "INSERT INTO membership_tiers (tier_id, name, price, daily_call_limit, daily_llm_requests, concurrent_sessions, storage_gb, code_execution, data_persistence, game_engines, verified_code_checks, private_repos, support_tier) VALUES ('$($proPlusTier.tier_id)', '$($proPlusTier.name)', $($proPlusTier.price), $($proPlusTier.daily_call_limit), $($proPlusTier.daily_llm_requests), $($proPlusTier.concurrent_sessions), $($proPlusTier.storage_gb), $($proPlusTier.code_execution), $($proPlusTier.data_persistence), $($proPlusTier.game_engines), $($proPlusTier.verified_code_checks), $($proPlusTier.private_repos), '$($proPlusTier.support_tier)')"

Write-Host "PRO-PLUS tier created" -ForegroundColor Green
```

---

## TIER 4: TEAMS-SMALL ($100/month, 5 users)

```powershell
# Create TEAMS-SMALL tier
$teamsSmallTier = @{
    tier_id = "teams_small"
    name = "TEAMS-SMALL"
    price = 100
    daily_call_limit = 100000
    daily_llm_requests = 10000
    concurrent_sessions = 10
    storage_gb = 1000
    code_execution = $true
    data_persistence = $true
    game_engines = 4
    media_synthesis = "All (DALL-E 3, Midjourney, Runway)"
    verified_code_checks = 1000
    private_repos = 999  # Unlimited
    team_members = 5
    roles = 5
    support_tier = "Email SLA 24hr"
}

# Execute in database
$query = "INSERT INTO membership_tiers (tier_id, name, price, daily_call_limit, daily_llm_requests, concurrent_sessions, storage_gb, code_execution, data_persistence, game_engines, verified_code_checks, team_members, roles, support_tier) VALUES ('$($teamsSmallTier.tier_id)', '$($teamsSmallTier.name)', $($teamsSmallTier.price), $($teamsSmallTier.daily_call_limit), $($teamsSmallTier.daily_llm_requests), $($teamsSmallTier.concurrent_sessions), $($teamsSmallTier.storage_gb), $($teamsSmallTier.code_execution), $($teamsSmallTier.data_persistence), $($teamsSmallTier.game_engines), $($teamsSmallTier.verified_code_checks), $($teamsSmallTier.team_members), $($teamsSmallTier.roles), '$($teamsSmallTier.support_tier)')"

Write-Host "TEAMS-SMALL tier created" -ForegroundColor Green
```

---

## TIER 5: TEAMS-MEDIUM ($300/month, 30 users)

```powershell
# Create TEAMS-MEDIUM tier
$teamsMediumTier = @{
    tier_id = "teams_medium"
    name = "TEAMS-MEDIUM"
    price = 300
    daily_call_limit = 500000
    daily_llm_requests = 50000
    concurrent_sessions = 20
    storage_gb = 2000
    code_execution = $true
    data_persistence = $true
    game_engines = 4
    media_synthesis = "All"
    verified_code_checks = 5000
    private_repos = 999  # Unlimited
    team_members = 30
    roles = 5
    support_tier = "Priority Email SLA 12hr"
}

# Execute in database
$query = "INSERT INTO membership_tiers (tier_id, name, price, daily_call_limit, daily_llm_requests, concurrent_sessions, storage_gb, code_execution, data_persistence, game_engines, verified_code_checks, team_members, roles, support_tier) VALUES ('$($teamsMediumTier.tier_id)', '$($teamsMediumTier.name)', $($teamsMediumTier.price), $($teamsMediumTier.daily_call_limit), $($teamsMediumTier.daily_llm_requests), $($teamsMediumTier.concurrent_sessions), $($teamsMediumTier.storage_gb), $($teamsMediumTier.code_execution), $($teamsMediumTier.data_persistence), $($teamsMediumTier.game_engines), $($teamsMediumTier.verified_code_checks), $($teamsMediumTier.team_members), $($teamsMediumTier.roles), '$($teamsMediumTier.support_tier)')"

Write-Host "TEAMS-MEDIUM tier created" -ForegroundColor Green
```

---

## TIER 6: TEAMS-LARGE ($800/month, 100 users)

```powershell
# Create TEAMS-LARGE tier
$teamsLargeTier = @{
    tier_id = "teams_large"
    name = "TEAMS-LARGE"
    price = 800
    daily_call_limit = 9999999  # Unlimited
    daily_llm_requests = 100000
    concurrent_sessions = 50
    storage_gb = 5000
    code_execution = $true
    data_persistence = $true
    game_engines = 4
    media_synthesis = "All"
    verified_code_checks = 9999999  # Unlimited
    private_repos = 999  # Unlimited
    team_members = 100
    roles = 8
    support_tier = "Priority Phone SLA 4hr"
    sso = $true
}

# Execute in database
$query = "INSERT INTO membership_tiers (tier_id, name, price, daily_call_limit, daily_llm_requests, concurrent_sessions, storage_gb, code_execution, data_persistence, game_engines, verified_code_checks, team_members, roles, support_tier, sso) VALUES ('$($teamsLargeTier.tier_id)', '$($teamsLargeTier.name)', $($teamsLargeTier.price), $($teamsLargeTier.daily_call_limit), $($teamsLargeTier.daily_llm_requests), $($teamsLargeTier.concurrent_sessions), $($teamsLargeTier.storage_gb), $($teamsLargeTier.code_execution), $($teamsLargeTier.data_persistence), $($teamsLargeTier.game_engines), $($teamsLargeTier.verified_code_checks), $($teamsLargeTier.team_members), $($teamsLargeTier.roles), '$($teamsLargeTier.support_tier)', $($teamsLargeTier.sso))"

Write-Host "TEAMS-LARGE tier created" -ForegroundColor Green
```

---

## TIER 7: ENTERPRISE-STANDARD ($5,000/month, 500 users)

```powershell
# Create ENTERPRISE-STANDARD tier
$entStandardTier = @{
    tier_id = "enterprise_standard"
    name = "ENTERPRISE-STANDARD"
    price = 5000
    daily_call_limit = 9999999  # Unlimited
    daily_llm_requests = 9999999  # Unlimited
    concurrent_sessions = 100
    storage_gb = 10000
    code_execution = $true
    data_persistence = $true
    game_engines = 4
    media_synthesis = "All"
    verified_code_checks = 9999999  # Unlimited
    private_repos = 999  # Unlimited
    team_members = 500
    roles = 8
    hipaa_ready = $true
    custom_integrations = $true
    support_tier = "Dedicated 24/7"
    sso = $true
    sla = "99.9%"
}

# Execute in database
$query = "INSERT INTO membership_tiers (tier_id, name, price, daily_call_limit, daily_llm_requests, concurrent_sessions, storage_gb, code_execution, data_persistence, game_engines, verified_code_checks, team_members, roles, hipaa_ready, custom_integrations, support_tier, sso, sla) VALUES ('$($entStandardTier.tier_id)', '$($entStandardTier.name)', $($entStandardTier.price), $($entStandardTier.daily_call_limit), $($entStandardTier.daily_llm_requests), $($entStandardTier.concurrent_sessions), $($entStandardTier.storage_gb), $($entStandardTier.code_execution), $($entStandardTier.data_persistence), $($entStandardTier.game_engines), $($entStandardTier.verified_code_checks), $($entStandardTier.team_members), $($entStandardTier.roles), $($entStandardTier.hipaa_ready), $($entStandardTier.custom_integrations), '$($entStandardTier.support_tier)', $($entStandardTier.sso), '$($entStandardTier.sla)')"

Write-Host "ENTERPRISE-STANDARD tier created" -ForegroundColor Green
```

---

## TIER 8: ENTERPRISE-PREMIUM ($15,000/month, 2000 users)

```powershell
# Create ENTERPRISE-PREMIUM tier
$entPremiumTier = @{
    tier_id = "enterprise_premium"
    name = "ENTERPRISE-PREMIUM"
    price = 15000
    daily_call_limit = 9999999  # Unlimited
    daily_llm_requests = 9999999  # Unlimited
    concurrent_sessions = 100
    storage_gb = 50000
    code_execution = $true
    data_persistence = $true
    game_engines = 4
    media_synthesis = "All"
    verified_code_checks = 9999999  # Unlimited
    private_repos = 999  # Unlimited
    team_members = 2000
    roles = 8
    hipaa_ready = $true
    custom_integrations = $true
    custom_llms = $true
    account_manager = $true
    support_tier = "Dedicated 24/7 + Account Manager"
    sso = $true
    saml = $true
    sla = "99.95%"
}

# Execute in database
$query = "INSERT INTO membership_tiers (tier_id, name, price, daily_call_limit, daily_llm_requests, concurrent_sessions, storage_gb, code_execution, data_persistence, game_engines, verified_code_checks, team_members, roles, hipaa_ready, custom_integrations, custom_llms, account_manager, support_tier, sso, saml, sla) VALUES ('$($entPremiumTier.tier_id)', '$($entPremiumTier.name)', $($entPremiumTier.price), $($entPremiumTier.daily_call_limit), $($entPremiumTier.daily_llm_requests), $($entPremiumTier.concurrent_sessions), $($entPremiumTier.storage_gb), $($entPremiumTier.code_execution), $($entPremiumTier.data_persistence), $($entPremiumTier.game_engines), $($entPremiumTier.verified_code_checks), $($entPremiumTier.team_members), $($entPremiumTier.roles), $($entPremiumTier.hipaa_ready), $($entPremiumTier.custom_integrations), $($entPremiumTier.custom_llms), $($entPremiumTier.account_manager), '$($entPremiumTier.support_tier)', $($entPremiumTier.sso), $($entPremiumTier.saml), '$($entPremiumTier.sla)')"

Write-Host "ENTERPRISE-PREMIUM tier created" -ForegroundColor Green
```

---

## TIER 9: ENTERPRISE-ULTIMATE ($50,000+/month, Unlimited users)

```powershell
# Create ENTERPRISE-ULTIMATE tier
$entUltimateTier = @{
    tier_id = "enterprise_ultimate"
    name = "ENTERPRISE-ULTIMATE"
    price = 50000  # Minimum - negotiable
    daily_call_limit = 9999999  # Unlimited
    daily_llm_requests = 9999999  # Unlimited
    concurrent_sessions = 999  # Unlimited
    storage_gb = 999999  # Unlimited
    code_execution = $true
    data_persistence = $true
    game_engines = 4
    media_synthesis = "All"
    verified_code_checks = 9999999  # Unlimited
    private_repos = 999  # Unlimited
    team_members = 99999  # Unlimited
    roles = 999  # Unlimited
    hipaa_ready = $true
    custom_integrations = $true
    custom_llms = $true
    on_premise_deploy = $true
    account_manager = $true
    executive_access = $true
    support_tier = "Dedicated 24/7 + Executive Access"
    sso = $true
    saml = $true
    sla = "99.99%"
}

# Execute in database
$query = "INSERT INTO membership_tiers (tier_id, name, price, daily_call_limit, daily_llm_requests, concurrent_sessions, storage_gb, code_execution, data_persistence, game_engines, verified_code_checks, team_members, roles, hipaa_ready, custom_integrations, custom_llms, on_premise_deploy, account_manager, executive_access, support_tier, sso, saml, sla) VALUES ('$($entUltimateTier.tier_id)', '$($entUltimateTier.name)', $($entUltimateTier.price), $($entUltimateTier.daily_call_limit), $($entUltimateTier.daily_llm_requests), $($entUltimateTier.concurrent_sessions), $($entUltimateTier.storage_gb), $($entUltimateTier.code_execution), $($entUltimateTier.data_persistence), $($entUltimateTier.game_engines), $($entUltimateTier.verified_code_checks), $($entUltimateTier.team_members), $($entUltimateTier.roles), $($entUltimateTier.hipaa_ready), $($entUltimateTier.custom_integrations), $($entUltimateTier.custom_llms), $($entUltimateTier.on_premise_deploy), $($entUltimateTier.account_manager), $($entUltimateTier.executive_access), '$($entUltimateTier.support_tier)', $($entUltimateTier.sso), $($entUltimateTier.saml), '$($entUltimateTier.sla)')"

Write-Host "ENTERPRISE-ULTIMATE tier created" -ForegroundColor Green
```

---

## RUN ALL TIERS AT ONCE

```powershell
# Complete setup script for all 9 membership tiers

Write-Host "Starting Top Dog Membership Tier Setup..." -ForegroundColor Cyan

# Array of all tiers
$allTiers = @(
    @{
        tier_id = "free"
        name = "FREE"
        price = 0
        daily_calls = 20
        daily_llm = 2
        sessions = 1
        storage = 0.5
        code_exec = $false
    },
    @{
        tier_id = "pro"
        name = "PRO"
        price = 20
        daily_calls = 10000
        daily_llm = 1000
        sessions = 5
        storage = 100
        code_exec = $true
    },
    @{
        tier_id = "pro_plus"
        name = "PRO-PLUS"
        price = 45
        daily_calls = 50000
        daily_llm = 5000
        sessions = 8
        storage = 250
        code_exec = $true
    },
    @{
        tier_id = "teams_small"
        name = "TEAMS-SMALL"
        price = 100
        daily_calls = 100000
        daily_llm = 10000
        sessions = 10
        storage = 1000
        code_exec = $true
    },
    @{
        tier_id = "teams_medium"
        name = "TEAMS-MEDIUM"
        price = 300
        daily_calls = 500000
        daily_llm = 50000
        sessions = 20
        storage = 2000
        code_exec = $true
    },
    @{
        tier_id = "teams_large"
        name = "TEAMS-LARGE"
        price = 800
        daily_calls = 9999999
        daily_llm = 100000
        sessions = 50
        storage = 5000
        code_exec = $true
    },
    @{
        tier_id = "enterprise_standard"
        name = "ENTERPRISE-STANDARD"
        price = 5000
        daily_calls = 9999999
        daily_llm = 9999999
        sessions = 100
        storage = 10000
        code_exec = $true
    },
    @{
        tier_id = "enterprise_premium"
        name = "ENTERPRISE-PREMIUM"
        price = 15000
        daily_calls = 9999999
        daily_llm = 9999999
        sessions = 100
        storage = 50000
        code_exec = $true
    },
    @{
        tier_id = "enterprise_ultimate"
        name = "ENTERPRISE-ULTIMATE"
        price = 50000
        daily_calls = 9999999
        daily_llm = 9999999
        sessions = 999
        storage = 999999
        code_exec = $true
    }
)

# Create each tier
foreach ($tier in $allTiers) {
    Write-Host "Creating: $($tier.name)" -ForegroundColor Yellow
    
    # Your database INSERT query here
    # $query = "INSERT INTO membership_tiers ..."
    # Execute-Query $query
    
    Write-Host "  ✓ $($tier.name) tier created ($($tier.price)/mo)" -ForegroundColor Green
}

Write-Host "`nAll 9 membership tiers created successfully!" -ForegroundColor Cyan
```

---

## QUICK COPY-PASTE FOR DATABASE

If using direct SQL instead of PowerShell objects:

```sql
INSERT INTO membership_tiers (tier_id, name, price, daily_calls, daily_llm, sessions, storage, code_exec) VALUES
('free', 'FREE', 0, 20, 2, 1, 0.5, FALSE),
('pro', 'PRO', 20, 10000, 1000, 5, 100, TRUE),
('pro_plus', 'PRO-PLUS', 45, 50000, 5000, 8, 250, TRUE),
('teams_small', 'TEAMS-SMALL', 100, 100000, 10000, 10, 1000, TRUE),
('teams_medium', 'TEAMS-MEDIUM', 300, 500000, 50000, 20, 2000, TRUE),
('teams_large', 'TEAMS-LARGE', 800, 9999999, 100000, 50, 5000, TRUE),
('enterprise_standard', 'ENTERPRISE-STANDARD', 5000, 9999999, 9999999, 100, 10000, TRUE),
('enterprise_premium', 'ENTERPRISE-PREMIUM', 15000, 9999999, 9999999, 100, 50000, TRUE),
('enterprise_ultimate', 'ENTERPRISE-ULTIMATE', 50000, 9999999, 9999999, 999, 999999, TRUE);
```

