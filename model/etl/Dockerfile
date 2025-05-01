FROM python:3.10-slim-bullseye

RUN apt-get update && apt-get install -y \
    unzip \
    build-essential libpq-dev libfreetype6-dev libpng-dev libjpeg-dev \
    libblas-dev liblapack-dev gfortran \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /etl

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Make the run script executable
RUN chmod +x run_etl.sh

# Run unzip > upload > cleanup > archive and the indexing script
CMD ["sh", "run_etl.sh"]