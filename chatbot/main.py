from dotenv import load_dotenv
load_dotenv()

import os
import requests
from langchain_core.tools import tool
import chromadb
from chromadb.utils import embedding_functions

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
    Epic Games, and GOG. Use when the user asks about pricing,
    discounts, sales, or where to buy a game cheaply."""
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
        body = f'search "{query}"; fields name,rating,total_rating_count,summary; limit 5;'
        res = requests.post(
            "https://api.igdb.com/v4/games",
            headers=headers,
            data=body,
            timeout=10
        )
        res.raise_for_status()
        games = res.json()
        if not games:
            return f"No results found for '{query}'."
        output = f"IGDB results for '{query}':\n"
        for g in games:
            rating = round(g.get("rating", 0), 1)
            output += f"- {g['name']} | Rating: {rating}/100\n"
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
    """Search historical video game sales data including global sales,
    regional sales, critic scores, and user scores. Use when the user
    asks about best-selling games, sales figures, or wants to compare
    commercial performance of titles."""
    try:
        results = collection.query(query_texts=[query], n_results=5)
        docs = results["documents"][0]
        if not docs:
            return "No sales data found for that query."
        return "Historical sales data:\n" + "\n".join(f"- {d}" for d in docs)
    except Exception as e:
        return f"Vector search error: {str(e)}"


if __name__ == "__main__":
    print("=== RAWG ===")
    print(search_game_info.invoke("Elden Ring"))
    print("\n=== CheapShark ===")
    print(get_game_deals.invoke("Elden Ring"))
    print("\n=== IGDB ===")
    print(get_game_rankings.invoke("open world RPG"))
    print("\n=== ChromaDB ===")
    print(search_sales_history.invoke("best selling Nintendo games"))



