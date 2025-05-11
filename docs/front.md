# - Web Application (Frontend)

The frontend is a **Streamlit web application** that allows users to interactively receive movie recommendations based on **Our Model** or Google's **Gemini AI**.

---

## - Access URLs

- **Main Interface**: [http://localhost:8501](http://localhost:8501)

Users can:

- Enter a movie description
- Select recommendation mode
- Filter by genres
- View detailed suggestions with posters, ratings, and summaries

---

## - Features

- **Two Recommendation Modes**:
  - **Our Model**: Uses hybrid semantic and genre-based filtering from FastAPI backend
  - **Gemini AI**: Uses Google Generative AI to creatively suggest matching movies

- **Genre Filtering**:
  - Choose **strict** or **relaxed** filtering when selecting genres

- **Preview Mode**:
  - Shows the movie title, rating, top actors, duration, and synopsis chunks

---

## 🐳 Docker Service

The frontend is deployed as a container and connects with backend (FastAPI) to request movie recommendations and displays results:

### - Dockerfile

```yaml
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

::: app.front.recommend
::: app.front.app