@echo off
REM Update hosts file with correct ingress IP

setlocal enabledelayedexpansion

set HOSTS_FILE=C:\Windows\System32\drivers\etc\hosts
set INGRESS_IP=129.212.190.208

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Need admin rights
    pause
    exit /b 1
)

echo Updating hosts file with ingress IP: %INGRESS_IP%

REM Remove old Q-IDE entries
for /f "tokens=*" %%a in ('findstr /V "q-ide.com www.q-ide.com api.q-ide.com topdog quellum" "%HOSTS_FILE%"') do (
    echo %%a >> "%HOSTS_FILE%.tmp"
)
move /Y "%HOSTS_FILE%.tmp" "%HOSTS_FILE%" >nul

REM Add new entries with correct IP
echo. >> "%HOSTS_FILE%"
echo # Q-IDE Ingress (Updated Nov 1, 2025) >> "%HOSTS_FILE%"
echo %INGRESS_IP% q-ide.com >> "%HOSTS_FILE%"
echo %INGRESS_IP% www.q-ide.com >> "%HOSTS_FILE%"
echo %INGRESS_IP% api.q-ide.com >> "%HOSTS_FILE%"
echo %INGRESS_IP% topdog.com >> "%HOSTS_FILE%"
echo %INGRESS_IP% www.topdog.com >> "%HOSTS_FILE%"
echo %INGRESS_IP% quellum.com >> "%HOSTS_FILE%"
echo %INGRESS_IP% www.quellum.com >> "%HOSTS_FILE%"
echo %INGRESS_IP% q >> "%HOSTS_FILE%"
echo %INGRESS_IP% topdog >> "%HOSTS_FILE%"
echo %INGRESS_IP% quellum >> "%HOSTS_FILE%"

echo Done! Flushing DNS...
ipconfig /flushdns

echo.
echo ✓ You can now access:
echo   http://q-ide.com
echo   http://topdog.com
echo   http://quellum.com
echo.
pause
