# - Backend (FastAPI)

The **FastAPI backend** service is responsible for handling user requests, running recommendation logic, and returning enriched movie suggestions.

---

## - Access URLs

- **FastAPI**: [http://localhost:8501](http://localhost:8501)

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## - Features

- **/recommend_movies** (POST):  
  Accepts a movie description and genre filters, and returns personalized movie suggestions.

- **/ (root)** (GET):  
  A health check route confirming the API is live.

---

## - Recommendation Flow

1. **User Input**: Accepts a query and genre selection.
2. **SBERT Encoding**: Converts the query to an embedding using a SentenceTransformer.
3. **Hybrid Search**: Combines cosine similarity and BM25 search in Elasticsearch.
4. **Genre Filtering**: Filters results by genre using strict or relaxed mode.
5. **Metadata Enrichment**: Fetches detailed metadata (title, poster, rating, actors) from BigQuery.
6. **Response**: Returns a structured list of top movie matches.

---

## 🐳 Docker Service

The backend is deployed as a container and connects with Elasticsearch and BigQuery:

### - Dockerfile

```yaml
FROM python:3.10-slim-bullseye

# Install system dependencies required for Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev libfreetype6-dev libpng-dev libjpeg-dev \
    libblas-dev liblapack-dev gfortran libffi-dev libssl-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /back

# Set env variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

::: app.back.config
::: app.back.main