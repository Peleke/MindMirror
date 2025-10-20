#!/bin/bash
set -e

# MindMirror Production: GCP Project Creation
# This script creates and configures a new GCP project for production deployment

echo "🏗️  MindMirror Production - GCP Project Setup"
echo "=============================================="

# Configuration
PROJECT_ID="${PROJECT_ID:-mindmirror-prod-$(date +%s)}"
PROJECT_NAME="MindMirror Production"
BILLING_ACCOUNT_ID="${BILLING_ACCOUNT_ID:-}"
REGION="${REGION:-us-central1}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Check prerequisites
command -v gcloud >/dev/null 2>&1 || error "gcloud CLI not found. Install from https://cloud.google.com/sdk/docs/install"

# Step 1: Get billing account if not provided
if [ -z "$BILLING_ACCOUNT_ID" ]; then
  warn "No BILLING_ACCOUNT_ID provided. Listing available billing accounts..."
  gcloud beta billing accounts list
  echo ""
  read -p "Enter your billing account ID (format: XXXXXX-XXXXXX-XXXXXX): " BILLING_ACCOUNT_ID

  if [ -z "$BILLING_ACCOUNT_ID" ]; then
    error "Billing account ID is required"
  fi
fi

info "Configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Project Name: $PROJECT_NAME"
echo "  Billing Account: $BILLING_ACCOUNT_ID"
echo "  Region: $REGION"
echo ""
read -p "Continue with this configuration? (y/n): " confirm
[[ "$confirm" != "y" ]] && error "Aborted by user"

# Step 2: Create project
info "Creating GCP project: $PROJECT_ID"
if gcloud projects describe "$PROJECT_ID" &>/dev/null; then
  warn "Project $PROJECT_ID already exists. Using existing project."
else
  gcloud projects create "$PROJECT_ID" \
    --name="$PROJECT_NAME" \
    --set-as-default || error "Failed to create project"
  info "Project created successfully"
fi

# Step 3: Link billing account
info "Linking billing account to project"
gcloud beta billing projects link "$PROJECT_ID" \
  --billing-account="$BILLING_ACCOUNT_ID" || error "Failed to link billing account"

# Step 4: Set default project
info "Setting default project"
gcloud config set project "$PROJECT_ID"

# Step 5: Enable required APIs (subset - full enable happens in bootstrap.sh)
info "Enabling essential APIs (this may take 2-3 minutes)..."
gcloud services enable \
  cloudresourcemanager.googleapis.com \
  serviceusage.googleapis.com \
  iam.googleapis.com \
  --project="$PROJECT_ID" || warn "Some APIs may already be enabled"

# Step 6: Save configuration
CONFIG_FILE=".gcp-project-config"
cat > "$CONFIG_FILE" <<EOF
# MindMirror Production - GCP Configuration
# Generated: $(date)

export GCP_PROJECT_ID="$PROJECT_ID"
export GCP_REGION="$REGION"
export GCP_BILLING_ACCOUNT="$BILLING_ACCOUNT_ID"
EOF

info "Configuration saved to $CONFIG_FILE"
info "To use this project in future shells, run:"
echo "  source $CONFIG_FILE"

# Step 7: Output next steps
echo ""
echo "=============================================="
echo -e "${GREEN}✅ GCP Project Setup Complete!${NC}"
echo "=============================================="
echo ""
echo "Next steps:"
echo "  1. Run: cd infra && ./bootstrap.sh"
echo "  2. Create Supabase project"
echo "  3. Run production deployment"
echo ""
echo "Project Details:"
echo "  Project ID: $PROJECT_ID"
echo "  Console URL: https://console.cloud.google.com/home/dashboard?project=$PROJECT_ID"
