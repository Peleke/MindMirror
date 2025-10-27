#!/usr/bin/env bash
# scripts/update-gateway.sh
# Manual gateway update script (Phase 1)
# Usage: ./scripts/update-gateway.sh [service1] [service2] ...
# Example: ./scripts/update-gateway.sh habits_service journal_service
# Or: ./scripts/update-gateway.sh all (updates all services)

set -euo pipefail

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-mindmirror-prod}"
REGION="${GCP_REGION:-us-central1}"
MESH_BUCKET="${MESH_BUCKET:-mindmirror-prod-mesh}"
WORKDIR=$(mktemp -d)

# Service URL mapping (production)
declare -A SERVICE_URLS=(
    [agent_service]="https://agent-service-${PROJECT_ID}.${REGION}.run.app/graphql"
    [journal_service]="https://journal-service-${PROJECT_ID}.${REGION}.run.app/graphql"
    [habits_service]="https://habits-service-${PROJECT_ID}.${REGION}.run.app/graphql"
    [meals_service]="https://meals-service-${PROJECT_ID}.${REGION}.run.app/graphql"
    [movements_service]="https://movements-service-${PROJECT_ID}.${REGION}.run.app/graphql"
    [practices_service]="https://practices-service-${PROJECT_ID}.${REGION}.run.app/graphql"
    [users_service]="https://users-service-${PROJECT_ID}.${REGION}.run.app/graphql"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    local missing=()

    command -v rover >/dev/null 2>&1 || missing+=("rover")
    command -v gsutil >/dev/null 2>&1 || missing+=("gsutil")
    command -v gcloud >/dev/null 2>&1 || missing+=("gcloud")

    if [ ${#missing[@]} -ne 0 ]; then
        log_error "Missing required dependencies: ${missing[*]}"
        log_info "Install rover: curl -sSL https://rover.apollo.dev/nix/latest | sh"
        log_info "Install gcloud: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
}

introspect_service() {
    local service=$1
    local url=${SERVICE_URLS[$service]:-}

    if [ -z "$url" ]; then
        log_error "Unknown service: $service"
        return 1
    fi

    log_info "Introspecting $service at $url"

    # Introspect with retry logic
    local max_retries=3
    local retry=0

    while [ $retry -lt $max_retries ]; do
        if rover subgraph introspect "$url" > "${WORKDIR}/${service}.graphql" 2>/dev/null; then
            log_info "✓ Successfully introspected $service"
            return 0
        fi

        retry=$((retry + 1))
        if [ $retry -lt $max_retries ]; then
            log_warn "Retry $retry/$max_retries for $service"
            sleep 2
        fi
    done

    log_error "Failed to introspect $service after $max_retries attempts"
    return 1
}

generate_supergraph_config() {
    local config_file="${WORKDIR}/supergraph-config.yaml"

    log_info "Generating supergraph configuration"

    cat > "$config_file" <<EOF
subgraphs:
EOF

    for service in "${!SERVICE_URLS[@]}"; do
        local schema_file="${WORKDIR}/${service}.graphql"
        if [ -f "$schema_file" ]; then
            cat >> "$config_file" <<YAML
  - name: ${service}
    routing_url: ${SERVICE_URLS[$service]}
    schema:
      file: ${schema_file}
YAML
        fi
    done

    echo "$config_file"
}

compose_supergraph() {
    local config_file=$1
    local output_file="${WORKDIR}/supergraph.graphql"

    log_info "Composing supergraph from subgraphs"

    if ! rover supergraph compose --config "$config_file" > "$output_file" 2>&1; then
        log_error "Supergraph composition failed!"
        log_error "Check schema compatibility and federation directives"
        return 1
    fi

    log_info "✓ Supergraph composed successfully"
    echo "$output_file"
}

upload_supergraph() {
    local supergraph_file=$1
    local timestamp=$(date +%s)
    local versioned_path="gs://${MESH_BUCKET}/supergraph-${timestamp}.graphql"
    local latest_path="gs://${MESH_BUCKET}/supergraph-latest.graphql"

    log_info "Uploading supergraph to GCS"

    # Upload versioned copy
    if ! gsutil cp "$supergraph_file" "$versioned_path"; then
        log_error "Failed to upload versioned supergraph"
        return 1
    fi
    log_info "✓ Uploaded $versioned_path"

    # Update latest
    if ! gsutil cp "$supergraph_file" "$latest_path"; then
        log_error "Failed to upload latest supergraph"
        return 1
    fi
    log_info "✓ Updated $latest_path"

    echo "$latest_path"
}

deploy_gateway() {
    local supergraph_url=$1

    log_info "Deploying mesh gateway with new supergraph"

    if ! gcloud run deploy mesh-gateway \
        --image="us-central1-docker.pkg.dev/${PROJECT_ID}/services/mesh-gateway:latest" \
        --set-env-vars="SUPERGRAPH_URL=${supergraph_url}" \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --quiet; then
        log_error "Gateway deployment failed!"
        return 1
    fi

    log_info "✓ Gateway deployed successfully"
}

verify_gateway() {
    local gateway_url="https://mesh-gateway-${PROJECT_ID}.${REGION}.run.app/graphql"

    log_info "Verifying gateway health"

    # Wait for deployment to stabilize
    sleep 5

    # Simple health check (GraphQL introspection query)
    if curl -sf -X POST "$gateway_url" \
        -H "Content-Type: application/json" \
        -d '{"query": "{ __schema { queryType { name } } }"}' \
        > /dev/null 2>&1; then
        log_info "✓ Gateway is healthy"
        return 0
    else
        log_error "Gateway health check failed!"
        log_warn "Check logs: gcloud logging tail \"resource.type=cloud_run_revision AND resource.labels.service_name=mesh-gateway\" --project=$PROJECT_ID"
        return 1
    fi
}

cleanup() {
    log_info "Cleaning up temporary files"
    rm -rf "$WORKDIR"
}

main() {
    local services=("$@")

    # Check dependencies
    check_dependencies

    # Determine which services to update
    if [ ${#services[@]} -eq 0 ] || [ "${services[0]}" = "all" ]; then
        log_info "Updating all services"
        services=("${!SERVICE_URLS[@]}")
    fi

    log_info "Services to update: ${services[*]}"

    # Trap cleanup on exit
    trap cleanup EXIT

    # Step 1: Introspect services
    local failed_introspections=()
    for service in "${services[@]}"; do
        if ! introspect_service "$service"; then
            failed_introspections+=("$service")
        fi
    done

    if [ ${#failed_introspections[@]} -ne 0 ]; then
        log_error "Failed to introspect services: ${failed_introspections[*]}"
        log_error "Aborting gateway update"
        exit 1
    fi

    # Step 2: Generate supergraph config
    local config_file
    config_file=$(generate_supergraph_config)

    # Step 3: Compose supergraph
    local supergraph_file
    if ! supergraph_file=$(compose_supergraph "$config_file"); then
        log_error "Composition failed - check schema compatibility"
        exit 1
    fi

    # Step 4: Upload to GCS
    local supergraph_url
    if ! supergraph_url=$(upload_supergraph "$supergraph_file"); then
        log_error "Upload failed"
        exit 1
    fi

    # Step 5: Deploy gateway
    if ! deploy_gateway "$supergraph_url"; then
        log_error "Deployment failed"
        exit 1
    fi

    # Step 6: Verify gateway
    if ! verify_gateway; then
        log_error "Gateway verification failed"
        exit 1
    fi

    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "Gateway update complete! 🚀"
    log_info "Updated services: ${services[*]}"
    log_info "Supergraph: $supergraph_url"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Run main
main "$@"
