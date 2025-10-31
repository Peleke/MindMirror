#!/usr/bin/env bash
# scripts/save-urls-to-secrets.sh
# Saves service URLs to GCP Secret Manager
# Usage: ./scripts/save-urls-to-secrets.sh <environment> <urls_json_file>
# Example: ./scripts/save-urls-to-secrets.sh staging service-urls.json

set -euo pipefail

ENVIRONMENT="${1:-staging}"
URLS_FILE="${2:-service-urls.json}"

# Configuration per environment
case "$ENVIRONMENT" in
    staging)
        PROJECT_ID="mindmirror-69"
        SECRET_NAME="service-urls-staging"
        ;;
    production)
        PROJECT_ID="mindmirror-prod"
        SECRET_NAME="service-urls-production"
        ;;
    *)
        echo "❌ ERROR: Invalid environment '$ENVIRONMENT'"
        echo "Usage: $0 <staging|production> <urls_json_file>"
        exit 1
        ;;
esac

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔐 Saving Service URLs to Secret Manager"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Environment: ${ENVIRONMENT}"
echo "Project: ${PROJECT_ID}"
echo "Secret: ${SECRET_NAME}"
echo "Input File: ${URLS_FILE}"
echo ""

# Validate input file exists
if [ ! -f "${URLS_FILE}" ]; then
    echo "❌ ERROR: URLs file not found: ${URLS_FILE}"
    exit 1
fi

# Validate JSON format
if ! jq empty "${URLS_FILE}" 2>/dev/null; then
    echo "❌ ERROR: Invalid JSON in ${URLS_FILE}"
    exit 1
fi

echo "📋 URLs to save:"
jq '.' "${URLS_FILE}"
echo ""

# Check if secret exists
echo "🔍 Checking if secret exists..."
if gcloud secrets describe "${SECRET_NAME}" --project="${PROJECT_ID}" &>/dev/null; then
    echo "✅ Secret exists, adding new version..."

    # Add new version
    gcloud secrets versions add "${SECRET_NAME}" \
        --project="${PROJECT_ID}" \
        --data-file="${URLS_FILE}"

    echo "✅ Added new version to secret: ${SECRET_NAME}"
else
    echo "📝 Secret doesn't exist, creating..."

    # Create secret
    gcloud secrets create "${SECRET_NAME}" \
        --project="${PROJECT_ID}" \
        --replication-policy="automatic" \
        --data-file="${URLS_FILE}"

    echo "✅ Created secret: ${SECRET_NAME}"
fi

# Verify the saved content
echo ""
echo "🔍 Verifying saved content..."
SAVED_CONTENT=$(gcloud secrets versions access latest \
    --secret="${SECRET_NAME}" \
    --project="${PROJECT_ID}")

echo "Saved URLs:"
echo "${SAVED_CONTENT}" | jq '.'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Service URLs saved to Secret Manager"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Secret: projects/${PROJECT_ID}/secrets/${SECRET_NAME}"
echo "Access with:"
echo "  gcloud secrets versions access latest \\"
echo "    --secret=${SECRET_NAME} \\"
echo "    --project=${PROJECT_ID}"
