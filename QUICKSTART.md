# Videogame Guru - Quick Reference

## 🚀 First Time Setup

```powershell
# Windows
git clone https://github.com/JVanderpool-repos/videogame_guru.git
cd videogame_guru
.\setup.ps1
# Edit chatbot\.env with your API keys
.\start.ps1
```

```bash
# macOS/Linux
git clone https://github.com/JVanderpool-repos/videogame_guru.git
cd videogame_guru
chmod +x *.sh
./setup.sh
# Edit chatbot/.env with your API keys
./start.sh
```

## 🔑 Required API Keys

Get these free API keys:

| Service | URL | Purpose |
|---------|-----|---------|
| GitHub Models | https://github.com/marketplace/models | LLM (gpt-4o-mini) |
| RAWG | https://rawg.io/apidocs | Game database |
| IGDB | https://dev.twitch.tv/console/apps | Game rankings |

Add them to `chatbot/.env`

## 🎯 Common Commands

### Start the App
```bash
.\start.ps1          # Windows
./start.sh           # macOS/Linux
```

### Manual Start
```bash
# Terminal 1 - Backend
cd chatbot
.venv\Scripts\activate    # Windows
source .venv/bin/activate # macOS/Linux
uvicorn api:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Re-ingest Data
```bash
cd chatbot
python ingest.py
```

### Test Agent
```bash
cd chatbot
python main.py
```

### Reset Everything
```bash
# Windows
Remove-Item -Recurse -Force .venv, chatbot\chroma_db, frontend\node_modules
.\setup.ps1

# macOS/Linux
rm -rf .venv chatbot/chroma_db frontend/node_modules
./setup.sh
```

## 🌐 URLs

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 💬 Example Queries

- "What is Elden Ring and is it on sale anywhere?"
- "Tell me about the best RPGs for PS5"
- "What are the top rated horror games?"
- "Find me deals on strategy games"
- "What were the best selling games in 2010?"

## 🛠️ Tech Stack

**Backend**: Python, LangChain, FastAPI, ChromaDB  
**Frontend**: React, Vite  
**APIs**: RAWG, CheapShark, IGDB, OpenAI/Azure

## 📁 Key Files

- `chatbot/.env` - Your API keys (copy from `.env.example`)
- `chatbot/main.py` - LangChain agent with tools
- `chatbot/api.py` - FastAPI server
- `frontend/src/App.jsx` - React chat interface

## 🆘 Troubleshooting

**"Module not found"**
```bash
pip install -r chatbot/requirements.txt
```

**"Can't connect to backend"**
- Ensure backend is running on port 8000
- Check `chatbot/.env` has all API keys

**"ChromaDB error"**
```bash
rm -rf chatbot/chroma_db  # or Remove-Item on Windows
cd chatbot && python ingest.py
```

---

For full documentation, see [README.md](README.md)
