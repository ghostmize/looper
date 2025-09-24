@echo off
echo ================================================
echo LOOPER v0.91 - DEBUG Build Script
echo by Ghosteam
echo ================================================
echo.
echo This will create a DEBUG version with console window
echo that shows all debug output and error messages.
echo.
echo Press any key to start the debug build...
pause >nul

cd /d "%~dp0"
python "build_exe - compression - debug.py"

echo.
echo ================================================
echo DEBUG BUILD COMPLETE!
echo ================================================
echo.
echo Your DEBUG executable is in the 'dist' folder:
echo Looper_v0.91_DEBUG_by_Ghosteam.exe
echo.
echo This version will:
echo - Keep the console window open
echo - Show all debug output
echo - Display FFmpeg errors
echo - Allow users to copy error messages
echo.
pause
