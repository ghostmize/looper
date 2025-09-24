@echo off
echo ========================================
echo Looper - Antivirus Whitelist Submission
echo ========================================
echo.

echo This script helps you submit Looper to antivirus vendors
echo for whitelisting (free alternative to code signing)
echo.

cd /d "%~dp0"
python submit_to_antivirus.py

echo.
echo Submission process completed!
pause






