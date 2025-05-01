import os
import time
import json
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# === Config ===
ES_URL = os.getenv("ELASTICSEARCH_URL")
print("DEBUG: ELASTICSEARCH_URL =", ES_URL)
print("DEBUG: ELASTICSEARCH_URL =", os.getenv("ELASTICSEARCH_URL"))
INDEX_NAME = os.getenv("INDEX_NAME")
VECTOR_DIM = int(os.getenv("VECTOR_DIM"))

TO_INSERT_DIR = os.getenv("TO_INSERT_DIR")

# === Connect to Elasticsearch ===
for i in range(10):
    try:
        es = Elasticsearch(ES_URL)
        version = es.info()["version"]["number"]
        print(f"✅ Connected to Elasticsearch {version}")
        break
    except Exception as e:
        print(f"⏳ Attempt {i+1}/10: {e}")
        time.sleep(2)
else:
    raise ConnectionError("❌ Elasticsearch did not become ready in time")

# === Create Index ===
if not es.indices.exists(index=INDEX_NAME):
    es.indices.create(
        index=INDEX_NAME,
        mappings={
            "properties": {
                "movie_id": {"type": "keyword"},
                "genres": {"type": "keyword"},
                "type": {"type": "keyword"},  # e.g., "short", "summary", "long"
                "chunk_id": {"type": "keyword"},
                "text": {"type": "text"},
                "vector": {
                    "type": "dense_vector",
                    "dims": VECTOR_DIM,
                    "index": True,
                    "similarity": "cosine"
                }
            }
        }
    )
    print(f"✅ Created index: {INDEX_NAME}")
else:
    print(f"ℹ️ Index '{INDEX_NAME}' already exists")

# === Upload JSON Files ===
uploaded_count = 0

for filename in os.listdir(TO_INSERT_DIR):
    if filename.endswith(".json"):
        filepath = os.path.join(TO_INSERT_DIR, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                doc_id = filename  # Avoid duplicates
                es.index(index=INDEX_NAME, id=doc_id, document=data)
                uploaded_count += 1
        except Exception as e:
            print(f"❌ Failed to upload {filename}: {e}")

print(f"📤 Uploaded {uploaded_count} JSON file(s) to index '{INDEX_NAME}'")