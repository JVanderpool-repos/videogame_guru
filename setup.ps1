# Videogame Guru - Setup Script
# This script sets up both backend and frontend dependencies

Write-Host "🎮 Setting up Videogame Guru..." -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}
$pythonVersion = python --version
Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green

# Check Node.js
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
if (!(Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js not found. Please install Node.js 16 or higher." -ForegroundColor Red
    exit 1
}
$nodeVersion = node --version
Write-Host "✅ Found Node.js: $nodeVersion" -ForegroundColor Green
Write-Host ""

# Setup Python Backend
Write-Host "📦 Setting up Python backend..." -ForegroundColor Cyan
if (!(Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
}

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r chatbot\requirements.txt
Write-Host "✅ Python dependencies installed" -ForegroundColor Green
Write-Host ""

# Setup Environment Variables
if (!(Test-Path "chatbot\.env")) {
    Write-Host "⚙️  Setting up environment variables..." -ForegroundColor Yellow
    Copy-Item "chatbot\.env.example" "chatbot\.env"
    Write-Host "✅ Created chatbot\.env from template" -ForegroundColor Green
    Write-Host "⚠️  IMPORTANT: Edit chatbot\.env and add your API keys!" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "✅ Environment file already exists" -ForegroundColor Green
    Write-Host ""
}

# Setup Frontend
Write-Host "📦 Setting up React frontend..." -ForegroundColor Cyan
Set-Location frontend
Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
npm install
Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green
Set-Location ..
Write-Host ""

# Ingest Data
Write-Host "📊 Checking game sales data..." -ForegroundColor Cyan
if (!(Test-Path "chatbot\chroma_db\chroma.sqlite3")) {
    Write-Host "Ingesting video game sales data into ChromaDB..." -ForegroundColor Yellow
    Set-Location chatbot
    python ingest.py
    Set-Location ..
    Write-Host "✅ Data ingestion complete" -ForegroundColor Green
} else {
    Write-Host "✅ ChromaDB already populated" -ForegroundColor Green
    Write-Host "💡 To re-ingest data, run: cd chatbot && python ingest.py" -ForegroundColor Gray
}
Write-Host ""

Write-Host "🎉 Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit chatbot\.env and add your API keys" -ForegroundColor White
Write-Host "2. Run .\start.ps1 to start the application" -ForegroundColor White
Write-Host ""
Write-Host "Get API keys from:" -ForegroundColor Cyan
Write-Host "  - GitHub Token: https://github.com/marketplace/models" -ForegroundColor Gray
Write-Host "  - RAWG API: https://rawg.io/apidocs" -ForegroundColor Gray
Write-Host "  - IGDB API: https://dev.twitch.tv/console/apps" -ForegroundColor Gray
