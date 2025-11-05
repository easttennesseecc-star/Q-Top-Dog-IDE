#!/usr/bin/env powershell

# PHASE4_QUICK_START.ps1
# Q-IDE Phase 4 Stripe Integration Quick Start
# Run this to get started immediately

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║           Q-IDE PHASE 4: STRIPE INTEGRATION QUICK START           ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Colors
$green = "Green"
$yellow = "Yellow"
$cyan = "Cyan"
$red = "Red"

# Step 1: Check prerequisites
Write-Host "STEP 1: Checking Prerequisites..." -ForegroundColor $cyan
Write-Host "────────────────────────────────" -ForegroundColor $cyan
Write-Host ""

# Check Node.js
Write-Host "  ✓ Checking Node.js..." -NoNewline
if (Get-Command npm -ErrorAction SilentlyContinue) {
    $nodeVersion = node --version
    Write-Host " OK ($nodeVersion)" -ForegroundColor $green
} else {
    Write-Host " MISSING - Install from https://nodejs.org" -ForegroundColor $red
    exit 1
}

# Check Python
Write-Host "  ✓ Checking Python..." -NoNewline
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = python --version
    Write-Host " OK ($pythonVersion)" -ForegroundColor $green
} else {
    Write-Host " MISSING - Install from https://python.org" -ForegroundColor $red
    exit 1
}

# Check Git
Write-Host "  ✓ Checking Git..." -NoNewline
if (Get-Command git -ErrorAction SilentlyContinue) {
    Write-Host " OK" -ForegroundColor $green
} else {
    Write-Host " MISSING - Install from https://git-scm.com" -ForegroundColor $red
}

Write-Host ""

# Step 2: Install frontend dependencies
Write-Host "STEP 2: Installing Frontend Dependencies..." -ForegroundColor $cyan
Write-Host "──────────────────────────────────────────" -ForegroundColor $cyan
Write-Host ""

Push-Location frontend

Write-Host "  Installing packages..." -ForegroundColor $yellow
npm install --save `
  @stripe/react-stripe-js `
  @stripe/js `
  axios `
  react-router-dom

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Frontend dependencies installed" -ForegroundColor $green
} else {
    Write-Host "  ✗ Failed to install dependencies" -ForegroundColor $red
    exit 1
}

Pop-Location

Write-Host ""

# Step 3: Setup environment
Write-Host "STEP 3: Configuring Environment..." -ForegroundColor $cyan
Write-Host "─────────────────────────────────" -ForegroundColor $cyan
Write-Host ""

$envFile = "backend\.env"

if (Test-Path $envFile) {
    Write-Host "  ✓ .env file already exists" -ForegroundColor $green
} else {
    Write-Host "  Creating .env file..." -ForegroundColor $yellow
    
    @"
# Stripe Test Keys (get from https://dashboard.stripe.com)
STRIPE_PUBLIC_KEY=pk_test_YOUR_KEY_HERE
STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET_HERE

# Pricing Tier IDs (from Stripe Products dashboard)
STRIPE_PRICE_ID_PRO=price_YOUR_ID_HERE
STRIPE_PRICE_ID_TEAMS=price_YOUR_ID_HERE
STRIPE_PRICE_ID_ENTERPRISE=price_YOUR_ID_HERE

# Frontend URL
FRONTEND_URL=http://localhost:5173

# Database
DATABASE_URL=sqlite:///./topdog_ide.db

# Environment
ENVIRONMENT=development
"@ | Out-File $envFile -Encoding UTF8

    Write-Host "  ✓ .env file created" -ForegroundColor $green
    Write-Host "  ⚠️  Edit backend/.env with your Stripe keys!" -ForegroundColor $yellow
}

Write-Host ""

# Step 4: Run verification
Write-Host "STEP 4: Running Verification..." -ForegroundColor $cyan
Write-Host "───────────────────────────────" -ForegroundColor $cyan
Write-Host ""

python PHASE4_VERIFICATION.py
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "⚠️  Some verification checks failed. See above for details." -ForegroundColor $yellow
}

Write-Host ""

# Summary
Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor $cyan
Write-Host "║                          NEXT STEPS                               ║" -ForegroundColor $cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor $cyan
Write-Host ""

Write-Host "1. GET STRIPE KEYS" -ForegroundColor $yellow
Write-Host "   • Go to: https://dashboard.stripe.com/register" -ForegroundColor $cyan
Write-Host "   • Create test account" -ForegroundColor $cyan
Write-Host "   • Copy public, secret, and webhook secret keys" -ForegroundColor $cyan
Write-Host "   • Paste into backend/.env" -ForegroundColor $cyan
Write-Host ""

Write-Host "2. CREATE STRIPE PRODUCTS" -ForegroundColor $yellow
Write-Host "   • Login to Stripe dashboard" -ForegroundColor $cyan
Write-Host "   • Products → Add Product" -ForegroundColor $cyan
Write-Host "   • Create 10 products (one per tier)" -ForegroundColor $cyan
Write-Host "   • Set monthly pricing" -ForegroundColor $cyan
Write-Host "   • Copy Price IDs to .env" -ForegroundColor $cyan
Write-Host ""

Write-Host "3. CONFIGURE WEBHOOK" -ForegroundColor $yellow
Write-Host "   • Settings → Webhooks → Add Endpoint" -ForegroundColor $cyan
Write-Host "   • URL: http://localhost:8000/api/billing/webhook" -ForegroundColor $cyan
Write-Host "   • Events: customer.subscription.*, invoice.payment.*" -ForegroundColor $cyan
Write-Host "   • Copy webhook secret to .env" -ForegroundColor $cyan
Write-Host ""

Write-Host "4. START SERVERS" -ForegroundColor $yellow
Write-Host "   Backend (Terminal 1):" -ForegroundColor $cyan
Write-Host "   $ cd backend" -ForegroundColor $white
Write-Host "   $ uvicorn main:app --reload" -ForegroundColor $white
Write-Host ""
Write-Host "   Frontend (Terminal 2):" -ForegroundColor $cyan
Write-Host "   $ cd frontend" -ForegroundColor $white
Write-Host "   $ npm run dev" -ForegroundColor $white
Write-Host ""

Write-Host "5. RUN TESTS" -ForegroundColor $yellow
Write-Host "   Follow: PHASE4_TESTING_GUIDE.md" -ForegroundColor $cyan
Write-Host "   13 test scenarios to verify everything works" -ForegroundColor $cyan
Write-Host ""

Write-Host "6. DEPLOY" -ForegroundColor $yellow
Write-Host "   When all tests pass, deploy to production!" -ForegroundColor $cyan
Write-Host ""

Write-Host "════════════════════════════════════════════════════════════════════" -ForegroundColor $cyan
Write-Host ""
Write-Host "Documentation:" -ForegroundColor $yellow
Write-Host "  • PHASE4_STRIPE_INTEGRATION_GUIDE.md - Full implementation guide" -ForegroundColor $cyan
Write-Host "  • PHASE4_TESTING_GUIDE.md - Testing procedures" -ForegroundColor $cyan
Write-Host "  • PHASE4_COMPLETE_IMPLEMENTATION.md - Quick start" -ForegroundColor $cyan
Write-Host "  • SECURITY_INFRASTRUCTURE_HARDENING.md - Security details" -ForegroundColor $cyan
Write-Host ""

Write-Host "Ready? Let's build a $300K+/month payment engine! 🚀" -ForegroundColor $green
Write-Host ""
