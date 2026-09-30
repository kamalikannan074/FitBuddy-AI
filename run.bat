@echo off
setlocal
title FitBuddy AI - Server Runner

echo ============================================================
echo FitBuddy AI Fitness ^& Nutrition Plan Generator
echo ============================================================
echo.

REM Check if local virtual environment exists
if exist "%~dp0venv\Scripts\activate.bat" (
    echo [INFO] Activating local virtual environment...
    call "%~dp0venv\Scripts\activate.bat"
) else (
    echo [INFO] Virtual environment 'venv' not found. Using system Python...
)

echo [INFO] Starting FastAPI server on http://127.0.0.1:8001
echo [INFO] Press Ctrl+C in this window to stop the server.
echo.

python -m uvicorn app.main:app --reload --port 8001

endlocal
