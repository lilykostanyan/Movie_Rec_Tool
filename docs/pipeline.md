# - Data Pipeline

The pipeline automates the full process of **collecting**, **processing**, and **uploading** movie data into a vector search engine (Elasticsearch) and cloud storage (Google BigQuery). This pipeline ensures scalable and efficient ingestion of new movie data for recommendation.

---

## - Workflow

1. **TT Code Scraping**  
   Uses Playwright to extract unique IMDb `tt` codes from genre-based search results. Simulates user scrolling and clicking "Show More" to dynamically load more movie IDs.

2. **Metadata & Synopsis Extraction**  
   Asynchronously visits movie and plot pages using `aiohttp` + `BeautifulSoup`, extracting:
   - Title, year, duration, rating, genres
   - Short synopsis, long synopsis, and user summaries

3. **Data Cleaning**  
   Removes rows with no narrative text and cleans extra characters, usernames, and unnecessary suffixes.

4. **Data Splitting**  
   - **Metadata File**: structured movie info  
   - **Synopsis File**: cleaned narrative texts, labeled by type (`short`, `long`, `summary`)

5. **Cloud Upload**  
   Metadata is uploaded to **Google Drive** via API, then ingested into **Google BigQuery**.

6. **Chunking & Embedding**  
   Synopsis text is chunked (~250 words) and embedded with **SBERT** into dense vectors using `SentenceTransformer`.

7. **Output Generation**  
   Each chunk + vector is saved as a `.json` file and archived into a ZIP for ingestion.

8. **ETL Trigger**  
   The ZIP is moved to `etl/data/jsons/`, where `run_etl.sh` automatically unzips and indexes all files into **Elasticsearch**.

---

## - Main Pipeline

::: app.pipeline.main_pipeline

## - Submodules

::: app.pipeline.scrape_tt_codes
::: app.pipeline.extract_movie_data
::: app.pipeline.clean_synopsis
::: app.pipeline.split_movie_data
::: app.pipeline.drive_upload
::: app.pipeline.bigquery_upload
::: app.pipeline.chunk_and_embed