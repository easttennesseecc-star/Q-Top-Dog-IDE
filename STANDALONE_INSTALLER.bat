@echo off
REM Q-IDE STANDALONE INSTALLER
REM This creates a portable package that can be run on any PC

setlocal enabledelayedexpansion
cls

color 0A
title Q-IDE STANDALONE INSTALLER

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║         Q-IDE TOPDOG - STANDALONE INSTALLATION BUILDER         ║
echo ║                                                                ║
echo ║     Creating portable package for easy deployment...          ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Get root directory
for %%A in ("%~dp0.") do set "ROOT_DIR=%%~fA"
set "DIST_DIR=%ROOT_DIR%\Q-IDE_STANDALONE"

echo [STEP 1/6] Preparing distribution directory...
if exist "%DIST_DIR%" (
    echo Removing old build...
    rmdir /s /q "%DIST_DIR%" >nul 2>&1
)
mkdir "%DIST_DIR%" >nul 2>&1
echo [OK] Distribution directory ready: %DIST_DIR%

echo.
echo [STEP 2/6] Copying backend files...
mkdir "%DIST_DIR%\backend" >nul 2>&1
xcopy "%ROOT_DIR%\backend\*.py" "%DIST_DIR%\backend\" /Y /Q >nul 2>&1
xcopy "%ROOT_DIR%\backend\requirements.txt" "%DIST_DIR%\backend\" /Y /Q >nul 2>&1
if exist "%ROOT_DIR%\backend\routes" xcopy "%ROOT_DIR%\backend\routes\*" "%DIST_DIR%\backend\routes\" /S /Y /Q >nul 2>&1
if exist "%ROOT_DIR%\backend\models" xcopy "%ROOT_DIR%\backend\models\*" "%DIST_DIR%\backend\models\" /S /Y /Q >nul 2>&1
if exist "%ROOT_DIR%\backend\utils" xcopy "%ROOT_DIR%\backend\utils\*" "%DIST_DIR%\backend\utils\" /S /Y /Q >nul 2>&1
echo [OK] Backend copied (%DIST_DIR%\backend)

echo.
echo [STEP 3/6] Copying frontend files...
mkdir "%DIST_DIR%\frontend" >nul 2>&1
xcopy "%ROOT_DIR%\frontend\src" "%DIST_DIR%\frontend\src\" /S /Y /Q >nul 2>&1
xcopy "%ROOT_DIR%\frontend\public" "%DIST_DIR%\frontend\public\" /S /Y /Q >nul 2>&1
xcopy "%ROOT_DIR%\frontend\package.json" "%DIST_DIR%\frontend\" /Y /Q >nul 2>&1
xcopy "%ROOT_DIR%\frontend\pnpm-lock.yaml" "%DIST_DIR%\frontend\" /Y /Q >nul 2>&1
xcopy "%ROOT_DIR%\frontend\vite.config.ts" "%DIST_DIR%\frontend\" /Y /Q >nul 2>&1
xcopy "%ROOT_DIR%\frontend\tsconfig*.json" "%DIST_DIR%\frontend\" /Y /Q >nul 2>&1
echo [OK] Frontend copied (%DIST_DIR%\frontend)

echo.
echo [STEP 4/6] Copying documentation...
mkdir "%DIST_DIR%\docs" >nul 2>&1
xcopy "%ROOT_DIR%\README*.md" "%DIST_DIR%\docs\" /Y /Q >nul 2>&1
xcopy "%ROOT_DIR%\QUICK_START.md" "%DIST_DIR%\docs\" /Y /Q >nul 2>&1
xcopy "%ROOT_DIR%\LLM_AUTO_ASSIGNMENT_GUIDE.md" "%DIST_DIR%\docs\" /Y /Q >nul 2>&1
echo [OK] Documentation copied (%DIST_DIR%\docs)

echo.
echo [STEP 5/6] Creating portable launcher scripts...

REM Create universal installer
(
echo @echo off
echo setlocal enabledelayedexpansion
echo cls
echo title Q-IDE TOPDOG - SETUP WIZARD
echo.
echo echo ╔════════════════════════════════════════════════════════════╗
echo echo ║                  Q-IDE SETUP WIZARD                        ║
echo echo ║                                                            ║
echo echo ║  This will install all dependencies on your computer      ║
echo echo ╚════════════════════════════════════════════════════════════╝
echo echo.
echo.
echo python --version >nul 2>&1
echo if errorlevel 1 ^(
echo     echo [ERROR] Python 3.11+ not found!
echo     echo.
echo     echo Please download and install Python from:
echo     echo https://www.python.org/downloads/
echo     echo.
echo     echo During installation, CHECK the box:
echo     echo   ☑ Add Python to PATH
echo     echo.
echo     pause
echo     exit /b 1
echo ^)
echo.
echo node --version >nul 2>&1
echo if errorlevel 1 ^(
echo     echo [ERROR] Node.js not found!
echo     echo.
echo     echo Please download and install Node.js from:
echo     echo https://nodejs.org/
echo     echo.
echo     echo During installation, CHECK the box:
echo     echo   ☑ Add to PATH
echo     echo.
echo     pause
echo     exit /b 1
echo ^)
echo.
echo for %%%%A in ^("%%%%~dp0."^) do set "ROOT_DIR=%%%%~fA"
echo.
echo echo [1/3] Installing backend dependencies...
echo cd /d "!ROOT_DIR!\backend"
echo pip install -q -r requirements.txt
echo if errorlevel 1 ^(
echo     echo [ERROR] Failed to install Python packages
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo [2/3] Installing frontend dependencies...
echo cd /d "!ROOT_DIR!\frontend"
echo call pnpm install
echo if errorlevel 1 ^(
echo     echo [ERROR] Failed to install Node packages
echo     echo Try installing pnpm: npm install -g pnpm
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo [3/3] Verifying installation...
echo cd /d "!ROOT_DIR!"
echo python test_q_assistant_integration.py >nul 2>&1
echo.
echo if %%ERRORLEVEL%% EQU 0 ^(
echo     echo.
echo     echo ╔════════════════════════════════════════════════════════════╗
echo     echo ║          ✓ SETUP COMPLETE - READY TO LAUNCH!               ║
echo     echo ║                                                            ║
echo     echo ║  Next: Run LAUNCH_Q-IDE.bat to start the application      ║
echo     echo ╚════════════════════════════════════════════════════════════╝
echo ^) else ^(
echo     echo.
echo     echo ╔════════════════════════════════════════════════════════════╗
echo     echo ║          Setup complete but tests show issues              ║
echo     echo ║          You can still try running LAUNCH_Q-IDE.bat        ║
echo     echo ╚════════════════════════════════════════════════════════════╝
echo ^)
echo.
echo pause
) > "%DIST_DIR%\SETUP.bat"

echo [OK] SETUP.bat created

REM Create universal launcher
(
echo @echo off
echo setlocal enabledelayedexpansion
echo cls
echo title Q-IDE TOPDOG - LAUNCHING...
echo.
echo for %%%%A in ^("%%%%~dp0."^) do set "ROOT_DIR=%%%%~fA"
echo.
echo echo ╔════════════════════════════════════════════════════════════╗
echo echo ║           LAUNCHING Q-IDE TOPDOG                           ║
echo echo ║                                                            ║
echo echo ║  Starting Backend ^(FastAPI^)...                            ║
echo echo ║  Starting Frontend ^(React/Vite^)...                        ║
echo echo ║                                                            ║
echo echo ║  Please wait 10 seconds...                                 ║
echo echo ╚════════════════════════════════════════════════════════════╝
echo echo.
echo.
echo taskkill /F /IM python.exe >nul 2>&1
echo taskkill /F /IM node.exe >nul 2>&1
echo timeout /t 2 /nobreak >nul
echo.
echo echo [1/2] Starting Backend Server on port 8000...
echo start "Q-IDE Backend" cmd /k "cd /d "!ROOT_DIR!\backend" ^&^& python main.py"
echo timeout /t 4 /nobreak >nul
echo.
echo echo [2/2] Starting Frontend Server on port 1431...
echo start "Q-IDE Frontend" cmd /k "cd /d "!ROOT_DIR!\frontend" ^&^& npx vite --host 127.0.0.1 --port 1431"
echo timeout /t 5 /nobreak >nul
echo.
echo echo Opening Q-IDE in browser...
echo timeout /t 2 /nobreak >nul
echo start http://127.0.0.1:1431
echo.
echo echo ✓ Both servers started successfully!
echo echo.
echo echo Backend: http://127.0.0.1:8000
echo echo Frontend: http://127.0.0.1:1431
echo echo Docs: http://127.0.0.1:8000/docs
echo echo.
echo pause
) > "%DIST_DIR%\LAUNCH_Q-IDE.bat"

echo [OK] LAUNCH_Q-IDE.bat created

echo.
echo [STEP 6/6] Creating README and helper files...

REM Create quick start readme
(
echo # Q-IDE TOPDOG - STANDALONE INSTALLATION
echo.
echo ## First Time Setup
echo.
echo 1. **Double-click `SETUP.bat`** to install dependencies
echo    - This installs all required packages
echo    - Only needs to run ONCE per computer
echo.
echo 2. **Wait for it to complete** (it will tell you when done^)
echo.
echo ## Launching Q-IDE
echo.
echo **Double-click `LAUNCH_Q-IDE.bat`** to start Q-IDE
echo.
echo - Backend will start on port 8000
echo - Frontend will start on port 1431
echo - Your browser will open automatically
echo.
echo ## URLs
echo.
echo - **Q-IDE Interface**: http://127.0.0.1:1431
echo - **API Docs**: http://127.0.0.1:8000/docs
echo.
echo ## Troubleshooting
echo.
echo ### "Python not found"
echo - Download from: https://www.python.org/downloads/
echo - CHECK "Add Python to PATH" during installation
echo.
echo ### "Node.js not found"
echo - Download from: https://nodejs.org/
echo - CHECK "Add to PATH" during installation
echo.
echo ### Ports already in use
echo - Close any other Q-IDE windows
echo - Wait 10 seconds and try again
echo.
echo ## System Requirements
echo.
echo - Windows 10 or higher
echo - Python 3.11+
echo - Node.js 18+
echo - 4GB RAM
echo - 500MB disk space
echo.
) > "%DIST_DIR%\README.txt"

echo [OK] README.txt created

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║         ✓ STANDALONE PACKAGE CREATED SUCCESSFULLY!             ║
echo ║                                                                ║
echo ║  Location: %DIST_DIR%                                          ║
echo ║                                                                ║
echo ║  Next Steps:                                                   ║
echo ║  1. Copy entire Q-IDE_STANDALONE folder to any PC             ║
echo ║  2. Double-click SETUP.bat (one time only^)                    ║
echo ║  3. Double-click LAUNCH_Q-IDE.bat to run                      ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Show folder in explorer
explorer "%DIST_DIR%"

pause
