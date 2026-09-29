@echo off
title PharmaCopilot Prototype Launcher
echo ============================================================
echo   Starting PharmaCopilot Prototype
echo   Backend:  http://127.0.0.1:8000
echo   Frontend: http://localhost:5173
echo ============================================================
echo.

:: Check for backend virtual environment
if not exist "%~dp0backend\.venv\Scripts\python.exe" (
    echo [ERROR] Backend virtual environment not found at backend\.venv
    echo Please set up backend\.venv or run: cd backend ^&^& python -m venv .venv ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)

:: Start Backend FastAPI server in new window
echo Starting FastAPI Backend...
start "PharmaCopilot Backend (FastAPI)" cmd /k "cd /d %~dp0backend && .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

:: Start Frontend Vite server in new window
echo Starting Vite Frontend...
start "PharmaCopilot Frontend (Vite React)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ============================================================
echo   Both services started!
echo   Open browser at: http://localhost:5173
echo ============================================================
echo.
pause
