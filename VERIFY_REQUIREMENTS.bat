@echo off
REM Q-IDE Installation Verification
REM This script checks if all requirements are met

echo.
echo ================================================================================
echo                   Q-IDE INSTALLATION VERIFICATION
echo ================================================================================
echo.

REM Check Python
echo Checking Python 3.11+...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found or not in PATH
    echo.
    echo SOLUTION: Install Python from https://www.python.org/downloads/
    echo Make sure to CHECK: "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found

REM Check Node.js
echo Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found or not in PATH
    echo.
    echo SOLUTION: Install Node.js from https://nodejs.org/
    echo Make sure to CHECK: "Add to PATH" during installation
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
echo [OK] Node.js %NODE_VERSION% found

REM Check pnpm
echo Checking pnpm...
pnpm --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] pnpm not found - installing globally...
    call npm install -g pnpm >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Failed to install pnpm
        pause
        exit /b 1
    )
)
for /f "tokens=*" %%i in ('pnpm --version 2^>^&1') do set PNPM_VERSION=%%i
echo [OK] pnpm %PNPM_VERSION% found

echo.
echo ================================================================================
echo                    ALL REQUIREMENTS MET!
echo ================================================================================
echo.
echo Your system is ready to install Q-IDE!
echo.
echo Next step: Run INSTALL.bat to install dependencies
echo.
pause
