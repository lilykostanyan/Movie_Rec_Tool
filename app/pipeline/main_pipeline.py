import asyncio
import shutil
from scrape_tt_codes import run_scraper
from extract_movie_data import run_crawler
from split_movie_data import split_movie_xlsx
from drive_upload import upload_metadata_to_drive
from bigquery_upload import upload_single_file_to_bigquery
from clean_synopsis import clean_romance_synopsis
from chunk_and_embed import run_chunk_and_embed_pipeline
from config import JSONS_FOLDER, TSV_FILENAME
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.utils.logger import logger

# === MAIN EXECUTION ===
logger.info("- Pipeline Launching...")

def run_pipeline():
    """
    Executes the main pipeline for processing IMDb movie data. The pipeline consists of the following steps:
    1. Scrape IMDb tt codes.
    2. Scrape movie metadata and synopsis.
    3. Split combined CSV into metadata and synopsis files.
    4. Upload metadata to Google Drive.
    5. Upload metadata from Google Drive to BigQuery.
    6. Clean synopsis data.
    7. Chunk and embed synopsis data.
    8. Move the resulting ZIP file to the `etl/data/jsons/` directory.
    """
    # Step 1: Scrape tt codes
    logger.info("- Step 1: Scraping tt codes from IMDb...")
    run_scraper()

    # Step 2: Scrape movie metadata and synopsis
    logger.info("- Step 2: Scraping movie metadata and synopsis...")
    asyncio.run(run_crawler(
        output_dir="imdb_data",
        num_movies=0
    ))

    # Step 3: Clean full data
    logger.info("- Step 3: Cleaning synopsis data...")
    clean_romance_synopsis(
        input_csv=None,
        output_csv=None
    )

    # Step 4: Split combined XLSX into metadata + synopsis
    logger.info("- Step 4: Splitting movie data into metadata and synopsis files...")
    metadata_path, synopsis_path = split_movie_xlsx()

    # Step 5: Upload metadata to Google Drive
    logger.info("- Step 5: Uploading metadata Excel to Google Drive...")
    upload_metadata_to_drive(file_path=None, file_name=None)

    # Step 6: Upload metadata from Drive to BigQuery
    logger.info("- Step 6: Uploading metadata from Drive to BigQuery...")
    upload_single_file_to_bigquery(
        target_file_name=None,
        dataset_id="romance_dataset",
        table_name="full_data_table"
    )

    # Step 7: Chunk and embed
    logger.info("- Step 7: Chunking and embedding synopsis...")
    run_chunk_and_embed_pipeline(
        input_excel=None,
        output_dir=None
    )

    # Step 7.5: Move ZIP to etl/data/jsons/
    src_zip = f"{JSONS_FOLDER}.zip"
    dst_zip = "../etl/data/jsons/" + src_zip

    # Ensure the destination directory exists and move the ZIP file
    os.makedirs("../etl/data/jsons", exist_ok=True)
    shutil.move(src_zip, dst_zip)
    logger.info(f"- Moved ZIP to: {dst_zip}")

    # === CLEANUP ===
    try:
        # Delete romance_newbatch.tsv
        if os.path.exists(TSV_FILENAME):
            os.remove(TSV_FILENAME)
            logger.info(f"- Removed file: {TSV_FILENAME}")

        # Delete imdb_data/ folder
        if os.path.exists("imdb_data"):
            shutil.rmtree("imdb_data")
            logger.info("- Removed folder: imdb_data/")

        # Delete romance_chunks_json/ folder
        if os.path.exists(JSONS_FOLDER):
            shutil.rmtree(JSONS_FOLDER)
            logger.info(f"- Removed folder: {JSONS_FOLDER}/")

    except Exception as e:
        logger.warning(f"- Cleanup issue: {e}")

    # Log pipeline completion
    logger.info("- Pipeline execution complete!")

if __name__ == "__main__":
    run_pipeline()