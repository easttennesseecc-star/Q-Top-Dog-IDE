@echo off
REM Q-IDE SIMPLE LAUNCHER - Just start the servers, no checks
setlocal enabledelayedexpansion
cls

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                   Q-IDE LAUNCHING                          ║
echo ║                                                            ║
echo ║            Starting Backend and Frontend...                ║
echo ║                                                            ║
echo ║       Please wait ~20 seconds for servers to start         ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Get root directory
for %%A in ("%~dp0.") do set "ROOT_DIR=%%~fA"

echo [1/3] Stopping old servers...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM python3.11.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 3 /nobreak >nul
echo [OK] Old servers stopped

echo.
echo [2/3] Starting Backend on port 8000...
start "Q-IDE Backend" cmd /k "title Q-IDE Backend ^& cd /d "%ROOT_DIR%\backend" ^& python main.py ^& pause"
timeout /t 5 /nobreak >nul

echo.
echo [3/3] Starting Frontend on port 1431...
start "Q-IDE Frontend" cmd /k "title Q-IDE Frontend ^& cd /d "%ROOT_DIR%\frontend" ^& npx vite --host 127.0.0.1 --port 1431 ^& pause"
timeout /t 7 /nobreak >nul

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║         ✓ SERVERS STARTED!                                 ║
echo ║                                                            ║
echo ║    Opening Q-IDE in browser...                            ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝

timeout /t 3 /nobreak >nul
start http://127.0.0.1:1431

echo.
echo ✓ Backend:  http://127.0.0.1:8000
echo ✓ Frontend: http://127.0.0.1:1431
echo.
echo Both servers are running in separate windows.
echo Close this window when done.
echo.
pause
