#!/usr/bin/env bash
# scripts/health-check-all.sh
# Verifies health of all deployed services
# Usage: ./scripts/health-check-all.sh [environment]
# Example: ./scripts/health-check-all.sh production

set -euo pipefail

ENVIRONMENT="${1:-production}"
PROJECT_ID="${GCP_PROJECT_ID:-mindmirror-prod}"
REGION="${GCP_REGION:-us-central1}"

# Service names (Cloud Run service names)
SERVICES=(
    "agent-service"
    "journal-service"
    "habits-service"
    "meals-service"
    "movements-service"
    "practices-service"
    "users-service"
    "mesh-gateway"
    "web-app"
)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

get_service_url() {
    local service=$1

    # Get URL from Cloud Run
    gcloud run services describe "$service" \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --format='value(status.url)' 2>/dev/null || echo ""
}

check_service_health() {
    local service=$1
    local url=$2

    # Try /health endpoint first
    local health_url="${url}/health"

    log_info "Checking $service at $health_url"

    # HTTP health check with timeout
    local response
    local http_code

    response=$(curl -sf -m 10 "$health_url" 2>&1) || true
    http_code=$(curl -sf -m 10 -o /dev/null -w "%{http_code}" "$health_url" 2>/dev/null || echo "000")

    if [ "$http_code" = "200" ]; then
        log_info "✓ $service is healthy (HTTP $http_code)"
        return 0
    else
        log_error "✗ $service is unhealthy (HTTP $http_code)"

        # Try root endpoint as fallback
        local root_code
        root_code=$(curl -sf -m 10 -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")

        if [ "$root_code" = "200" ] || [ "$root_code" = "404" ]; then
            log_warn "  Service is running but /health endpoint failed"
            log_warn "  Root endpoint returned HTTP $root_code"
            return 1
        else
            log_error "  Service appears to be down"
            return 1
        fi
    fi
}

check_graphql_endpoint() {
    local service=$1
    local url="${2}/graphql"

    log_info "Checking GraphQL endpoint for $service"

    # Simple introspection query
    local query='{"query": "{ __schema { queryType { name } } }"}'

    local response
    response=$(curl -sf -m 10 -X POST "$url" \
        -H "Content-Type: application/json" \
        -d "$query" 2>/dev/null) || true

    if echo "$response" | grep -q "queryType"; then
        log_info "✓ $service GraphQL endpoint is healthy"
        return 0
    else
        log_error "✗ $service GraphQL endpoint failed"
        return 1
    fi
}

get_service_metrics() {
    local service=$1

    # Get basic metrics from Cloud Run
    log_info "Fetching metrics for $service..."

    local revision
    revision=$(gcloud run services describe "$service" \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --format='value(status.latestReadyRevisionName)' 2>/dev/null || echo "unknown")

    local instance_count
    instance_count=$(gcloud run services describe "$service" \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --format='value(spec.template.spec.containerConcurrency)' 2>/dev/null || echo "unknown")

    echo "  Revision: $revision"
    echo "  Concurrency: $instance_count"
}

main() {
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "Health Check: $ENVIRONMENT environment"
    log_info "Project: $PROJECT_ID"
    log_info "Region: $REGION"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    local failed_services=()
    local healthy_count=0

    for service in "${SERVICES[@]}"; do
        echo ""
        log_info "━━━ Checking $service ━━━"

        local url
        url=$(get_service_url "$service")

        if [ -z "$url" ]; then
            log_error "Service not found or not deployed"
            failed_services+=("$service")
            continue
        fi

        # Check HTTP health
        if check_service_health "$service" "$url"; then
            healthy_count=$((healthy_count + 1))

            # For GraphQL services, also check GraphQL endpoint
            case "$service" in
                agent-service|journal-service|habits-service|meals-service|movements-service|practices-service|users-service|mesh-gateway)
                    if ! check_graphql_endpoint "$service" "$url"; then
                        failed_services+=("$service (GraphQL)")
                    fi
                    ;;
            esac

            # Get metrics
            get_service_metrics "$service"
        else
            failed_services+=("$service")
        fi
    done

    echo ""
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "Health Check Summary"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    if [ ${#failed_services[@]} -eq 0 ]; then
        log_info "✓ All services healthy ($healthy_count/${#SERVICES[@]})"
        echo ""
        log_info "Production is ready! 🚀"
        exit 0
    else
        log_error "✗ Failed services: ${failed_services[*]}"
        log_error "Healthy: $healthy_count/${#SERVICES[@]}"
        echo ""
        log_error "Check logs for failed services:"
        for failed_service in "${failed_services[@]}"; do
            # Remove (GraphQL) suffix for log command
            local service_name="${failed_service%% (*}"
            echo "  gcloud logging tail \"resource.type=cloud_run_revision AND resource.labels.service_name=$service_name\" --project=$PROJECT_ID"
        done
        exit 1
    fi
}

# Run main
main
