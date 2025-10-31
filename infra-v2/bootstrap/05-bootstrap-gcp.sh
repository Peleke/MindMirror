#!/bin/bash
set -e

# Swae Production: GCP Bootstrap
# This is the equivalent of infra/bootstrap.sh but for infra-v2

echo "🚀 Swae Production - GCP Infrastructure Bootstrap"
echo "=================================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# Configuration
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
REGION="${REGION:-us-central1}"
STATE_BUCKET="${STATE_BUCKET:-mindmirror-tofu-state}"
ARTIFACT_REGISTRY="${ARTIFACT_REGISTRY:-swae}"

# Validate project is set
if [ -z "$PROJECT_ID" ]; then
  error "No GCP project set. Run: gcloud config set project PROJECT_ID"
fi

info "Configuration:"
echo "  Project: $PROJECT_ID"
echo "  Region: $REGION"
echo "  State Bucket: $STATE_BUCKET"
echo "  Artifact Registry: $ARTIFACT_REGISTRY"
echo ""
read -p "Continue? (y/n): " confirm
[[ "$confirm" != "y" ]] && error "Aborted by user"

# Step 1: Enable required APIs
step "1/5: Enabling required GCP APIs"
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
  info "Enabling $api..."
  gcloud services enable "$api" --project="$PROJECT_ID" 2>/dev/null || warn "Already enabled: $api"
done

info "✅ All APIs enabled"

# Step 2: Create GCS state bucket
step "2/5: Creating OpenTofu state bucket"

if gsutil ls "gs://$STATE_BUCKET" &>/dev/null; then
  warn "Bucket gs://$STATE_BUCKET already exists"
else
  info "Creating bucket: gs://$STATE_BUCKET"
  gsutil mb -p "$PROJECT_ID" -l "$REGION" "gs://$STATE_BUCKET"

  # Enable versioning for state backups
  gsutil versioning set on "gs://$STATE_BUCKET"

  info "✅ State bucket created with versioning enabled"
fi

# Step 3: Create Artifact Registry
step "3/5: Creating Artifact Registry for Docker images"

if gcloud artifacts repositories describe "$ARTIFACT_REGISTRY" \
  --location="$REGION" \
  --project="$PROJECT_ID" &>/dev/null; then
  warn "Artifact Registry $ARTIFACT_REGISTRY already exists"
else
  info "Creating Artifact Registry: $ARTIFACT_REGISTRY"
  gcloud artifacts repositories create "$ARTIFACT_REGISTRY" \
    --repository-format=docker \
    --location="$REGION" \
    --description="Swae production container images" \
    --project="$PROJECT_ID" || warn "Failed to create registry"

  info "✅ Artifact Registry created"
fi

# Step 4: Create service account for OpenTofu
step "4/5: Creating service account for OpenTofu deployments"

SA_NAME="tofu-deployer"
SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

if gcloud iam service-accounts describe "$SA_EMAIL" --project="$PROJECT_ID" &>/dev/null; then
  warn "Service account $SA_EMAIL already exists"
else
  info "Creating service account: $SA_NAME"
  gcloud iam service-accounts create "$SA_NAME" \
    --display-name="OpenTofu Deployment Service Account" \
    --project="$PROJECT_ID" || warn "Failed to create service account"
fi

# Grant necessary roles
info "Granting IAM roles to service account..."

REQUIRED_ROLES=(
  "roles/run.admin"
  "roles/iam.serviceAccountUser"
  "roles/storage.admin"
  "roles/secretmanager.admin"
  "roles/artifactregistry.admin"
  "roles/compute.networkAdmin"
  "roles/pubsub.admin"
)

for role in "${REQUIRED_ROLES[@]}"; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SA_EMAIL" \
    --role="$role" \
    --condition=None \
    --project="$PROJECT_ID" &>/dev/null || warn "Role $role may already be bound"
done

info "✅ Service account configured"

# Step 5: Setup Workload Identity Federation (for GitHub Actions)
step "5/5: Setting up Workload Identity Federation"

POOL_NAME="github-actions"
PROVIDER_NAME="github-oidc"

# Create workload identity pool
if gcloud iam workload-identity-pools describe "$POOL_NAME" \
  --location="global" \
  --project="$PROJECT_ID" &>/dev/null; then
  warn "Workload identity pool $POOL_NAME already exists"
else
  info "Creating workload identity pool: $POOL_NAME"
  gcloud iam workload-identity-pools create "$POOL_NAME" \
    --location="global" \
    --display-name="GitHub Actions Pool" \
    --project="$PROJECT_ID" || warn "Failed to create pool"
fi

# Create OIDC provider
if gcloud iam workload-identity-pools providers describe "$PROVIDER_NAME" \
  --workload-identity-pool="$POOL_NAME" \
  --location="global" \
  --project="$PROJECT_ID" &>/dev/null; then
  warn "OIDC provider $PROVIDER_NAME already exists"
else
  info "Creating GitHub OIDC provider: $PROVIDER_NAME"
  gcloud iam workload-identity-pools providers create-oidc "$PROVIDER_NAME" \
    --workload-identity-pool="$POOL_NAME" \
    --location="global" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
    --project="$PROJECT_ID" || warn "Failed to create provider"
fi

# Grant service account access to GitHub Actions
# Note: You'll need to update this with your actual GitHub repo
GITHUB_REPO="${GITHUB_REPO:-your-org/swae}"
warn "IMPORTANT: Update GITHUB_REPO variable with your actual repository"
info "Example: export GITHUB_REPO='your-org/swae' before running this script"

if [ "$GITHUB_REPO" != "your-org/swae" ]; then
  info "Granting GitHub Actions access for repo: $GITHUB_REPO"

  gcloud iam service-accounts add-iam-policy-binding "$SA_EMAIL" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')/locations/global/workloadIdentityPools/$POOL_NAME/attribute.repository/$GITHUB_REPO" \
    --project="$PROJECT_ID" || warn "Failed to grant WIF access"
fi

info "✅ Workload Identity Federation configured"

# Summary
echo ""
echo "=================================================="
echo -e "${GREEN}✅ GCP Bootstrap Complete!${NC}"
echo "=================================================="
echo ""
echo "Resources created:"
echo "  • State bucket: gs://$STATE_BUCKET"
echo "  • Artifact Registry: $REGION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REGISTRY"
echo "  • Service account: $SA_EMAIL"
echo "  • Workload Identity Pool: $POOL_NAME"
echo ""
info "Next steps:"
echo "  1. Run: ./01-setup-secrets.sh"
echo "  2. Run: ./02-setup-supabase.sh"
echo "  3. Run: ./03-run-migrations.sh"
echo "  4. Run: ./04-apply-rls-policies.sh"
echo "  5. Deploy infrastructure: cd ../ && tofu init && tofu apply"
echo ""
warn "IMPORTANT: Update GITHUB_REPO in this script or environment for CI/CD"
