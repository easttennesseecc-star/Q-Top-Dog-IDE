param(
  [string]$Email = "you@example.com",
  # For production replace with SecureString handling
  [string]$UserPassword = "password123",
  [string]$ApiHost = "127.0.0.1",
  [int]$Port = 8000,
  [int]$Funds = 0,
  [string]$DevFundsKey = "local-dev-seed",
  [string]$DevSeedKey = "local-dev-seed"
)

$ErrorActionPreference = 'Stop'
$base = "http://$ApiHost`:$Port"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "[1/7] Activating venv..." -ForegroundColor Cyan
& "$PSScriptRoot\..\.venv\Scripts\Activate.ps1"

# Ensure env keys for easy local use
$env:DEV_FUNDS_KEY = $DevFundsKey
$env:DEV_SEED_KEY = $DevSeedKey
if (-not $env:FOUNDER_EMAIL) { $env:FOUNDER_EMAIL = $Email }

function Test-Health($url) {
  try { Invoke-RestMethod -Uri "$url/health" -Method GET -TimeoutSec 2 | Out-Null; return $true } catch { return $false }
}

Write-Host "[2/7] Ensuring API is running at $base ..." -ForegroundColor Cyan
if (-not (Test-Health $base)) {
  Write-Host "  Starting uvicorn..." -ForegroundColor Yellow
  $venvPython = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"
  if (-not (Test-Path $venvPython)) {
    Write-Host "  Warning: venv python not found at $venvPython, falling back to 'python' on PATH" -ForegroundColor Yellow
    $venvPython = "python"
  }
  $cmd = "& `"$venvPython`" -m uvicorn backend.main:app --host $ApiHost --port $Port"
  Start-Process powershell -ArgumentList "-NoLogo","-NoExit","-Command",$cmd | Out-Null
  # Wait for readiness
  $maxWait = 40; $ok = $false
  for ($i=0; $i -lt $maxWait; $i++) {
    Start-Sleep -Seconds 1
    if (Test-Health $base) { $ok = $true; break }
  }
  if (-not $ok) { throw "API did not become healthy at $base within ${maxWait}s" }
}

Write-Host "[3/7] Registering user (idempotent)..." -ForegroundColor Cyan
try {
  $regBody = @{ email=$Email; username=($Email.Split('@')[0]); password=$UserPassword } | ConvertTo-Json
  Invoke-RestMethod -Uri "$base/api/v1/auth/register" -Method POST -ContentType 'application/json' -Body $regBody | Out-Null
} catch { Write-Host "  Register likely already done (continuing)" -ForegroundColor DarkGray }

Write-Host "[4/7] Logging in..." -ForegroundColor Cyan
$loginBody = @{ email=$Email; password=$UserPassword } | ConvertTo-Json
$login = Invoke-RestMethod -Uri "$base/api/v1/auth/login" -Method POST -ContentType 'application/json' -Body $loginBody
$jwt = $login.data.token
if (-not $jwt) { throw "Login failed; no token returned" }

Write-Host "[5/9] Seeding dev tiers and subscription..." -ForegroundColor Cyan
Invoke-RestMethod -Uri "$base/api/tier/dev/seed" -Method POST -Headers @{ Authorization = "Bearer $jwt"; 'X-Dev-Seed-Key' = $DevSeedKey } | Out-Null

Write-Host "[6/9] Checking tier limits..." -ForegroundColor Cyan
$limits = Invoke-RestMethod -Uri "$base/api/tier/limits" -Method GET -Headers @{ Authorization = "Bearer $jwt" }
Write-Host ("  Tier: {0}  Limit: {1}  Used today: {2}  Remaining: {3}" -f $limits.data.tier.name, $limits.data.limit, $limits.data.used, $limits.data.remaining)

if ($Funds -gt 0) {
  Write-Host "[7/9] Seeding funds (dev only)..." -ForegroundColor Cyan
  $fundsBody = @{ email=$Email; amount=$Funds; txn_id="dev-seed" } | ConvertTo-Json
  Invoke-RestMethod -Uri "$base/api/v1/auth/dev/add-funds" -Method POST -ContentType 'application/json' -Body $fundsBody -Headers @{ 'X-Dev-Funds-Key'=$DevFundsKey } | Out-Null
} else {
  Write-Host "[7/9] Skipping funds seeding (Funds=0; using tier-based limits)" -ForegroundColor DarkGray
}

Write-Host "[8/9] Listing models and fetching recommendations..." -ForegroundColor Cyan
$models = Invoke-RestMethod -Uri "$base/api/v1/marketplace/models?limit=5" -Method GET
$firstModel = ($models.data | Select-Object -First 1).id
$recBody = @{ query = "Generate a Python function"; budget = "medium" } | ConvertTo-Json
$recs = Invoke-RestMethod -Uri "$base/api/v1/marketplace/recommendations" -Method POST -ContentType 'application/json' -Body $recBody -Headers @{ Authorization = "Bearer $jwt" }
$chosen = if ($recs.data.Length -gt 0) { $recs.data[0].model_id } else { $firstModel }

Write-Host "[9/9] Chatting with agent..." -ForegroundColor Cyan
$chatBody = @{ model_id=$chosen; messages=@(@{ role="user"; content="Say hi in one sentence." }) } | ConvertTo-Json -Depth 5
$chat = Invoke-RestMethod -Uri "$base/api/v1/agent/chat" -Method POST -ContentType 'application/json' -Body $chatBody -Headers @{ Authorization = "Bearer $jwt" }

Write-Host "\n=== Quickstart Results ===" -ForegroundColor Green
Write-Host ("Model: {0}" -f $chosen)
Write-Host ("Response: {0}" -f $chat.data.response)
Write-Host ("Cost: ${0}" -f ([math]::Round($chat.data.cost,4)))
if ($chat.data.rate_limit) { Write-Host ("Remaining calls today: {0}/{1} (tier: {2})" -f $chat.data.rate_limit.remaining, $chat.data.rate_limit.limit, $chat.data.rate_limit.tier) }
