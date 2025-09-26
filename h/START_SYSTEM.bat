@echo off
echo ============================================================
echo GUARDIAN TOOLS COMPLETE SYSTEM STARTUP
echo ============================================================
echo.
echo This will start both services in separate windows:
echo 1. MRV Sender (http://localhost:3005)
echo 2. ESP32 Dashboard with Guardian Tools (http://localhost:5000)
echo.
echo Press any key to start both services...
pause >nul

echo.
echo Starting MRV Sender in new window...
start "MRV Sender" cmd /k "start_mrv_sender.bat"

echo Waiting 3 seconds...
timeout /t 3 /nobreak >nul

echo Starting Dashboard in new window...
start "ESP32 Dashboard" cmd /k "start_dashboard.bat"

echo.
echo ============================================================
echo SYSTEM STARTUP COMPLETE
echo ============================================================
echo.
echo ACCESS POINTS:
echo - ESP32 Dashboard:     http://localhost:5000
echo - Guardian Dashboard:  http://localhost:5000/guardian
echo - MRV Sender:          http://localhost:3005
echo.
echo ESP32 ENDPOINT:
echo POST http://localhost:5000/api/energy-data
echo.
echo Both services are running in separate windows.
echo Close those windows to stop the services.
echo.
pause