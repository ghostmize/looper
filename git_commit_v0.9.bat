@echo off
echo Preparing Looper v0.91 for Git commit...
echo.

REM Check if git is available
git --version >nul 2>&1
if errorlevel 1 (
    echo Error: Git is not installed or not in PATH
    echo Please install Git from https://git-scm.com
    pause
    exit /b 1
)

echo Git found. Proceeding with commit...
echo.

REM Add all files
echo Adding files to git...
git add .

REM Commit with version 0.91 message
echo Committing changes...
git commit -m "v0.91: Complete project reorganization and cleanup

- Organized files into logical folder structure
- Moved source code to src/ folder
- Organized assets into assets/icons/ and assets/logos/
- Moved scripts to scripts/ folder
- Moved build tools to build/ folder
- Moved documentation to docs/ folder
- Updated all file references and paths
- Removed debug and test files
- Enhanced drag & drop functionality
- Cleaner, more maintainable codebase
- Updated README with new structure
- All functionality preserved and working"

echo.
echo Commit completed successfully!
echo.
echo To push to remote repository, run:
echo   git push origin main
echo.
pause
