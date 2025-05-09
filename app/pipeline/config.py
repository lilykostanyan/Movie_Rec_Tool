import os
from dotenv import load_dotenv

# Load environment variables from a .env file into the environment.
load_dotenv()

# Retrieve the base URL for the application from the environment variables.
URL = os.getenv("URL")

# Retrieve the name of the TSV file to be processed from the environment variables.
TSV_FILENAME = os.getenv("TSV_FILENAME")

# The TSV file containing the tt codes
PROCESSED_IDS = os.getenv("PROCESSED_IDS")

# Retrieve the name of the output file for the scraped data from the environment variables.
OUTPUT_FILE = os.getenv("OUTPUT_FILE")

# Retrieve the name of the cleaned output file from the environment variables.
CLEANED_OUTPUT_FILE = os.getenv("CLEANED_OUTPUT_FILE")

# Retrieve the name of the metadata file from the environment variables.
MOVIE_METADATA_FILE = os.getenv("MOVIE_METADATA_FILE")

# Retrieve the name of the synopsis file from the environment variables.
MOVIE_SYNOPSIS_FILE = os.getenv("MOVIE_SYNOPSIS_FILE")

# Retrieve the path to the output file for the processed data from the environment variables.
OUTPUT_FILE_PATH= os.getenv("OUTPUT_FILE_PATH")

# Retrieve the path to the cleaned output file from the environment variables.
CLEANED_OUTPUT_FILE_PATH=os.getenv("CLEANED_OUTPUT_FILE_PATH")

# Retrieve the path to the metadata file from the environment variables.
MOVIE_METADATA_PATH=os.getenv("MOVIE_METADATA_PATH")

# Retrieve the path to the synopsis file from the environment variables.
MOVIE_SYNOPSIS_PATH=os.getenv("MOVIE_SYNOPSIS_PATH")

# Retrieve the path to the chunks directory from the environment variables.
CHUNKS_ZIP_PATH=os.getenv("CHUNKS_ZIP_PATH")

# Retrieve the name of the JSON file to be processed from the environment variables.
JSONS_FOLDER=os.getenv("JSONS_FOLDER")

# Retrieve the maximum number of clicks allowed, convert it to an integer, and store it.
MAX_CLICKS = int(os.getenv("MAX_CLICKS"))

# Retrieve the scopes for API access from the environment variables and store them as a list.
SCOPES = [os.getenv("SCOPES")]

# Retrieve the path to the service account file for authentication from the environment variables.
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")

# Retrieve the folder ID for Google Drive operations from the environment variables.
FOLDER_ID = os.getenv("FOLDER_ID")