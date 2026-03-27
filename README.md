# 🎮 Videogame Guru

An AI-powered video game assistant chatbot that helps you discover games, find deals, explore sales history, and get expert rankings. Built with LangChain agents, multiple gaming APIs, and a React frontend.

> **⚡ Quick Start**: See [QUICKSTART.md](QUICKSTART.md) for a condensed setup guide.

## ✨ Features

- **Game Information**: Get detailed info about any game including ratings, genres, platforms, and release dates with cover images (powered by RAWG API)
- **PC Deal Browser**: Browse the hottest PC game deals and sales happening right now, sorted by discount percentage - perfect for finding free games and deep discounts (powered by CheapShark API)
- **Price Checker**: Check current prices for specific games across Steam, Epic Games, GOG, Humble, and more stores (powered by CheapShark API)
- **Game Rankings**: Discover top-rated games by genre, platform, or franchise with cover art from IGDB (powered by IGDB API)
- **Sales History**: Search historical video game sales data (1980-2020) with semantic search (powered by ChromaDB vector database)
- **Conversational Memory**: The agent remembers context within each chat session
- **Modern UI**: Clean, responsive React frontend with markdown support and image display

## 🛠️ Tech Stack

### Backend
- **Python 3.x** - Core language
- **LangChain** - Agent framework and tool orchestration
- **FastAPI** - REST API server
- **ChromaDB** - Vector database for sales data
- **Sentence Transformers** - Text embeddings (all-MiniLM-L6-v2)
- **OpenAI/Azure** - LLM (gpt-4o-mini via Azure inference)

### Frontend
- **React 19** - UI framework
- **Vite** - Build tool and dev server
- **React Markdown** - Message rendering

### APIs Integrated
- **RAWG** - Video game database
- **CheapShark** - Game deals aggregator
- **IGDB** (Twitch) - Game rankings and metadata
- **OpenAI/Azure** - Language model inference

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn
- API keys for:
  - GitHub Token (for Azure AI inference)
  - RAWG API
  - IGDB Client ID & Secret
  - (Or OpenAI API key if using OpenAI directly)

## 🚀 Quick Start (Automated)

### Option A: One-Command Setup (Recommended)

**Windows (PowerShell):**
```powershell
git clone https://github.com/JVanderpool-repos/videogame_guru.git
cd videogame_guru
.\setup.ps1
```

**macOS/Linux:**
```bash
git clone https://github.com/JVanderpool-repos/videogame_guru.git
cd videogame_guru
chmod +x setup.sh start.sh
./setup.sh
```

The setup script will:
- ✅ Check prerequisites (Python, Node.js)
- ✅ Create Python virtual environment
- ✅ Install all backend dependencies
- ✅ Install all frontend dependencies
- ✅ Create `.env` template from `.env.example`
- ✅ Ingest game sales data into ChromaDB

**After setup:**
1. Edit `chatbot/.env` and add your API keys (see [Getting API Keys](#-getting-api-keys))
2. Run the application:

**Windows:**
```powershell
.\start.ps1
```

**macOS/Linux:**
```bash
./start.sh
```

The application will open at `http://localhost:5173`

---

## 🔧 Manual Installation

If you prefer manual setup or need more control:

### 1. Clone the Repository

```bash
git clone https://github.com/JVanderpool-repos/videogame_guru.git
cd videogame_guru
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r chatbot/requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend
npm install
cd ..
```

### 4. Environment Configuration

```bash
# Copy the example env file
cp chatbot/.env.example chatbot/.env
# On Windows: copy chatbot\.env.example chatbot\.env
```

Edit `chatbot/.env` and add your API keys:

```env
GITHUB_TOKEN=your_actual_token_here
RAWG_API_KEY=your_actual_key_here
IGDB_CLIENT_ID=your_actual_client_id_here
IGDB_CLIENT_SECRET=your_actual_client_secret_here
```

### 5. Ingest Game Sales Data

```bash
cd chatbot
python ingest.py
cd ..
```

### 6. Run the Application

**Terminal 1 - Backend:**
```bash
cd chatbot
# Activate venv if not already active
uvicorn api:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Access at `http://localhost:5173`

## 📁 Project Structure

```
videogame_guru/
├── setup.ps1                   # Automated setup (Windows)
├── setup.sh                    # Automated setup (macOS/Linux)
├── start.ps1                   # Start both servers (Windows)
├── start.sh                    # Start both servers (macOS/Linux)
├── README.md                   # Documentation
│
├── chatbot/                    # Python backend
│   ├── api.py                  # FastAPI server
│   ├── main.py                 # LangChain agent with tools
│   ├── ingest.py               # Data ingestion script
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Environment template
│   ├── .env                    # Your API keys (create from .env.example)
│   ├── data/
│   │   └── Video_Games.csv     # Historical sales data
│   └── chroma_db/              # Vector database (auto-generated)
│
└── frontend/                   # React frontend
    ├── src/
    │   ├── App.jsx             # Main chat component
    │   ├── App.css             # Styles
    │   └── main.jsx            # Entry point
    ├── package.json            # Node dependencies
    └── vite.config.js          # Vite configuration
```

## 🔧 API Endpoints

### `POST /chat`

Send a message to the chatbot agent.

**Request Body:**
```json
{
  "message": "What are the best RPGs?",
  "session_id": "optional_session_id"
}
```

**Response:**
```json
{
  "response": "Here are the top RPGs..."
}
```

### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

## 🤖 Agent Tools

The LangChain agent has access to five specialized tools:

### 1. `search_game_info`
- Searches for game details including rating, genres, platforms, release date, and cover images
- Source: RAWG API
- Use case: "Tell me about Elden Ring"

### 2. `browse_current_deals`
- Browses the best PC game deals happening right now across all stores, sorted by savings
- Shows free games and biggest discounts
- Source: CheapShark API
- Use case: "What are the top PC deals?" or "Show me current sales"

### 3. `get_game_deals`
- Gets current prices for a specific PC game across Steam, Epic, GOG, Humble, and other stores
- Shows both regular prices and active discounts
- Source: CheapShark API
- Use case: "What's the price of Cyberpunk 2077?" or "Is Elden Ring on sale?"

### 4. `get_game_rankings`
- Gets top-rated games by genre, platform, or franchise with cover art
- Supports modern platforms (PS5, Xbox Series X/S, Switch 2)
- Source: IGDB API
- Use case: "What are the best PS5 games?" or "Top rated RPGs"

### 5. `search_sales_history`
- Semantic search over historical sales data (1980-2020)
- Includes PS4, Xbox One, PS3, Xbox 360, Wii, and older platforms
- Source: ChromaDB vector database
- Use case: "Best selling Wii games" or "Games from 2010 with high critic scores"

## 💡 Example Queries

**Game Information:**
- "What is Elden Ring?"
- "Tell me about Baldur's Gate 3"

**Deals & Pricing:**
- "What are the top PC game deals right now?"
- "Show me current sales"
- "What's the price of Cyberpunk 2077?"
- "Is Elden Ring on sale anywhere?"

**Rankings & Recommendations:**
- "What are the best PS5 games?"
- "Top rated horror games"
- "Best RPGs for Nintendo Switch"

**Sales History (1980-2020):**
- "What were the best selling games in 2010?"
- "Compare sales of Mario and Sonic games"
- "Most popular Wii games"

## 🧪 Testing

The backend includes built-in tests in `main.py`. Run them with:

```bash
cd chatbot
python main.py
```

This will test each tool individually and the agent's ability to use them together with memory.

## 🐛 Troubleshooting

### Common Issues

**"Could not reach RAWG/CheapShark/IGDB API"**
- Check your internet connection
- Verify API keys are correctly set in `chatbot/.env`
- IGDB requires both `IGDB_CLIENT_ID` and `IGDB_CLIENT_SECRET`

**"Module not found" errors**
- Ensure virtual environment is activated
- Run `pip install -r chatbot/requirements.txt` again
- On Windows: `.venv\Scripts\activate`
- On macOS/Linux: `source .venv/bin/activate`

**Frontend can't connect to backend**
- Ensure backend is running on port 8000
- Check CORS settings in `chatbot/api.py` match your frontend URL
- Verify frontend is trying to connect to `http://localhost:8000`

**ChromaDB errors**
- Delete `chatbot/chroma_db/` folder and run `python ingest.py` again
- Ensure `data/Video_Games.csv` exists and is readable

**PowerShell script execution policy error**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Port already in use**
- Backend (8000): Kill the process using the port or change port in startup scripts
- Frontend (5173): Vite will automatically use next available port (5174, etc.)

### Reset Everything

```bash
# Windows
Remove-Item -Recurse -Force .venv, chatbot\chroma_db, chatbot\__pycache__, frontend\node_modules
.\setup.ps1

# macOS/Linux
rm -rf .venv chatbot/chroma_db chatbot/__pycache__ frontend/node_modules
./setup.sh
```

## 📝 Development Notes

### Project Scripts

- `setup.ps1` / `setup.sh` - Complete project setup with dependency installation
- `start.ps1` / `start.sh` - Launch both frontend and backend servers
- `chatbot/ingest.py` - Ingest CSV data into ChromaDB vector database
- `chatbot/main.py` - Run agent tests and tool demonstrations

### Environment Variables

All API keys are stored in `chatbot/.env`:
- Use `chatbot/.env.example` as a template
- Never commit `.env` to version control (already in `.gitignore`)
- Azure/GitHub Models token works with `gpt-4o-mini`
- Can substitute `OPENAI_API_KEY` for direct OpenAI access

## 🔑 Getting API Keys

1. **GitHub Token**: Sign up for [GitHub Models](https://github.com/marketplace/models) (free tier available)
2. **RAWG API**: Register at [rawg.io/apidocs](https://rawg.io/apidocs) (free, no credit card)
3. **IGDB API**: Register at [Twitch Developer Console](https://dev.twitch.tv/console/apps) (free)

## ⚠️ Known Limitations

### Data Coverage

**Historical Sales Data (ChromaDB)**
- **Time Period**: Only covers games from 1980-2020
- **Missing Platforms**: Does NOT include PlayStation 5, Xbox Series X/S, or Nintendo Switch 2
- **Missing Games**: Any games released after 2020 are not in the historical sales database
- **Use Case**: Best for querying older platforms (PS4, Xbox One, original Nintendo Switch, PS3, Wii, etc.)

**Game Rankings (IGDB)**
- **New Platforms**: Xbox Series X/S and other very new platforms may have limited exclusive game data
- **Fallback Behavior**: When platform exclusives aren't available, the chatbot automatically searches for highly-rated multi-platform games available on that platform
- **Rating Threshold**: Requires games to have a minimum rating (60+) and rating count (5+) to appear in results

**Game Deals & Pricing (CheapShark)**
- **PC Only**: Only tracks deals and prices for PC games across Steam, Epic Games, GOG, and other PC stores
- **Console Deals**: Cannot find deals for PlayStation, Xbox, or Nintendo games
- **Workaround**: For console games, the chatbot will use the rankings tool to suggest top-rated games instead

### API Limitations

- **Rate Limits**: External APIs (RAWG, IGDB, CheapShark) have rate limits; excessive requests may be throttled
- **API Availability**: Chatbot functionality depends on third-party API uptime
- **Data Freshness**: Game information and deals are only as current as the external APIs provide

### Session Memory

- **Scope**: Conversation memory is scoped to individual session IDs
- **Persistence**: Memory is stored in-memory and cleared when the backend restarts
- **No Cross-Session**: Different sessions cannot access each other's conversation history

## 🤖 Development Methodology

This project was built using AI pair programming with Claude Sonnet as a development assistant. AI assistance was used for:

- Code generation and implementation
- Debugging and error resolution
- Code review and architectural guidance
- Troubleshooting API integrations

All code was reviewed, tested, and understood by the developer.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **RAWG** for comprehensive game database API
- **CheapShark** for game deals aggregation
- **IGDB** for game rankings and metadata
- **LangChain** for agent framework
- **OpenAI/Azure** for LLM capabilities
