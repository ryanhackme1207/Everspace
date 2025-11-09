@echo off
echo.
echo ============================================================
echo         EverSpace Chat - Startup Script
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/4] Checking Python environment...
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)
echo     OK - Virtual environment found
echo.

echo [2/4] Checking Redis connection...
.venv\Scripts\python.exe -c "import redis; r = redis.Redis(host='localhost', port=6379); r.ping(); print('     OK - Redis is running')" 2>nul
if errorlevel 1 (
    echo     WARNING: Redis is not running!
    echo.
    echo     Please start Redis first:
    echo     - If using Memurai: Start from Start Menu
    echo     - If using WSL: wsl sudo service redis-server start
    echo     - If using Docker: docker start redis
    echo.
    echo     Press Ctrl+C to cancel, or any key to continue anyway...
    pause >nul
)
echo.

echo [3/4] Checking required packages...
.venv\Scripts\python.exe -c "import channels, daphne, redis" 2>nul
if errorlevel 1 (
    echo     WARNING: Some packages missing
    echo     Installing required packages...
    .venv\Scripts\python.exe -m pip install channels channels-redis daphne redis
)
echo     OK - All packages installed
echo.

echo [4/4] Starting Django with Daphne (WebSocket support)...
echo.
echo ============================================================
echo     Server starting on: http://localhost:8000
echo     Press Ctrl+C to stop the server
echo ============================================================
echo.

.venv\Scripts\python.exe -m daphne -p 8000 discord_chat.asgi:application

echo.
echo ============================================================
echo     Server stopped
echo ============================================================
pause
