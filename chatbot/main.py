from dotenv import load_dotenv
load_dotenv()

import os
import requests
from langchain_core.tools import tool

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

if __name__ == "__main__":
    print("=== RAWG ===")
    print(search_game_info.invoke("Elden Ring"))
    print("\n=== CheapShark ===")
    print(get_game_deals.invoke("Elden Ring"))

