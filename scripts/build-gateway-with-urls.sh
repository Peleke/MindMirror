#!/usr/bin/env bash
# scripts/build-gateway-with-urls.sh
# Builds gateway Docker image with service URLs injected from Secret Manager
# Usage: ./scripts/build-gateway-with-urls.sh <environment> <version_tag>
# Example: ./scripts/build-gateway-with-urls.sh staging v1.0.0-abc1234

set -euo pipefail

ENVIRONMENT="${1:-staging}"
VERSION_TAG="${2}"

if [ -z "${VERSION_TAG}" ]; then
    echo "❌ ERROR: Version tag is required"
    echo "Usage: $0 <environment> <version_tag>"
    exit 1
fi

# Configuration per environment
case "$ENVIRONMENT" in
    staging)
        PROJECT_ID="mindmirror-69"
        REGISTRY="us-east4-docker.pkg.dev/mindmirror-69/mindmirror"
        SECRET_NAME="service-urls-staging"
        ;;
    production)
        PROJECT_ID="mindmirror-prod"
        REGISTRY="us-east4-docker.pkg.dev/mindmirror-prod/mindmirror"
        SECRET_NAME="service-urls-production"
        ;;
    *)
        echo "❌ ERROR: Invalid environment '$ENVIRONMENT'"
        echo "Usage: $0 <staging|production> <version_tag>"
        exit 1
        ;;
esac

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏗️  Building Gateway with Service URLs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Environment: ${ENVIRONMENT}"
echo "Version: ${VERSION_TAG}"
echo "Project: ${PROJECT_ID}"
echo "Registry: ${REGISTRY}"
echo ""

# Fetch service URLs from Secret Manager
echo "🔐 Fetching service URLs from Secret Manager..."
echo "Secret: projects/${PROJECT_ID}/secrets/${SECRET_NAME}"

SERVICE_URLS=$(gcloud secrets versions access latest \
    --secret="${SECRET_NAME}" \
    --project="${PROJECT_ID}")

if [ -z "${SERVICE_URLS}" ]; then
    echo "❌ ERROR: Failed to fetch service URLs from Secret Manager"
    exit 1
fi

echo "✅ Fetched service URLs:"
echo "${SERVICE_URLS}" | jq '.'
echo ""

# Parse individual URLs
export JOURNAL_SERVICE_URL=$(echo "${SERVICE_URLS}" | jq -r '.journal_service_url')
export AGENT_SERVICE_URL=$(echo "${SERVICE_URLS}" | jq -r '.agent_service_url')
export HABITS_SERVICE_URL=$(echo "${SERVICE_URLS}" | jq -r '.habits_service_url')
export MEALS_SERVICE_URL=$(echo "${SERVICE_URLS}" | jq -r '.meals_service_url')
export MOVEMENTS_SERVICE_URL=$(echo "${SERVICE_URLS}" | jq -r '.movements_service_url')
export PRACTICES_SERVICE_URL=$(echo "${SERVICE_URLS}" | jq -r '.practices_service_url')
export USERS_SERVICE_URL=$(echo "${SERVICE_URLS}" | jq -r '.users_service_url')

echo "📋 Service URLs for gateway build:"
echo "  - Journal: ${JOURNAL_SERVICE_URL}"
echo "  - Agent: ${AGENT_SERVICE_URL}"
echo "  - Habits: ${HABITS_SERVICE_URL}"
echo "  - Meals: ${MEALS_SERVICE_URL}"
echo "  - Movements: ${MOVEMENTS_SERVICE_URL}"
echo "  - Practices: ${PRACTICES_SERVICE_URL}"
echo "  - Users: ${USERS_SERVICE_URL}"
echo ""

# Build gateway image
IMAGE_NAME="${REGISTRY}/mesh:${VERSION_TAG}"

echo "🏗️  Building gateway image..."
echo "Image: ${IMAGE_NAME}"
echo ""

docker build \
    -t "${IMAGE_NAME}" \
    --build-arg JOURNAL_SERVICE_URL="${JOURNAL_SERVICE_URL}" \
    --build-arg AGENT_SERVICE_URL="${AGENT_SERVICE_URL}" \
    --build-arg HABITS_SERVICE_URL="${HABITS_SERVICE_URL}" \
    --build-arg MEALS_SERVICE_URL="${MEALS_SERVICE_URL}" \
    --build-arg MOVEMENTS_SERVICE_URL="${MOVEMENTS_SERVICE_URL}" \
    --build-arg PRACTICES_SERVICE_URL="${PRACTICES_SERVICE_URL}" \
    --build-arg USERS_SERVICE_URL="${USERS_SERVICE_URL}" \
    -f mesh/Dockerfile \
    mesh/

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Gateway image built successfully"
    echo "Image: ${IMAGE_NAME}"
else
    echo ""
    echo "❌ Gateway image build failed"
    exit 1
fi

# Push image to registry
echo ""
echo "📤 Pushing gateway image to registry..."

docker push "${IMAGE_NAME}"

if [ $? -eq 0 ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ Gateway Build & Push Complete"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Image: ${IMAGE_NAME}"
    echo "Environment: ${ENVIRONMENT}"
    echo "Version: ${VERSION_TAG}"
else
    echo ""
    echo "❌ Failed to push gateway image"
    exit 1
fi
