# 🎥 Movie Recommendation Tool

**Authors:**  
Anna Hovakimyan  
Lili Kostanyan  

**Created:** 09/05/2025

---

## 📚 Documentation

For a more detailed documentation check :  
🔗  - !!!!!

---

## Prerequisites (What You Need Before You Start)

Make sure the following tools are installed on your computer:

- [Python 3.10+](https://www.python.org/downloads/) – To run Python scripts  
- [Docker](https://www.docker.com/products/docker-desktop) – To run the application 

---

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

3. Build and start the Docker containers:
   ```bash
   docker-compose up --build
   ```

4. Open new terminal:
   ```bash
   cd app/pipeline
   ```

5. From inside the project directory, install the required Python packages by running:
   ```bash
   pip install -r requirements.txt
   ```

   and then, install the necessary Playwright browser binaries:
   ```bash
   playwright install
   ```

5. Run the pipeline (no need to wait until Docker is fully up)
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
```json
GET movies-bm25-vector/_count
```

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
>   if you see a line like `VARIABLE_NAME=` with nothing after the `=`, it means  
>   **you still need to enter a value manually**  
> - Your Google service account JSON file is placed inside a folder named `client_secrets/` (this folder must be created manually)  
> - The variable `SERVICE_ACCOUNT_FILE` in your `.env` file points to the correct path (e.g., `client_secrets/your-service-account.json`)

---

**Quick Setup Guide for Environment Variables**:

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

   ```plaintext
   app/
   ├── client_secrets/
   │   └── your-service-account.json
   ```

2. Open `.env` and update this line:
SERVICE_ACCOUNT_FILE=client_secrets/your-service-account.json - ??????????

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

## Docker

## ETL

## API

We created a service for the **API** part of the project, which handles core functionalities such as

### **Features**


### **Requests** 

---

## **Services**
We use Docker services for efficient deployment and management of components.  

### **Database** 

## Web Application

We created a service for the **front-end** part of the project, which is responsible for hosting the **Streamlit web application**.

### Dockerfile

```Dockerfile
# Dockerfile