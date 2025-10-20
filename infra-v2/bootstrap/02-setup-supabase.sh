#!/bin/bash
set -e

# MindMirror Production: Supabase Setup
# This script creates a Supabase production project and configures it

echo "🗄️  MindMirror Production - Supabase Setup"
echo "=========================================="

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

# Check for Supabase CLI
if ! command -v supabase &>/dev/null; then
  error "Supabase CLI not found. Install: npm install -g supabase"
fi

info "Supabase CLI found: $(supabase --version)"

# Configuration
SUPABASE_PROJECT_NAME="${SUPABASE_PROJECT_NAME:-mindmirror-production}"
SUPABASE_REGION="${SUPABASE_REGION:-us-east-1}"
SUPABASE_PLAN="${SUPABASE_PLAN:-free}"  # free or pro

echo ""
echo "Configuration:"
echo "  Project Name: $SUPABASE_PROJECT_NAME"
echo "  Region: $SUPABASE_REGION"
echo "  Plan: $SUPABASE_PLAN"
echo ""

# Step 1: Login to Supabase
step "1/5: Supabase Authentication"
info "Checking Supabase login status..."

if ! supabase projects list &>/dev/null; then
  warn "Not logged in to Supabase"
  info "Opening browser for authentication..."
  supabase login || error "Failed to login to Supabase"
fi

info "✅ Authenticated with Supabase"

# Step 2: Check if project exists
step "2/5: Checking for existing project"

existing_project=$(supabase projects list --output json 2>/dev/null | jq -r ".[] | select(.name == \"$SUPABASE_PROJECT_NAME\") | .id" || echo "")

if [ -n "$existing_project" ]; then
  warn "Project '$SUPABASE_PROJECT_NAME' already exists (ID: $existing_project)"
  read -p "Use existing project? (y/n): " use_existing

  if [[ "$use_existing" == "y" ]]; then
    PROJECT_ID="$existing_project"
    info "Using existing project: $PROJECT_ID"
  else
    error "Please choose a different project name"
  fi
else
  # Step 3: Create project
  step "3/5: Creating Supabase project"
  warn "This will create a new Supabase project. This may take 2-3 minutes."
  read -p "Continue? (y/n): " confirm
  [[ "$confirm" != "y" ]] && error "Aborted by user"

  info "Creating project: $SUPABASE_PROJECT_NAME"

  # Note: Supabase CLI doesn't support programmatic project creation yet
  # Users must create via dashboard
  echo ""
  warn "MANUAL STEP REQUIRED:"
  echo "  1. Open: https://app.supabase.com/new"
  echo "  2. Create project with name: $SUPABASE_PROJECT_NAME"
  echo "  3. Select region: $SUPABASE_REGION"
  echo "  4. Generate a strong database password (save it!)"
  echo "  5. Wait for project to finish provisioning (~2 minutes)"
  echo ""
  read -p "Press Enter after project is created..."

  # Refresh project list
  info "Fetching project details..."
  PROJECT_ID=$(supabase projects list --output json | jq -r ".[] | select(.name == \"$SUPABASE_PROJECT_NAME\") | .id")

  if [ -z "$PROJECT_ID" ]; then
    error "Project not found. Please verify it was created in the dashboard."
  fi

  info "✅ Project found: $PROJECT_ID"
fi

# Step 4: Get project credentials
step "4/5: Retrieving project credentials"

info "Fetching API keys and connection details..."

# Get project details
PROJECT_URL=$(supabase projects list --output json | jq -r ".[] | select(.id == \"$PROJECT_ID\") | .url")

if [ -z "$PROJECT_URL" ]; then
  error "Failed to get project URL"
fi

info "Project URL: $PROJECT_URL"

# Get API keys (requires manual retrieval)
echo ""
warn "API Keys must be retrieved manually:"
echo "  1. Open: https://app.supabase.com/project/$PROJECT_ID/settings/api"
echo "  2. Copy the following values:"
echo "     - anon/public key"
echo "     - service_role key (keep this secret!)"
echo "     - JWT Secret (in JWT Settings)"
echo "  3. Database URL: https://app.supabase.com/project/$PROJECT_ID/settings/database"
echo ""

read -sp "Paste anon key: " ANON_KEY
echo ""
read -sp "Paste service_role key: " SERVICE_ROLE_KEY
echo ""
read -sp "Paste JWT secret: " JWT_SECRET
echo ""
read -p "Paste database URL (postgres://...): " DATABASE_URL

# Validate inputs
[ -z "$ANON_KEY" ] && error "Anon key required"
[ -z "$SERVICE_ROLE_KEY" ] && error "Service role key required"
[ -z "$JWT_SECRET" ] && error "JWT secret required"
[ -z "$DATABASE_URL" ] && error "Database URL required"

# Step 5: Store in GCP Secret Manager (if available)
step "5/5: Storing credentials"

if command -v gcloud &>/dev/null; then
  PROJECT_GCP=$(gcloud config get-value project 2>/dev/null)

  if [ -n "$PROJECT_GCP" ]; then
    info "Storing credentials in GCP Secret Manager (project: $PROJECT_GCP)"

    echo -n "$PROJECT_URL" | gcloud secrets versions add SUPABASE_URL --data-file=- --project="$PROJECT_GCP" 2>/dev/null || \
      warn "Failed to update SUPABASE_URL (may need to create secret first)"

    echo -n "$ANON_KEY" | gcloud secrets versions add SUPABASE_ANON_KEY --data-file=- --project="$PROJECT_GCP" 2>/dev/null || \
      warn "Failed to update SUPABASE_ANON_KEY"

    echo -n "$SERVICE_ROLE_KEY" | gcloud secrets versions add SUPABASE_SERVICE_ROLE_KEY --data-file=- --project="$PROJECT_GCP" 2>/dev/null || \
      warn "Failed to update SUPABASE_SERVICE_ROLE_KEY"

    echo -n "$JWT_SECRET" | gcloud secrets versions add SUPABASE_JWT_SECRET --data-file=- --project="$PROJECT_GCP" 2>/dev/null || \
      warn "Failed to update SUPABASE_JWT_SECRET"

    echo -n "$DATABASE_URL" | gcloud secrets versions add DATABASE_URL --data-file=- --project="$PROJECT_GCP" 2>/dev/null || \
      warn "Failed to update DATABASE_URL"

    info "✅ Credentials stored in Secret Manager"
  fi
fi

# Save to local env file
ENV_FILE="env.production.supabase"
cat > "$ENV_FILE" <<EOF
# MindMirror Production - Supabase Configuration
# Generated: $(date)
# WARNING: This file contains secrets - do NOT commit to git

export SUPABASE_PROJECT_ID="$PROJECT_ID"
export SUPABASE_URL="$PROJECT_URL"
export SUPABASE_ANON_KEY="$ANON_KEY"
export SUPABASE_SERVICE_ROLE_KEY="$SERVICE_ROLE_KEY"
export SUPABASE_JWT_SECRET="$JWT_SECRET"
export DATABASE_URL="$DATABASE_URL"
EOF

info "Credentials saved to: $ENV_FILE"

# Summary
echo ""
echo "=========================================="
echo -e "${GREEN}✅ Supabase Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Project Details:"
echo "  Project ID: $PROJECT_ID"
echo "  Project URL: $PROJECT_URL"
echo "  Dashboard: https://app.supabase.com/project/$PROJECT_ID"
echo ""
echo "Credentials stored in:"
echo "  - GCP Secret Manager (if available)"
echo "  - Local file: $ENV_FILE"
echo ""
warn "IMPORTANT: Keep $ENV_FILE secure and do NOT commit to git!"
echo ""
info "Next steps:"
echo "  1. Run database migrations: ./scripts/03-run-migrations.sh"
echo "  2. Apply RLS policies: ./scripts/04-apply-rls-policies.sh"
echo "  3. Deploy infrastructure: make production-deploy"
