@echo off
REM Start the Q-IDE Backend Server
REM This script starts the FastAPI backend on port 8000

echo [*] Q-IDE Backend Launcher
echo [*] Starting FastAPI server...
echo.

cd /d C:\Quellum-topdog-ide\backend

python -c "import sys; sys.path.insert(0, '.'); from uvicorn import run; run('main:app', host='0.0.0.0', port=8000, reload=False, log_level='info')" 

if errorlevel 1 (
    echo [!] Server failed to start
    echo [!] Check if main.py has any import errors
    pause
    exit /b 1
)
