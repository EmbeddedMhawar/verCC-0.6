@echo off
echo ========================================
echo MRV Processing Pipeline Setup
echo ========================================
echo.

echo Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install Python dependencies!
    pause
    exit /b 1
)

echo.
echo Setting up mrv-sender...
python setup_mrv_sender.py
if %errorlevel% neq 0 (
    echo Setup failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Run: start_mrv_sender.bat
echo 2. Run: test_endpoints.bat
echo 3. Run: run_pipeline.bat
echo.
pause