@echo off
REM Q-IDE Hosts File Update Script
REM Run as Administrator

echo.
echo ========================================
echo Q-IDE Domain Configuration
echo ========================================
echo.

REM Check if running as admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script requires Administrator privileges!
    echo.
    echo Please right-click this file and select "Run as administrator"
    pause
    exit /b 1
)

echo Adding Q-IDE domain names to hosts file...
echo.

REM Backup hosts file
set HOSTS_FILE=C:\Windows\System32\drivers\etc\hosts
set BACKUP_FILE=C:\Windows\System32\drivers\etc\hosts.backup_%date:~-4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
copy "%HOSTS_FILE%" "%BACKUP_FILE%"
echo ✓ Backup created: %BACKUP_FILE%
echo.

REM Add entries to hosts file
echo. >> "%HOSTS_FILE%"
echo # Q-IDE Domain Names (Added November 1, 2025) >> "%HOSTS_FILE%"
echo 134.199.134.151 q-ide.com >> "%HOSTS_FILE%"
echo 134.199.134.151 www.q-ide.com >> "%HOSTS_FILE%"
echo 134.199.134.151 api.q-ide.com >> "%HOSTS_FILE%"
echo 134.199.134.151 topdog.com >> "%HOSTS_FILE%"
echo 134.199.134.151 www.topdog.com >> "%HOSTS_FILE%"
echo 134.199.134.151 quellum.com >> "%HOSTS_FILE%"
echo 134.199.134.151 www.quellum.com >> "%HOSTS_FILE%"
echo 134.199.134.151 q >> "%HOSTS_FILE%"
echo 134.199.134.151 topdog >> "%HOSTS_FILE%"
echo 134.199.134.151 quellum >> "%HOSTS_FILE%"

echo ✓ Domains added successfully!
echo.
echo ========================================
echo You can now access your site with:
echo ========================================
echo   http://q-ide.com
echo   http://topdog.com
echo   http://quellum.com
echo   http://q
echo   http://topdog
echo   http://quellum
echo.
echo ========================================
echo.

REM Flush DNS cache
echo Flushing DNS cache...
ipconfig /flushdns
echo ✓ DNS cache flushed!
echo.

pause
