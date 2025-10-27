#!/usr/bin/env bash
# scripts/changed-services.sh
# Detects which services changed between base branch and HEAD
# Outputs JSON array for GitHub Actions matrix
# Usage: ./scripts/changed-services.sh [base-branch]
# Example: ./scripts/changed-services.sh origin/main

set -euo pipefail

BASE="${1:-origin/main}"

# Fetch base branch for comparison (suppress errors if already fetched)
git fetch origin main --depth=1 2>/dev/null || true

# Get list of changed files
CHANGED_FILES=$(git diff --name-only "$BASE"...HEAD)

# Track which services changed (use associative array for deduplication)
declare -A services_map

# Parse changed files and map to services
while IFS= read -r file; do
    case "$file" in
        # Python services (main services)
        src/agent_service/*)
            services_map[agent_service]=1
            ;;
        src/journal_service/*)
            services_map[journal_service]=1
            ;;
        habits_service/*)
            services_map[habits_service]=1
            ;;
        meals_service/*)
            services_map[meals_service]=1
            ;;
        movements_service/*)
            services_map[movements_service]=1
            ;;
        practices_service/*)
            services_map[practices_service]=1
            ;;
        users_service/*)
            services_map[users_service]=1
            ;;

        # Celery worker
        celery-worker/*)
            services_map[celery_worker]=1
            ;;

        # Mesh/Gateway
        mesh/*|gateway/*)
            services_map[mesh_gateway]=1
            ;;

        # Frontend
        web/*)
            services_map[web_app]=1
            ;;
        mindmirror-mobile/*)
            services_map[mobile_app]=1
            ;;

        # Shared modules (affects multiple services)
        src/shared/*)
            # Shared module changed → rebuild all Python services
            services_map[agent_service]=1
            services_map[journal_service]=1
            services_map[habits_service]=1
            services_map[meals_service]=1
            services_map[movements_service]=1
            services_map[practices_service]=1
            services_map[users_service]=1
            services_map[celery_worker]=1
            ;;

        # Docker/infrastructure changes (rebuild all)
        docker-compose.yml|Dockerfile|*/Dockerfile)
            services_map[agent_service]=1
            services_map[journal_service]=1
            services_map[habits_service]=1
            services_map[meals_service]=1
            services_map[movements_service]=1
            services_map[practices_service]=1
            services_map[users_service]=1
            services_map[celery_worker]=1
            services_map[mesh_gateway]=1
            services_map[web_app]=1
            ;;

        # CI/CD changes (don't trigger service builds)
        .github/*|scripts/*|docs/*)
            # Skip - these don't require service rebuilds
            ;;

        *)
            # Unknown file - log but don't fail
            >&2 echo "Unknown file pattern: $file (skipping)"
            ;;
    esac
done <<< "$CHANGED_FILES"

# Convert associative array keys to JSON array
services=()
for service in "${!services_map[@]}"; do
    services+=("\"$service\"")
done

# Output JSON array
if [ ${#services[@]} -eq 0 ]; then
    echo "[]"
else
    # Join with commas
    services_json=$(IFS=,; echo "${services[*]}")
    echo "[${services_json}]"
fi
