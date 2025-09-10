@echo off
echo ========================================
echo LOOPER v0.91 - Code Signed Executable Builder
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
echo Building code-signed portable executable...
echo.

REM Check if certificate file is provided
if "%1"=="" (
    echo Usage: build_looper_signed.bat [certificate_file] [password]
    echo.
    echo Examples:
    echo   build_looper_signed.bat
    echo   build_looper_signed.bat "C:\certs\mycert.pfx" "mypassword"
    echo   build_looper_signed.bat "C:\certs\mycert.pfx" "mypassword" --verify
    echo.
    echo Building without code signing...
    cd /d "%~dp0"
    python build_exe_with_signing.py
) else (
    echo Certificate file: %1
    if "%2"=="" (
        echo Building with code signing (no password)...
        cd /d "%~dp0"
        python build_exe_with_signing.py --cert "%1"
    ) else (
        echo Building with code signing (with password)...
        cd /d "%~dp0"
        python build_exe_with_signing.py --cert "%1" --password "%2" %3
    )
)

echo.
echo Build process completed!
pause
