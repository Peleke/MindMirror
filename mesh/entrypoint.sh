#!/bin/sh
set -e

# This script generates the mesh configuration at runtime based on environment variables,
# ensuring the correct service URLs are used whether running locally or in CI.

echo "Generating mesh config with the following URLs:"
echo "JOURNAL_SERVICE_URL: ${JOURNAL_SERVICE_URL}"
echo "AGENT_SERVICE_URL: ${AGENT_SERVICE_URL}"

# Generate the dynamic mesh config file.
# It uses the environment variables passed to the container, with sensible defaults for local development.
echo "import { defineConfig, loadGraphQLHTTPSubgraph } from '@graphql-mesh/compose-cli'

export const composeConfig = defineConfig({
  subgraphs: [
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Journal', {
        endpoint: '${JOURNAL_SERVICE_URL:-http://journal_service:8001}/graphql',
      }),
    },
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Agent', {
        endpoint: '${AGENT_SERVICE_URL:-http://agent_service:8000}/graphql',
      })
    },
  ]
})" > mesh.config.dynamic.ts

# Execute the main command passed to the docker container (e.g., from docker-compose or docker run).
# This allows the container to remain flexible.
exec "$@" 