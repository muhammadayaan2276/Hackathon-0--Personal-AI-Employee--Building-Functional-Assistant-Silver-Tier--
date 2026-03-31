@echo off
REM AI Employee - Quick Start Script (Windows)
REM Run this to start all services with PM2

echo ==============================================
echo   AI Employee - Silver Tier Quick Start
echo ==============================================
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

cd /d "%PROJECT_ROOT%"

echo Project root: %PROJECT_ROOT%
echo.

REM Check prerequisites
echo Checking prerequisites...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.13+
    exit /b 1
)
echo ✓ Python installed

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found. Please install Node.js 18+
    exit /b 1
)
echo ✓ Node.js installed

REM Check PM2
pm2 --version >nul 2>&1
if errorlevel 1 (
    echo PM2 not found. Installing...
    npm install -g pm2
)
echo ✓ PM2 installed

echo.
echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Starting services with PM2...
echo.

REM Start all services
pm2 start ecosystem.config.json

echo.
echo Waiting for services to start...
timeout /t 3 /nobreak >nul

echo.
echo Service Status:
echo.
pm2 status

echo.
echo ==============================================
echo   AI Employee Started Successfully!
echo ==============================================
echo.
echo Useful commands:
echo.
echo   View status:     pm2 status
echo   View logs:       pm2 logs
echo   Stop all:        pm2 stop all
echo   Restart all:     pm2 restart all
echo.
echo Logs location:  AI_Employee_Vault\Logs\
echo.
echo To run on system startup:
echo   pm2 startup
echo   pm2 save
echo.

pause
