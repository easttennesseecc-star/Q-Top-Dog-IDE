param(
  [string]$Repo = "easttennesseecc-star/Q-Top-Dog-IDE",
  [string]$StagingRef = "main",
  [string]$ProdEnvironment = "prod",
  [string]$Strategy = "canary",
  [string]$StagingNamespace = "topdog-staging",
  [string]$ProdNamespace = "topdog-ide",
  [string]$ProdConfirm = "PROCEED-PROD",
  [string]$StagingHost = "staging-app.topdog-ide.com",
  [string]$ProdHost = "topdog-ide.com",
  [string]$GoogleToken = "",
  [string]$SlackWebhookUrl = $env:SLACK_WEBHOOK_URL
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Require-Gh {
  if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "GitHub CLI 'gh' is required. Install via https://cli.github.com/ and run 'gh auth login'."
  }
}

function Invoke-Workflow {
  param(
    [Parameter(Mandatory=$true)][string]$WorkflowName,
    [Parameter(Mandatory=$true)][hashtable]$Inputs
  )
  $args = @('workflow','run',"$WorkflowName",'--repo',"$Repo")
  foreach ($k in $Inputs.Keys) { $args += @('-f',"$k=$($Inputs[$k])") }
  Write-Host "Dispatching workflow: $WorkflowName ..." -ForegroundColor Cyan
  gh @args | Out-Null
  Start-Sleep -Seconds 3
  $run = gh run list --repo "$Repo" --workflow "$WorkflowName" --limit 1 --json databaseId,status,conclusion,workflowName | ConvertFrom-Json | Select-Object -First 1
  if (-not $run) { throw "Unable to find workflow run for $WorkflowName" }
  $runId = $run.databaseId
  Write-Host "Waiting for run $runId ..." -ForegroundColor Cyan
  gh run watch $runId --repo "$Repo" --exit-status
}

function Test-Url {
  param([Parameter(Mandatory=$true)][string]$Url)
  try {
    $r = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 30
    if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 300) {
      Write-Host "OK: $Url" -ForegroundColor Green
      return $true
    }
    else { Write-Host "WARN ($($r.StatusCode)): $Url" -ForegroundColor Yellow; return $false }
  } catch { Write-Host "FAIL: $Url - $($_.Exception.Message)" -ForegroundColor Red; return $false }
}

function Smoke-Staging {
  Write-Host "Staging smoke-checks..." -ForegroundColor Cyan
  $ok = $true
  $ok = (Test-Url "https://$StagingHost/health") -and $ok
  $ok = (Test-Url "https://$StagingHost/robots.txt") -and $ok
  $ok = (Test-Url "https://$StagingHost/sitemap.xml") -and $ok
  if ($GoogleToken) { $ok = (Test-Url "https://$StagingHost/google$GoogleToken.html") -and $ok }
  $null = Test-Url "https://$StagingHost/BingSiteAuth.xml"  # optional depending on token
  return $ok
}

function Smoke-Prod {
  Write-Host "Production smoke-checks..." -ForegroundColor Cyan
  $ok = $true
  $ok = (Test-Url "https://$ProdHost/health") -and $ok
  $ok = (Test-Url "https://$ProdHost/robots.txt") -and $ok
  $ok = (Test-Url "https://$ProdHost/sitemap.xml") -and $ok
  if ($GoogleToken) { $ok = (Test-Url "https://$ProdHost/google$GoogleToken.html") -and $ok }
  $null = Test-Url "https://$ProdHost/BingSiteAuth.xml"  # optional depending on token
  return $ok
}

function Notify-Slack {
  param([string]$Text)
  if (-not $SlackWebhookUrl) { return }
  try {
    $payload = @{ text = $Text } | ConvertTo-Json -Compress
    Invoke-RestMethod -Uri $SlackWebhookUrl -Method Post -ContentType 'application/json' -Body $payload | Out-Null
  } catch { Write-Warning "Slack notify failed: $($_.Exception.Message)" }
}

Require-Gh

Notify-Slack ":rocket: Starting staging deploy for $Repo@${env:GITHUB_SHA} (ref=$StagingRef)"

# 1) Deploy to Staging
Invoke-Workflow -WorkflowName "Deploy to Staging" -Inputs @{ ref = $StagingRef }
$stageOk = Smoke-Staging

# 2) Canary/Prod deploy
Notify-Slack ":traffic_light: Starting canary/prod deploy for $Repo (ns=$ProdNamespace)"
Invoke-Workflow -WorkflowName "deploy-canary.yml" -Inputs @{
  environment = $ProdEnvironment
  strategy    = $Strategy
  namespace   = $ProdNamespace
  prod_confirm= $ProdConfirm
}
$prodOk = Smoke-Prod

if ($stageOk -and $prodOk) {
  Write-Host "All checks passed." -ForegroundColor Green
  Notify-Slack "✅ Deploy complete. Staging+Prod checks passed for $Repo."
  exit 0
} else {
  Write-Error "One or more checks failed."
  Notify-Slack "❌ Deploy finished with failures. Investigate staging/prod checks."
  exit 1
}
