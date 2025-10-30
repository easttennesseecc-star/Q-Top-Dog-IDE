@echo off
REM ============================================================================
REM Q-IDE TOPDOG - PROFESSIONAL SINGLE LAUNCHER
REM
REM This is the official single-click launcher for Q-IDE
REM Double-click this file to start Q-IDE - it's that simple!
REM
REM Works like any professional desktop application (Discord, VS Code, etc.)
REM ============================================================================

setlocal enabledelayedexpansion

color 0B
title Q-IDE Topdog - Launching...

for %%A in ("%~dp0.") do set "ROOT_DIR=%%~fA"

cls

echo.
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                            ║
echo ║                         🚀 Q-IDE TOPDOG                                    ║
echo ║                                                                            ║
echo ║                    Professional AI Development IDE                         ║
echo ║                                                                            ║
echo ║                          Starting up...                                    ║
echo ║                                                                            ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.

REM ============================================================================
REM STEP 1: Stop any existing processes
REM ============================================================================
echo [*] Preparing systems...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM python3.11.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM ============================================================================
REM STEP 2: Verify setup
REM ============================================================================
echo [*] Checking directories...
if not exist "!ROOT_DIR!\backend" (
    color 0C
    echo.
    echo ✗ ERROR: Backend directory not found!
    echo.
    pause
    exit /b 1
)
if not exist "!ROOT_DIR!\frontend" (
    color 0C
    echo.
    echo ✗ ERROR: Frontend directory not found!
    echo.
    pause
    exit /b 1
)
echo [✓] Setup verified

REM ============================================================================
REM STEP 3: Start services
REM ============================================================================
echo.
echo [*] Starting backend server on port 8000...
cd /d "!ROOT_DIR!\backend"
start "Q-IDE Backend" cmd /k "python main.py"
timeout /t 5 /nobreak >nul

echo [*] Starting frontend server on port 1431...
cd /d "!ROOT_DIR!\frontend"
start "Q-IDE Frontend" cmd /k "pnpm run dev"
timeout /t 6 /nobreak >nul

REM ============================================================================
REM STEP 4: Launch application
REM ============================================================================
echo [*] Opening Q-IDE in browser...
timeout /t 2 /nobreak >nul
start http://127.0.0.1:1431

echo.
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                            ║
echo ║                    ✓ Q-IDE TOPDOG LAUNCHED SUCCESSFULLY!                  ║
echo ║                                                                            ║
echo ║                  Application Opening in Your Browser                       ║
echo ║                                                                            ║
echo ║  Website:  http://127.0.0.1:1431                                          ║
echo ║  Backend:  http://127.0.0.1:8000                                          ║
echo ║  API Docs: http://127.0.0.1:8000/docs                                     ║
echo ║                                                                            ║
echo ║  Server windows are running in the background.                            ║
echo ║  Keep them open while using Q-IDE.                                        ║
echo ║                                                                            ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.

timeout /t 8 /nobreak >nul

exit /b 0
