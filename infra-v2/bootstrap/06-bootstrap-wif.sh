#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# Staging
export STAGING_PROJECT="mindmirror-69"
export STAGING_PROJECT_NUM=$(gcloud projects describe $STAGING_PROJECT --format='value(projectNumber)')
export GITHUB_REPO="Peleke/MindMirror"
export SA_NAME="github-actions-staging"
export SA_EMAIL="${SA_NAME}@${STAGING_PROJECT}.iam.gserviceaccount.com"

echo "=================================================="
info "Setting up Workload Identity Federation for GitHub Actions"
echo "  Project: $STAGING_PROJECT"
echo "  GitHub Repo: $GITHUB_REPO"
echo "  Service Account: $SA_EMAIL"
echo "=================================================="
echo ""

# Step 1: Create service account if it doesn't exist
step "1/4: Creating service account"

if gcloud iam service-accounts describe "$SA_EMAIL" --project="$STAGING_PROJECT" &>/dev/null; then
  warn "Service account $SA_EMAIL already exists"
else
  info "Creating service account: $SA_NAME"
  gcloud iam service-accounts create "$SA_NAME" \
    --display-name="GitHub Actions Staging Deployer" \
    --project="$STAGING_PROJECT"

  info "✅ Service account created"
fi

# Step 2: Grant necessary roles to service account
step "2/4: Granting IAM roles to service account"

REQUIRED_ROLES=(
  "roles/run.admin"
  "roles/iam.serviceAccountUser"
  "roles/iam.serviceAccountAdmin"
  "roles/storage.admin"
  "roles/secretmanager.admin"
  "roles/artifactregistry.admin"
  "roles/compute.networkAdmin"
  "roles/pubsub.admin"
)

for role in "${REQUIRED_ROLES[@]}"; do
  gcloud projects add-iam-policy-binding "$STAGING_PROJECT" \
    --member="serviceAccount:$SA_EMAIL" \
    --role="$role" \
    --condition=None &>/dev/null || warn "Role $role may already be bound"
done

info "✅ IAM roles configured"

# Step 3: Create WIF pool + provider
step "3/4: Creating Workload Identity Pool and Provider"

if gcloud iam workload-identity-pools describe "github-pool" \
  --location="global" \
  --project="${STAGING_PROJECT}" &>/dev/null; then
  warn "Workload identity pool 'github-pool' already exists"
else
  info "Creating workload identity pool: github-pool"
  gcloud iam workload-identity-pools create "github-pool" \
    --project="${STAGING_PROJECT}" \
    --location="global" \
    --display-name="GitHub Actions Pool"
  info "✅ Pool created"
fi

if gcloud iam workload-identity-pools providers describe "github-oidc" \
  --workload-identity-pool="github-pool" \
  --location="global" \
  --project="${STAGING_PROJECT}" &>/dev/null; then
  warn "OIDC provider 'github-oidc' already exists"
else
  info "Creating GitHub OIDC provider: github-oidc"
  gcloud iam workload-identity-pools providers create-oidc "github-oidc" \
    --project="${STAGING_PROJECT}" \
    --location="global" \
    --workload-identity-pool="github-pool" \
    --display-name="GitHub OIDC Provider" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.ref=assertion.ref" \
    --attribute-condition="assertion.repository_owner == '$(echo $GITHUB_REPO | cut -d'/' -f1)'"
  info "✅ OIDC provider created"
fi

# Step 4: Bind service account to WIF
step "4/4: Binding service account to Workload Identity Pool"

info "Granting workloadIdentityUser role to GitHub Actions"
gcloud iam service-accounts add-iam-policy-binding "$SA_EMAIL" \
  --project="${STAGING_PROJECT}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${STAGING_PROJECT_NUM}/locations/global/workloadIdentityPools/github-pool/attribute.repository/${GITHUB_REPO}" \
  &>/dev/null || warn "Binding may already exist"

info "✅ Service account bound to WIF pool"

# Summary
echo ""
echo "=================================================="
echo -e "${GREEN}✅ WIF Setup Complete!${NC}"
echo "=================================================="
echo ""
echo "Configuration:"
echo "  • Service Account: $SA_EMAIL"
echo "  • WIF Pool: github-pool"
echo "  • WIF Provider: github-oidc"
echo "  • GitHub Repo: $GITHUB_REPO"
echo ""
info "Next steps:"
echo "  1. Add these secrets to your GitHub repository:"
echo "     - GCP_STAGING_PROJECT_NUM: $STAGING_PROJECT_NUM"
echo "     - GCP_PRODUCTION_PROJECT_NUM: (from production bootstrap)"
echo "  2. Test WIF authentication with: gh workflow run test-wif-auth.yml"
echo ""
