#!/bin/bash
set -e

# MindMirror Production: Secret Manager Setup
# This script creates all required secrets in Google Secret Manager

echo "🔐 MindMirror Production - Secret Manager Setup"
echo "================================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Check if project is set
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
  error "No GCP project set. Run: gcloud config set project PROJECT_ID"
fi

info "Setting up secrets for project: $PROJECT_ID"

# Function to create or update secret
create_secret() {
  local secret_name=$1
  local secret_description=$2
  local prompt_text=$3
  local is_multiline=${4:-false}

  echo ""
  info "Setting up secret: $secret_name"
  echo "  Description: $secret_description"

  # Check if secret exists
  if gcloud secrets describe "$secret_name" --project="$PROJECT_ID" &>/dev/null; then
    warn "Secret $secret_name already exists"
    read -p "Update with new value? (y/n): " update
    if [[ "$update" != "y" ]]; then
      info "Skipping $secret_name"
      return
    fi
  else
    # Create secret
    gcloud secrets create "$secret_name" \
      --replication-policy="automatic" \
      --project="$PROJECT_ID" || error "Failed to create secret $secret_name"
  fi

  # Get secret value
  if [ "$is_multiline" = true ]; then
    echo "$prompt_text"
    echo "  (Press Ctrl+D when done)"
    secret_value=$(cat)
  else
    read -sp "$prompt_text: " secret_value
    echo ""
  fi

  if [ -z "$secret_value" ]; then
    warn "Empty value provided, skipping"
    return
  fi

  # Add secret version
  echo -n "$secret_value" | gcloud secrets versions add "$secret_name" \
    --data-file=- \
    --project="$PROJECT_ID" || error "Failed to add secret version"

  info "✅ Secret $secret_name configured"
}

# Check for required APIs
info "Checking if Secret Manager API is enabled..."
if ! gcloud services list --enabled --filter="name:secretmanager.googleapis.com" --project="$PROJECT_ID" | grep -q secretmanager; then
  warn "Secret Manager API not enabled. Enabling now..."
  gcloud services enable secretmanager.googleapis.com --project="$PROJECT_ID"
  sleep 5
fi

echo ""
echo "================================================"
echo "You will be prompted to enter values for each secret."
echo "Press Enter to skip a secret (keep existing value)."
echo "================================================"

# Supabase Secrets
echo ""
info "📦 SUPABASE CONFIGURATION"
info "These values come from your Supabase project settings"
info "URL: https://app.supabase.com/project/_/settings/database"

create_secret "SUPABASE_URL" \
  "Supabase project URL" \
  "Enter Supabase URL (e.g., https://xxxxx.supabase.co)"

create_secret "SUPABASE_ANON_KEY" \
  "Supabase anonymous key (public)" \
  "Enter Supabase anon key"

create_secret "SUPABASE_SERVICE_ROLE_KEY" \
  "Supabase service role key (private)" \
  "Enter Supabase service role key"

create_secret "SUPABASE_JWT_SECRET" \
  "JWT signing secret" \
  "Enter Supabase JWT secret"

create_secret "DATABASE_URL" \
  "PostgreSQL connection string" \
  "Enter DATABASE_URL (postgres://...)" \
  false

create_secret "SUPABASE_CA_CERT_PATH" \
  "Database SSL certificate path" \
  "Enter CA cert path (usually empty for Supabase cloud)"

# External Service Secrets
echo ""
info "🤖 EXTERNAL SERVICES"

create_secret "OPENAI_API_KEY" \
  "OpenAI API key for LLM and embeddings" \
  "Enter OpenAI API key (sk-...)"

create_secret "QDRANT_URL" \
  "Qdrant vector database URL" \
  "Enter Qdrant URL (e.g., https://xxxxx.qdrant.io)"

create_secret "QDRANT_API_KEY" \
  "Qdrant API key" \
  "Enter Qdrant API key"

create_secret "REDIS_URL" \
  "Redis connection string" \
  "Enter Redis URL (e.g., redis://...)"

# Internal Secrets
echo ""
info "🔑 INTERNAL SECRETS"

create_secret "REINDEX_SECRET_KEY" \
  "Secret key for journal reindexing endpoint" \
  "Enter reindex secret key (or press Enter to generate)"

if ! gcloud secrets versions list REINDEX_SECRET_KEY --limit=1 --project="$PROJECT_ID" &>/dev/null; then
  # Generate random key if not provided
  RANDOM_KEY=$(openssl rand -hex 32)
  echo -n "$RANDOM_KEY" | gcloud secrets versions add REINDEX_SECRET_KEY \
    --data-file=- \
    --project="$PROJECT_ID"
  info "Generated random reindex secret key"
fi

# Service URLs (will be populated after deployment)
echo ""
info "🌐 SERVICE URLS"
info "These will be updated after services are deployed"

for service in AGENT_SERVICE JOURNAL_SERVICE HABITS_SERVICE MEALS_SERVICE CELERY_WORKER VOUCHERS_WEB_BASE; do
  secret_name="${service}_URL"

  if ! gcloud secrets describe "$secret_name" --project="$PROJECT_ID" &>/dev/null; then
    gcloud secrets create "$secret_name" \
      --replication-policy="automatic" \
      --project="$PROJECT_ID" || warn "Failed to create $secret_name"

    # Add placeholder value
    echo -n "https://pending-deployment" | gcloud secrets versions add "$secret_name" \
      --data-file=- \
      --project="$PROJECT_ID" || warn "Failed to add placeholder"
  fi
done

# Summary
echo ""
echo "================================================"
echo -e "${GREEN}✅ Secret Manager Setup Complete!${NC}"
echo "================================================"
echo ""
info "Secrets created in project: $PROJECT_ID"
info "View secrets: https://console.cloud.google.com/security/secret-manager?project=$PROJECT_ID"
echo ""
warn "IMPORTANT: Service URLs are currently placeholders."
warn "They will be updated automatically after first deployment."
echo ""
info "Next steps:"
echo "  1. Verify secrets in GCP Console"
echo "  2. Run Supabase setup script"
echo "  3. Deploy infrastructure with OpenTofu"
