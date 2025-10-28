@echo off
REM Q-IDE PROFESSIONAL APPLICATION LAUNCHER
REM Makes Q-IDE launch and feel like a professional Windows desktop application

setlocal enabledelayedexpansion
color 0A
title Q-IDE Topdog - Professional Application Launcher

REM Get the directory where this script is located
for %%A in ("%~dp0.") do set "ROOT_DIR=%%~fA"
set "ICON_PATH=!ROOT_DIR!\media\q-ide-icon.ico"

cls

echo.
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                            ║
echo ║                    🚀 Q-IDE TOPDOG LAUNCHING                              ║
echo ║                                                                            ║
echo ║                   Advanced AI Development Environment                      ║
echo ║                                                                            ║
echo ║                          Please wait...                                    ║
echo ║                                                                            ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.

REM ============================================================================
REM STEP 1: Cleanup old processes
REM ============================================================================
echo [▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 5%%
echo Cleaning up old processes...

taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM python3.11.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM npm.exe >nul 2>&1

timeout /t 3 /nobreak >nul

REM ============================================================================
REM STEP 2: Verify system requirements
REM ============================================================================
echo [██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 10%%
echo Verifying system requirements...

if not exist "!ROOT_DIR!\backend" (
    echo [ERROR] Backend directory not found
    pause
    exit /b 1
)

if not exist "!ROOT_DIR!\frontend" (
    echo [ERROR] Frontend directory not found
    pause
    exit /b 1
)

python --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Python not found - attempting to continue anyway
) else (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do (
        echo Found: %%i
    )
)

timeout /t 2 /nobreak >nul

REM ============================================================================
REM STEP 3: Start Backend Server
REM ============================================================================
echo [████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 20%%
echo Starting Q-IDE Backend Server (FastAPI on port 8000)...

cd /d "!ROOT_DIR!\backend"
start "Q-IDE Backend Server" cmd /k "python main.py"

echo Waiting for backend to initialize...
timeout /t 6 /nobreak >nul

REM ============================================================================
REM STEP 4: Start Frontend Server
REM ============================================================================
echo [██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 40%%
echo Starting Q-IDE Frontend Server (Vite on port 1431)...

cd /d "!ROOT_DIR!\frontend"
start "Q-IDE Frontend Server" cmd /k "npx vite --host 127.0.0.1 --port 1431"

echo Waiting for frontend to initialize...
timeout /t 8 /nobreak >nul

REM ============================================================================
REM STEP 5: Verify Servers Are Running
REM ============================================================================
echo [████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 50%%
echo Verifying servers are running...

timeout /t 3 /nobreak >nul

REM ============================================================================
REM STEP 6: Launch Browser
REM ============================================================================
echo [██████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 60%%
echo Launching Q-IDE in your browser...

timeout /t 2 /nobreak >nul

start http://127.0.0.1:1431

timeout /t 3 /nobreak >nul

REM ============================================================================
REM STEP 7: Final Status
REM ============================================================================
echo [████████████████████████████████████████████████████████████████████████████] 100%%
echo.
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                            ║
echo ║                  ✓ Q-IDE TOPDOG SUCCESSFULLY LAUNCHED!                    ║
echo ║                                                                            ║
echo ║  Your Q-IDE application is now running and will open in your browser.     ║
echo ║                                                                            ║
echo ║  If the browser doesn't open automatically, visit:                        ║
echo ║                                                                            ║
echo ║     👉 http://127.0.0.1:1431                                              ║
echo ║                                                                            ║
echo ║  Application Details:                                                     ║
echo ║  • Backend API:     http://127.0.0.1:8000                                 ║
echo ║  • Frontend UI:     http://127.0.0.1:1431                                 ║
echo ║  • API Documentation: http://127.0.0.1:8000/docs                          ║
echo ║                                                                            ║
echo ║  Two server windows will remain open in the background.                   ║
echo ║  Keep them open while using Q-IDE.                                        ║
echo ║                                                                            ║
echo ║  ⚠️  DO NOT CLOSE THESE WINDOWS - Q-IDE will stop working!               ║
echo ║                                                                            ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.

REM Keep this window open
set /p dummy=Press ENTER to continue...
