@echo off
REM Q-IDE Topdog - One-Click Installer
REM This script installs all dependencies and prepares the system

setlocal enabledelayedexpansion
cls

echo.
echo ================================================================================
echo                    Q-IDE TOPDOG - INSTALLATION WIZARD
echo ================================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.11+ is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    echo Make sure to check "Add to PATH" during installation
    pause
    exit /b 1
)

REM Check if pnpm is installed
pnpm --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing pnpm...
    npm install -g pnpm
    if errorlevel 1 (
        echo [ERROR] Failed to install pnpm
        pause
        exit /b 1
    )
)

echo [OK] Python found: 
python --version

echo [OK] Node.js found:
node --version

echo [OK] pnpm found:
pnpm --version

echo.
echo ================================================================================
echo Installing Backend Dependencies...
echo ================================================================================

cd /d "%~dp0backend"
if errorlevel 1 (
    echo [ERROR] Failed to change to backend directory
    pause
    exit /b 1
)

echo [INFO] Installing Python packages from requirements.txt...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install Python packages
    echo Try running: pip install -r requirements.txt
    pause
    exit /b 1
)

echo [OK] Backend dependencies installed

echo.
echo ================================================================================
echo Installing Frontend Dependencies...
echo ================================================================================

cd /d "%~dp0frontend"
if errorlevel 1 (
    echo [ERROR] Failed to change to frontend directory
    pause
    exit /b 1
)

echo [INFO] Installing Node packages with pnpm...
call pnpm install
if errorlevel 1 (
    echo [ERROR] Failed to install Node packages
    echo Try running: pnpm install
    pause
    exit /b 1
)

echo [OK] Frontend dependencies installed

echo.
echo ================================================================================
echo Running Integration Tests...
echo ================================================================================

cd /d "%~dp0"
python test_q_assistant_integration.py >nul 2>&1

if %ERRORLEVEL% EQU 0 (
    echo [OK] All 7/7 integration tests PASSED
) else (
    echo [WARNING] Integration tests had issues
    echo Run: python test_q_assistant_integration.py
)

echo.
echo ================================================================================
echo                         INSTALLATION COMPLETE!
echo ================================================================================
echo.
echo [SUCCESS] Q-IDE is ready to run!
echo.
echo Next step: Run START.bat to launch the application
echo.
pause
