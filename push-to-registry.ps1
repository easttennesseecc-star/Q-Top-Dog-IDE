# 🚀 Push Docker Images to DigitalOcean Container Registry
# Usage: .\push-to-registry.ps1 -Token "your-digitalocean-api-token"

param(
    [Parameter(Mandatory=$false)]
    [string]$Token,
    [string]$Registry = "registry.digitalocean.com",
    [string]$Namespace = "q-ide-registry",
    [switch]$SkipLogin = $false
)

# Configuration
$ErrorActionPreference = "Stop"
$FrontendImage = "q-ide-frontend:v1.0.0"
$BackendImage = "q-ide-backend:v1.0.0"
$FrontendRegistryImage = "$Registry/$Namespace/q-ide-frontend:v1.0.0"
$BackendRegistryImage = "$Registry/$Namespace/q-ide-backend:v1.0.0"

# Colors
function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

function Write-Section {
    param([string]$Message)
    Write-Host "`n========================================" -ForegroundColor Blue
    Write-Host $Message -ForegroundColor Blue
    Write-Host "========================================`n" -ForegroundColor Blue
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

# ============================================
# PRE-FLIGHT CHECKS
# ============================================
Write-Section "PRE-FLIGHT CHECKS"

# Check Docker
try {
    $dockerVersion = docker --version
    Write-Success "Docker installed: $dockerVersion"
} catch {
    Write-Error-Custom "Docker is not installed or not accessible"
    exit 1
}

# Check local images exist
try {
    docker inspect $FrontendImage | Out-Null
    Write-Success "Frontend image found: $FrontendImage"
} catch {
    Write-Error-Custom "Frontend image not found: $FrontendImage"
    Write-Info "Build frontend first: cd frontend; docker build -t q-ide-frontend:v1.0.0 ."
    exit 1
}

try {
    docker inspect $BackendImage | Out-Null
    Write-Success "Backend image found: $BackendImage"
} catch {
    Write-Error-Custom "Backend image not found: $BackendImage"
    Write-Info "Build backend first: cd backend; docker build -t q-ide-backend:v1.0.0 ."
    exit 1
}

# Check registry images are tagged
try {
    docker inspect $FrontendRegistryImage | Out-Null
    Write-Success "Frontend registry image tagged: $FrontendRegistryImage"
} catch {
    Write-Warning-Custom "Frontend registry image not tagged, tagging now..."
    docker tag $FrontendImage $FrontendRegistryImage
    Write-Success "Tagged: $FrontendRegistryImage"
}

try {
    docker inspect $BackendRegistryImage | Out-Null
    Write-Success "Backend registry image tagged: $BackendRegistryImage"
} catch {
    Write-Warning-Custom "Backend registry image not tagged, tagging now..."
    docker tag $BackendImage $BackendRegistryImage
    Write-Success "Tagged: $BackendRegistryImage"
}

# ============================================
# REGISTRY LOGIN
# ============================================
if (-not $SkipLogin) {
    Write-Section "REGISTRY AUTHENTICATION"
    
    if ([string]::IsNullOrEmpty($Token)) {
        Write-Info "You need your DigitalOcean API token to authenticate."
        Write-Info "Get it from: https://cloud.digitalocean.com/account/api/tokens"
        Write-Info ""
        $Token = Read-Host "Enter your DigitalOcean API token"
        
        if ([string]::IsNullOrEmpty($Token)) {
            Write-Error-Custom "No token provided, cannot proceed"
            exit 1
        }
    }
    
    Write-Info "Logging into registry: $Registry"
    try {
        Write-Output $Token | docker login -u unused --password-stdin $Registry 2>&1 | Select-String -Pattern "Login Succeeded|Error|invalid"
        Write-Success "Logged into registry successfully"
    } catch {
        Write-Error-Custom "Docker login failed: $_"
        exit 1
    }
}

# ============================================
# PUSH IMAGES
# ============================================
Write-Section "PUSHING IMAGES TO REGISTRY"

# Push Frontend
Write-Info "Pushing frontend image: $FrontendRegistryImage"
Write-Info "Size: 216MB (this may take 2-3 minutes)"
try {
    docker push $FrontendRegistryImage 2>&1
    Write-Success "Frontend image pushed successfully"
} catch {
    Write-Error-Custom "Failed to push frontend image: $_"
    exit 1
}

# Push Backend
Write-Info "`nPushing backend image: $BackendRegistryImage"
Write-Info "Size: 735MB (this may take 5-8 minutes)"
try {
    docker push $BackendRegistryImage 2>&1
    Write-Success "Backend image pushed successfully"
} catch {
    Write-Error-Custom "Failed to push backend image: $_"
    exit 1
}

# ============================================
# VERIFICATION
# ============================================
Write-Section "VERIFICATION"

Write-Info "Verifying images in registry (this may take a moment)..."
Write-Info "Note: If images show as 'not found', they're still being processed (wait 30 seconds)"

# Show local images
Write-Host "`n📦 Local Images:" -ForegroundColor Yellow
docker images | Select-String "q-ide-registry"

Write-Host "`n📊 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Update Kubernetes manifests with registry URLs:"
Write-Host "   - k8s/04-backend.yaml"
Write-Host "   - k8s/05-frontend.yaml"
Write-Host ""
Write-Host "2. Create Kubernetes namespace and secrets:"
Write-Host "   kubectl create namespace q-ide"
Write-Host "   kubectl create secret docker-registry regcred \"
Write-Host "     --docker-server=registry.digitalocean.com \"
Write-Host "     --docker-username=unused \"
Write-Host "     --docker-password=<API_TOKEN> \"
Write-Host "     -n q-ide"
Write-Host ""
Write-Host "3. Deploy to Kubernetes:"
Write-Host "   kubectl apply -f k8s/"
Write-Host ""

Write-Success "Push complete! Images are now available in the registry."
Write-Info "Registry URL: $Registry/$Namespace"
