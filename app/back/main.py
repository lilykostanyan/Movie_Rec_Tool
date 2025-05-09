from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Literal
from google.cloud import bigquery
import numpy as np
from collections import defaultdict
import re
import os
from dotenv import load_dotenv
import warnings
from config import (
    get_elasticsearch,
    get_sentence_transformer,
    get_bigquery_client,
    ES_INDEX,
    TOP_K,
    BQ_TABLE
)
from utils.logger import logger

# Load environment variables from a .env file
load_dotenv()

logger.info("- Back Launching...")

# Suppress warnings related to BigQuery Storage module not found
warnings.filterwarnings(
    "ignore",
    message="BigQuery Storage module not found, fetch data with the REST endpoint instead.",
    category=UserWarning,
)

# Parse genre options from environment variables
GENRE_OPTIONS = [g.strip() for g in os.getenv("GENRE_OPTIONS").split(",") if g]

# === FASTAPI APP ===
app = FastAPI()

@app.get("/")
def root():
    """
    Root endpoint to check if the API is running.

    Returns:
        dict: A message indicating the API is running.
    """
    return {"message": "- API is running. Use /docs to test."}

# === ELASTICSEARCH, MODEL, BQ CLIENT ===
# Initialize Elasticsearch client
es = get_elasticsearch()
# Load the sentence transformer model
model = get_sentence_transformer()
# Initialize BigQuery client
bq = get_bigquery_client()

# === INPUT MODEL ===
class MovieRequest(BaseModel):
    """
    Represents the request body for the movie recommendation endpoint.

    Attributes:
        query (str): The search query for movie recommendations.
        use_genre_filter (bool): Whether to filter results by genre.
        selected_genres (Optional[List[str]]): List of genres to filter by.
        filtering_mode (Optional[Literal["strict", "relaxed"]]): Mode for genre filtering.
        num_recs (int): Number of recommendations to return.
    """
    query: str
    use_genre_filter: bool = False
    selected_genres: Optional[List[str]] = []
    filtering_mode: Optional[Literal["strict", "relaxed"]] = "strict"
    num_recs: int = 5

# === UTILITY ===
def chunk_sort_key(chunk_id):
    """
    Generates a sorting key for chunk IDs based on their type and numerical order.

    Args:
        chunk_id (str): The chunk ID to generate a sort key for.

    Returns:
        tuple: A tuple containing the type order and numerical components of the chunk ID.
    """
    parts = chunk_id.split("-")
    type_order = {"sh": 0, "short": 0, "summary": 1, "lon": 2, "long": 2}
    type_val = type_order.get(parts[1], 99)
    secondary = list(map(int, re.findall(r"\d+", "-".join(parts[2:]))))
    return (type_val, *secondary)

# === ENDPOINT ===
@app.post("/recommend_movies")
def recommend_movies(request: MovieRequest):
    """
    Recommends movies based on a query and optional genre filters.

    Args:
        request (MovieRequest): The request body containing query and filter options.

    Returns:
        dict: A dictionary containing the recommended movies and their metadata.
    """
    query_vector = model.encode(request.query).tolist()

    # Construct the Elasticsearch query
    query_filter = []
    if request.use_genre_filter and request.selected_genres:
        query_filter.append({"terms": {"genres": request.selected_genres}})

    search_body = {
        "size": TOP_K,
        "_source": ["movie_id", "chunk_id", "text", "type", "genres"],
        "query": {
            "script_score": {
                "query": {
                    "bool": {
                        "should": [{"match": {"text": request.query}}],
                        "filter": query_filter
                    }
                },
                "script": {
                    "source": "0.3 * _score + 0.7 * cosineSimilarity(params.query_vector, 'vector') + 1.0",
                    "params": {"query_vector": query_vector}
                }
            }
        }
    }

    # Execute the search query
    res = es.search(index=ES_INDEX, body=search_body)

    movie_scores = defaultdict(list)
    chunk_meta = defaultdict(list)

    for hit in res["hits"]["hits"]:
        doc = hit["_source"]
        movie_id = doc["movie_id"]
        score = hit["_score"]
        movie_scores[movie_id].append(score)
        chunk_meta[movie_id].append({
            "chunk_id": doc["chunk_id"],
            "text": doc["text"],
            "type": doc["type"],
            "score": score,
            "genres": doc.get("genres", [])
        })

    avg_scores = {m: np.mean(s) for m, s in movie_scores.items()}
    top_movie_ids = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)[:request.num_recs]
    top_movie_ids = [mid for mid, _ in top_movie_ids]

    if not top_movie_ids:
        return {"results": []}

    # Fetch metadata from BigQuery
    query_str = f"""
    SELECT
      tconst AS movie_id,
      ANY_VALUE(movie_title) AS movie_title,
      ANY_VALUE(movie_year) AS movie_year,
      ANY_VALUE(age_rating) AS age_rating,
      ANY_VALUE(duration) AS duration,
      ANY_VALUE(imdb_rating) AS imdb_rating,
      ANY_VALUE(top_5_actors) AS top_5_actors,
      ANY_VALUE(poster_url) AS poster_url
    FROM {BQ_TABLE}
    WHERE tconst IN UNNEST(@movie_ids)
    GROUP BY movie_id
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ArrayQueryParameter("movie_ids", "STRING", top_movie_ids)]
    )
    genre_df = bq.query(query_str, job_config=job_config).to_dataframe()
    title_map = dict(zip(genre_df["movie_id"], genre_df["movie_title"]))
    meta_map = genre_df.set_index("movie_id").to_dict(orient="index")

    # Filter by genres
    filtered_movie_ids = []
    if request.use_genre_filter and request.selected_genres:
        selected_genres_set = set(g.strip().lower() for g in request.selected_genres)
        for movie_id in top_movie_ids:
            all_genres = set()
            for chunk in chunk_meta[movie_id]:
                all_genres.update(chunk.get("genres", []))
            all_genres_set = set(g.strip().lower() for g in all_genres)
            if request.filtering_mode == "relaxed":
                if selected_genres_set & all_genres_set:
                    filtered_movie_ids.append(movie_id)
            else:
                if selected_genres_set.issubset(all_genres_set):
                    filtered_movie_ids.append(movie_id)
    else:
        filtered_movie_ids = top_movie_ids

    # Fallback: return top results even if none match genres
    if request.use_genre_filter and not filtered_movie_ids:
        filtered_movie_ids = top_movie_ids

    # Prepare the final results
    results = []
    for movie_id in filtered_movie_ids:
        chunks = chunk_meta[movie_id]
        sorted_chunks = sorted(chunks, key=lambda x: chunk_sort_key(x["chunk_id"]))
        genres = sorted(set(g for chunk in chunks for g in chunk.get("genres", [])))
        meta = meta_map.get(movie_id, {})
        top_actors = meta.get("top_5_actors", "")
        top_actors = ", ".join([a.strip() for a in top_actors.split(",")]) if top_actors else "Actors not found"
        result = {
            "movie_id": movie_id,
            "title": title_map.get(movie_id, "Unknown Title"),
            "year": meta.get("movie_year", "Year not found"),
            "age_rating": meta.get("age_rating", "Rating not found"),
            "duration": meta.get("duration", "Duration not found"),
            "imdb_rating": meta.get("imdb_rating", "IMDb rating not found"),
            "top_actors": top_actors,
            "poster_url": meta.get("poster_url", "Poster URL not found"),
            "genres": genres,
            "preview_chunks": [
                {
                    "type": chunk["type"],
                    "text": chunk["text"][:300] + "..."
                }
                for chunk in sorted_chunks[:3]
            ]
        }
        results.append(result)

    return {"results": results}

logger.info("- Back Ready! ...")