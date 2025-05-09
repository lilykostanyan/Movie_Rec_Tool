import os
import time
import json
from config import get_elasticsearch, INDEX_NAME, VECTOR_DIM, TO_INSERT_DIR
from utils.logger import logger

logger.info("- ETL Launching...")

# === CONNECT TO ELASTICSEARCH ===
# Attempt to connect to the Elasticsearch instance up to 10 times.
# Logs the connection status and raises a ConnectionError if unsuccessful.
for i in range(10):
    try:
        es = get_elasticsearch()
        version = es.info()["version"]["number"]
        logger.info(f"- Connected to Elasticsearch {version}")
        break
    except Exception as e:
        logger.info(f"- Attempt {i+1}/10: {e}")
        time.sleep(2)
else:
    raise ConnectionError("- Elasticsearch did not become ready in time")

# === CREATE INDEX ===
# Check if the Elasticsearch index specified by `INDEX_NAME` exists.
# If it does not exist, create the index with the specified mappings.
# The mappings include fields for movie metadata and a dense vector for similarity search.
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
# Iterate through all JSON files in the directory specified by `TO_INSERT_DIR`.
# Upload the contents of each file to the Elasticsearch index.
# Logs the number of successfully uploaded files and any errors encountered.
uploaded_count = 0

for filename in os.listdir(TO_INSERT_DIR):
    if filename.endswith(".json"):  # Process only JSON files
        filepath = os.path.join(TO_INSERT_DIR, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)  # Load JSON data from the file
                doc_id = filename  # Use the filename as the unique document ID
                es.index(index=INDEX_NAME, id=doc_id, document=data)  # Index the document in Elasticsearch
                uploaded_count += 1
        except Exception as e:
            logger.info(f"- Failed to upload {filename}: {e}")

logger.info(f"- Uploaded {uploaded_count} JSON file(s) to index '{INDEX_NAME}'")

logger.info("- ETL Ready! ...")