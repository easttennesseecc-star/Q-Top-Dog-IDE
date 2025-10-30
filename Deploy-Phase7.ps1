# 🚀 PHASE 7: PRODUCTION DEPLOYMENT - WINDOWS POWERSHELL SCRIPT
# This script automates deployment to Digital Ocean App Platform
# Requirements: Digital Ocean CLI (doctl) installed and authenticated, Docker Desktop running

param(
    [string]$AppName = "quellum-topdog-ai",
    [string]$Region = "nyc3",
    [switch]$SkipDockerBuild,
    [switch]$SkipPush
)

# Configuration
$DockerRegistry = "registry.digitalocean.com"
$ImageName = "topdog-latest"
$ErrorActionPreference = "Stop"

# Color functions
function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Section {
    param([string]$Message)
    Write-Host "========================================" -ForegroundColor Blue
    Write-Host $Message -ForegroundColor Blue
    Write-Host "========================================" -ForegroundColor Blue
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

# Pre-flight checks
Write-Section "PRE-FLIGHT CHECKS"

# Check Docker
try {
    docker --version | Out-Null
    Write-Success "Docker found"
} catch {
    Write-Error-Custom "Docker is not installed or not accessible"
    exit 1
}

# Check doctl
try {
    doctl version | Out-Null
    Write-Success "Digital Ocean CLI (doctl) found"
} catch {
    Write-Error-Custom "doctl is not installed"
    Write-Host "Download from: https://github.com/digitalocean/doctl/releases"
    exit 1
}

# Check doctl authentication
try {
    $authCheck = doctl auth list 2>&1
    if ($authCheck -match "access-token") {
        Write-Success "Digital Ocean authenticated"
    } else {
        Write-Error-Custom "Digital Ocean CLI not authenticated"
        Write-Host "Run: doctl auth init"
        exit 1
    }
} catch {
    Write-Error-Custom "Could not verify Digital Ocean authentication"
    exit 1
}

# Check app.yaml
if (!(Test-Path "app.yaml")) {
    Write-Error-Custom "app.yaml not found in current directory"
    exit 1
}
Write-Success "app.yaml found"

# Check Dockerfile
if (!(Test-Path "Dockerfile")) {
    Write-Error-Custom "Dockerfile not found in current directory"
    exit 1
}
Write-Success "Dockerfile found"

Write-Success "All pre-flight checks passed"

# STEP 1: Build Docker Image
if (-not $SkipDockerBuild) {
    Write-Section "STEP 1: BUILD DOCKER IMAGE"
    
    Write-Host "Building Docker image: $ImageName"
    docker build -t $ImageName`:latest .
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker image built successfully"
    } else {
        Write-Error-Custom "Docker build failed"
        exit 1
    }
} else {
    Write-Section "STEP 1: BUILD DOCKER IMAGE (SKIPPED)"
}

# STEP 2: Push to Digital Ocean Registry
if (-not $SkipPush) {
    Write-Section "STEP 2: PUSH TO DIGITAL OCEAN REGISTRY"
    
    # Get registry namespace
    try {
        $Namespace = doctl account get --format namespace --no-header
        $RegistryUrl = "registry.digitalocean.com/$Namespace"
        Write-Success "Registry URL: $RegistryUrl"
    } catch {
        Write-Error-Custom "Could not get registry information"
        exit 1
    }
    
    # Tag image
    $FullImageName = "$RegistryUrl/$AppName`:latest"
    Write-Host "Tagging image: $FullImageName"
    docker tag $ImageName`:latest $FullImageName
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Docker tag failed"
        exit 1
    }
    Write-Success "Image tagged"
    
    # Login to registry
    Write-Host "Logging into Digital Ocean registry..."
    $Token = doctl auth-token
    Write-Output $Token | docker login -u unused --password-stdin registry.digitalocean.com
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Docker login failed"
        exit 1
    }
    Write-Success "Logged into Digital Ocean registry"
    
    # Push image
    Write-Host "Pushing image to registry..."
    docker push $FullImageName
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Image pushed successfully"
    } else {
        Write-Error-Custom "Docker push failed"
        exit 1
    }
} else {
    Write-Section "STEP 2: PUSH TO DIGITAL OCEAN REGISTRY (SKIPPED)"
}

# STEP 3: Create/Update Digital Ocean App
Write-Section "STEP 3: CREATE/UPDATE DIGITAL OCEAN APP"

try {
    $AppExists = doctl apps list --format name --no-header | Select-String -Pattern $AppName -Quiet
    
    if ($AppExists) {
        Write-Success "App exists: $AppName"
    } else {
        Write-Host "Creating new app from app.yaml..."
        doctl apps create --spec app.yaml
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "App created successfully"
        } else {
            Write-Error-Custom "App creation failed"
            exit 1
        }
    }
} catch {
    Write-Error-Custom "Could not check app status"
    exit 1
}

# STEP 4: Deploy Application
Write-Section "STEP 4: DEPLOY APPLICATION"

try {
    $AppId = doctl apps list --format id,name --no-header | Select-String -Pattern $AppName | ForEach-Object { $_.Split()[0] }
    
    if ([string]::IsNullOrEmpty($AppId)) {
        Write-Error-Custom "Could not find app ID for $AppName"
        exit 1
    }
    
    Write-Success "App ID: $AppId"
    
    Write-Host "Creating deployment..."
    doctl apps create-deployment $AppId
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Deployment creation failed"
        exit 1
    }
    
    Write-Success "Deployment created, waiting for completion..."
    
    # Wait for deployment
    $WaitTime = 0
    $MaxWait = 600  # 10 minutes
    
    while ($WaitTime -lt $MaxWait) {
        Start-Sleep -Seconds 10
        $WaitTime += 10
        
        try {
            $Status = doctl apps get $AppId --format status --no-header
            
            if ($Status -eq "ACTIVE") {
                Write-Success "Deployment completed successfully!"
                break
            }
            
            if ($WaitTime % 60 -eq 0) {
                Write-Host "Still deploying... (${WaitTime}s elapsed)" -ForegroundColor Cyan
            }
        } catch {
            # Continue waiting
        }
    }
    
    if ($Status -ne "ACTIVE") {
        Write-Error-Custom "Deployment failed or timed out"
        exit 1
    }
} catch {
    Write-Error-Custom "Deployment step failed: $_"
    exit 1
}

# STEP 5: Get App URL
Write-Section "STEP 5: GET APP DETAILS"

try {
    $AppUrl = doctl apps get $AppId --format live-url --no-header
    Write-Success "App URL: $AppUrl"
} catch {
    Write-Error-Custom "Could not get app URL"
    exit 1
}

# STEP 6: Verify Deployment
Write-Section "STEP 6: VERIFY DEPLOYMENT"

Write-Host "Testing health endpoint..."
try {
    $Response = Invoke-WebRequest -Uri "$AppUrl/health" -ErrorAction SilentlyContinue
    if ($Response.StatusCode -eq 200) {
        Write-Success "Health check passed (HTTP 200)"
    } else {
        Write-Warning-Custom "Health check returned HTTP $($Response.StatusCode)"
    }
} catch {
    Write-Warning-Custom "Health endpoint not accessible"
}

# STEP 7: Configuration Instructions
Write-Section "STEP 7: ENVIRONMENT VARIABLES"

Write-Warning-Custom "Please configure the following environment variables in Digital Ocean:"
Write-Host ""
Write-Host "1. Go to Digital Ocean Dashboard → Apps → $AppName → Settings"
Write-Host "2. Click 'Edit and Deploy'"
Write-Host "3. Add these environment variables:"
Write-Host ""
Write-Host "   DATABASE_URL=<your-database-url>"
Write-Host "   API_SECRET_KEY=<strong-random-key>"
Write-Host "   ENVIRONMENT=production"
Write-Host "   DEBUG=false"
Write-Host "   STRIPE_API_KEY=sk_live_<your-key>"
Write-Host "   STRIPE_WEBHOOK_SECRET=whsec_<your-secret>"
Write-Host ""
Write-Host "4. Click 'Deploy'"
Write-Host ""

# STEP 8: Stripe Webhook Setup
Write-Section "STEP 8: STRIPE WEBHOOK SETUP"

$WebhookUrl = "$AppUrl/webhooks/stripe"
Write-Host "Configure this webhook URL in Stripe Dashboard:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   $WebhookUrl"
Write-Host ""
Write-Host "Webhook events to enable:" -ForegroundColor Cyan
Write-Host "   • charge.succeeded"
Write-Host "   • charge.failed"
Write-Host "   • customer.subscription.updated"
Write-Host "   • customer.subscription.deleted"
Write-Host ""

# STEP 9: Summary
Write-Section "🎉 DEPLOYMENT COMPLETE!"

Write-Host ""
Write-Host "Application Details:" -ForegroundColor Cyan
Write-Host "  Name: $AppName"
Write-Host "  ID: $AppId"
Write-Host "  URL: $AppUrl"
Write-Host "  Region: $Region"
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Set environment variables in Digital Ocean console"
Write-Host "  2. Configure Stripe webhooks (URL above)"
Write-Host "  3. Run database migrations (if needed)"
Write-Host "  4. Test payment flow"
Write-Host "  5. Monitor application logs"
Write-Host ""
Write-Host "Useful Commands:" -ForegroundColor Cyan
Write-Host "  View Logs:"
Write-Host "    doctl apps logs $AppId --follow"
Write-Host ""
Write-Host "  View App Details:"
Write-Host "    doctl apps get $AppId"
Write-Host ""

Write-Success "Deployment script completed successfully!"
Write-Success "Your app is now live at: $AppUrl"

Write-Host ""
Write-Host "=====================================" -ForegroundColor Blue
Write-Host "🚀 PHASE 7: DEPLOYMENT COMPLETE" -ForegroundColor Blue
Write-Host "=====================================" -ForegroundColor Blue
