#!/usr/bin/env pwsh
# Docker Build Script for Q-IDE - Windows PowerShell
# Simple, robust version for Kubernetes deployment

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('build', 'push', 'test', 'cleanup', 'all', 'help')]
    [string]$Action = 'build',
    
    [Parameter(Mandatory=$false)]
    [string]$Registry = 'your-registry',

    [Parameter(Mandatory=$false)]
    [string]$Version = 'v1.0.0'
)

$frontendImage = "q-ide-frontend"
$backendImage = "q-ide-backend"
$frontendTag = "$frontendImage`:$Version"
$backendTag = "$backendImage`:$Version"

$ErrorActionPreference = 'Stop'

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-InfoMsg {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host ("=" * 70) -ForegroundColor Cyan
}

function Check-Prerequisites {
    Write-Header "Checking Prerequisites"
    
    try {
        $dockerVersion = docker --version
        Write-Success "Docker: $dockerVersion"
    }
    catch {
        Write-ErrorMsg "Docker not found!"
        exit 1
    }

    try {
        docker ps | Out-Null
        Write-Success "Docker daemon running"
    }
    catch {
        Write-ErrorMsg "Docker daemon not running!"
        exit 1
    }
}

function Build-Frontend {
    Write-Header "Building Frontend Image"
    Write-InfoMsg "Image: $frontendTag"
    
    if (-not (Test-Path "frontend\Dockerfile")) {
        Write-ErrorMsg "frontend/Dockerfile not found!"
        exit 1
    }

    $startTime = Get-Date
    Push-Location frontend
    
    try {
        docker build -t "$frontendTag" .
        Pop-Location
        $duration = (Get-Date) - $startTime
        Write-Success "Frontend built in $($duration.TotalSeconds)s"
    }
    catch {
        Pop-Location
        Write-ErrorMsg "Frontend build failed!"
        exit 1
    }
}

function Build-Backend {
    Write-Header "Building Backend Image"
    Write-InfoMsg "Image: $backendTag"
    
    if (-not (Test-Path "backend\Dockerfile")) {
        Write-ErrorMsg "backend/Dockerfile not found!"
        exit 1
    }

    $startTime = Get-Date
    Push-Location backend
    
    try {
        docker build -t "$backendTag" .
        Pop-Location
        $duration = (Get-Date) - $startTime
        Write-Success "Backend built in $($duration.TotalSeconds)s"
    }
    catch {
        Pop-Location
        Write-ErrorMsg "Backend build failed!"
        exit 1
    }
}

function Verify-Images {
    Write-Header "Verifying Images"
    
    $fe = docker images $frontendImage --format "{{.Size}}"
    $be = docker images $backendImage --format "{{.Size}}"
    
    Write-InfoMsg "Frontend: $fe"
    Write-InfoMsg "Backend: $be"
    
    Write-Success "Both images ready!"
}

function Push-Images {
    Write-Header "Pushing to Registry"
    
    if ($Registry -eq "your-registry") {
        Write-ErrorMsg "Registry not set! Example:"
        Write-InfoMsg "  .\docker-build-simple.ps1 -Action push -Registry docker.io/myuser"
        exit 1
    }

    $registryFrontend = "$Registry/$frontendImage`:$Version"
    $registryBackend = "$Registry/$backendImage`:$Version"
    
    try {
        Write-InfoMsg "Tagging frontend: $registryFrontend"
        docker tag "$frontendTag" "$registryFrontend"
        
        Write-InfoMsg "Pushing frontend..."
        docker push "$registryFrontend"
        Write-Success "Frontend pushed!"
        
        Write-InfoMsg "Tagging backend: $registryBackend"
        docker tag "$backendTag" "$registryBackend"
        
        Write-InfoMsg "Pushing backend..."
        docker push "$registryBackend"
        Write-Success "Backend pushed!"
    }
    catch {
        Write-ErrorMsg "Push failed!"
        exit 1
    }
}

function Cleanup-Images {
    Write-Header "Cleaning Up"
    docker image prune -f
    Write-Success "Cleanup complete"
}

function Show-Help {
    Write-Host ""
    Write-Host "Q-IDE Docker Build Script" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "USAGE: .\docker-build-simple.ps1 -Action [action]"
    Write-Host ""
    Write-Host "ACTIONS:"
    Write-Host "  build    - Build Docker images locally (default)"
    Write-Host "  push     - Push to registry (requires -Registry)"
    Write-Host "  cleanup  - Remove dangling images"
    Write-Host "  all      - Build and show summary"
    Write-Host "  help     - Show this help"
    Write-Host ""
    Write-Host "EXAMPLES:"
    Write-Host "  .\docker-build-simple.ps1"
    Write-Host "  .\docker-build-simple.ps1 -Action push -Registry docker.io/myuser"
    Write-Host ""
}

# Main
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Q-IDE Docker Build (Windows PowerShell)         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

try {
    switch ($Action) {
        'build' {
            Check-Prerequisites
            Build-Frontend
            Build-Backend
            Verify-Images
            Write-Host ""
            Write-Success "BUILD COMPLETE!"
        }
        'push' {
            Check-Prerequisites
            Push-Images
            Write-Success "PUSH COMPLETE!"
        }
        'cleanup' {
            Cleanup-Images
        }
        'all' {
            Check-Prerequisites
            Build-Frontend
            Build-Backend
            Verify-Images
            Cleanup-Images
            Write-Host ""
            Write-Success "READY FOR KUBERNETES DEPLOYMENT!"
        }
        'help' {
            Show-Help
        }
        default {
            Show-Help
        }
    }
}
catch {
    Write-ErrorMsg "Error occurred during build"
    Write-Host $_
    exit 1
}
