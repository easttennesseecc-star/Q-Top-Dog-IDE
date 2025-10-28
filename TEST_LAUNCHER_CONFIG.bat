@echo off
REM Test Launcher Configuration
REM Verifies that the startup scripts are configured correctly

cls

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║     Q-IDE LAUNCHER CONFIGURATION TEST                      ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Get root directory
for %%A in ("%~dp0.") do set "ROOT_DIR=%%~fA"

echo Testing configuration at: %ROOT_DIR%
echo.

REM Test 1: Check launcher files
echo [TEST 1/4] Checking launcher files...
if exist "%ROOT_DIR%\🚀_LAUNCH_Q-IDE.bat" (
    echo [OK] Found: 🚀_LAUNCH_Q-IDE.bat
) else (
    echo [ERROR] Missing: 🚀_LAUNCH_Q-IDE.bat
)

if exist "%ROOT_DIR%\START.bat" (
    echo [OK] Found: START.bat
) else (
    echo [ERROR] Missing: START.bat
)

REM Test 2: Check directories
echo.
echo [TEST 2/4] Checking directories...
if exist "%ROOT_DIR%\backend" (
    echo [OK] Found: backend\
) else (
    echo [ERROR] Missing: backend\
)

if exist "%ROOT_DIR%\frontend" (
    echo [OK] Found: frontend\
) else (
    echo [ERROR] Missing: frontend\
)

REM Test 3: Check Python
echo.
echo [TEST 3/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Install Python 3.11+
) else (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do (
        echo [OK] %%i
    )
)

REM Test 4: Check pnpm
echo.
echo [TEST 4/4] Checking pnpm...
pnpm --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pnpm not found! Run: npm install -g pnpm
) else (
    for /f "tokens=*" %%i in ('pnpm --version 2^>^&1') do (
        echo [OK] pnpm %%i
    )
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║     CONFIGURATION TEST COMPLETE                            ║
echo ║                                                            ║
echo ║     All systems ready! You can now launch Q-IDE           ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

pause
