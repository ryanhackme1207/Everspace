@echo off
echo ========================================
echo   Keep-Alive Bot Launcher
echo ========================================
echo.

:: Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo Virtual environment not found!
    echo Please run: python -m venv .venv
    pause
    exit /b
)

:: Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

:: Install requirements if needed
echo.
echo Checking dependencies...
pip install requests flask --quiet

:: Get user choice
echo.
echo Choose which bot to run:
echo 1. Simple Keep-Alive Bot
echo 2. Advanced Keep-Alive Bot (with multiple endpoints)
echo 3. Keep-Alive Bot with Web Dashboard
echo.
set /p choice="Enter choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo Starting Simple Keep-Alive Bot...
    python keep_alive_bot.py
) else if "%choice%"=="2" (
    echo.
    echo Starting Advanced Keep-Alive Bot...
    python keep_alive_advanced.py
) else if "%choice%"=="3" (
    echo.
    echo Starting Keep-Alive Bot with Dashboard...
    echo Dashboard will be available at http://localhost:5000
    python keep_alive_dashboard.py
) else (
    echo Invalid choice!
    pause
    exit /b
)

pause
