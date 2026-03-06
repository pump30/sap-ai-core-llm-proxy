@echo off
REM Quick test script for the desktop application
REM This runs the app directly without packaging

cd /d "%~dp0"

echo Starting SAP AI Core LLM Proxy Desktop Application...
echo.
echo NOTE: Make sure config.json exists in the current directory.
echo Press Ctrl+C to stop.
echo.

python app_desktop.py --debug

pause