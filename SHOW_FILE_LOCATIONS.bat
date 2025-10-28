@echo off
REM Q-IDE File Finder
REM Shows you exactly where all important files are

setlocal enabledelayedexpansion

cls

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                                                           ║
echo ║           Q-IDE - File Location Guide                     ║
echo ║                                                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo Current Directory: %CD%
echo.

echo ┌─ LAUNCH FILES (Pick one to start) ─────────────────────┐
echo │                                                           │
echo │  [EASIEST]   🚀_LAUNCH_Q-IDE.bat                          │
echo │              → Double-click this! (Has rocket emoji)      │
echo │                                                           │
echo │  [RECOMMENDED] CREATE_DESKTOP_SHORTCUT.bat               │
echo │              → Run once to create desktop icon           │
echo │              → Then double-click desktop icon daily      │
echo │                                                           │
echo │  [ORIGINAL]  START.bat                                   │
echo │              → Original launcher (still works great)     │
echo │                                                           │
echo │  [FIRST TIME] INSTALL.bat                                │
echo │              → Run this first if not installed yet       │
echo │                                                           │
echo └───────────────────────────────────────────────────────────┘
echo.

echo ┌─ DOCUMENTATION FILES (Read before launching) ──────────┐
echo │                                                           │
echo │  HOW_TO_LAUNCH_Q-IDE.md                                  │
echo │  → You are here! This is the quick guide               │
echo │                                                           │
echo │  QUICK_START.md                                          │
echo │  → 3-step quick start guide                             │
echo │                                                           │
echo │  README_INSTALLATION.md                                  │
echo │  → Full installation and troubleshooting guide          │
echo │                                                           │
echo │  INSTALLATION_PACKAGE_READY.md                          │
echo │  → Complete system overview                             │
echo │                                                           │
echo └───────────────────────────────────────────────────────────┘
echo.

echo ┌─ FOLDER STRUCTURE ────────────────────────────────────────┐
echo │                                                           │
if exist "backend" (
    echo │  ✓ backend\        → Python/FastAPI server
) else (
    echo │  ✗ backend\        → NOT FOUND
)

if exist "frontend" (
    echo │  ✓ frontend\       → React/Vite UI
) else (
    echo │  ✗ frontend\       → NOT FOUND
)

if exist "logs" (
    echo │  ✓ logs\           → Application logs
) else (
    echo │  ~ logs\           → (Created on first launch)
)

echo │                                                           │
echo └───────────────────────────────────────────────────────────┘
echo.

echo ┌─ QUICK START ──────────────────────────────────────────────┐
echo │                                                           │
echo │  Step 1: Double-click 🚀_LAUNCH_Q-IDE.bat                │
echo │          (The file with the rocket emoji)               │
echo │                                                           │
echo │  Step 2: Wait 3-5 seconds for startup                   │
echo │                                                           │
echo │  Step 3: Browser opens to http://localhost:1431          │
echo │                                                           │
echo │  Step 4: Complete Setup Wizard                           │
echo │                                                           │
echo │  Step 5: Start building!                                │
echo │                                                           │
echo └───────────────────────────────────────────────────────────┘
echo.

echo Ready to launch? Follow the guide above!
echo.

pause
