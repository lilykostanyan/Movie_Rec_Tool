import streamlit as st
import requests
import google.generativeai as genai
from config import GEMINI_API_KEY, BACKEND_URL
import ast
import re

def gemini_recommendation(query: str, num_recs: int) -> str:
    """
    Generates movie recommendations using the Gemini Generative AI model.

    Args:
        query (str): The input query describing the type of story or movie.
        num_recs (int): The number of movie recommendations to generate.

    Returns:
        str: The generated text containing movie recommendations.
    """
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"Suggest {num_recs} movies that match this kind of story:\n{query}"
    response = model.generate_content(prompt)
    return response.text

def custom_model_recommendation(query: str, num_recs: int, use_filter: bool,
                                selected_genres: list, filtering_mode: str) -> dict:
    """
    Fetches movie recommendations from a custom backend model.

    Args:
        query (str): The input query describing the type of story or movie.
        num_recs (int): The number of movie recommendations to generate.
        use_filter (bool): Whether to apply genre-based filtering.
        selected_genres (list): List of genres to filter the recommendations by.
        filtering_mode (str): The filtering mode ('strict' or 'relaxed').

    Returns:
        dict: The JSON response from the backend containing movie recommendations.
    """
    payload = {
        "query": query,
        "use_genre_filter": use_filter,
        "selected_genres": selected_genres,
        "filtering_mode": filtering_mode,
        "num_recs": num_recs
    }

    response = requests.post(f"{BACKEND_URL}/recommend_movies", json=payload)
    return response.json()

def format_runtime(runtime_str):
    """
    Formats a runtime string by normalizing 'hours' and 'minutes' into a consistent format.

    Args:
        runtime_str (str): The runtime string to format.

    Returns:
        str: The formatted runtime string, or 'N/A' if the input is empty or not a string.
    """
    if not runtime_str or not isinstance(runtime_str, str):
        return "N/A"

    # Normalize both "hour" and "hours" into one consistent format
    runtime_str = re.sub(r"(\d+)\s*hours?", r"\1 hours ", runtime_str)
    runtime_str = re.sub(r"(\d+)\s*minutes?", r"\1 minutes ", runtime_str)

    return runtime_str.strip()

def display_movie(movie: dict) -> None:
    """
    Displays movie details in a Streamlit app with emojis and clean formatting.

    Args:
        movie (dict): A dictionary containing movie details such as title, year, genres,
                      IMDb rating, age rating, duration, top actors, poster URL, and preview chunks.

    Returns:
        None
    """
    st.markdown(f"### 🎬 {movie.get('title', 'Unknown')} ({movie.get('year', 'N/A')})")
    st.markdown(f"**Genres:** {', '.join(movie.get('genres', []))}")

    imdb = movie.get("imdb_rating", "N/A")
    rating = movie.get("age_rating", "N/A")
    runtime = format_runtime(movie.get("duration", ""))

    st.markdown(f"⭐️ IMDb: {imdb} &nbsp;&nbsp;&nbsp; 🔞 Rating: {rating} &nbsp;&nbsp;&nbsp; 🕒 Runtime: {runtime}")

    # Actor list cleanup
    raw_actors = movie.get("top_actors", [])
    try:
        if isinstance(raw_actors, str):
            actors = ast.literal_eval(raw_actors)
        else:
            actors = raw_actors
        actor_str = ", ".join(actors)
    except Exception:
        actor_str = "N/A"
    st.markdown(f"🎭 Top Actors: {actor_str}")

    if movie.get("poster_url"):
        st.image(movie["poster_url"], width=150)

    st.markdown("📖 **Preview:**")
    for chunk in movie.get("preview_chunks", []):
        st.markdown(f"*({chunk.get('type', 'N/A')})* {chunk.get('text', '')}")

    st.markdown("---")