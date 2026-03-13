from dotenv import load_dotenv
load_dotenv()

import os
import requests
from langchain.tools import tool

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

if __name__ == "__main__":
    print(search_game_info.invoke("Elden Ring"))
