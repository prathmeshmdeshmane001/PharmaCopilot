# PharmaCopilot Prototype Launcher (PowerShell)
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Starting PharmaCopilot Prototype" -ForegroundColor Cyan
Write-Host "  Backend:  http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$BackendPython = Join-Path $ScriptDir "backend\.venv\Scripts\python.exe"

if (-not (Test-Path $BackendPython)) {
    Write-Host "[ERROR] Backend virtual environment not found at $BackendPython" -ForegroundColor Red
    Write-Host "Please set up backend\.venv or run: cd backend; python -m venv .venv; pip install -r requirements.txt"
    exit 1
}

# Start Backend
Write-Host "Launching FastAPI Backend..." -ForegroundColor Green
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "cd /d `"$ScriptDir\backend`" && .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

# Start Frontend
Write-Host "Launching Vite Frontend..." -ForegroundColor Green
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "cd /d `"$ScriptDir\frontend`" && npm run dev"

Write-Host ""
Write-Host "PharmaCopilot services launched in separate terminal windows." -ForegroundColor Yellow
Write-Host "Navigate to http://localhost:5173 in your browser." -ForegroundColor Yellow
