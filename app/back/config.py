import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from google.cloud import bigquery
from google.oauth2 import service_account

# Load environment variables from a .env file.
# This allows sensitive information like URLs and credentials to be stored securely.
load_dotenv()

# Elasticsearch URL, timeout, and index name are loaded from environment variables
ES_URL = os.getenv("ELASTICSEARCH_URL")
ES_TIMEOUT = int(os.getenv("ELASTICSEARCH_TIMEOUT"))  # Default timeout is 30 seconds
ES_INDEX = os.getenv("ES_INDEX")  # Elasticsearch index name

# Number of top results to retrieve, defaulting to 10
TOP_K = int(os.getenv("TOP_K"))

# Google Cloud Project and BigQuery configuration
BQ_PROJECT_ID = os.getenv("BQ_PROJECT_ID")
BQ_TABLE = os.getenv("BQ_TABLE")  # BigQuery table name
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")  # Path to the service account file
SCOPE = [os.getenv("SCOPE")]  # Scopes for Google Cloud API access

# Model name for the sentence transformer, defaulting to "bert-base-nli-mean-tokens"
MODEL_NAME = os.getenv("MODEL_NAME")

def get_elasticsearch() -> Elasticsearch:
    """
    Creates and returns an Elasticsearch client instance.

    Returns:
        Elasticsearch: Configured Elasticsearch client with the specified URL and timeout.
    """
    return Elasticsearch(ES_URL, request_timeout=ES_TIMEOUT)

def get_sentence_transformer() -> SentenceTransformer:
    """
    Loads and returns the sentence transformer model.

    Returns:
        SentenceTransformer: Pre-trained sentence transformer model for generating embeddings.
    """
    return SentenceTransformer(MODEL_NAME)

def get_bigquery_client() -> bigquery.Client:
    """
    Creates and returns a BigQuery client using service account credentials.

    Returns:
        bigquery.Client: Authenticated BigQuery client configured with the service account file.
    """
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPE
    )
    return bigquery.Client(credentials=credentials, project=BQ_PROJECT_ID)