# 🎥 Movie Recommendation Tool

**Authors:**  
Anna Hovakimyan  
Lili Kostanyan  

**Created:** 09/05/2025

---

## 📚 Documentation

For a more detailed documentation check :  
🔗  - https://lilykostanyan.github.io/Movie_Rec_Tool/

---

## Prerequisites (What You Need Before You Start)

Make sure the following tools are installed on your computer:

- [Python 3.10+](https://www.python.org/downloads/) – To run Python scripts  
- [Docker](https://www.docker.com/products/docker-desktop) – To run the application 

## Installation

Before getting started, ensure you have the following:

1. Clone the repository:
   ```bash
   git clone https://github.com/lilykostanyan/Movie_Rec_Tool.git
   ```

2. Open the project directory (Movie_Rec_Tool) and change directory:
   ```bash
   cd app
   ```

3. To run this project end-to-end, you will need the following files, which will be shared via a **Google Drive link**:

    a. `.env` files for each service (folder):  
      - `etl/.env`  
      - `back/.env`  
      - `front/.env`
      - `pipeline/.env`

      Place the `.env` files into their respective folders (`etl/`, `back/`, `front/`, `pipeline/`) 

      - Copy the example file:
        ```bash
        cp .env.example .env
        ```
      Open each `.env` file and fill in any missing values (lines with `VARIABLE_NAME=  `)

    b. Google service credentials:  
      - `client_secrets/your-service-account.json`  
      *(this folder must be created manually in the app folder)*

      ```plaintext
    app/
    ├── client_secrets/
    │   └── your-service-account.json
    ```

      - Open `back/.env`, `pipeline/.env` and update this line:
      SERVICE_ACCOUNT_FILE=client_secrets/your-service-account.json

4. Open the provided with a ZIP file containing preprocessed `.json` files from **Google Drive**.

  - **Place the `.zip` file** inside the following folder:

  > Example folder structure after placement:
  ```plaintext
  app/
  ├── etl/
  │ └── data/
  │ │ └── jsons/
  │ │  ├── move_data.zip
  │ └── ...
  ```

5. Build and start the Docker containers:
   ```bash
   docker-compose up --build
   ```

6. Open new terminal:
   ```bash
   cd app/pipeline
   ```

7. From inside the project directory, install the required Python packages by running:
   ```bash
   pip install -r requirements.txt
   ```

   and then, install the necessary Playwright browser binaries:
   ```bash
   playwright install
   ```

8. Run the pipeline (no need to wait until Docker is fully up)
   ```bash
   python main_pipeline.py
   ``` 

---

## Access the Application

After running `docker-compose up --build`, you can access the different parts of the application using the following URLs:

- **Elasticsearch**: [http://localhost:9200](http://localhost:9200) 

  Elasticsearch stores all the synopses and powers the search functionality. Visiting this URL confirms the server is running (There should be some JSON output).

---

- **Kibana Dashboard**: [http://localhost:5601](http://localhost:5601) 

  Kibana provides a UI to visually inspect and manage your Elasticsearch index:
   1. Click on the **menu icon (☰)** in the top-left corner of the page.
   2. Scroll down and click on **Dev Tools**.
   3. In the console that appears, you can run queries like:

   - counts documents in the index
   ```json
   GET movies-bm25-vector/_count
   ```
   - retrieves documents from the index
   ```json
   GET movies-bm25-vector/_search
   ```

---

- **FastAPI Backend**: [http://localhost:8000](http://localhost:8000) 

  The FastAPI backend handles the core recommendation logic and communication with Elasticsearch.
  Use the built-in [Swagger UI](http://localhost:8000/docs) to explore and test API endpoints.

---

Finally, open the **Streamlit** application.

- **Streamlit Frontend**: [http://localhost:8501](http://localhost:8501) 

  This is the main user interface for the application.

   - Choose between Gemini AI or Our Model

   - Enter a custom movie description

   - Optionally filter by genre

   - See detailed movie suggestions with posters, ratings, actors, and synopsis previews

--- 

> **Note:**  
> Before accessing any URLs, make sure:
>
> - Docker is running on your machine  
> - You’ve created a `.env` file based on the provided `.env.example`
> - All required environment variables are **filled in correctly** —  
>   (if you see a line like `VARIABLE_NAME=  ` with nothing after the `=`, it means  
>   **you still need to enter a value manually**)
> - Your Google service account JSON file is placed inside a folder named `client_secrets/` (this folder must be created manually)  
> - The variable `SERVICE_ACCOUNT_FILE` in your `.env` file points to the correct path (e.g., `client_secrets/your-service-account.json`)

---

### Project Schema
```plaintext
Final-Capstone/
├── app/ 
│ ├── etl/ 
│ │ ├── .env (NOT committed)
│ │ ├── .env.example (committed)
│ │ ├── load.py
│ │ ├── Dockerfile
│ │ ├── requirements.txt
│ │ └── ... # Other helper modules
│ ├── back/ 
│ │ ├── .env (NOT committed)
│ │ ├── .env.example (committed)
│ │ ├── main.py
│ │ ├── Dockerfile
│ │ ├── requirements.txt
│ │ └── ... # Other backend modules
│ ├── front/ 
│ │ ├── .env (NOT committed)
│ │ ├── .env.example (committed)
│ │ ├── app.py 
│ │ ├── Dockerfile
│ │ ├── requirements.txt
│ │ └── ... # UI logic and styling
│ ├── pipeline/
│ │ ├── .env (NOT committed)
│ │ ├── .env.example (committed) 
│ │ ├── main_pipeline.py 
│ │ └── ... # All data processing and embedding scripts
│ └── docker-compose.yml # Defines and runs multi-container Docker services
│
├── client_secrets/ # (NOT committed)
│ └── your-service-account.json # service account JSON file
│
├── README.md
└── ... # Additional helper files
```

---

## 🐳 Docker

This project uses Docker to manage all core services. After running `docker-compose up --build`, the following containers will be launched:

## Components Overview

- **ETL:** Loads vectorized `.json` files into Elasticsearch
- **Backend (FastAPI):** Processes search requests and returns smart recommendations
- **Frontend (Streamlit):** User interface to interact with both Gemini AI and the our model
- **Elasticsearch + Kibana:** Vector search engine and dashboard

---

### 1. **ETL**
A Python-based service that loads pre-processed movie data (from `.json` files) into Elasticsearch.

- Triggered automatically on `docker-compose up`
- Reads data from the `etl/data/` directory
- Logs activity to `shared_logs/`

```yaml
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

---

### 2. **Backend (FastAPI)**
Handles recommendation logic and exposes API endpoints to serve the frontend.

- Handling movie recommendation requests from the frontend
- Querying **Elasticsearch** using script scoring + genre filtering
- Fetching additional movie metadata from **Google BigQuery**
- Returning clean and structured JSON responses to be rendered in the UI

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

#### Main Features

- Exposes a single endpoint:  
  `POST /recommend_movies`  
  Accepts a description, genre filters (optional), and number of desired results.

- Uses **semantic vector search** powered by a SentenceTransformer model and Elasticsearch's `dense_vector` field

- Implements **genre-based filtering** with two modes:
  - `strict` → match all selected genres
  - `relaxed` → match any selected genre

- Enhances results with movie info from BigQuery:  
  (title, year, IMDb rating, age rating, top 5 actors, poster image, etc.)

---

#### Test Tool

Once the backend is running, test it via Swagger UI:  
[http://localhost:8000/docs](http://localhost:8000/docs)

You can try out the `POST /recommend_movies` endpoint interactively from there.

---

> ! Make sure `.env` is correctly set in `/app/back/`, with variables like `GENRE_OPTIONS`, `BQ_TABLE`, `SERVICE_ACCOUNT_FILE`, etc., before launching the backend.

---

### 3. **Frontend (Streamlit)**
The user interface for selecting genres, entering queries, and viewing movie recommendations.

```yaml
FROM python:3.10-slim-bullseye

# Install system dependencies required for Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev libfreetype6-dev libpng-dev libjpeg-dev \
    libblas-dev liblapack-dev gfortran libffi-dev libssl-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
FROM python:3.10-slim-bullseye

RUN apt-get update && apt-get install -y \
    build-essential \
    libfreetype6-dev libpng-dev libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /front

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt .

RUN pip3 install --upgrade pip \
 && pip3 install --no-cache-dir --force-reinstall numpy pandas \
 && pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.headless=true", "--server.runOnSave=true", "--server.address=0.0.0.0"]
```

---

#### Features:

- Choose between two recommendation modes:
  - **Our Model** – Uses a vector-based similarity search via the backend
  - **Gemini AI** – Uses Google's Generative AI to suggest movies based on creative input

- Describe the kind of movie you're looking for in plain text

- Optional:
  - Filter by genre(s)
  - Choose strict vs. relaxed filtering mode
  - Select how many movie recommendations you want (1–5)

- Results include:
  - 🎬 Title and release year
  - ⭐ IMDb rating, 🔞 Age rating, 🕒 Duration
  - 🎭 Top actors
  - 🖼 Poster image
  - 📖 Short preview text from the synopsis

---

#### How It Works:

- The UI is defined in `app/front/app.py`
- Logic for making API requests and formatting results is in `recommend.py`
- Communicates with the backend at `http://localhost:8000/recommend_movies`

> The app runs at: [http://localhost:8501](http://localhost:8501)

> ! Make sure the `.env` file in `/front/` is configured correctly (especially `BACKEND_URL` and `GEMINI_API_KEY`).

---

### Volume Mounts & Env Setup

- `.env` files for each service are located in their respective folders (`etl/`, `back/`, `front/`)
- `client_secrets/` holds your private Google service credentials (mounted read-only)
- All containers use a shared `shared_logs/` folder for centralized logging

---

> ! Make sure to fill in all environment variables before launching the containers. Missing values may cause services to fail.

---

### Services (Docker Compose)

The following services are defined in `docker-compose.yaml`:

---

#### **elasticsearch**
- Stores vectorized movie data
- Runs on port **9200**
- Used by the backend to perform similarity search
- Includes a health check to ensure it's ready before other services start

---

#### **kibana**
- Visual dashboard for Elasticsearch
- Runs on port **5601**
- Lets you inspect indexed documents and run test queries via **Dev Tools**

---

#### **etl**
- Loads preprocessed `.json` files (from `pipeline/`) into Elasticsearch
- Mounted volumes:
  - `etl/data/` → where movie chunks live
  - `shared_logs/` → stores log output
- Depends on Elasticsearch being healthy

---

#### **back** (FastAPI)
- Hosts the backend API on port **8000**
- Handles recommendation logic and serves data to the frontend
- Connects to both Elasticsearch and Google BigQuery
- Mounts GCP credentials via `client_secrets/`

---

#### **front** (Streamlit)
- Runs the user interface on port **8501**
- Sends queries to the backend and displays movie recommendations
- Uses `shared_logs/` for centralized logging

---

#### Volumes
- `esdata`: Persists Elasticsearch data between runs

---

 ```yaml
services:
  elasticsearch:
    container_name: elasticsearch5
    image: docker.elastic.co/elasticsearch/elasticsearch:8.5.1
    restart: always
    ports:
      - "9200:9200"
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - ES_JAVA_OPTS=-Xms512m -Xmx512m
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9200/_cluster/health"]
      interval: 5s
      timeout: 3s
      retries: 20
    volumes:
      - esdata:/usr/share/elasticsearch/data

  kibana:
    container_name: kibana5
    restart: always
    image: docker.elastic.co/kibana/kibana:8.5.1
    ports:
      - "5601:5601"
    depends_on:
      elasticsearch:
        condition: service_healthy
    environment:
      - ELASTICSEARCH_URL=http://elasticsearch:9200

  etl:
    container_name: etl5
    build:
      context: ./etl
      dockerfile: Dockerfile
    depends_on:
      elasticsearch:
        condition: service_healthy
    restart: on-failure
    env_file:
      - ./etl/.env
    volumes:
      - ./etl/data:/etl/data
      - ./shared_logs:/etl/logs
    environment:
      - PYTHONPATH=/app

  back:
    container_name: back5
    build:
      context: ./back
      dockerfile: Dockerfile
    depends_on:
      elasticsearch:
        condition: service_healthy
    env_file:
      - ./back/.env
    ports:
      - "8000:8000"
    volumes:
      - ./back:/back
      - ~/.cache/huggingface:/root/.cache/huggingface
      - ./client_secrets/enduring-brace-451209-q3-35cf0810d57c.json:/back/client_secrets/enduring-brace-451209-q3-35cf0810d57c.json:ro
      - ./shared_logs:/back/logs
    environment:
      - PYTHONPATH=/app

  front:
    container_name: front5
    build:
      context: ./front
      dockerfile: Dockerfile
    env_file:
      - ./front/.env
    ports:
      - "8501:8501"
    volumes:
      - ./front:/front
      - ./shared_logs:/app/shared_logs
    environment:
      - PYTHONPATH=/app
    depends_on:
      - back

volumes:
  esdata:
```

---