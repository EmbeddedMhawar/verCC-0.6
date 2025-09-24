@echo off
REM Guardian Configuration Validation Script for Windows
REM Usage: validate_guardian.bat [options]

echo Starting Guardian Configuration Validation...
python validate_guardian_config.py %*

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Validation completed successfully
) else (
    echo.
    echo ❌ Validation failed - check the output above
)

pause