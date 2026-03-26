#!/bin/bash
# Videogame Guru - Setup Script (macOS/Linux)
# This script sets up both backend and frontend dependencies

echo "🎮 Setting up Videogame Guru..."
echo ""

# Check Python
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8 or higher."
    exit 1
fi
python_version=$(python3 --version)
echo "✅ Found: $python_version"

# Check Node.js
echo "Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 16 or higher."
    exit 1
fi
node_version=$(node --version)
echo "✅ Found Node.js: $node_version"
echo ""

# Setup Python Backend
echo "📦 Setting up Python backend..."
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing Python dependencies..."
pip install -r chatbot/requirements.txt
echo "✅ Python dependencies installed"
echo ""

# Setup Environment Variables
if [ ! -f "chatbot/.env" ]; then
    echo "⚙️  Setting up environment variables..."
    cp chatbot/.env.example chatbot/.env
    echo "✅ Created chatbot/.env from template"
    echo "⚠️  IMPORTANT: Edit chatbot/.env and add your API keys!"
    echo ""
else
    echo "✅ Environment file already exists"
    echo ""
fi

# Setup Frontend
echo "📦 Setting up React frontend..."
cd frontend
echo "Installing Node.js dependencies..."
npm install
echo "✅ Frontend dependencies installed"
cd ..
echo ""

# Ingest Data
echo "📊 Checking game sales data..."
if [ ! -f "chatbot/chroma_db/chroma.sqlite3" ]; then
    echo "Ingesting video game sales data into ChromaDB..."
    cd chatbot
    python ingest.py
    cd ..
    echo "✅ Data ingestion complete"
else
    echo "✅ ChromaDB already populated"
    echo "💡 To re-ingest data, run: cd chatbot && python ingest.py"
fi
echo ""

echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit chatbot/.env and add your API keys"
echo "2. Run ./start.sh to start the application"
echo ""
echo "Get API keys from:"
echo "  - GitHub Token: https://github.com/marketplace/models"
echo "  - RAWG API: https://rawg.io/apidocs"
echo "  - IGDB API: https://dev.twitch.tv/console/apps"
