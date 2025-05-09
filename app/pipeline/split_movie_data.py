import pandas as pd
from config import MOVIE_METADATA_FILE, MOVIE_SYNOPSIS_FILE, CLEANED_OUTPUT_FILE
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.utils.logger import logger

def split_movie_xlsx(input_csv=None, output_dir="imdb_data"):
    """
    Splits an XLSX file containing movie data into two separate files:
    one for metadata and another for synopsis.

    Args:
        input_csv (str): Path to the input CSV file containing movie data.
        output_dir (str): Directory where the output files will be saved.
                          Defaults to "imdb_data".

    Returns:
        tuple: A tuple containing the paths to the metadata and synopsis files.
               (metadata_path, synopsis_path)
    """
    if input_csv is None:
        input_csv = f"{output_dir}/{CLEANED_OUTPUT_FILE}"
    # Read the input CSV file into a DataFrame
    df = pd.read_csv(input_csv)

    # Define the columns to be included in the metadata file
    metadata_cols = [
        'tconst',          # Unique identifier for the movie
        'movie_title',     # Title of the movie
        'movie_year',      # Release year of the movie
        'age_rating',      # Age rating of the movie
        'duration',        # Duration of the movie
        'imdb_rating',     # IMDb rating of the movie
        'top_5_actors',    # List of top 5 actors in the movie
        'poster_url'       # URL of the movie's poster
    ]

    # Define the columns to be included in the synopsis file
    synopsis_cols = [
        'tconst',          # Unique identifier for the movie
        'genres',          # List of genres associated with the movie
        'short_synopsis',  # Short synopsis of the movie
        'summaries',       # List of summaries for the movie
        'long_synopsis'    # Detailed synopsis of the movie
    ]

    # Create separate DataFrames for metadata and synopsis
    metadata_df = df[metadata_cols].copy()
    synopsis_df = df[synopsis_cols].copy()

    # Define the output file paths
    metadata_path = f"{output_dir}/{MOVIE_METADATA_FILE}"
    synopsis_path = f"{output_dir}/{MOVIE_SYNOPSIS_FILE}"

    # Save the metadata DataFrame to an Excel file
    metadata_df.to_excel(metadata_path, index=False)

    # Save the synopsis DataFrame to a CSV file
    synopsis_df.to_excel(synopsis_path, index=False)

    # Log the paths of the saved files
    logger.info(f"- Saved metadata to: {metadata_path}")
    logger.info(f"- Saved synopsis to: {synopsis_path}")

    # Return the paths of the saved files
    return metadata_path, synopsis_path