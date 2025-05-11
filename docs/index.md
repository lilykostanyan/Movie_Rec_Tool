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