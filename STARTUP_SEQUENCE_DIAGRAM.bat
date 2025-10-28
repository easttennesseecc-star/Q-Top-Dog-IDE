@echo off
REM Visual Startup Sequence Diagram

cls

echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                                                                        ║
echo ║              Q-IDE FLAWLESS STARTUP SEQUENCE DIAGRAM                   ║
echo ║                                                                        ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.

echo SEQUENCE:
echo ═════════════════════════════════════════════════════════════════════════
echo.

echo  START LAUNCHER
echo      ↓
echo  [STEP 1/6] Clean up old processes
echo      ├─→ taskkill python.exe
echo      ├─→ taskkill node.exe
echo      └─→ wait 2 seconds
echo      ↓
echo  [STEP 2/6] Verify directories
echo      ├─→ check backend/ exists
echo      ├─→ check frontend/ exists
echo      └─→ exit if missing
echo      ↓
echo  [STEP 3/6] Check Python
echo      ├─→ python --version
echo      └─→ exit if not found
echo      ↓
echo  [STEP 4/6] Check pnpm
echo      ├─→ pnpm --version
echo      └─→ exit if not found
echo      ↓
echo  [STEP 5/6] START BACKEND
echo      ├─→ open new window "Q-IDE Backend Server"
echo      ├─→ cd backend/
echo      ├─→ python main.py
echo      ├─→ wait 4 seconds for startup
echo      └─→ wait 2 more seconds for stability
echo      ↓
echo  Server Running: http://localhost:8000
echo      ↓
echo  [STEP 6/6] START FRONTEND
echo      ├─→ open new window "Q-IDE Frontend Server"
echo      ├─→ cd frontend/
echo      ├─→ pnpm run dev
echo      ├─→ wait 5 seconds for startup
echo      └─→ wait 2 more seconds for stability
echo      ↓
echo  Server Running: http://localhost:1431
echo      ↓
echo  [SUCCESS] BOTH SERVERS STARTED
echo      ├─→ wait 3 seconds
echo      └─→ open browser to http://localhost:1431
echo      ↓
echo  BROWSER OPENS
echo      ├─→ URL: http://localhost:1431
echo      ├─→ Q-IDE Setup Wizard displays
echo      └─→ User begins setup
echo      ↓
echo  Q-IDE READY FOR USE! 🎉
echo.

echo ═════════════════════════════════════════════════════════════════════════
echo.

echo TOTAL TIME: 15-20 seconds
echo.

echo WINDOWS CREATED:
echo  1. Main launcher window (this one)
echo  2. Q-IDE Backend Server window (Python)
echo  3. Q-IDE Frontend Server window (Node.js)
echo  4. Browser window (Chrome/Firefox/Edge)
echo.

echo URLS AVAILABLE:
echo  ✓ Frontend:  http://localhost:1431
echo  ✓ Backend:   http://localhost:8000
echo  ✓ API Docs:  http://localhost:8000/docs
echo.

echo STATUS:
echo  Backend:  RUNNING (if you see window with python code)
echo  Frontend: RUNNING (if you see window with npm/pnpm messages)
echo  Browser:  OPEN (should show Q-IDE interface)
echo.

echo WHAT TO DO IF SOMETHING FAILS:
echo  1. Check the error message in the failing window
echo  2. Read FLAWLESS_STARTUP_GUIDE.md for solutions
echo  3. Run TEST_LAUNCHER_CONFIG.bat to verify setup
echo  4. Close all windows and try again
echo.

echo KEEP BOTH WINDOWS OPEN:
echo  ❌ DO NOT close the backend window
echo  ❌ DO NOT close the frontend window
echo  ✅ DO minimize them if you want
echo  ✅ You can close them anytime and restart
echo.

pause
