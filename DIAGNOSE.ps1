#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Q-IDE Diagnostics & Troubleshooting Tool

.DESCRIPTION
    Runs comprehensive diagnostics on Q-IDE installation and identifies issues

.EXAMPLE
    .\DIAGNOSE.ps1
    # Runs full diagnostic suite
#>

$Colors = @{
    'Success' = 'Green'
    'Error'   = 'Red'
    'Warning' = 'Yellow'
    'Info'    = 'Cyan'
    'Debug'   = 'Gray'
}

function Write-Status {
    param([string]$Message, [string]$Status = 'Checking')
    Write-Host "  $Status : $Message" -ForegroundColor $Colors[$Status]
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
}

function Test-Requirement {
    param([string]$Name, [scriptblock]$Test)
    
    Write-Host "  • Checking $Name..." -NoNewline
    
    try {
        $result = & $Test
        if ($result) {
            Write-Host " ✓" -ForegroundColor Green
            return $true
        } else {
            Write-Host " ✗" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host " ✗" -ForegroundColor Red
        return $false
    }
}

# Start diagnostics
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          Q-IDE Diagnostics & Troubleshooting Tool          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$issues = @()

# 1. System Requirements
Write-Section "SYSTEM REQUIREMENTS"

# Python
if (Test-Requirement "Python 3.9+" { python --version 2>$null }) {
    $version = python --version 2>&1
    Write-Status $version "Success"
} else {
    Write-Status "Python not found (required)" "Error"
    $issues += "Python 3.9+ is required but not installed"
}

# Node.js
if (Test-Requirement "Node.js" { node --version 2>$null }) {
    $version = node --version 2>&1
    Write-Status $version "Success"
} else {
    Write-Status "Node.js not found (required)" "Error"
    $issues += "Node.js is required but not installed"
}

# pnpm
if (Test-Requirement "pnpm" { pnpm --version 2>$null }) {
    $version = pnpm --version 2>&1
    Write-Status $version "Success"
} else {
    Write-Status "pnpm not found (required)" "Error"
    $issues += "pnpm is required but not installed. Run: npm install -g pnpm"
}

# 2. Project Structure
Write-Section "PROJECT STRUCTURE"

$dirs = @(
    'backend',
    'frontend',
    'backend/logs',
    'backend/data'
)

foreach ($dir in $dirs) {
    if (Test-Path $dir) {
        Write-Status "$dir" "Success"
    } else {
        Write-Status "$dir not found" "Error"
        $issues += "Missing directory: $dir"
    }
}

# 3. Key Files
Write-Section "KEY FILES"

$files = @(
    'backend/main.py',
    'backend/requirements.txt',
    'frontend/package.json',
    'frontend/vite.config.ts'
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Status $file "Success"
    } else {
        Write-Status "$file not found" "Error"
        $issues += "Missing file: $file"
    }
}

# 4. Python Dependencies
Write-Section "PYTHON DEPENDENCIES"

if (Test-Path 'backend/requirements.txt') {
    $deps = @('fastapi', 'uvicorn', 'sqlalchemy', 'pydantic')
    
    foreach ($dep in $deps) {
        try {
            $depName = $dep.Replace('-', '_')
            $version = python -c "import $depName; print('$dep installed')" 2>&1
            if ($version -like '*installed*') {
                Write-Status "$dep" "Success"
            } else {
                Write-Status "$dep not installed" "Warning"
                $issues += "Python package $dep not installed. Run: pip install -r backend/requirements.txt"
            }
        } catch {
            Write-Status "$dep not installed" "Warning"
            $issues += "Python package $dep not installed. Run: pip install -r backend/requirements.txt"
        }
    }
} else {
    Write-Status "requirements.txt not found" "Error"
    $issues += "backend/requirements.txt missing"
}

# 5. Node Modules
Write-Section "NODE MODULES"

if (Test-Path 'frontend/node_modules') {
    $count = (Get-ChildItem frontend/node_modules -Directory | Measure-Object).Count
    Write-Status "node_modules: $count packages installed" "Success"
} else {
    Write-Status "node_modules not installed" "Warning"
    $issues += "Frontend dependencies not installed. Run: cd frontend && pnpm install"
}

# 6. Port Availability
Write-Section "PORT AVAILABILITY"

$ports = @(
    @{ Port = 8000; Name = 'Backend API' },
    @{ Port = 1431; Name = 'Frontend Dev Server' },
    @{ Port = 11434; Name = 'Ollama (optional)' }
)

foreach ($portInfo in $ports) {
    $connection = Test-NetConnection -ComputerName 127.0.0.1 -Port $portInfo.Port -WarningAction SilentlyContinue
    if ($connection.TcpTestSucceeded) {
        $process = Get-NetTCPConnection -LocalPort $portInfo.Port -ErrorAction SilentlyContinue
        if ($process) {
            $proc = Get-Process -Id $process.OwningProcess -ErrorAction SilentlyContinue
            Write-Status "Port $($portInfo.Port) - $($portInfo.Name): IN USE (PID: $($proc.Id))" "Warning"
        }
    } else {
        Write-Status "Port $($portInfo.Port) - $($portInfo.Name): Available" "Success"
    }
}

# 7. Database
Write-Section "DATABASE"

$dbPath = 'backend/data/q_ide.db'
if (Test-Path $dbPath) {
    $size = (Get-Item $dbPath).Length / 1KB
    Write-Status "Database found ($([math]::Round($size, 2)) KB)" "Success"
    
    # Try to query tables
    try {
        $tables = sqlite3 $dbPath ".tables" 2>&1 | Measure-Object
        if ($tables.Count -gt 0) {
            Write-Status "Database has tables" "Success"
        } else {
            Write-Status "Database is empty (will be created on startup)" "Warning"
        }
    } catch {
        Write-Status "Could not read database (might be corrupted)" "Error"
        $issues += "Database at $dbPath might be corrupted. You can safely delete it and it will be recreated."
    }
} else {
    Write-Status "Database not found (will be created on startup)" "Info"
}

# 8. Environment Variables
Write-Section "ENVIRONMENT VARIABLES"

$envVars = @('OPENAI_API_KEY', 'GOOGLE_API_KEY', 'GITHUB_TOKEN')

foreach ($var in $envVars) {
    $value = [System.Environment]::GetEnvironmentVariable($var)
    if ($value) {
        $masked = $value.Substring(0, [Math]::Min(5, $value.Length)) + "***"
        Write-Status "$var : $masked" "Success"
    } else {
        Write-Status "$var : Not set" "Info"
    }
}

# 9. Git Status
Write-Section "GIT STATUS"

if (Test-Path '.git') {
    try {
        $branch = git rev-parse --abbrev-ref HEAD 2>&1
        $status = git status --short 2>&1
        $changes = ($status | Measure-Object).Count
        
        Write-Status "Branch: $branch" "Success"
        Write-Status "Uncommitted changes: $changes files" $(if ($changes -gt 0) { 'Warning' } else { 'Success' })
    } catch {
        Write-Status "Could not read git status" "Error"
    }
} else {
    Write-Status "Not a git repository" "Info"
}

# 10. Logs
Write-Section "LOGS"

$logDir = 'backend/logs'
if (Test-Path $logDir) {
    $logs = Get-ChildItem $logDir -File
    if ($logs.Count -gt 0) {
        Write-Status "Found $($logs.Count) log files" "Success"
        
        # Show latest errors
        $errors = Select-String "ERROR" ($logDir + '/*') -ErrorAction SilentlyContinue
        if ($errors.Count -gt 0) {
            Write-Status "Found $($errors.Count) ERROR messages in logs" "Warning"
            Write-Host ""
            Write-Host "Recent errors:" -ForegroundColor Yellow
            $errors | Select-Object -Last 3 | ForEach-Object {
                Write-Host "  $_" -ForegroundColor Gray
            }
        }
    } else {
        Write-Status "No log files found" "Info"
    }
} else {
    Write-Status "Logs directory not found" "Info"
}

# Summary
Write-Section "SUMMARY"

if ($issues.Count -eq 0) {
    Write-Host ""
    Write-Host "✅ All diagnostics passed! Your system is ready." -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Run:  .\START_DEBUG.ps1"
    Write-Host "  2. Or:   .\START.bat"
    Write-Host "  3. Or:   .\START_DEBUG.bat"
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "⚠️  Found $($issues.Count) issue(s) to resolve:" -ForegroundColor Yellow
    Write-Host ""
    
    for ($i = 0; $i -lt $issues.Count; $i++) {
        Write-Host "  $($i + 1). $($issues[$i])" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "How to fix:" -ForegroundColor Cyan
    Write-Host "  1. Install missing requirements (Python, Node.js, pnpm)"
    Write-Host "  2. Install dependencies:"
    Write-Host "     - Backend:  pip install -r backend/requirements.txt"
    Write-Host "     - Frontend: pnpm install"
    Write-Host "  3. Check ports are available (kill processes if needed)"
    Write-Host "  4. Run this diagnostic again"
    Write-Host ""
}

# Detailed Backend Check
Write-Section "DETAILED BACKEND CHECK"

Write-Host "  Testing Python import chain..." -ForegroundColor Cyan
try {
    $output = python -c @"
import sys
print(f"  Python: {sys.version}")
import fastapi
print(f"  ✓ fastapi: {fastapi.__version__}")
import sqlalchemy
print(f"  ✓ sqlalchemy: {sqlalchemy.__version__}")
import pydantic
print(f"  ✓ pydantic: {pydantic.__version__}")
print("  All backend dependencies OK")
"@ 2>&1
    Write-Host $output -ForegroundColor Green
} catch {
    Write-Host "  ✗ Backend dependency check failed" -ForegroundColor Red
    Write-Host "  Run: pip install -r backend/requirements.txt" -ForegroundColor Yellow
}

# Detailed Frontend Check
Write-Section "DETAILED FRONTEND CHECK"

Write-Host "  Checking frontend build system..." -ForegroundColor Cyan
try {
    Push-Location frontend
    $output = pnpm run build --dry-run 2>&1 | Select-Object -First 5
    Write-Host "  ✓ Frontend build system OK" -ForegroundColor Green
    Pop-Location
} catch {
    Write-Host "  ✗ Frontend build check failed" -ForegroundColor Red
    Write-Host "  Run: cd frontend && pnpm install" -ForegroundColor Yellow
}

# Disk Space
Write-Section "SYSTEM RESOURCES"

$drive = Get-Item -Path c:\
$freeSpace = $drive.AvailableFreeSpace / 1GB

Write-Status "Free disk space: $([math]::Round($freeSpace, 2)) GB" $(if ($freeSpace -gt 5) { 'Success' } else { 'Warning' })

# Recommendations
Write-Section "RECOMMENDATIONS"

Write-Host ""
Write-Host "Best practices for local testing:" -ForegroundColor Cyan
Write-Host "  1. Use START_DEBUG.ps1 for detailed debug output"
Write-Host "  2. Keep DevTools (F12) open while testing"
Write-Host "  3. Monitor backend/logs/app.log in real-time"
Write-Host "  4. Use Ctrl+C to gracefully stop services"
Write-Host "  5. Run tests: pnpm test (frontend), pytest -v (backend)"
Write-Host "  6. Check database: sqlite3 backend/data/q_ide.db '.schema'"
Write-Host "  7. Reset if needed: rm backend/data/q_ide.db (recreated on startup)"
Write-Host ""

Write-Host "For more help:" -ForegroundColor Cyan
Write-Host "  See: LOCAL_TESTING_AND_DEBUGGING.md"
Write-Host ""
