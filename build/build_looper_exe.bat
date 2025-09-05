@echo off
echo ========================================
echo LOOPER v0.9 - Executable Builder
echo by Ghosteam
echo ========================================
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

echo.
echo Building portable executable...
cd /d "%~dp0"
python build_exe.py

echo.
echo Build process completed!
pause

