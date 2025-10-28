@echo off
REM Quick Gemini API Key Setup for Q-IDE
REM This script helps you add your Google Gemini API key

cls
echo.
echo ============================================================
echo.
echo          GOOGLE GEMINI SETUP FOR Q-IDE
echo.
echo ============================================================
echo.
echo This will help you set up Gemini as your LLM for Q Assistant.
echo Gemini has great voice capabilities!
echo.
pause

REM Check if API key is already set
setlocal enabledelayedexpansion
if not "!GOOGLE_API_KEY!"=="" (
    echo [OK] GOOGLE_API_KEY already set in environment
    echo Current value: !GOOGLE_API_KEY:~0,10!...
    echo.
    set /p REPLACE="Replace it? (y/n): "
    if /i not "!REPLACE!"=="y" (
        goto end
    )
)

echo.
echo STEP 1: Get Your Gemini API Key
echo ================================
echo 1. Open your browser to: https://ai.google.dev
echo 2. Click "Get API Key"
echo 3. Create or select a Google Cloud project
echo 4. Copy your API key (long string starting with "AIza...")
echo.
pause

set /p APIKEY="Paste your API key here: "

if "!APIKEY!"=="" (
    echo [ERROR] No API key provided!
    pause
    goto end
)

echo.
echo Setting GOOGLE_API_KEY in environment variables...
setx GOOGLE_API_KEY "!APIKEY!" >nul

if !errorlevel! equ 0 (
    echo [OK] API key saved successfully!
    echo.
    echo STEP 2: Restart Q-IDE
    echo ============================
    echo You need to restart Q-IDE for the changes to take effect.
    echo.
    echo STEP 3: Assign Gemini to Q Assistant
    echo ============================
    echo 1. Open Q-IDE
    echo 2. Go to "LLM Setup" tab
    echo 3. Click "Providers" tab
    echo 4. Find "Google Gemini" and click "Setup"
    echo 5. Go to "Roles" tab
    echo 6. Find "Q Assistant (Chat)"
    echo 7. Click "Configure"
    echo 8. Select "Gemini Pro"
    echo 9. Click "Assign Model"
    echo.
    echo Done! Q Assistant will now use Gemini with voice!
) else (
    echo [ERROR] Failed to save API key!
    echo Please try setting it manually in Windows Settings
    echo Environment Variables ^> User variables ^> New ^> GOOGLE_API_KEY
)

:end
echo.
pause
