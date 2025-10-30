#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Q-IDE Debug Launcher - Start Q-IDE with full debugging capabilities

.DESCRIPTION
    Starts both backend and frontend with debug logging, opens browser, and streams logs

.PARAMETER Backend
    Start only backend

.PARAMETER Frontend
    Start only frontend

.PARAMETER Port
    Port for frontend (default: 1431)

.PARAMETER BackendPort
    Port for backend (default: 8000)

.EXAMPLE
    .\START_DEBUG.ps1
    # Starts both backend and frontend with debugging

.EXAMPLE
    .\START_DEBUG.ps1 -Backend
    # Starts only backend

.EXAMPLE
    .\START_DEBUG.ps1 -Frontend -Port 3000
    # Starts frontend on port 3000
#>

param(
    [switch]$Backend,
    [switch]$Frontend,
    [int]$Port = 1431,
    [int]$BackendPort = 8000
)

# Color codes for output
$Colors = @{
    'Success' = 'Green'
    'Error'   = 'Red'
    'Warning' = 'Yellow'
    'Info'    = 'Cyan'
}

function Write-ColorOutput {
    param([string]$Message, [string]$Color = 'White')
    Write-Host $Message -ForegroundColor $Color
}

function Test-Port {
    param([int]$Port)
    $connection = Test-NetConnection -ComputerName 127.0.0.1 -Port $Port -WarningAction SilentlyContinue
    return $connection.TcpTestSucceeded
}

function Kill-ProcessOnPort {
    param([int]$Port)
    $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($connection) {
        $process = Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue
        if ($process) {
            Write-ColorOutput "Killing process $($process.Name) (PID: $($process.Id)) on port $Port" $Colors['Warning']
            Stop-Process -Id $process.Id -Force
            Start-Sleep -Seconds 1
        }
    }
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       Q-IDE Local Testing & Debugging Launcher             ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "backend\main.py")) {
    Write-ColorOutput "❌ ERROR: backend\main.py not found" $Colors['Error']
    Write-ColorOutput "Please run this script from the Q-IDE root directory" $Colors['Error']
    exit 1
}

# Validate Python
Write-ColorOutput "[1/6] Checking Python installation..." $Colors['Info']
try {
    $pythonVersion = python --version 2>&1 | Select-Object -First 1
    Write-ColorOutput "✓ $pythonVersion" $Colors['Success']
} catch {
    Write-ColorOutput "❌ Python not found. Please install Python 3.9+" $Colors['Error']
    exit 1
}

# Validate pnpm
if ($Frontend -or -not $Backend) {
    Write-ColorOutput "[2/6] Checking pnpm installation..." $Colors['Info']
    try {
        $pnpmVersion = pnpm --version 2>&1
        Write-ColorOutput "✓ pnpm $pnpmVersion" $Colors['Success']
    } catch {
        Write-ColorOutput "❌ pnpm not found. Please install Node.js and pnpm" $Colors['Error']
        exit 1
    }
}

# Install dependencies
if ($Backend -or -not $Frontend) {
    Write-ColorOutput "[3/6] Installing/updating backend dependencies..." $Colors['Info']
    Push-Location backend
    python -m pip install -r requirements.txt -q
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "❌ Failed to install backend dependencies" $Colors['Error']
        Pop-Location
        exit 1
    }
    Pop-Location
    Write-ColorOutput "✓ Backend dependencies installed" $Colors['Success']
}

if ($Frontend -or -not $Backend) {
    Write-ColorOutput "[4/6] Installing/updating frontend dependencies..." $Colors['Info']
    Push-Location frontend
    pnpm install -q --no-optional 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "❌ Failed to install frontend dependencies" $Colors['Error']
        Pop-Location
        exit 1
    }
    Pop-Location
    Write-ColorOutput "✓ Frontend dependencies installed" $Colors['Success']
}

# Check for port conflicts
Write-ColorOutput "[5/6] Checking for port conflicts..." $Colors['Info']

if ($Backend -or -not $Frontend) {
    if (Test-Port $BackendPort) {
        Write-ColorOutput "⚠ Port $BackendPort is in use, attempting to free it..." $Colors['Warning']
        Kill-ProcessOnPort $BackendPort
    }
}

if ($Frontend -or -not $Backend) {
    if (Test-Port $Port) {
        Write-ColorOutput "⚠ Port $Port is in use, attempting to free it..." $Colors['Warning']
        Kill-ProcessOnPort $Port
    }
}

Write-ColorOutput "✓ Ports available" $Colors['Success']

# Start services
Write-ColorOutput "[6/6] Starting services..." $Colors['Info']
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "STARTING SERVICES:" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Start backend
if ($Backend -or -not $Frontend) {
    Write-ColorOutput "🔧 Backend: Starting on http://localhost:$BackendPort" $Colors['Info']
    
    $backendJob = Start-Job -ScriptBlock {
        param($BackendPort)
        Set-Location (Get-Item $using:PWD).FullName
        cd backend
        python main.py --log-level debug 2>&1
    } -ArgumentList $BackendPort
    
    Write-Host "   Waiting for backend to start..." -ForegroundColor Gray
    Start-Sleep -Seconds 2
    
    if ($backendJob.State -eq 'Running') {
        Write-ColorOutput "✓ Backend started (Job ID: $($backendJob.Id))" $Colors['Success']
    }
}

# Start frontend
if ($Frontend -or -not $Backend) {
    Write-ColorOutput "⚡ Frontend: Starting on http://localhost:$Port" $Colors['Info']
    
    $frontendJob = Start-Job -ScriptBlock {
        param($Port)
        Set-Location (Get-Item $using:PWD).FullName
        cd frontend
        $env:VITE_PORT = $Port
        pnpm run dev 2>&1
    } -ArgumentList $Port
    
    Write-Host "   Waiting for frontend to start..." -ForegroundColor Gray
    Start-Sleep -Seconds 3
    
    if ($frontendJob.State -eq 'Running') {
        Write-ColorOutput "✓ Frontend started (Job ID: $($frontendJob.Id))" $Colors['Success']
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan

# Open browser
if ($Frontend -or -not $Backend) {
    Write-Host ""
    Write-ColorOutput "🌐 Opening browser to http://localhost:$Port..." $Colors['Info']
    Start-Process "http://localhost:$Port"
    Start-Sleep -Seconds 1
}

# Display next steps
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ SERVICES RUNNING!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-ColorOutput "📍 ENDPOINTS:" $Colors['Info']
if ($Backend -or -not $Frontend) {
    Write-Host "   Backend:  http://localhost:$BackendPort"
    Write-Host "   Docs:     http://localhost:$BackendPort/docs"
}
if ($Frontend -or -not $Backend) {
    Write-Host "   Frontend: http://localhost:$Port"
}

Write-Host ""
Write-ColorOutput "📋 LOGS:" $Colors['Info']
Write-Host "   Backend:  backend\logs\app.log"
Write-Host "   Frontend: (shown in terminal below)"

Write-Host ""
Write-ColorOutput "🐛 DEBUGGING:" $Colors['Info']
Write-Host "   1. Press F12 in the browser for DevTools"
Write-Host "   2. Check backend logs with: Get-Content backend\logs\app.log -Wait"
Write-Host "   3. Check database with: sqlite3 backend\data\q_ide.db '.tables'"

Write-Host ""
Write-ColorOutput "⚙️  COMMANDS:" $Colors['Info']
Write-Host "   Stop all:     Ctrl+C"
Write-Host "   View logs:    Get-Content backend\logs\app.log -Tail 50 -Wait"
Write-Host "   Test backend: curl http://localhost:$BackendPort/health"

Write-Host ""
Write-ColorOutput "💡 TIPS:" $Colors['Info']
Write-Host "   - Use Ctrl+C to gracefully stop services"
Write-Host "   - Check browser console (F12) for frontend errors"
Write-Host "   - Backend debug output will show in terminal"
Write-Host "   - Database: backend\data\q_ide.db"

Write-Host ""
Write-ColorOutput "📚 For more help, see LOCAL_TESTING_AND_DEBUGGING.md" $Colors['Info']
Write-Host ""

# Stream logs if running both services
if (($Backend -or -not $Frontend) -and ($Frontend -or -not $Backend)) {
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "LIVE LOGS (Press Ctrl+C to stop)" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    
    # Stream backend logs
    if ($Backend -or -not $Frontend) {
        Get-Job | Where-Object {$_.State -eq 'Running'} | Receive-Job -AsStream
    }
}

# Keep window open
Write-Host ""
Write-ColorOutput "Press any key to stop all services..." $Colors['Warning']
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Cleanup
Write-Host ""
Write-ColorOutput "Stopping services..." $Colors['Info']
Get-Job | Stop-Job
Write-ColorOutput "✓ All services stopped" $Colors['Success']
