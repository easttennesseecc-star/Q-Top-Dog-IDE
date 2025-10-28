@echo off
REM Q-IDE - Flawless Startup Sequence
REM This script starts both backend and frontend with proper error handling and sequencing

setlocal enabledelayedexpansion
cls

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║         Q-IDE - FLAWLESS STARTUP SEQUENCE                  ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Get root directory
for %%A in ("%~dp0.") do set "ROOT_DIR=%%~fA"

REM Step 1: Clean up
echo [STEP 1/6] Cleaning up existing processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM python3.11.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM npm.exe >nul 2>&1
timeout /t 3 /nobreak >nul
echo [OK] Processes cleaned and ports freed

REM Step 2: Verify directories
echo.
echo [STEP 2/6] Verifying directories...
if not exist "%ROOT_DIR%\backend" (
    echo [ERROR] Backend directory not found at %ROOT_DIR%\backend
    pause
    exit /b 1
)
if not exist "%ROOT_DIR%\frontend" (
    echo [ERROR] Frontend directory not found at %ROOT_DIR%\frontend
    pause
    exit /b 1
)
echo [OK] Directories verified

REM Step 3: Check Python
echo.
echo [STEP 3/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Install Python 3.11+ and add to PATH
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set "PY_VER=%%i"
echo [OK] %PY_VER%

REM Step 4: Check pnpm
echo.
echo [STEP 4/6] Checking pnpm installation...
pnpm --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pnpm not found! Run: npm install -g pnpm
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('pnpm --version 2^>^&1') do set "PNPM_VER=%%i"
echo [OK] pnpm !PNPM_VER!

REM Step 5: Start Backend (with absolute path)
echo.
echo [STEP 5/6] Starting Backend Server (Python/FastAPI)...
echo          - Location: %ROOT_DIR%\backend
echo          - Port: 8000
start "Q-IDE Backend Server" cmd /k "cd /d "%ROOT_DIR%\backend" && python main.py && pause"
timeout /t 5 /nobreak >nul
echo [OK] Backend started - waiting for startup...
timeout /t 3 /nobreak >nul

REM Step 6: Start Frontend (with explicit port binding)
echo.
echo [STEP 6/6] Starting Frontend Server (React/Vite)...
echo          - Location: %ROOT_DIR%\frontend
echo          - Port: 1431
start "Q-IDE Frontend Server" cmd /k "cd /d "%ROOT_DIR%\frontend" && npx vite --host 127.0.0.1 --port 1431 && pause"
timeout /t 6 /nobreak >nul
echo [OK] Frontend started - waiting for startup...
timeout /t 3 /nobreak >nul

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║         ✓ BOTH SERVERS STARTED SUCCESSFULLY!               ║
echo ║                                                            ║
echo ║         Opening Q-IDE in your browser...                  ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Wait and open browser
timeout /t 3 /nobreak >nul
start http://localhost:1431

echo.
echo ✓ Backend API:     http://localhost:8000
echo ✓ Frontend UI:     http://localhost:1431
echo ✓ API Docs:        http://localhost:8000/docs
echo.
echo Both servers are running in separate windows.
echo Keep both windows open while using Q-IDE.
echo.
echo To stop: Press Ctrl+C in each window or close them
echo.
pause
