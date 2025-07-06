#!/usr/bin/env bash

set -e

# --------------------
# MindMirror Infra Defaults
# --------------------

PROJECT_ID="mindmirror-69"
PROJECT_NUMERICAL_ID="3858903851"
REGION="us-east4"
STATE_BUCKET="mindmirror-tofu-state"
ARTIFACT_REPO="mindmirror"
GITHUB_REPO="Peleke/MindMirror"
WIF_POOL="github-pool"
WIF_PROVIDER="github-provider"
SA="open-tofu-deployer"

echo "== Enabling required services =="
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com \
  redis.googleapis.com

echo "== Creating GCS bucket for tofu state =="
if ! gsutil ls -b gs://${STATE_BUCKET} >/dev/null 2>&1; then
  gsutil mb -p $PROJECT_ID -l $REGION gs://${STATE_BUCKET}
else
  echo "Bucket $STATE_BUCKET already exists"
fi

echo "== Creating Artifact Registry repo =="
if ! gcloud artifacts repositories describe $ARTIFACT_REPO --location=$REGION >/dev/null 2>&1; then
  gcloud artifacts repositories create $ARTIFACT_REPO \
    --repository-format=docker \
    --location=$REGION \
    --description="Docker images for MindMirror"
else
  echo "Artifact Registry $ARTIFACT_REPO already exists"
fi

echo "== Creating service account $SA =="
if ! gcloud iam service-accounts describe ${SA}@${PROJECT_ID}.iam.gserviceaccount.com >/dev/null 2>&1; then
  gcloud iam service-accounts create $SA \
    --description="Deploy OpenTofu infra" \
    --display-name="OpenTofu Deployer"
else
  echo "Service account $SA already exists"
fi

echo "== Assigning IAM roles to $SA =="
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.reader"

echo "== Creating Workload Identity Pool $WIF_POOL =="
if ! gcloud iam workload-identity-pools describe $WIF_POOL --location="global" >/dev/null 2>&1; then
  gcloud iam workload-identity-pools create $WIF_POOL \
    --location="global" \
    --display-name="GitHub Pool"
else
  echo "Workload Identity Pool $WIF_POOL already exists"
fi

echo "== Creating Workload Identity Provider $WIF_PROVIDER =="
if ! gcloud iam workload-identity-pools providers describe $WIF_PROVIDER \
     --location="global" --workload-identity-pool=$WIF_POOL >/dev/null 2>&1; then
  gcloud iam workload-identity-pools providers create-oidc $WIF_PROVIDER \
    --workload-identity-pool=$WIF_POOL \
    --location="global" \
    --display-name="GitHub Provider" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
    --attribute-condition="attribute.repository == 'Peleke/MindMirror'" \
    --issuer-uri="https://token.actions.githubusercontent.com"
else
  echo "Workload Identity Provider $WIF_PROVIDER already exists"
fi

echo "== Binding $SA to GitHub repo for WIF =="
gcloud iam service-accounts add-iam-policy-binding ${SA}@${PROJECT_ID}.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMERICAL_ID}/locations/global/workloadIdentityPools/${WIF_POOL}/attribute.repository/${GITHUB_REPO}"

echo "== Bootstrap complete ✅ =="
