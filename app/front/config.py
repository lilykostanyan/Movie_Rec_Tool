import os
from dotenv import load_dotenv

# Load environment variables from a .env file into the process's environment variables.
load_dotenv()

# Retrieve the Gemini API key from the environment variables.
# This key is used to authenticate requests to the Gemini API.
api_key = os.getenv("GEMINI_API_KEY")

# GEMINI_API_KEY: The API key for accessing the Gemini API.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# BACKEND_URL: The base URL for the backend server.
BACKEND_URL = os.getenv("BACKEND_URL")

# GENRE_OPTIONS: A list of genre options parsed from the environment variable `GENRE_OPTIONS`.
# The genres are split by commas and stripped of any leading or trailing whitespace.
GENRE_OPTIONS = [g.strip() for g in os.getenv("GENRE_OPTIONS").split(",") if g]