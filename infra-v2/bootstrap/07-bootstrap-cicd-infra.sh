#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
step() { echo -e "${BLUE}[STEP]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Parse environment argument (default: staging)
ENVIRONMENT="${1:-staging}"

if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
  error "Invalid environment: $ENVIRONMENT"
  echo "Usage: $0 [staging|production]"
  echo "  Default: staging"
  exit 1
fi

# Set project and resources based on environment
if [[ "$ENVIRONMENT" == "production" ]]; then
  export PROJECT_ID="mindmirror-prod"
  export REGION="us-east4"
  export STATE_BUCKET="mindmirror-tofu-state"
  export ARTIFACT_REGISTRY="mindmirror"
else
  export PROJECT_ID="mindmirror-69"
  export REGION="us-east4"
  export STATE_BUCKET="mindmirror-tofu-state-staging"
  export ARTIFACT_REGISTRY="mindmirror"
fi

echo "=================================================="
info "Setting up CI/CD Infrastructure for GitHub Actions"
echo "  Environment: $ENVIRONMENT"
echo "  Project: $PROJECT_ID"
echo "  Region: $REGION"
echo "  State Bucket: $STATE_BUCKET"
echo "  Artifact Registry: $ARTIFACT_REGISTRY"
echo "=================================================="
echo ""

# Step 1: Enable required APIs
step "1/3: Enabling required GCP APIs"
info "This may take 2-3 minutes..."

REQUIRED_APIS=(
  "compute.googleapis.com"
  "run.googleapis.com"
  "secretmanager.googleapis.com"
  "artifactregistry.googleapis.com"
  "storage.googleapis.com"
  "cloudresourcemanager.googleapis.com"
  "iam.googleapis.com"
  "iamcredentials.googleapis.com"
  "sts.googleapis.com"
  "pubsub.googleapis.com"
  "vpcaccess.googleapis.com"
)

for api in "${REQUIRED_APIS[@]}"; do
  gcloud services enable "$api" --project="$PROJECT_ID" 2>/dev/null || warn "$api already enabled"
done

info "✅ All APIs enabled"

# Step 2: Create GCS state bucket
step "2/3: Creating Terraform/OpenTofu state bucket"

if gcloud storage buckets describe "gs://$STATE_BUCKET" --project="$PROJECT_ID" &>/dev/null; then
  warn "Bucket gs://$STATE_BUCKET already exists"
else
  info "Creating bucket: gs://$STATE_BUCKET"
  gcloud storage buckets create "gs://$STATE_BUCKET" \
    --project="$PROJECT_ID" \
    --location="$REGION" \
    --uniform-bucket-level-access

  # Enable versioning for state backups
  gcloud storage buckets update "gs://$STATE_BUCKET" \
    --versioning

  info "✅ State bucket created with versioning enabled"
fi

# Step 3: Create Artifact Registry
step "3/3: Creating Artifact Registry for Docker images"

if gcloud artifacts repositories describe "$ARTIFACT_REGISTRY" \
  --location="$REGION" \
  --project="$PROJECT_ID" &>/dev/null; then
  warn "Artifact Registry $ARTIFACT_REGISTRY already exists"
else
  info "Creating Artifact Registry: $ARTIFACT_REGISTRY"
  gcloud artifacts repositories create "$ARTIFACT_REGISTRY" \
    --repository-format=docker \
    --location="$REGION" \
    --description="MindMirror $ENVIRONMENT container images" \
    --project="$PROJECT_ID"

  info "✅ Artifact Registry created"
fi

# Summary
echo ""
echo "=================================================="
echo -e "${GREEN}✅ CI/CD Infrastructure Complete!${NC}"
echo "=================================================="
echo ""
echo "Configuration:"
echo "  • State Bucket: gs://$STATE_BUCKET"
echo "  • Artifact Registry: $REGION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REGISTRY"
echo "  • Region: $REGION"
echo ""
info "Resources are ready for GitHub Actions workflows"
echo ""
