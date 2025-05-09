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