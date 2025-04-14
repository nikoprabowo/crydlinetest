#!/bin/bash

# Set path
GCS_BUCKET="crydlinetest-data-bucket"
GCS_SCRIPT_PATH="gs://${GCS_BUCKET}/scripts/spark_job.py"

# Jalankan Spark job di Dataproc
echo "Menjalankan Spark job di cluster Dataproc..."
gcloud dataproc jobs submit pyspark "${GCS_SCRIPT_PATH}" \
  --cluster=crydlinetest-cluster \
  --region=asia-southeast1 \
  --properties=spark.hadoop.fs.gs.system.bucket=crydlinetest-data-bucket,spark.bigquery.temp.gcs.bucket=crydlinetest-data-bucket

echo "Selesai!"