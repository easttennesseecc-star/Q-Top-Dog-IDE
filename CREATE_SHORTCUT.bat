@echo off
REM ============================================================================
REM Q-IDE TOPDOG - CREATE DESKTOP SHORTCUT
REM
REM This script creates a professional desktop shortcut for Q-IDE
REM The shortcut will launch Q-IDE with a single click
REM ============================================================================

setlocal enabledelayedexpansion

color 0B
title Q-IDE - Create Desktop Shortcut

for %%A in ("%~dp0.") do set "ROOT_DIR=%%~fA"

cls

echo.
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                            ║
echo ║              Q-IDE TOPDOG - DESKTOP SHORTCUT CREATOR                       ║
echo ║                                                                            ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.

REM Create the shortcut using PowerShell
echo Creating desktop shortcut...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command "^
    $DesktopPath = [Environment]::GetFolderPath('Desktop'); ^
    $ShortcutPath = Join-Path $DesktopPath 'Q-IDE Topdog.lnk'; ^
    $LauncherPath = '%ROOT_DIR%\Q-IDE.bat'; ^
    $IconPath = '%ROOT_DIR%\media\q-ide-icon.ico'; ^
    ^
    $shell = New-Object -ComObject WScript.Shell; ^
    $shortcut = $shell.CreateShortcut($ShortcutPath); ^
    $shortcut.TargetPath = $LauncherPath; ^
    $shortcut.WorkingDirectory = '%ROOT_DIR%'; ^
    $shortcut.Description = 'Launch Q-IDE Topdog - Advanced AI Development IDE'; ^
    if (Test-Path $IconPath) { ^
        $shortcut.IconLocation = $IconPath; ^
    } ^
    $shortcut.Save(); ^
    ^
    Write-Host 'Shortcut created successfully!'; ^
    Write-Host ('Path: ' + $ShortcutPath); ^
"

echo.
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                            ║
echo ║                    ✓ SHORTCUT CREATED SUCCESSFULLY!                       ║
echo ║                                                                            ║
echo ║  A new shortcut has been added to your Desktop named:                     ║
echo ║                                                                            ║
echo ║           "Q-IDE Topdog.lnk"                                              ║
echo ║                                                                            ║
echo ║  Simply double-click it to launch Q-IDE anytime!                          ║
echo ║                                                                            ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.

pause

exit /b 0
