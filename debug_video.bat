@echo off
echo FFmpeg Debug Script for Looper
echo =============================

if "%~1"=="" (
    echo Usage: debug_video.bat "path\to\your\video.mp4"
    echo.
    echo This script will test FFmpeg operations on your video file
    echo to help identify any processing issues.
    pause
    exit /b 1
)

echo Testing video file: %1
echo.

python debug_ffmpeg.py "%~1"

echo.
echo Debug complete! Check the output above for any errors.
pause
