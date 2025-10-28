@echo off
REM Q-IDE ULTIMATE FLAWLESS LAUNCHER v2
REM Fixed paths and proper error handling

setlocal enabledelayedexpansion

cls
color 0A
title Q-IDE TOPDOG - LAUNCHING

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║                  Q-IDE TOPDOG - LAUNCHING                     ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Get the directory where this script is located
for %%A in ("%~dp0.") do set "ROOT_DIR=%%~fA"

echo [STEP 1/5] Cleaning up old servers...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM python3.11.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 3 /nobreak >nul
echo [OK] Old processes stopped

echo.
echo [STEP 2/5] Verifying directories exist...
if not exist "!ROOT_DIR!\backend" (
    echo [ERROR] Backend directory not found at: !ROOT_DIR!\backend
    pause
    exit /b 1
)
if not exist "!ROOT_DIR!\frontend" (
    echo [ERROR] Frontend directory not found at: !ROOT_DIR!\frontend
    pause
    exit /b 1
)
echo [OK] Directories verified

echo.
echo [STEP 3/5] Starting Backend Server...
echo     Location: !ROOT_DIR!\backend
echo     Command: python main.py
cd /d "!ROOT_DIR!\backend"
start "Q-IDE Backend" cmd /k "python main.py & pause"
timeout /t 5 /nobreak >nul
echo [OK] Backend started

echo.
echo [STEP 4/5] Starting Frontend Server...
echo     Location: !ROOT_DIR!\frontend
echo     Command: npx vite
cd /d "!ROOT_DIR!\frontend"
start "Q-IDE Frontend" cmd /k "npx vite --host 127.0.0.1 --port 1431 & pause"
timeout /t 7 /nobreak >nul
echo [OK] Frontend started

echo.
echo [STEP 5/5] Opening Q-IDE in browser...
timeout /t 3 /nobreak >nul
start http://127.0.0.1:1431

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║          ✓ Q-IDE STARTED SUCCESSFULLY!                        ║
echo ║                                                                ║
echo ║     Backend:  http://127.0.0.1:8000                          ║
echo ║     Frontend: http://127.0.0.1:1431                          ║
echo ║                                                                ║
echo ║  Your browser is opening now...                               ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

pause
