import os
import json
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

# Load .env
load_dotenv()

# === Config ===
ES_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
INDEX_NAME = "movies-bm25-vector"

# Connect to Elasticsearch
es = Elasticsearch(ES_URL)
if not es.ping():
    raise ConnectionError("Failed to connect to Elasticsearch")

# Create index if it doesn't exist
if not es.indices.exists(index=INDEX_NAME):
    es.indices.create(
        index=INDEX_NAME,
        mappings={
            "properties": {
                "movie_id": {"type": "keyword"},
                "genres": {"type": "keyword"},
                "type": {"type": "keyword"},
                "chunk_id": {"type": "keyword"},
                "text": {"type": "text"},
                "vector": {
                    "type": "dense_vector",
                    "dims": 768,
                    "index": True,
                    "similarity": "cosine"
                }
            }
        }
    )
    print(f"✅ Created index: {INDEX_NAME}")
else:
    print(f"ℹ️ Index '{INDEX_NAME}' already exists")

# Load and upload all JSON files in the current directory
json_dir = os.path.dirname(__file__)
for filename in os.listdir(json_dir):
    if filename.endswith(".json"):
        filepath = os.path.join(json_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                es.index(index=INDEX_NAME, document=data)
                print(f"📤 Uploaded {filename}")
        except Exception as e:
            print(f"❌ Failed to upload {filename}: {e}")