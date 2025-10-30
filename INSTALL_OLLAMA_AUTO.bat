@echo off
REM ============================================================================
REM Q-IDE OLLAMA INSTALLER - LAUNCHER
REM This launcher runs the PowerShell installer with admin rights
REM ============================================================================

echo.
echo ============================================================================
echo             Q-IDE AUTOMATED OLLAMA INSTALLER LAUNCHER
echo ============================================================================
echo.
echo This will:
echo  1. Request admin permissions
echo  2. Download Ollama
echo  3. Install it automatically
echo  4. Download llama2 model
echo  5. Offer optional Google Gemini setup
echo.
echo Estimated time: 15-20 minutes
echo.

REM Check if running as admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Requesting admin permissions...
    echo.
    
    REM Re-run as admin
    powershell -Command "Start-Process powershell -ArgumentList '-NoExit', '-ExecutionPolicy', 'Bypass', '-File', '%~dpn0.ps1' -Verb RunAs"
    exit /b 0
)

REM If we get here, we're admin - run PowerShell script
echo [OK] Running installer...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dpn0.ps1"
exit /b %errorlevel%
