@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo SETUP: DRONE AI NAVIGATION SIMULATOR
echo ==========================================
echo Project directory: %CD%

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    pause
    exit /b 1
)

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already exists.
)

echo Activating virtual environment...
call ".venv\Scripts\activate.bat"
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment.
    pause
    exit /b 1
)

echo Installing requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements.
    pause
    exit /b 1
)

echo.
echo Setup completed successfully!
echo You can now run run_simulation.bat
pause
endlocal
