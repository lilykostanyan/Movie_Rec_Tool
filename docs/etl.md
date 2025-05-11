# - ETL Module

The **ETL module** is responsible for inserting preprocessed and embedded movie `.json` files into **Elasticsearch**.

## - Database (NoSQL - Elasticsearch)

In `load.py`, we use the `elasticsearch` Python client to:

- Connect to the Elasticsearch server (with retry logic)
- Create an index (if it doesn't exist)
- Insert the `.json` documents from the data folder
- Each document includes:
  - `movie_id`
  - `genres`
  - `type` (short, summary, or long)
  - `chunk_id`
  - `text`
  - `vector` (768-dim dense vector)

> Indexing uses `cosine similarity` to support semantic search.

---

## 🐳 Docker Setup (ETL Service)

The ETL service is containerized and configured to run a `run_etl.sh` script which:

1. Waits for a `.zip` file of JSON chunks to appear in the `data/jsons/` folder.
```plaintext
app/
├── etl/
│ └── data/
│ │ └── jsons/
│ │  ├── move_data.zip
│ └── ...
└──
```
2. Unzips and flattens the directory structure.
3. Executes `load.py` to push the content into Elasticsearch.
4. Cleans and archives the `.zip` file after successful upload.

### - Dockerfile

```dockerfile
FROM python:3.10-slim-bullseye

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    unzip \
    build-essential libpq-dev libfreetype6-dev libpng-dev libjpeg-dev \
    libblas-dev liblapack-dev gfortran \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /etl

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip3 install --upgrade pip && pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Make the run script executable
RUN chmod +x run_etl.sh

# Run the ETL process
CMD ["sh", "run_etl.sh"]
```

::: app.etl.run_etl
::: app.etl.load