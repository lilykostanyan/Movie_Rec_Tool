import os
import time
import json
from config import get_elasticsearch, INDEX_NAME, VECTOR_DIM, TO_INSERT_DIR
from utils.logger import logger

logger.info("- ETL Launching...")

# === CONNECT TO ELASTICSEARCH ===
def connect_to_elasticsearch(retries: int = 10, delay: int = 2):
    """
    Attempts to connect to Elasticsearch with retry logic.

    Args:
        retries (int): Number of retry attempts.
        delay (int): Delay in seconds between attempts.

    Returns:
        Elasticsearch: An instance of the Elasticsearch client.

    Raises:
        ConnectionError: If connection fails after all attempts.
    """
    for i in range(retries):
        try:
            es = get_elasticsearch()
            version = es.info()["version"]["number"]
            logger.info(f"- Connected to Elasticsearch {version}")
            return es
        except Exception as e:
            logger.info(f"- Attempt {i+1}/{retries}: {e}")
            time.sleep(delay)
    raise ConnectionError("- Elasticsearch did not become ready in time")

# === CREATE INDEX ===
def create_index(es):
    """
    Creates an Elasticsearch index with the required mappings if it doesn't exist.

    Args:
        es (Elasticsearch): Elasticsearch client.
    """
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(
            index=INDEX_NAME,
            mappings={
                "properties": {
                    "movie_id": {"type": "keyword"},  # Unique identifier for the movie
                    "genres": {"type": "keyword"},  # List of genres associated with the movie
                    "type": {"type": "keyword"},  # Type of text (e.g., "short", "summary", "long")   
                    "chunk_id": {"type": "keyword"},  # Identifier for text chunks
                    "text": {"type": "text"},  # Text content of the document
                    "vector": {
                        "type": "dense_vector",  # Dense vector for similarity search
                        "dims": VECTOR_DIM,  # Dimensionality of the vector
                        "index": True,  # Enable indexing for the vector
                        "similarity": "cosine"  # Use cosine similarity for vector comparison
                    }
                }
            }
        )
        logger.info(f"- Created index: {INDEX_NAME}")
    else:
        logger.info(f"- Index '{INDEX_NAME}' already exists")

# === UPLOAD JSON FILES ===
def upload_documents(es):
    """
    Uploads JSON documents from the `TO_INSERT_DIR` to Elasticsearch.

    Args:
        es (Elasticsearch): Elasticsearch client.
    """
    uploaded_count = 0
    for filename in os.listdir(TO_INSERT_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(TO_INSERT_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    es.index(index=INDEX_NAME, id=filename, document=data)
                    uploaded_count += 1
            except Exception as e:
                logger.info(f"- Failed to upload {filename}: {e}")
    logger.info(f"- Uploaded {uploaded_count} JSON file(s) to index '{INDEX_NAME}'")

logger.info("- ETL Ready! ...")