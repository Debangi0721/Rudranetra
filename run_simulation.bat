@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo 3D AI/ML DRONE NAVIGATION SIMULATOR
echo ==========================================
echo Project directory: %CD%

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Project virtual environment not found.
    echo Run setup.bat first.
    pause
    exit /b 1
)

call ".venv\Scripts\activate.bat"

if not exist "scripts\run_simulation.py" (
    echo ERROR: Simulation entry point not found.
    echo Inspect the project and correct this path.
    pause
    exit /b 1
)

python "scripts\run_simulation.py"

if errorlevel 1 (
    echo.
    echo ERROR: Simulation failed. Read the traceback above.
    pause
    exit /b 1
)

echo.
echo Simulation process completed.
pause
endlocal
