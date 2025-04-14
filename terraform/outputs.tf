# ====================================
# 🔧 EDIT VARIABLES AS YOUR CONDITION
# ====================================

output "bucket_name" {
  description = "The name of the GCS bucket"
  value       = google_storage_bucket.your_bucket.name
}

output "bigquery_dataset_id" {
  description = "The ID of the BigQuery dataset"
  value       = google_bigquery_dataset.your_dataset.dataset_id
}

output "dataproc_cluster_name" {
  description = "The name of the Dataproc cluster"
  value       = google_dataproc_cluster.your_cluster.name
}

output "composer_environment_name" {
  description = "The name of the Cloud Composer (Airflow) environment"
  value       = google_composer_environment.your_airflow.name
}

output "composer_airflow_uri" {
  description = "The Airflow UI URI"
  value       = google_composer_environment.your_airflow.config[0].airflow_uri
}