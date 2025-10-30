@echo off
REM Q-IDE Debug Startup Script
REM Purpose: Start Q-IDE with debug logging enabled for troubleshooting
REM Usage: Run this script to start both backend and frontend with verbose output

setlocal enabledelayedexpansion

echo ====================================================
echo  Q-IDE Local Testing & Debugging Startup
echo ====================================================
echo.

REM Check if we're in the right directory
if not exist "backend\main.py" (
    echo ERROR: backend\main.py not found
    echo Please run this script from the Q-IDE root directory
    pause
    exit /b 1
)

echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.9+
    pause
    exit /b 1
)
echo ✓ Python OK

echo.
echo [2/5] Checking Node.js/pnpm installation...
pnpm --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pnpm not found. Please install Node.js and pnpm
    pause
    exit /b 1
)
echo ✓ pnpm OK

echo.
echo [3/5] Installing backend dependencies...
cd backend
pip install -r requirements.txt -q
if errorlevel 1 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)
echo ✓ Backend dependencies installed
cd ..

echo.
echo [4/5] Installing frontend dependencies...
cd frontend
pnpm install -q
if errorlevel 1 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)
echo ✓ Frontend dependencies installed
cd ..

echo.
echo [5/5] Starting services...
echo.
echo ====================================================
echo  BACKEND: Starting on http://localhost:8000
echo  FRONTEND: Starting on http://localhost:1431
echo ====================================================
echo.
echo LOGS:
echo  - Backend: backend\logs\app.log
echo  - Frontend: Terminal output below
echo.
echo Press Ctrl+C to stop all services
echo.

REM Start backend in a new window
start "Q-IDE Backend (Debug)" cmd /k "cd backend && python main.py --log-level debug"

REM Wait a moment for backend to start
timeout /t 3 /nobreak

REM Start frontend in a new window
start "Q-IDE Frontend (Debug)" cmd /k "cd frontend && pnpm run dev"

REM Wait for frontend to start
timeout /t 3 /nobreak

REM Open browser
echo.
echo Opening http://localhost:1431 in your browser...
start http://localhost:1431

echo.
echo ====================================================
echo  Services started! Check the new terminal windows
echo ====================================================
echo.
echo DEBUGGING TIPS:
echo  1. Press F12 in the browser to open Developer Tools
echo  2. Check backend logs: backend\logs\app.log
echo  3. Frontend logs appear in the "Q-IDE Frontend" terminal
echo  4. Use Ctrl+C in each terminal to stop services
echo.
pause
