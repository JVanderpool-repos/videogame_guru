# Videogame Guru - Startup Script
# This script starts both backend and frontend servers

Write-Host "🎮 Starting Videogame Guru..." -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (!(Test-Path "chatbot\.env")) {
    Write-Host "❌ chatbot\.env not found!" -ForegroundColor Red
    Write-Host "Run .\setup.ps1 first to set up the project." -ForegroundColor Yellow
    exit 1
}

# Check if dependencies are installed
if (!(Test-Path ".venv")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Run .\setup.ps1 first to set up the project." -ForegroundColor Yellow
    exit 1
}

if (!(Test-Path "frontend\node_modules")) {
    Write-Host "❌ Frontend dependencies not found!" -ForegroundColor Red
    Write-Host "Run .\setup.ps1 first to set up the project." -ForegroundColor Yellow
    exit 1
}

Write-Host "Starting backend API server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\chatbot'; & ..\\.venv\Scripts\Activate.ps1; uvicorn api:app --reload --port 8000"

Start-Sleep -Seconds 2

Write-Host "Starting frontend dev server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm run dev"

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "✅ Servers starting!" -ForegroundColor Green
Write-Host ""
Write-Host "Access the application at:" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "  Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C in each terminal window to stop the servers." -ForegroundColor Gray
