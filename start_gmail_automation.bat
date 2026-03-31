@echo off
REM Gmail Automation Starter
REM This script starts Gmail Orchestrator with proper environment

cd /d "%~dp0"

set GEMINI_API_KEY=AIzaSyAxkzMP5rjLM5rfWrot1_M8amSxrk9nFwk
set PYTHONIOENCODING=utf-8
chcp 65001 >nul

echo Starting Gmail Automation...
python scripts\gmail_orchestrator.py
