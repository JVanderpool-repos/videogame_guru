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
        return (
            f"Title: {g['name']}\n"
            f"Released: {g.get('released', 'N/A')}\n"
            f"Rating: {g.get('rating', 'N/A')}/5\n"
            f"Genres: {genres}\n"
            f"Platforms: {platforms}\n"
            f"Metacritic: {g.get('metacritic', 'N/A')}"
        )
    except requests.exceptions.HTTPError as e:
        return f"RAWG API error: {str(e)}"
    except requests.exceptions.ConnectionError:
        return "Could not reach RAWG API. Check your connection."


@tool
def get_game_deals(game_title: str) -> str:
    """Find current PC game deals and lowest prices across Steam,
    Epic Games, and GOG. IMPORTANT: Only works for PC games, NOT for
    PlayStation, Xbox, or Nintendo games. Use when the user asks about
    PC game pricing, discounts, or sales."""
    try:
        res = requests.get(
            "https://www.cheapshark.com/api/1.0/deals",
            params={"title": game_title, "pageSize": 3, "sortBy": "Price"},
            timeout=10
        )
        res.raise_for_status()
        deals = res.json()
        if not deals:
            return f"No current deals found for '{game_title}'."
        output = f"Current deals for '{game_title}':\n"
        for d in deals:
            output += (
                f"- {d['title']}: ${d['salePrice']} "
                f"(normal ${d['normalPrice']}, "
                f"{float(d['savings']):.0f}% off)\n"
            )
        return output
    except requests.exceptions.ConnectionError:
        return "Could not reach CheapShark API. Try again shortly."


def get_igdb_token():
    res = requests.post("https://id.twitch.tv/oauth2/token", params={
        "client_id": os.getenv("IGDB_CLIENT_ID"),
        "client_secret": os.getenv("IGDB_CLIENT_SECRET"),
        "grant_type": "client_credentials"
    })
    return res.json()["access_token"]

@tool
def get_game_rankings(query: str) -> str:
    """Get top-rated or most popular games by genre, platform, or
    franchise. Use for questions like 'best RPGs', 'top Nintendo
    games', or 'most popular games of all time'."""
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
            f'fields name, rating, total_rating_count, genres.name, platforms.name; '
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
                f'fields name, rating, total_rating_count, genres.name, platforms.name; '
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
                output = f"Top-rated games available on this platform (including multi-platform titles):\n"
                for g in games:
                    rating = round(g.get("rating", 0), 1)
                    genres = ", ".join([x["name"] for x in g.get("genres", [])])
                    platforms = ", ".join([x["name"] for x in g.get("platforms", [])][:4])
                    if len(g.get("platforms", [])) > 4:
                        platforms += "..."
                    output += f"- {g['name']} | Rating: {rating}/100 | Genres: {genres} | Platforms: {platforms}\n"
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

        output = f"Top results for '{query}':\n"
        for g in games:
            rating = round(g.get("rating", 0), 1)
            genres = ", ".join([x["name"] for x in g.get("genres", [])])
            platforms = ", ".join([x["name"] for x in g.get("platforms", [])][:4])  # Show first 4 platforms
            if len(g.get("platforms", [])) > 4:
                platforms += "..."
            output += f"- {g['name']} | Rating: {rating}/100 | Genres: {genres} | Platforms: {platforms}\n"
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


tools = [search_game_info, get_game_deals, get_game_rankings, search_sales_history]

memory = MemorySaver()

agent_with_memory = create_agent(
    model=llm,
    tools=tools,
    checkpointer=memory,
    system_prompt="""You are Videogame Guru, an expert AI assistant for all things video games.
    You help users find games they'll love, check deals, explore sales history, and get rankings.
    Be enthusiastic, knowledgeable, and conversational.
    
    CRITICAL: ALWAYS use your tools to answer questions. Never just ask clarifying questions without trying tools first.
    
    Tool usage guidelines:
    - For "best", "top", "popular" games -> use get_game_rankings immediately
    - For PC game "deals", "sale", "cheap", "price" -> use get_game_deals (PC ONLY)
    - For console deals -> explain deals tool is PC-only, then use get_game_rankings for top games
    - For specific game info -> use search_game_info immediately
    - For historical sales (pre-2021, PS4/Xbox360/Wii/Switch 1/etc) -> use search_sales_history
    
    Your historical sales database: 1980-2020 only (PS4, Xbox One, original Switch, PS3, Wii, etc).
    Does NOT include: PS5, Xbox Series X/S, Switch 2, or games after 2020.
    
    For modern platforms (PS5, Xbox Series X, Switch 2, or 2021+ games): Use get_game_rankings and search_game_info.
    
    When users ask vague questions: Make reasonable assumptions and use tools proactively. 
    Example: "Switch 2 games" -> use get_game_rankings("switch 2 games")
    Example: "Switch games" -> use get_game_rankings("nintendo switch")
    
    Never make up data. If tools return no results, say so clearly and suggest alternatives."""
)


if __name__ == "__main__":
    print("=== RAWG ===")
    print(search_game_info.invoke("Elden Ring"))
    print("\n=== CheapShark ===")
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
