# 🎥 Movie Recommendation Tool

**Authors:**  
Anna Hovakimyan  
Lili Kostanyan  

**Created:** 09/05/2025

**Capstone — BS in Data Science, American University of Armenia**

---

## - Overview

This project presents a **content-based** movie recommendation system that leverages **natural language processing**, **semantic search**, and **genre filtering** to deliver relevant and engaging movie suggestions. Users interact through a web interface built with **Streamlit**, supported by a backend powered by **FastAPI**, **Elasticsearch**, and **Google BigQuery**.

At its core, the system encodes user-provided plot descriptions using **Sentence-BERT (SBERT)** embeddings and performs a **hybrid search** — combining semantic similarity (cosine distance on vector embeddings) and lexical relevance (BM25 scoring) in a **70:30** ratio. The interface allows users to apply strict or relaxed genre filters, choose how many recommendations to receive, and even interact via a conversational **Gemini AI** assistant for more natural queries.

Movie synopses are preprocessed, chunked, and embedded before being indexed in Elasticsearch for fast retrieval. Final recommendations are enriched with metadata (such as titles, ratings, posters, and actors) fetched from Google BigQuery to provide a visually rich and informative experience.

The proposed system demonstrates how hybrid embedding-based retrieval, combined with genre filtering, can offer **accurate**, **flexible**, and **user-friendly** movie recommendations.

---

## - Goal

To recommend movies based on:
- A user-provided description or preference
- Genre-based filtering (strict or relaxed)
- An optional conversational AI assistant powered by Gemini API

---

## - Key Features

- **Hybrid Retrieval:** Combines semantic similarity (SBERT embeddings) with BM25 ranking.
- **Interactive UI:** Streamlit app lets users select genres, adjust filters, and input free-text queries.
- **Genre Filtering:** Supports both strict (AND) and relaxed (OR) filtering across genres.
- **Two Modes of Recommendation:**
  - Our Model (SBERT + BM25)
  - Gemini AI (chatbot-style experience)
- **Visual Results:** Includes movie posters, actors, ratings, and summaries.
- **Scalable Infrastructure:** All components containerized using Docker.

---

## - Architecture

- **ETL Service:** Loads vectorized `.json` movie synopses into Elasticsearch.
- **Elasticsearch:** Stores embeddings and handles similarity search.
- **Kibana:** Offers visual inspection of indexed data.
- **Backend:** FastAPI app that performs semantic search and data enrichment from BigQuery.
- **Frontend:** Streamlit UI for user interaction and displaying recommendations.

---

## - Technology Stack

- Python 3.10+  
- Playwright, BeautifulSoup, SBERT, and aiohttp (for scraping and preprocessing)
- Google BigQuery 
- Sentence-BERT (SentenceTransformers)  
- Docker & Docker Compose  
- Elasticsearch + Kibana 
- FastAPI  
- Streamlit   
- Gemini AI (optional)

---

## - Project Structure

```plaintext
Movie_Rec_Tool/
├── app/
│   ├── etl/           # Data loader for Elasticsearch
│   ├── back/          # FastAPI backend
│   ├── front/         # Streamlit frontend
│   ├── pipeline/      # Chunking, embedding, uploading logic
│   ├── docker-compose.yml
│   └── client_secrets/  # Google credentials
└──
```

---

## - Installation

Before getting started, ensure you have the following:

1. Clone the repository:
   ```bash
   git clone https://github.com/lilykostanyan/Movie_Rec_Tool.git
   ```

2. Open the project directory (Movie_Rec_Tool) and change directory:
   ```bash
   cd app
   ```

3. To run this project end-to-end, you will need the following files, which will be shared via a **Google Drive link** (inside `env.txt` for all of them):

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

## - Access the Application

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
   ```bash
   GET movies-bm25-vector/_count
   ```
   - retrieves documents from the index
   ```bash
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