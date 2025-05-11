# 🎥 Movie Recommendation Tool

**Authors:**  
Anna Hovakimyan  
Lili Kostanyan  

**Created:** 09/05/2025

---

## 🧠 Overview

This project presents a content-based movie recommendation system that combines semantic search with genre filtering to deliver relevant and engaging movie suggestions. Users can interact through a web interface powered by Streamlit and backed by FastAPI, Elasticsearch, and Google BigQuery.

---

## 🎯 Goal

To recommend movies based on:
- A user-provided description or preference
- Genre-based filtering (strict or relaxed)
- An optional conversational AI assistant powered by Gemini API

---

## 🧩 Key Features

- **Hybrid Retrieval:** Combines semantic similarity (SBERT embeddings) with BM25 ranking.
- **Interactive UI:** Streamlit app lets users select genres, adjust filters, and input free-text queries.
- **Two Modes of Recommendation:**
  - Our Model (SBERT + BM25)
  - Gemini AI (chatbot-style experience)
- **Visual Results:** Includes movie posters, actors, ratings, and summaries.
- **Scalable Infrastructure:** All components containerized using Docker.

---

## 🔧 Architecture

- **ETL Service:** Loads vectorized `.json` movie synopses into Elasticsearch.
- **Backend:** FastAPI app that performs semantic search and data enrichment from BigQuery.
- **Frontend:** Streamlit UI for user interaction and displaying recommendations.
- **Elasticsearch:** Stores embeddings and handles similarity search.
- **Kibana:** Offers visual inspection of indexed data.

---

## 🧪 Technology Stack

- Python 3.10+  
- Sentence-BERT (SentenceTransformers)  
- Docker & Docker Compose  
- FastAPI  
- Streamlit  
- Google BigQuery  
- Elasticsearch + Kibana  
- Gemini AI (optional)

---

## 🗂 Project Structure

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