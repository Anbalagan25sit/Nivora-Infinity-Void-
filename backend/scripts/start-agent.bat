@echo off
REM ============================================================================
REM Nivora Agent - Windows Startup Script
REM ============================================================================

echo.
echo ========================================================================
echo   NIVORA VOICE AGENT - Starting...
echo ========================================================================
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo.
    echo Please run: python -m venv venv
    echo Then: venv\Scripts\activate
    echo Then: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo.
    echo Please create .env file with your credentials.
    echo.
    pause
    exit /b 1
)

echo [2/3] Loading environment variables...
echo [3/3] Starting LiveKit Agent...
echo.
echo ========================================================================
echo   Agent is running! Connect via:
echo   - LiveKit Playground: https://cloud.livekit.io/
echo   - Web Interface: Open Nivora-web-page/chat.html
echo ========================================================================
echo.
echo Press Ctrl+C to stop the agent
echo.

REM Use 'start' instead of 'dev' for Windows compatibility
REM 'dev' mode uses Unix IPC which causes DuplexClosed errors on Windows
python agent.py start

pause
