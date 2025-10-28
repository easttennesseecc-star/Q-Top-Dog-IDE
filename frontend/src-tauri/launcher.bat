@echo off
REM Q-IDE Launcher Script for Windows
REM This script launches Q-IDE from the Windows Start Menu or Desktop

setlocal enabledelayedexpansion

REM Get the application name
set APP_NAME=Q-IDE (TopDog)

REM Try multiple possible locations
set "POSSIBLE_LOCATIONS[0]=%ProgramFiles%\Q-IDE\Q-IDE.exe"
set "POSSIBLE_LOCATIONS[1]=%ProgramFiles(x86)%\Q-IDE\Q-IDE.exe"
set "POSSIBLE_LOCATIONS[2]=%LocalAppData%\Programs\Q-IDE\Q-IDE.exe"
set "POSSIBLE_LOCATIONS[3]=%ProgramData%\Q-IDE\Q-IDE.exe"

REM Check each location
set APP_PATH=
for /l %%i in (0,1,3) do (
    if exist "!POSSIBLE_LOCATIONS[%%i]!" (
        set "APP_PATH=!POSSIBLE_LOCATIONS[%%i]!"
        goto found
    )
)

REM If not found, search in Program Files
if not defined APP_PATH (
    for /f "delims=" %%a in ('dir /b "%ProgramFiles%\Q-IDE" 2^>nul') do (
        if exist "%ProgramFiles%\Q-IDE\%%a\Q-IDE.exe" (
            set "APP_PATH=%ProgramFiles%\Q-IDE\%%a\Q-IDE.exe"
            goto found
        )
    )
)

REM If still not found, show error
if not defined APP_PATH (
    echo.
    echo ======================================
    echo.
    echo Error: Q-IDE not found!
    echo.
    echo Q-IDE may not be installed properly.
    echo Please reinstall using the MSI installer.
    echo.
    echo Download from: https://github.com/quellum/q-ide/releases
    echo.
    echo ======================================
    echo.
    pause
    exit /b 1
)

:found
REM App found, launch it
start "" "!APP_PATH!"

REM Success message (show briefly, then close)
timeout /t 2 /nobreak

exit /b 0
