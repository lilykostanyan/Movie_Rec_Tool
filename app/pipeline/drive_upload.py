from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
from config import SERVICE_ACCOUNT_FILE, SCOPES, FOLDER_ID, MOVIE_METADATA_FILE
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.utils.logger import logger

def upload_metadata_to_drive(file_path: str = None, file_name: str = None) -> str:

    """
    Uploads a metadata file to Google Drive.

    Args:
        file_path (str): The local path to the file to be uploaded.
                         Default is "imdb_data/romance_metadata.xlsx".
        file_name (str): The name of the file as it will appear in Google Drive.
                         Default is "romance_metadata.xlsx".

    Returns:
        str: The ID of the uploaded file in Google Drive.
    """
    if file_path is None:
        file_path = f"imdb_data/{MOVIE_METADATA_FILE}"
    if file_name is None:
        file_name = MOVIE_METADATA_FILE

    # Define the MIME type for an Excel file.
    mime_type: str = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    # Authenticate using the service account credentials and the specified scopes.
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)

    # Define the metadata for the file to be uploaded, including its name and parent folder ID.
    file_metadata: dict = {
        'name': file_name,
        'parents': [FOLDER_ID]
    }

    # Create a MediaFileUpload object to handle the file upload.
    media = MediaFileUpload(file_path, mimetype=mime_type)

    # Upload the file to Google Drive and retrieve the response containing the file ID.
    response: dict = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    # Extract the file ID from the response and log the upload success.
    file_id: str = response.get("id")
    logger.info(f"- Uploaded '{file_name}' with file ID: {file_id}")
    return file_id

