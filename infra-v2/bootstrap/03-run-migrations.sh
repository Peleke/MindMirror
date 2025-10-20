#!/bin/bash
set -e

# MindMirror Production: Database Migrations
# This script runs all Alembic migrations for production database

echo "📊 MindMirror Production - Database Migrations"
echo "=============================================="

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

# Check prerequisites
command -v poetry >/dev/null 2>&1 || error "Poetry not found. Install from https://python-poetry.org"

# Get DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
  warn "DATABASE_URL not set in environment"

  # Try to get from GCP Secret Manager
  if command -v gcloud &>/dev/null; then
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
    if [ -n "$PROJECT_ID" ]; then
      info "Fetching DATABASE_URL from Secret Manager..."
      DATABASE_URL=$(gcloud secrets versions access latest --secret="DATABASE_URL" --project="$PROJECT_ID" 2>/dev/null)
    fi
  fi

  # Still not found - prompt user
  if [ -z "$DATABASE_URL" ]; then
    read -p "Enter DATABASE_URL (postgres://...): " DATABASE_URL
  fi
fi

[ -z "$DATABASE_URL" ] && error "DATABASE_URL is required"

info "Using database: ${DATABASE_URL%%@*}@***"  # Mask password

# Export for Alembic
export DATABASE_URL

# Migration directories
MIGRATIONS=(
  "src/alembic-config"          # Agent, Journal, Habits (shared DB)
  "habits_service/alembic"      # Habits service
  "movements_service/alembic"   # Movements service
  "practices_service/alembic"   # Practices service
  "users_service/alembic"       # Users service
)

echo ""
warn "This will run migrations on the PRODUCTION database!"
echo "  Database: ${DATABASE_URL%%@*}@***"
echo ""
read -p "Continue? (y/n): " confirm
[[ "$confirm" != "y" ]] && error "Aborted by user"

# Run migrations for each service
for migration_dir in "${MIGRATIONS[@]}"; do
  if [ ! -d "$migration_dir" ]; then
    warn "Migration directory not found: $migration_dir (skipping)"
    continue
  fi

  step "Running migrations: $migration_dir"

  cd "$migration_dir"

  # Check if poetry.lock exists (indicates Poetry project)
  if [ -f "pyproject.toml" ]; then
    info "Installing dependencies with Poetry..."
    poetry install --no-interaction || warn "Failed to install dependencies"

    info "Running Alembic upgrade..."
    poetry run alembic upgrade head || error "Migration failed for $migration_dir"
  else
    # Try direct alembic command
    info "Running Alembic upgrade (no Poetry)..."
    alembic upgrade head || error "Migration failed for $migration_dir"
  fi

  info "✅ Migrations complete: $migration_dir"

  # Return to root
  cd - >/dev/null
  echo ""
done

# Summary
echo "=============================================="
echo -e "${GREEN}✅ All Migrations Complete!${NC}"
echo "=============================================="
echo ""
info "Database schema is up to date"
info "Next step: Apply RLS policies (./scripts/04-apply-rls-policies.sh)"
