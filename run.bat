@echo off
title Plant Disease Information Agent
echo ========================================================
echo    Plant Disease Information Agent - Setup & Launch
echo ========================================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found on your system.
    echo Please download and install Python from https://www.python.org/
    echo (Make sure to check "Add Python to PATH" during installation!)
    echo.
    pause
    exit /b
)

:: Create virtual environment if missing
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

:: Install / verify dependencies
echo Installing dependencies...
.venv\Scripts\pip install -r requirements.txt

:: Launch backend and open browser
echo.
echo Starting Plant Disease Agent on http://localhost:8000 ...
start "" http://localhost:8000
.venv\Scripts\python backend\main.py

pause
