@echo off
echo Checking FFmpeg installation...
echo.

ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo FFmpeg is not installed or not in PATH
    echo.
    echo To install FFmpeg:
    echo 1. Go to https://ffmpeg.org/download.html
    echo 2. Download the Windows builds
    echo 3. Extract to a folder (e.g., C:\ffmpeg)
    echo 4. Add the bin folder to your system PATH
    echo.
    echo Or use a package manager:
    echo - Chocolatey: choco install ffmpeg
    echo - Scoop: scoop install ffmpeg
    echo.
    echo After installation, restart this application.
    pause
    exit /b 1
) else (
    echo FFmpeg is installed and working correctly!
    echo.
    ffmpeg -version | findstr "ffmpeg version"
    echo.
    echo You can now run Looper successfully.
    pause
)

