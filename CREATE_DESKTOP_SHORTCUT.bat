@echo off
REM Create Desktop Shortcut for Q-IDE
REM This script creates a convenient shortcut on your desktop

setlocal enabledelayedexpansion

cls
echo.
echo Creating Desktop Shortcut...
echo.

REM Get the project root directory
set "PROJECT_ROOT=%~dp0"
set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"

REM Create VBS script to make the shortcut
set "TEMP_VBS=%TEMP%\CreateQIDEShortcut.vbs"

(
echo Set objShell = CreateObject("WScript.Shell"^)
echo Set objFSO = CreateObject("Scripting.FileSystemObject"^)
echo.
echo strDesktop = objShell.SpecialFolders("Desktop"^)
echo strLauncherPath = "%PROJECT_ROOT%\LAUNCH_Q-IDE_PROFESSIONAL.bat"
echo strShortcutPath = objFSO.BuildPath(strDesktop, "Q-IDE Topdog.lnk"^)
echo.
echo Set objLink = objShell.CreateShortCut(strShortcutPath^)
echo objLink.TargetPath = strLauncherPath
echo objLink.WorkingDirectory = "%PROJECT_ROOT%"
echo objLink.Description = "Q-IDE Topdog - Advanced AI Development Environment"
echo objLink.IconLocation = "C:\Windows\System32\shell32.dll,13"
echo objLink.Save
echo.
echo MsgBox "Q-IDE Desktop shortcut created successfully!", 64, "Q-IDE Topdog"
) > "%TEMP_VBS%"

REM Run the VBS script
cscript.exe "%TEMP_VBS%"

REM Clean up
del "%TEMP_VBS%" /q

echo.
echo [SUCCESS] Desktop shortcut created!
echo.
echo You can now launch Q-IDE by double-clicking the "Q-IDE Topdog" icon on your desktop.
echo This is the recommended way to launch Q-IDE as a professional application.
echo.
pause
