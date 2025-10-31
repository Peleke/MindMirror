#!/usr/bin/env bash
# scripts/extract-service-urls.sh
# Extracts service URLs from Terraform outputs and formats them as JSON for Secret Manager
# Usage: ./scripts/extract-service-urls.sh <environment> <working_directory>
# Example: ./scripts/extract-service-urls.sh staging infra

set -euo pipefail

ENVIRONMENT="${1:-staging}"
WORKING_DIR="${2:-infra}"

# Send diagnostic output to stderr so only JSON goes to stdout
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
echo "📡 Extracting Service URLs from Terraform" >&2
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
echo "Environment: ${ENVIRONMENT}" >&2
echo "Working Directory: ${WORKING_DIR}" >&2
echo "" >&2

# Navigate to infra directory
cd "${WORKING_DIR}"

# Extract service URLs using Terraform output
echo "🔍 Running: tofu output -json" >&2
OUTPUTS=$(tofu output -json)

# Parse each service URL
JOURNAL_URL=$(echo "${OUTPUTS}" | jq -r '.journal_service_url.value // empty')
AGENT_URL=$(echo "${OUTPUTS}" | jq -r '.agent_service_url.value // empty')
HABITS_URL=$(echo "${OUTPUTS}" | jq -r '.habits_service_url.value // empty')
MEALS_URL=$(echo "${OUTPUTS}" | jq -r '.meals_service_url.value // empty')
MOVEMENTS_URL=$(echo "${OUTPUTS}" | jq -r '.movements_service_url.value // empty')
PRACTICES_URL=$(echo "${OUTPUTS}" | jq -r '.practices_service_url.value // empty')
USERS_URL=$(echo "${OUTPUTS}" | jq -r '.users_service_url.value // empty')

echo "📋 Extracted URLs:" >&2
echo "  - Journal: ${JOURNAL_URL:-<not found>}" >&2
echo "  - Agent: ${AGENT_URL:-<not found>}" >&2
echo "  - Habits: ${HABITS_URL:-<not found>}" >&2
echo "  - Meals: ${MEALS_URL:-<not found>}" >&2
echo "  - Movements: ${MOVEMENTS_URL:-<not found>}" >&2
echo "  - Practices: ${PRACTICES_URL:-<not found>}" >&2
echo "  - Users: ${USERS_URL:-<not found>}" >&2
echo "" >&2

# Validate that we have at least some URLs
if [ -z "${JOURNAL_URL}" ] && [ -z "${AGENT_URL}" ]; then
    echo "❌ ERROR: No service URLs found in Terraform outputs" >&2
    echo "This usually means Terraform apply hasn't run yet or outputs are not configured" >&2
    exit 1
fi

# Generate JSON payload for Secret Manager (only this goes to stdout)
echo "📝 Generating JSON payload..." >&2
cat <<EOF
{
  "journal_service_url": "${JOURNAL_URL}",
  "agent_service_url": "${AGENT_URL}",
  "habits_service_url": "${HABITS_URL}",
  "meals_service_url": "${MEALS_URL}",
  "movements_service_url": "${MOVEMENTS_URL}",
  "practices_service_url": "${PRACTICES_URL}",
  "users_service_url": "${USERS_URL}"
}
EOF

echo "" >&2
echo "✅ Service URLs extracted successfully" >&2
