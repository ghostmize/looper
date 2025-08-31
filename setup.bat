@echo off
echo Looper Setup - Perfect Video Loops
echo =================================
echo.

echo This script will set up Looper and install all required dependencies.
echo.

REM Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.7 or higher from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

REM Check if pip is available
echo Checking pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo pip found and working.
echo.

REM Install Python dependencies
echo Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)

echo Python dependencies installed successfully!
echo.

REM Check FFmpeg
echo Checking FFmpeg installation...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo WARNING: FFmpeg is not installed or not in PATH
    echo.
    echo Looper requires FFmpeg for video processing.
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
    echo After installing FFmpeg, run this setup script again.
    echo.
    pause
    exit /b 1
)

echo FFmpeg found:
ffmpeg -version | findstr "ffmpeg version"
echo.

echo =================================
echo Setup completed successfully!
echo.
echo You can now run Looper by double-clicking run_looper.bat
echo or by running: python launch_looper.py
echo.
pause

