import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

# Load environment variables from a .env file.
# This allows sensitive information like URLs and credentials to be stored securely.
load_dotenv()

# Retrieve the URL of the Elasticsearch instance from the environment variable `ELASTICSEARCH_URL`.
ES_URL = os.getenv("ELASTICSEARCH_URL")

# Retrieve the name of the Elasticsearch index to be used from the environment variable `INDEX_NAME`.
INDEX_NAME = os.getenv("INDEX_NAME")

# Retrieve the dimensionality of the vectors to be processed from the environment variable `VECTOR_DIM`.
# Convert the value to an integer since environment variables are loaded as strings.
VECTOR_DIM = int(os.getenv("VECTOR_DIM"))

# Retrieve the directory path containing files to be inserted into Elasticsearch from the environment variable `TO_INSERT_DIR`.
TO_INSERT_DIR = os.getenv("TO_INSERT_DIR")

def get_elasticsearch():
    """
    Creates and returns an Elasticsearch client instance.

    Returns:
        Elasticsearch: An instance of the Elasticsearch client connected to the URL specified in the environment variable `ELASTICSEARCH_URL`.
    """
    return Elasticsearch(ES_URL)