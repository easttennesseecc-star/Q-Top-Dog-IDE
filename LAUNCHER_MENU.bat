@echo off
REM ============================================================================
REM Q-IDE LAUNCHER DASHBOARD - INTERACTIVE MENU
REM ============================================================================

setlocal enabledelayedexpansion

for %%A in ("%~dp0.") do set "ROOT_DIR=%%~fA"

:MENU
cls
color 0B
title Q-IDE Topdog - Launcher Menu

echo.
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                            ║
echo ║                        Q-IDE TOPDOG LAUNCHER MENU                         ║
echo ║                                                                            ║
echo ║                    Professional AI Development IDE                         ║
echo ║                                                                            ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.
echo.
echo  Choose an option:
echo.
echo     [1] ► Launch Q-IDE (Standard)
echo     [2] ► Launch Q-IDE with Debug Output
echo     [3] ► Run System Diagnostics
echo     [4] ► Create Desktop Shortcut
echo     [5] ► Open Documentation
echo     [6] ► Stop All Services
echo     [0] ► Exit
echo.
echo ════════════════════════════════════════════════════════════════════════════
echo.

set /p CHOICE="Enter your choice (0-6): "

if "%CHOICE%"=="1" goto LAUNCH_STANDARD
if "%CHOICE%"=="2" goto LAUNCH_DEBUG
if "%CHOICE%"=="3" goto DIAGNOSTICS
if "%CHOICE%"=="4" goto CREATE_SHORTCUT
if "%CHOICE%"=="5" goto DOCUMENTATION
if "%CHOICE%"=="6" goto STOP_SERVICES
if "%CHOICE%"=="0" goto EXIT
if "%CHOICE%"=="" goto MENU

echo Invalid choice. Please try again.
timeout /t 2 /nobreak >nul
goto MENU

REM ============================================================================
REM OPTION 1: STANDARD LAUNCH
REM ============================================================================
:LAUNCH_STANDARD
cls
color 0B

echo.
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                            ║
echo ║                    🚀 LAUNCHING Q-IDE TOPDOG                               ║
echo ║                                                                            ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.

call "!ROOT_DIR!\Q-IDE.bat"
pause
goto MENU

REM ============================================================================
REM OPTION 2: DEBUG LAUNCH
REM ============================================================================
:LAUNCH_DEBUG
cls
color 0B

echo.
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                            ║
echo ║                 🔧 LAUNCHING WITH DEBUG OUTPUT                             ║
echo ║                                                                            ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.

cd /d "!ROOT_DIR!"
call powershell -NoProfile ".\START_DEBUG.ps1"
pause
goto MENU

REM ============================================================================
REM OPTION 3: SYSTEM DIAGNOSTICS
REM ============================================================================
:DIAGNOSTICS
cls
color 0B

echo.
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                            ║
echo ║              🔍 RUNNING SYSTEM DIAGNOSTICS                                 ║
echo ║                                                                            ║
echo ║              This will check your system requirements...                    ║
echo ║                                                                            ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.

cd /d "!ROOT_DIR!"
call powershell -NoProfile ".\DIAGNOSE.ps1"
pause
goto MENU

REM ============================================================================
REM OPTION 4: CREATE SHORTCUT
REM ============================================================================
:CREATE_SHORTCUT
cls
color 0B

echo.
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                            ║
echo ║            📌 CREATING DESKTOP SHORTCUT                                    ║
echo ║                                                                            ║
echo ║         A shortcut will be placed on your Desktop                          ║
echo ║                                                                            ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.

cd /d "!ROOT_DIR!"
call "!ROOT_DIR!\CREATE_SHORTCUT.bat"
echo.
echo ✓ Shortcut created successfully!
echo   Look for "Q-IDE Topdog.lnk" on your Desktop
echo.
pause
goto MENU

REM ============================================================================
REM OPTION 5: DOCUMENTATION
REM ============================================================================
:DOCUMENTATION
cls
color 0B

echo.
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                            ║
echo ║            📚 Q-IDE DOCUMENTATION & GUIDES                                 ║
echo ║                                                                            ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.
echo.
echo  Available Documentation:
echo.
echo     [1] Professional Launch Guide (PROFESSIONAL_LAUNCH_GUIDE.md)
echo     [2] Quick Reference (TESTING_QUICK_REFERENCE.md)
echo     [3] Local Testing & Debugging (LOCAL_TESTING_AND_DEBUGGING.md)
echo     [4] System Architecture (SYSTEM_ARCHITECTURE.md)
echo     [0] Back to Main Menu
echo.
echo ════════════════════════════════════════════════════════════════════════════
echo.

set /p DOC_CHOICE="Enter your choice (0-4): "

if "%DOC_CHOICE%"=="1" start "" "!ROOT_DIR!\PROFESSIONAL_LAUNCH_GUIDE.md"
if "%DOC_CHOICE%"=="2" start "" "!ROOT_DIR!\TESTING_QUICK_REFERENCE.md"
if "%DOC_CHOICE%"=="3" start "" "!ROOT_DIR!\LOCAL_TESTING_AND_DEBUGGING.md"
if "%DOC_CHOICE%"=="4" start "" "!ROOT_DIR!\SYSTEM_ARCHITECTURE.md"

timeout /t 2 /nobreak >nul
goto MENU

REM ============================================================================
REM OPTION 6: STOP SERVICES
REM ============================================================================
:STOP_SERVICES
cls
color 0C

echo.
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                            ║
echo ║             ⛔ STOPPING ALL SERVICES                                        ║
echo ║                                                                            ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.
echo Stopping Python services...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 1 /nobreak >nul
echo ✓ Python processes stopped
echo.
echo Stopping Node.js services...
taskkill /F /IM node.exe >nul 2>&1
timeout /t 1 /nobreak >nul
echo ✓ Node.js processes stopped
echo.
echo.
echo All services have been stopped.
echo.
pause
goto MENU

REM ============================================================================
REM EXIT
REM ============================================================================
:EXIT
cls
color 0B

echo.
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                            ║
echo ║                  Thank you for using Q-IDE Topdog!                         ║
echo ║                                                                            ║
echo ║         For more information, visit: http://127.0.0.1:1431                ║
echo ║                                                                            ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.

endlocal
exit /b 0
