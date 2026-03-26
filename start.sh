#!/bin/bash
# Videogame Guru - Startup Script (macOS/Linux)
# This script starts both backend and frontend servers

echo "🎮 Starting Videogame Guru..."
echo ""

# Check if .env exists
if [ ! -f "chatbot/.env" ]; then
    echo "❌ chatbot/.env not found!"
    echo "Run ./setup.sh first to set up the project."
    exit 1
fi

# Check if dependencies are installed
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Run ./setup.sh first to set up the project."
    exit 1
fi

if [ ! -d "frontend/node_modules" ]; then
    echo "❌ Frontend dependencies not found!"
    echo "Run ./setup.sh first to set up the project."
    exit 1
fi

echo "Starting backend API server..."
gnome-terminal -- bash -c "cd chatbot && source ../.venv/bin/activate && uvicorn api:app --reload --port 8000; exec bash" 2>/dev/null || \
xterm -e "cd chatbot && source ../.venv/bin/activate && uvicorn api:app --reload --port 8000" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd '"$PWD"'/chatbot && source ../.venv/bin/activate && uvicorn api:app --reload --port 8000"' 2>/dev/null &

sleep 2

echo "Starting frontend dev server..."
gnome-terminal -- bash -c "cd frontend && npm run dev; exec bash" 2>/dev/null || \
xterm -e "cd frontend && npm run dev" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd '"$PWD"'/frontend && npm run dev"' 2>/dev/null &

sleep 2

echo ""
echo "✅ Servers starting!"
echo ""
echo "Access the application at:"
echo "  Frontend: http://localhost:5173"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C in each terminal window to stop the servers."
