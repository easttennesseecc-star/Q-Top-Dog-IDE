# Q-IDE Windows Build Script
# Builds a production MSI installer for Windows standalone deployment

param(
    [switch]$Release = $false,
    [switch]$Clean = $false
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  Q-IDE Windows Production Build" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow
$checks = @(
    @{ Name = "Node.js"; Command = "node --version" },
    @{ Name = "pnpm"; Command = "pnpm --version" },
    @{ Name = "Rust"; Command = "rustc --version" },
    @{ Name = "Cargo"; Command = "cargo --version" }
)

foreach ($check in $checks) {
    try {
        $output = & cmd /c $check.Command 2>&1
        Write-Host "  ✅ $($check.Name): $output" -ForegroundColor Green
    }
    catch {
        Write-Host "  ❌ $($check.Name) not found!" -ForegroundColor Red
        Write-Host "     Please install from: https://nodejs.org, https://pnpm.io, https://rustup.rs" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""

# Clean if requested
if ($Clean) {
    Write-Host "🧹 Cleaning previous builds..." -ForegroundColor Yellow
    Push-Location $ScriptDir
    if (Test-Path "frontend/dist") {
        Remove-Item -Recurse -Force "frontend/dist" -ErrorAction SilentlyContinue
    }
    if (Test-Path "frontend/src-tauri/target") {
        Remove-Item -Recurse -Force "frontend/src-tauri/target" -ErrorAction SilentlyContinue
    }
    Pop-Location
    Write-Host "  ✅ Clean complete" -ForegroundColor Green
    Write-Host ""
}

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
Push-Location $ScriptDir
pnpm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ pnpm install failed!" -ForegroundColor Red
    exit 1
}
Write-Host "  ✅ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Build frontend
Write-Host "🏗️  Building frontend..." -ForegroundColor Yellow
Push-Location "$ScriptDir/frontend"
pnpm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ Frontend build failed!" -ForegroundColor Red
    Pop-Location
    exit 1
}
Write-Host "  ✅ Frontend build complete" -ForegroundColor Green
Pop-Location
Write-Host ""

# Build Tauri application
Write-Host "📦 Building Tauri application..." -ForegroundColor Yellow
Push-Location "$ScriptDir/frontend"

$tauriCmd = "pnpm tauri build"
if ($Release) {
    $tauriCmd += " --release"
}

& cmd /c $tauriCmd
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ Tauri build failed!" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host "  ✅ Tauri build complete" -ForegroundColor Green
Pop-Location
Write-Host ""

# Find the MSI installer
$msiPath = Get-ChildItem -Path "$ScriptDir/frontend/src-tauri/target/release/bundle/msi" -Filter "*.msi" -ErrorAction SilentlyContinue | Select-Object -First 1

if ($msiPath) {
    Write-Host "✅ Build successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📍 Installer location:" -ForegroundColor Cyan
    Write-Host "   $($msiPath.FullName)" -ForegroundColor White
    Write-Host ""
    Write-Host "🚀 To install:" -ForegroundColor Yellow
    Write-Host "   1. Double-click the MSI file" -ForegroundColor White
    Write-Host "   2. Follow the installation wizard" -ForegroundColor White
    Write-Host "   3. Click 'Finish' and Q-IDE will launch automatically" -ForegroundColor White
    Write-Host ""
}
else {
    Write-Host "⚠️  MSI not found in expected location" -ForegroundColor Yellow
    Write-Host "   Checking alternative locations..." -ForegroundColor Yellow
    $altPath = Get-ChildItem -Path "$ScriptDir/frontend/src-tauri/target" -Recurse -Filter "*.msi" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($altPath) {
        Write-Host "   Found at: $($altPath.FullName)" -ForegroundColor White
    }
}
