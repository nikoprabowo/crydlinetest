terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  credentials = var.credentials_path
  project     = var.project_id
  region      = var.region
}

# ================================================
# Google Cloud Storage (Bucket)
# ================================================
resource "google_storage_bucket" "your_bucket" {
  name                        = var.bucket_name
  location                    = upper(var.region)
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  force_destroy               = true
}

# ================================================
# BigQuery (Dataset)
# ================================================
resource "google_bigquery_dataset" "your_dataset" {
  dataset_id    = var.dataset_id
  friendly_name = var.dataset_friendly_name
  location      = var.region
}

# ================================================
# Dataproc (Apache Spark)
# ================================================
resource "google_dataproc_cluster" "your_cluster" {
  name    = var.cluster_name
  project = var.project_id
  region  = var.region

  cluster_config {
    staging_bucket = google_storage_bucket.your_bucket.name

    gce_cluster_config {
      service_account        = var.service_account
      service_account_scopes = ["https://www.googleapis.com/auth/cloud-platform"]
      zone                   = var.zone
      internal_ip_only       = true
    }

    master_config {
      num_instances = 1
      machine_type  = var.machine_type
      disk_config {
        boot_disk_type    = "pd-balanced"
        boot_disk_size_gb = 30
      }
    }

    worker_config {
      num_instances = 0
    }

    software_config {
      image_version = "2.1-ubuntu20"
      optional_components = []
    }

    endpoint_config {
      enable_http_port_access = true
    }
  }
}

# ================================================
# Google Cloud Composer (Managed Apache Airflow)
# ================================================
resource "google_composer_environment" "your_airflow" {
  name   = var.composer_name
  region = var.region

  config {
    software_config {
      image_version = var.composer_image_version
    }

    node_config {
      service_account = var.service_account
      network         = "default"
    }

    environment_size = "ENVIRONMENT_SIZE_SMALL"
  }
}