# NovaChat AI - Start Both Frontend and Backend
# This script starts both the frontend (Vite) and backend (FastAPI) simultaneously

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  NovaChat AI - Starting Services" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$backendPath = "$PSScriptRoot\backend"
$frontendPath = "$PSScriptRoot\frontend"

# Check if paths exist
if (-not (Test-Path $backendPath)) {
    Write-Host "❌ Backend path not found: $backendPath" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $frontendPath)) {
    Write-Host "❌ Frontend path not found: $frontendPath" -ForegroundColor Red
    exit 1
}

# Start Backend
Write-Host "🚀 Starting Backend (FastAPI)..." -ForegroundColor Green
Write-Host "   Location: $backendPath" -ForegroundColor Gray
Write-Host "   Server: http://127.0.0.1:8000" -ForegroundColor Gray

$backendJob = Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; `$venv = '.\venv\Scripts\Activate.ps1'; if (Test-Path `$venv) { & `$venv }; uvicorn main:app --reload" -PassThru
Start-Sleep -Seconds 2

# Start Frontend
Write-Host "🚀 Starting Frontend (Vite + React)..." -ForegroundColor Green
Write-Host "   Location: $frontendPath" -ForegroundColor Gray
Write-Host "   Server: http://localhost:5173" -ForegroundColor Gray

$frontendJob = Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; npm run dev" -PassThru
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Both services are starting!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Frontend:  http://localhost:5173" -ForegroundColor Cyan
Write-Host "🔌 Backend:   http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Press Ctrl+C in either window to stop a service" -ForegroundColor Yellow
Write-Host "⚠️  Make sure your OpenAI API key is set in .env" -ForegroundColor Yellow
Write-Host ""

# Wait for both jobs (this will keep the script running)
$backendJob, $frontendJob | Wait-Process
