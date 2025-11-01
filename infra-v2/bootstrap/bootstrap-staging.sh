#!/bin/bash
set -e

# Staging Bootstrap Orchestrator
# Runs all necessary scripts to set up staging environment

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

ENVIRONMENT="staging"

echo "=========================================================="
echo -e "${BLUE}MindMirror Staging Bootstrap${NC}"
echo "=========================================================="
echo ""
echo "This script will set up:"
echo "  1. CI/CD Infrastructure (Artifact Registry, State Bucket)"
echo "  2. Workload Identity Federation (Service Account, WIF Pool)"
echo "  3. Required APIs and permissions"
echo ""
echo -e "${YELLOW}Environment: $ENVIRONMENT${NC}"
echo -e "${YELLOW}Project: mindmirror-69${NC}"
echo ""
read -p "Continue? (y/n): " confirm
[[ "$confirm" != "y" ]] && { error "Aborted by user"; exit 1; }
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Step 1: Set up CI/CD infrastructure
step "STEP 1/2: Setting up CI/CD Infrastructure"
echo ""
"$SCRIPT_DIR/07-bootstrap-cicd-infra.sh" "$ENVIRONMENT"
echo ""
info "✅ CI/CD infrastructure complete"
echo ""

# Step 2: Set up Workload Identity Federation
step "STEP 2/2: Setting up Workload Identity Federation"
echo ""
"$SCRIPT_DIR/06-bootstrap-wif.sh" "$ENVIRONMENT"
echo ""
info "✅ Workload Identity Federation complete"
echo ""

# Final summary
echo "=========================================================="
echo -e "${GREEN}✅ Staging Bootstrap Complete!${NC}"
echo "=========================================================="
echo ""
echo "What was created:"
echo "  • GCS State Bucket: gs://mindmirror-tofu-state-staging"
echo "  • Artifact Registry: us-east4-docker.pkg.dev/mindmirror-69/mindmirror"
echo "  • Service Account: github-actions-staging@mindmirror-69.iam.gserviceaccount.com"
echo "  • WIF Pool: github-pool"
echo "  • WIF Provider: github-oidc"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Add GitHub repository secret:"
echo "     ${YELLOW}GCP_STAGING_PROJECT_NUM${NC}"
echo "     Value: Run this command to get it:"
echo "     ${YELLOW}gcloud projects describe mindmirror-69 --format='value(projectNumber)'${NC}"
echo ""
echo "  2. Test deployment workflow:"
echo "     ${YELLOW}git push origin staging${NC}"
echo ""
echo "  3. Monitor workflow execution:"
echo "     ${YELLOW}gh run list --workflow staging-deploy.yml --limit 1${NC}"
echo ""
