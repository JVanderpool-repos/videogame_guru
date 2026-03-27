from dotenv import load_dotenv
load_dotenv()

import os
import requests
from langchain_core.tools import tool
import chromadb
from chromadb.utils import embedding_functions
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver


# LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("GITHUB_TOKEN"),
    base_url="https://models.inference.ai.azure.com"
)


## tools

@tool
def search_game_info(game_title: str) -> str:
    """Search for a video game's details including rating, genres,
    platforms, and release date. Use when the user asks about a
    specific game's description, reviews, or general information."""
    try:
        params = {
            "key": os.getenv("RAWG_API_KEY"),
            "search": game_title,
            "page_size": 1
        }
        res = requests.get("https://api.rawg.io/api/games", params=params, timeout=10)
        res.raise_for_status()
        results = res.json().get("results", [])
        if not results:
            return f"No game found matching '{game_title}'."
        g = results[0]
        genres = ", ".join([x["name"] for x in g.get("genres", [])])
        platforms = ", ".join([x["platform"]["name"] for x in g.get("platforms", [])])
        
        result = f"**{g['name']}**\n\n"
        
        # Add cover image if available
        if g.get('background_image'):
            result += f"![{g['name']}]({g['background_image']})\n\n"
        
        result += (
            f"**Released:** {g.get('released', 'N/A')}\n"
            f"**Rating:** {g.get('rating', 'N/A')}/5\n"
            f"**Genres:** {genres}\n"
            f"**Platforms:** {platforms}\n"
            f"**Metacritic:** {g.get('metacritic', 'N/A')}"
        )
        return result
    except requests.exceptions.HTTPError as e:
        return f"RAWG API error: {str(e)}"
    except requests.exceptions.ConnectionError:
        return "Could not reach RAWG API. Check your connection."


@tool
def browse_current_deals() -> str:
    """Browse the best current PC game deals and sales happening right now 
    across all stores. Use when the user asks for "current deals", "sales", 
    "what's on sale", or "best deals" WITHOUT specifying a particular game. 
    Shows top discounted games sorted by savings percentage. PC only."""
    try:
        # Get current deals sorted by savings percentage
        res = requests.get(
            "https://www.cheapshark.com/api/1.0/deals",
            params={
                "sortBy": "Savings",
                "pageSize": 10,
                "onSale": 1
            },
            timeout=10
        )
        res.raise_for_status()
        deals = res.json()
        
        if not deals:
            return "No active PC game deals found right now. Try checking back later!"
        
        # Store name mapping
        store_map = {
            "1": "Steam", "7": "GOG", "8": "Origin", "11": "Humble", 
            "13": "Uplay", "15": "Fanatical", "23": "GameBillet",
            "25": "Epic", "27": "Gamesplanet"
        }
        
        output = "🔥 **Top PC Game Deals Right Now:**\n\n"
        
        for deal in deals[:10]:
            title = deal.get("title", "Unknown")
            sale_price = float(deal.get("salePrice", 0))
            normal_price = float(deal.get("normalPrice", 0))
            savings = float(deal.get("savings", 0))
            store_id = deal.get("storeID", "")
            store_name = store_map.get(store_id, "Store")
            
            output += f"**{title}**\n"
            output += f"${sale_price:.2f} ~~${normal_price:.2f}~~ ({savings:.0f}% off) - {store_name}\n\n"
        
        return output
        
    except requests.exceptions.ConnectionError:
        return "Could not reach CheapShark API. Try again shortly."
    except Exception as e:
        return f"Error fetching current deals: {str(e)}"


@tool
def get_game_deals(game_title: str) -> str:
    """Find current PC game prices and deals for a SPECIFIC game across Steam, 
    Epic Games, and GOG. Shows current prices from all stores, highlighting any 
    active discounts. Use when the user asks about a specific game's price or deals.
    IMPORTANT: Only works for PC games, NOT for PlayStation, Xbox, or Nintendo games."""
    try:
        # First, search for the game to get its ID
        search_res = requests.get(
            "https://www.cheapshark.com/api/1.0/games",
            params={"title": game_title, "limit": 1},
            timeout=10
        )
        search_res.raise_for_status()
        games = search_res.json()
        
        if not games:
            return f"No PC game found matching '{game_title}' in the price database."
        
        game = games[0]
        game_id = game["gameID"]
        game_name = game["external"]
        
        # Get detailed pricing info for all stores
        details_res = requests.get(
            f"https://www.cheapshark.com/api/1.0/games?id={game_id}",
            timeout=10
        )
        details_res.raise_for_status()
        game_details = details_res.json()
        
        # Store name mapping (complete list from CheapShark API)
        store_names = {
            "1": "Steam",
            "2": "GamersGate", 
            "3": "GreenManGaming",
            "4": "Amazon",
            "7": "GOG",
            "8": "Origin",
            "11": "Humble Store",
            "13": "Uplay",
            "15": "Fanatical",
            "21": "WinGameStore",
            "23": "GameBillet",
            "24": "Voidu",
            "25": "Epic Games Store",
            "27": "Gamesplanet",
            "30": "IndieGala",
            "33": "DLGamer"
        }
        
        # Priority order for displaying stores (show these first if available)
        priority_stores = ["1", "25", "7", "11", "15"]  # Steam, Epic, GOG, Humble, Fanatical
        
        deals = game_details.get("deals", [])
        if not deals:
            return f"No pricing information available for '{game_name}'."
        
        # Separate priority stores from others
        priority_deals = []
        other_deals = []
        
        for deal in deals:
            store_id = deal.get("storeID")
            if store_id in priority_stores and store_id in store_names:
                priority_deals.append((store_id, deal))
            elif store_id in store_names:
                other_deals.append((store_id, deal))
        
        # Combine: priority stores first, then others (limit to 8 total)
        all_deals = priority_deals + other_deals
        all_deals = all_deals[:8]
        
        if not all_deals:
            return f"No major store prices available for '{game_name}'."
        
        # Format output
        output = f"**{game_name}** - Current PC Prices:\n\n"
        
        for store_id, deal in all_deals:
            store_name = store_names[store_id]
            retail_price = float(deal.get("retailPrice", 0))
            sale_price = float(deal.get("price", 0))
            savings = float(deal.get("savings", 0))
            
            if savings > 0:
                output += f"🔥 **{store_name}**: ${sale_price:.2f} ~~${retail_price:.2f}~~ ({savings:.0f}% off)\n"
            else:
                output += f"**{store_name}**: ${sale_price:.2f}\n"
            
        return output
        
    except requests.exceptions.ConnectionError:
        return "Could not reach CheapShark API. Try again shortly."
    except Exception as e:
        return f"Error fetching prices: {str(e)}"


def get_igdb_token():
    res = requests.post("https://id.twitch.tv/oauth2/token", params={
        "client_id": os.getenv("IGDB_CLIENT_ID"),
        "client_secret": os.getenv("IGDB_CLIENT_SECRET"),
        "grant_type": "client_credentials"
    })
    return res.json()["access_token"]

@tool
def get_game_rankings(query: str) -> str:
    """Get top-rated or most popular games by genre, platform, or franchise.
    
    IMPORTANT: When calling this tool, preserve the platform name from the user's question in the query.
    Examples:
    - User asks "best PS5 games" -> call get_game_rankings("ps5 games") or get_game_rankings("best ps5 games")
    - User asks "top Xbox games" -> call get_game_rankings("top xbox games")
    - User asks "best RPGs" -> call get_game_rankings("best RPGs")
    
    The query parameter should include platform names (PS5, Xbox, Switch, etc.) when the user mentions them."""
    try:
        token = get_igdb_token()
        headers = {
            "Client-ID": os.getenv("IGDB_CLIENT_ID"),
            "Authorization": f"Bearer {token}"
        }

        # Map common keywords to IGDB genre/platform IDs
        genre_map = {
            "rpg": 12, "shooter": 5, "fighting": 4, "platformer": 8,
            "strategy": 15, "horror": 19, "adventure": 31, "sports": 14
        }
        # Order matters - check more specific terms first
        platform_keywords = [
            ("switch 2", 508),
            ("switch2", 508),
            ("xbox series x", 169),
            ("xbox series s", 169),
            ("xbox series", 169),
            ("xbox one", 49),
            ("xbox 360", 12),
            ("ps5", 167),
            ("ps4", 48),
            ("switch", 130),
            ("nintendo", 130),
            ("xbox", 169),  # Default to Series X|S for current gen
            ("pc", 6),
        ]

        query_lower = query.lower()
        genre_ids = [str(v) for k, v in genre_map.items() if k in query_lower]
        
        # Find platform IDs - check longer/more specific keywords first
        platform_ids = []
        for keyword, pid in platform_keywords:
            if keyword in query_lower:
                platform_ids.append(str(pid))
                break  # Use only the most specific match
        
        platform_ids = list(set(platform_ids))

        where_clauses = ["rating > 60", "total_rating_count > 5"]
        if genre_ids:
            where_clauses.append(f"genres = [{','.join(genre_ids)}]")
        if platform_ids:
            # For single platform, use direct value. For multiple, use OR logic
            if len(platform_ids) == 1:
                where_clauses.append(f"platforms = {platform_ids[0]}")
            else:
                platform_conditions = " | ".join([f"platforms = {pid}" for pid in platform_ids])
                where_clauses.append(f"({platform_conditions})")

        where = " & ".join(where_clauses)
        body = (
            f'fields name, rating, total_rating_count, genres.name, platforms.name, cover.url; '
            f'where {where}; '
            f'sort rating desc; '
            f'limit 5;'
        )

        res = requests.post(
            "https://api.igdb.com/v4/games",
            headers=headers,
            data=body,
            timeout=10
        )
        res.raise_for_status()
        games = res.json()

        if not games and platform_ids:
            # Fallback: Try finding ANY highly-rated games available on this platform
            # (not just exclusives) by using array syntax which allows multi-platform games
            where_clauses_fallback = ["rating > 80", "total_rating_count > 50"]
            if genre_ids:
                where_clauses_fallback.append(f"genres = [{','.join(genre_ids)}]")
            where_clauses_fallback.append(f"platforms = [{','.join(platform_ids)}]")
            
            where_fallback = " & ".join(where_clauses_fallback)
            body_fallback = (
                f'fields name, rating, total_rating_count, genres.name, platforms.name, cover.url; '
                f'where {where_fallback}; '
                f'sort rating desc; '
                f'limit 5;'
            )
            
            res_fallback = requests.post(
                "https://api.igdb.com/v4/games",
                headers=headers,
                data=body_fallback,
                timeout=10
            )
            games = res_fallback.json()
            
            if games:
                output = f"Top-rated games available on this platform (including multi-platform titles):\n\n"
                for g in games:
                    rating = round(g.get("rating", 0), 1)
                    genres = ", ".join([x["name"] for x in g.get("genres", [])])
                    platforms = ", ".join([x["name"] for x in g.get("platforms", [])][:4])
                    if len(g.get("platforms", [])) > 4:
                        platforms += "..."
                    
                    # Add cover image if available
                    cover = g.get('cover', {})
                    if cover and cover.get('url'):
                        cover_url = "https:" + cover['url'].replace('t_thumb', 't_cover_big')
                        output += f"![{g['name']}]({cover_url})\n\n"
                    
                    output += f"**{g['name']}** | Rating: {rating}/100 | Genres: {genres} | Platforms: {platforms}\n\n"
                return output

        if not games:
            # Still no results even after fallback
            platform_name = ""
            if "xbox series" in query_lower:
                platform_name = "Xbox Series X|S"
            elif "ps5" in query_lower:
                platform_name = "PlayStation 5"
            elif "switch 2" in query_lower:
                platform_name = "Nintendo Switch 2"
            
            if platform_name:
                return (f"I couldn't find games for {platform_name} in the rankings database. "
                       f"This platform might be too new or have limited data. "
                       f"Try asking about a specific game title instead, and I can look up its details!")
            return f"No highly rated results found for '{query}'. Try being more specific or ask about a particular game title."

        output = f"Top results for '{query}':\n\n"
        for g in games:
            rating = round(g.get("rating", 0), 1)
            genres = ", ".join([x["name"] for x in g.get("genres", [])])
            platforms = ", ".join([x["name"] for x in g.get("platforms", [])][:4])  # Show first 4 platforms
            if len(g.get("platforms", [])) > 4:
                platforms += "..."
            
            # Add cover image if available
            cover = g.get('cover', {})
            if cover and cover.get('url'):
                cover_url = "https:" + cover['url'].replace('t_thumb', 't_cover_big')
                output += f"![{g['name']}]({cover_url})\n\n"
            
            output += f"**{g['name']}** | Rating: {rating}/100 | Genres: {genres} | Platforms: {platforms}\n\n"
        return output

    except Exception as e:
        return f"IGDB error: {str(e)}"



## ChromaDB setup
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("vgsales", embedding_function=ef)


@tool
def search_sales_history(query: str) -> str:
    """Search historical video game sales data (1980-2020) including global sales,
    regional sales, critic scores, and user scores for platforms like PS4, Xbox One,
    PS3, Xbox 360, Wii, original Nintendo Switch, and older. IMPORTANT: This database 
    does NOT include PS5, Xbox Series X/S, Nintendo Switch 2, or games released after 2020. 
    For newer platforms/games, you MUST use get_game_rankings or search_game_info instead."""
    try:
        results = collection.query(query_texts=[query], n_results=5)
        docs = results["documents"][0]
        if not docs:
            return "No sales data found for that query in the historical database (1980-2020)."
        return "Historical sales data (1980-2020):\n" + "\n".join(f"- {d}" for d in docs)
    except Exception as e:
        return f"Vector search error: {str(e)}"


tools = [search_game_info, get_game_deals, browse_current_deals, get_game_rankings, search_sales_history]

memory = MemorySaver()

agent_with_memory = create_agent(
    model=llm,
    tools=tools,
    checkpointer=memory,
    system_prompt="""You are Videogame Guru, an expert AI assistant for all things video games.
    You help users find games they'll love, check deals, explore sales history, and get rankings.
    Be enthusiastic, knowledgeable, and conversational.
    
    CRITICAL RULES:
    1. ALWAYS use your tools to answer questions. Never just ask clarifying questions without trying tools first.
    2. ONLY provide information that comes directly from your tools. DO NOT add games, facts, or details from your training data.
    3. If a tool returns results, use ONLY those results. Do not supplement with additional games or information.
    4. When tools return game cover images in markdown format (![title](url)), preserve them EXACTLY as-is in your response.
    
    Tool usage guidelines:
    - For "best", "top", "popular" games -> use get_game_rankings immediately
    - For general PC "deals", "sales", "what's on sale" (no specific game) -> use browse_current_deals
    - For specific game PC pricing (e.g., "Elden Ring price") -> use get_game_deals with game title
    - For console deals -> explain deals tool is PC-only, then use get_game_rankings for top games
    - For specific game info -> use search_game_info immediately
    - For historical sales (pre-2021, PS4/Xbox360/Wii/Switch 1/etc) -> use search_sales_history
    
    Your historical sales database: 1980-2020 only (PS4, Xbox One, original Switch, PS3, Wii, etc).
    Does NOT include: PS5, Xbox Series X/S, Switch 2, or games after 2020.
    
    For modern platforms (PS5, Xbox Series X, Switch 2, or 2021+ games): Use get_game_rankings and search_game_info.
    
    When users ask vague questions: Make reasonable assumptions and use tools proactively. 
    Example: "Switch 2 games" -> use get_game_rankings("switch 2 games")
    Example: "Switch games" -> use get_game_rankings("nintendo switch")
    Example: "top deals" -> use browse_current_deals()
    Example: "Skyrim price" -> use get_game_deals("Skyrim")
    
    IMPORTANT: Never make up data or add information not provided by tools. If tools return no results, 
    say so clearly and suggest alternatives. Do not supplement tool results with your own knowledge."""
)


if __name__ == "__main__":
    print("=== RAWG ===")
    print(search_game_info.invoke("Elden Ring"))
    print("\n=== Browse Current Deals ===")
    print(browse_current_deals.invoke({}))
    print("\n=== CheapShark (Specific Game) ===")
    print(get_game_deals.invoke("Elden Ring"))
    print("\n=== IGDB ===")
    print(get_game_rankings.invoke("open world RPG"))
    print("\n=== ChromaDB ===")
    print(search_sales_history.invoke("best selling Nintendo games"))
    print("\n=== AGENT TEST ===")
    config = {"configurable": {"thread_id": "test"}}
    response = agent_with_memory.invoke(
        {"messages": [("user", "What is Elden Ring and is it on sale anywhere?")]},
        config=config
    )
    print(response["messages"][-1].content)
    print("\n=== MEMORY TEST ===")
    response2 = agent_with_memory.invoke(
        {"messages": [("user", "What platforms did you just tell me it's on?")]},
        config=config
    )
    print(response2["messages"][-1].content)
