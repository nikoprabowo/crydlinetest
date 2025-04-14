#!/bin/bash

# ================================================================
# 🛠️  Spark Job Runner for Google Cloud Dataproc
# This script uploads a PySpark job to GCS and runs it on Dataproc
# ================================================================

# ✅ CONFIGURATION - Update these variables before running
# Local path to your PySpark script in the VM
VM_SCRIPT_PATH="/path/to/your/spark_job.py"  # <-- Replace with the actual local path

# GCS bucket where the script will be uploaded
GCS_BUCKET="your-gcs-bucket-name"  # <-- Replace with your GCS bucket name

# Destination path in GCS
GCS_SCRIPT_PATH="gs://${GCS_BUCKET}/scripts/spark_job.py"

# Dataproc cluster name and region
CLUSTER_NAME="your-dataproc-cluster"  # <-- Replace with your Dataproc cluster name
REGION="your-region"  # e.g., asia-southeast1

# GCS bucket for temporary BigQuery or Spark files
TEMP_BUCKET="${GCS_BUCKET}"  # Change this if you use a different temp bucket

# ================================================================
# 📤 Upload the PySpark script to GCS
# ================================================================
echo "Uploading spark_job.py to ${GCS_SCRIPT_PATH}..."
gsutil cp "${VM_SCRIPT_PATH}" "${GCS_SCRIPT_PATH}"

# ================================================================
# 🔥 Submit the Spark job to Dataproc
# ================================================================
echo "Submitting Spark job to Dataproc cluster '${CLUSTER_NAME}'..."

gcloud dataproc jobs submit pyspark "${GCS_SCRIPT_PATH}" \
  --cluster="${CLUSTER_NAME}" \
  --region="${REGION}" \
  --properties="spark.hadoop.fs.gs.system.bucket=${GCS_BUCKET},spark.bigquery.temp.gcs.bucket=${TEMP_BUCKET}"

echo "✅ Spark job completed successfully!"