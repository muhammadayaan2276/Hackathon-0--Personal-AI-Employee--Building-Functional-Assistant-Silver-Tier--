@echo off
REM Gmail Automation - Task Scheduler Setup
REM This script registers Gmail Orchestrator to run at startup

echo Setting up Gmail Automation in Task Scheduler...

cd /d "%~dp0"

REM Create scheduled task to run at user login
schtasks /Create /TN "Gmail Automation" /TR "\"%CD%\start_gmail_automation.bat\"" /SC ONLOGON /RU "%USERNAME%" /F

echo.
echo ✅ Gmail Automation task created!
echo The automation will start when you log in.
echo.
echo To run manually: python scripts\gmail_orchestrator.py
echo To remove task: schtasks /Delete /TN "Gmail Automation" /F

pause
