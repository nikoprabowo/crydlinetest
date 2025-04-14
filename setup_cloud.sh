#!/bin/bash

# Exit if an error
set -e

# ===============================
# User Configuration (EDIT THIS)
# ===============================
PROJECT_ID="yourprojectid"         # 🔧 Replace with your GCP project ID
VM_USER="yourname"                 # 🔧 Replace with your VM username

# ===============================
# Derived Variables (NO EDIT NEEDED)
# ===============================
SERVICE_ACCOUNT_NAME="${PROJECT_ID}-sa"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
ZONE="asia-southeast1-a"
VM_NAME="${PROJECT_ID}-vm"
KEY_FILE="${HOME}/${SERVICE_ACCOUNT_NAME}-key.json"

# ===============================
# Set GCP Project
# ===============================
echo "📌 Setting GCP project..."
gcloud config set project $PROJECT_ID

# ===============================
# Enable GCP APIs
# ===============================
echo "✅ Enabling required GCP APIs..."
gcloud services enable \
    compute.googleapis.com \
    dataproc.googleapis.com \
    bigquery.googleapis.com \
    composer.googleapis.com \
    cloudresourcemanager.googleapis.com \
    iam.googleapis.com \
    storage.googleapis.com

# ===============================
# Create Service Account
# ===============================
echo "🔐 Creating service account: $SERVICE_ACCOUNT_NAME..."
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
    --description="Service Account for ${PROJECT_ID}" \
    --display-name="${PROJECT_ID} Service Account"

# ===============================
# Assign Roles to Service Account
# ===============================
echo "🔑 Assigning IAM roles..."
ROLES=(
  roles/editor
  roles/storage.admin
  roles/bigquery.admin
  roles/compute.admin
  roles/dataproc.admin
  roles/composer.admin
  roles/iam.serviceAccountUser
  roles/dataproc.worker
)

for ROLE in "${ROLES[@]}"; do
  echo "→ Assigning $ROLE..."
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="$ROLE"
done

# ===============================
# Create VM Instance
# ===============================
echo "💻 Creating VM instance: $VM_NAME..."
gcloud compute instances create $VM_NAME \
    --zone=$ZONE \
    --machine-type=e2-medium \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=30GB

# ===============================
# Create Service Account Key
# ===============================
echo "📄 Creating JSON key file for service account..."
gcloud iam service-accounts keys create $KEY_FILE \
    --iam-account=$SERVICE_ACCOUNT_EMAIL

# ===============================
# Copy Key File to VM
# ===============================
echo "📦 Copying key file to VM..."
gcloud compute scp $KEY_FILE ${VM_USER}@${VM_NAME}:~ --zone=$ZONE

echo "✅ All setup steps completed!"