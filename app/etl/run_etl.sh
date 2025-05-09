#!/bin/sh
set -e

# Print a message indicating the start of the load process.
echo "- Starting load process..."

# Create directories for storing JSON files to be inserted and archived ZIP files.
mkdir -p "$TO_INSERT_DIR" "$ARCHIVE_DIR"

# Continuously check for the presence of ZIP files in the directory specified by `JSONS_DIR`.
# If no ZIP files are found, wait for 5 seconds before checking again.
while true; do
  zip_files=$(find "$JSONS_DIR" -maxdepth 1 -name "*.zip")  # Find ZIP files in `JSONS_DIR`.
  if [ -n "$zip_files" ]; then  # If ZIP files are found, exit the loop.
    break
  fi
  echo "- Waiting for ZIP files in $JSONS_DIR..."  # Log a message indicating the wait.
  sleep 5  # Wait for 5 seconds before the next check.
done

# Iterate over each ZIP file found in `JSONS_DIR`.
for zip_file in $zip_files; do
  base=$(basename "$zip_file" .zip)  # Extract the base name of the ZIP file (without extension).
  echo "- Found zip: $base.zip"  # Log the name of the found ZIP file.

  # Skip processing if the ZIP file has already been archived.
  if [ -e "$ARCHIVE_DIR/$base.zip" ]; then
    echo "- Already archived: $base.zip — skipping"  # Log a message indicating the skip.
    continue
  fi

  # Unzip the contents of the ZIP file into the directory specified by `TO_INSERT_DIR`.
  echo "- Unzipping: $zip_file → $TO_INSERT_DIR"
  unzip -oq "$zip_file" -d "$TO_INSERT_DIR"

  # Flatten the directory structure by moving JSON files from subdirectories to `TO_INSERT_DIR`.
  echo "- Flattening directory..."
  find "$TO_INSERT_DIR" -mindepth 2 -type f -name "*.json" -exec mv -t "$TO_INSERT_DIR" {} +

  # Remove any remaining subdirectories in `TO_INSERT_DIR`.
  find "$TO_INSERT_DIR" -mindepth 1 -type d -exec rm -rf {} +

  # Run the Python script `load.py` to process the unzipped JSON files.
  echo "- Running on unzipped JSONs..."
  python load.py

  # Clean up the `TO_INSERT_DIR` by removing its contents and recreating the directory.
  echo "- Cleaning up $TO_INSERT_DIR..."
  rm -rf "$TO_INSERT_DIR"
  mkdir -p "$TO_INSERT_DIR"

  # Archive the processed ZIP file by moving it to the directory specified by `ARCHIVE_DIR`.
  echo "- Archiving zip file..."
  archived_path="$ARCHIVE_DIR/$(basename "$zip_file")"
  if mv "$zip_file" "$archived_path"; then
    echo "- Archived $zip_file → $archived_path"  # Log a message indicating successful archiving.
  else
    echo "- Failed to archive $zip_file"  # Log an error message if archiving fails.
    exit 1  # Exit the script with an error code.
  fi

  # Log a message indicating the completion of processing for the current ZIP file.
  echo "- Finished processing: $base"
done

# Log a message indicating that all ZIP files have been processed.
echo "- All ZIPs processed."