import io
import pandas as pd
from google.cloud import bigquery
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload
import warnings
from typing import Optional
from config import SERVICE_ACCOUNT_FILE, MOVIE_METADATA_FILE
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.utils.logger import logger

# Suppress FutureWarning about pandas-gbq compatibility issues
warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
    module="google.cloud.bigquery._pandas_helpers"
)

# Suppress UserWarning about missing BigQuery Storage API
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    module="google.cloud.bigquery.table"
)

# Load service account credentials from the specified file and define the required scopes.
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=[
        "https://www.googleapis.com/auth/drive",  # Access to Google Drive
        "https://www.googleapis.com/auth/bigquery"  # Access to BigQuery
    ]
)

# Initialize the Google Drive API client using the authenticated credentials.
drive_service = build("drive", "v3", credentials=credentials)

# Initialize the BigQuery client using the authenticated credentials and project ID.
bq_client = bigquery.Client(credentials=credentials, project="enduring-brace-451209-q3")

def upload_single_file_to_bigquery(
    target_file_name: Optional[str] = None,
    folder_id="1sJcfq2h5NCOO2DNz2RxeIgSq-HYhl9Kg",
    dataset_id="romance_dataset",
    table_name="full_data_table"
) -> Optional[None]:
    """
    Uploads a single Excel file from Google Drive to a BigQuery table.

    Args:
        target_file_name (str): The name of the target Excel file to search for in Google Drive.
        folder_id (str): The ID of the Google Drive folder containing the file.
        dataset_id (str): The ID of the BigQuery dataset where the table resides.
        table_name (str): The name of the BigQuery table to upload data to.

    Returns:
        None
    """
    if target_file_name is None:
        target_file_name = MOVIE_METADATA_FILE

    # Query Google Drive for the file with the specified name and MIME type in the given folder.
    query: str = f"'{folder_id}' in parents and name='{target_file_name}' and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])

    if not files:
        logger.info(f"- File '{target_file_name}' not found in folder.")
        return None

    file: dict = files[0]
    file_id: str = file['id']
    logger.info(f"- Found file: {file['name']} (ID: {file_id})")

    # Use the Google Drive API to download the file content into a memory buffer.
    request = drive_service.files().get_media(fileId=file_id)
    file_stream = io.BytesIO()
    downloader = MediaIoBaseDownload(file_stream, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        logger.info(f"- Download {int(status.progress() * 100)}% complete.")
    file_stream.seek(0)

    # Read the Excel file into a pandas DataFrame and remove duplicate rows based on the "tconst" column.
    xls = pd.ExcelFile(file_stream)
    df = xls.parse(xls.sheet_names[0])
    df = df.drop_duplicates(subset=["tconst"])  # Remove internal duplicates

    # Query the BigQuery table for existing rows and filter them out from the DataFrame.
    full_table_id = f"{bq_client.project}.{dataset_id}.{table_name}"
    query = f"SELECT tconst FROM {full_table_id}"
    existing = bq_client.query(query).to_dataframe()
    existing_set = set(existing['tconst'])

    original_len = len(df)
    df = df[~df['tconst'].isin(existing_set)]
    logger.info(f"- Removed {original_len - len(df)} rows already in BigQuery.")

    if df.empty:
        logger.info("- No new rows to upload.")
        return None

    # Add a "staging_raw_id" column to the DataFrame if it does not already exist.
    if "staging_raw_id" not in df.columns:
        df.insert(0, "staging_raw_id", range(1, len(df) + 1))

    # Convert specific columns to string type to ensure compatibility with BigQuery schema.
    columns_to_stringify = ['movie_year', 'imdb_rating']

    for col in columns_to_stringify:
        if col in df.columns:
            df[col] = df[col].astype(str)

    # Configure the BigQuery load job to append data to the table and upload the DataFrame.
    job_config = bigquery.LoadJobConfig(
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND  # Append new rows to the table
    )

    load_job = bq_client.load_table_from_dataframe(df, full_table_id, job_config=job_config)
    load_job.result()  # Wait for the job to complete

    logger.info(f"- Uploaded {len(df)} new row(s) to BigQuery table {full_table_id}")
    return None

