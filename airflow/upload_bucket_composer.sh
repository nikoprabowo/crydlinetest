#!/bin/bash

# === CONFIGURATION ===
# Modify these variables to match your setup

# GCS Composer bucket name (no "gs://" prefix and rename)
COMPOSER_BUCKET="your-composer-bucket"

# Local paths (Replace path as your condition)
LOCAL_DAG_PATH="you_path/upload_to_dags/your_dag.py"
LOCAL_DATA_FOLDER="you_path/upload_to_data"
LOCAL_REQUIREMENTS="you_path/upload_to_plugins/requirements.txt"

# === UPLOAD DAG FILE ===
echo "Uploading DAG script to Composer DAGs folder..."
gsutil cp "$LOCAL_DAG_PATH" "gs://${COMPOSER_BUCKET}/dags/"

# === UPLOAD DATA FOLDER CONTENT ===
echo "Uploading all contents of 'upload_to_data' to Composer 'data' folder..."
gsutil -m cp -r "${LOCAL_DATA_FOLDER}/*" "gs://${COMPOSER_BUCKET}/data/"

# === UPLOAD REQUIREMENTS FILE ===
echo "Uploading requirements.txt to Composer plugins folder..."
gsutil cp "$LOCAL_REQUIREMENTS" "gs://${COMPOSER_BUCKET}/plugins/"

echo "✅ All files successfully uploaded to Composer bucket."
