#!/bin/sh
set -e

echo "🚀 Starting ETL process..."

mkdir -p "$TO_INSERT_DIR" "$ARCHIVE_DIR"

zip_found=false  # Flag to track if any .zip was actually found and processed

for zip_file in "$JSONS_DIR"/*.zip; do
  # Avoid literal "*.zip" when no files exist
  if [ ! -f "$zip_file" ]; then
    continue
  fi

  zip_found=true

  base=$(basename "$zip_file" .zip)
  echo "📦 Found zip: $base.zip"

  # Skip if already archived
  if [ -e "$ARCHIVE_DIR/$base.zip" ]; then
    echo "⏭️  Already archived: $base.zip — skipping"
    continue
  fi

  echo "🔓 Unzipping: $zip_file → $TO_INSERT_DIR"
  unzip -oq "$zip_file" -d "$TO_INSERT_DIR"

  echo "📁 Flattening directory..."
  find "$TO_INSERT_DIR" -type f -name "*.json" -exec mv {} "$TO_INSERT_DIR" \;
  find "$TO_INSERT_DIR" -mindepth 1 -type d -exec rm -rf {} +

  echo "🚀 Running ETL on unzipped JSONs..."
  python load.py

  echo "🧹 Cleaning up to_insert folder..."
  rm -rf "$TO_INSERT_DIR"/*

  echo "📦 Archiving zip file..."
  archived_path="$ARCHIVE_DIR/$(basename "$zip_file")"
  if mv "$zip_file" "$archived_path"; then
    echo "✅ Archived $zip_file → $archived_path"
  else
    echo "❌ Failed to archive $zip_file"
    exit 1
  fi

  echo "✅ Finished processing: $base"
done

# If no actual zip files existed
if [ "$zip_found" = false ]; then
  echo "ℹ️  No zip files found in $JSONS_DIR"
fi

echo "🎉 All ZIPs processed."