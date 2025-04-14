# ====================================
# 🔧 EDIT VARIABLES AS YOUR CONDITION
# ====================================

variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "yourprojectid"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "asia-southeast1"
}

variable "zone" {
  description = "GCP Zone"
  type        = string
  default     = "asia-southeast1-a"
}

variable "credentials_path" {
  description = "Path to service account JSON credentials"
  type        = string
  default     = "/workspace/auth/your-sa-key.json"
}

variable "bucket_name" {
  description = "Name of the GCS bucket"
  type        = string
  default     = "your-data-bucket"
}

variable "dataset_id" {
  description = "BigQuery Dataset ID"
  type        = string
  default     = "your_data"
}

variable "dataset_friendly_name" {
  description = "BigQuery Dataset Friendly Name"
  type        = string
  default     = "Your Data"
}

variable "cluster_name" {
  description = "Name of the Dataproc cluster"
  type        = string
  default     = "your-cluster"
}

variable "machine_type" {
  description = "Machine type for Dataproc master node"
  type        = string
  default     = "e2-standard-2"
}

variable "service_account" {
  description = "Service account email used in all resources"
  type        = string
  default     = "your-sa@yourprojectid.iam.gserviceaccount.com"
}

variable "composer_name" {
  description = "Cloud Composer (Airflow) Environment name"
  type        = string
  default     = "your-airflow"
}

variable "composer_image_version" {
  description = "Composer image version"
  type        = string
  default     = "composer-3-airflow-2.10.2"
}