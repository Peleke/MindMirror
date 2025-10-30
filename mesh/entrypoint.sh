#!/bin/sh
set -e

echo "--- MESH-COMPOSE ENTRYPOINT DEBUG ---"
echo "Received JOURNAL_SERVICE_URL: [${JOURNAL_SERVICE_URL}]"
echo "Received AGENT_SERVICE_URL: [${AGENT_SERVICE_URL}]"
echo "Received HABITS_SERVICE_URL: [${HABITS_SERVICE_URL}]"
echo "Received MEALS_SERVICE_URL: [${MEALS_SERVICE_URL}]"
echo "Received MOVEMENTS_SERVICE_URL: [${MOVEMENTS_SERVICE_URL}]"
echo "Received PRACTICES_SERVICE_URL: [${PRACTICES_SERVICE_URL}]"
echo "Received USERS_SERVICE_URL: [${USERS_SERVICE_URL}]"
echo "Received VOUCHERS_WEB_BASE_URL: [${VOUCHERS_WEB_BASE_URL}]"
echo "--- END DEBUG ---"

# This script generates the mesh configuration at runtime based on environment variables,
# ensuring the correct service URLs are used whether running locally or in CI.

echo "Generating mesh config with the following URLs:"
echo "JOURNAL_SERVICE_URL: ${JOURNAL_SERVICE_URL}"
echo "AGENT_SERVICE_URL: ${AGENT_SERVICE_URL}"
echo "HABITS_SERVICE_URL: ${HABITS_SERVICE_URL}"
echo "MEALS_SERVICE_URL: ${MEALS_SERVICE_URL}"
echo "PRACTICES_SERVICE_URL: ${PRACTICES_SERVICE_URL}"
echo "USERS_SERVICE_URL: ${USERS_SERVICE_URL}"
echo "VOUCHERS_WEB_BASE_URL: ${VOUCHERS_WEB_BASE_URL}"

# Generate the dynamic mesh config file.
# It uses the environment variables passed to the container, with sensible defaults for local development.
# NOTE: Uses /sdl endpoint for schema introspection (no auth required) while /graphql requires JWT
echo "import { defineConfig, loadGraphQLHTTPSubgraph } from '@graphql-mesh/compose-cli'

export const composeConfig = defineConfig({
  subgraphs: [
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Journal', {
        endpoint: '${JOURNAL_SERVICE_URL:-http://journal_service:8001}/graphql',
        schemaEndpoint: '${JOURNAL_SERVICE_URL:-http://journal_service:8001}/sdl',
      }),
    },
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Agent', {
        endpoint: '${AGENT_SERVICE_URL:-http://agent_service:8000}/graphql',
        schemaEndpoint: '${AGENT_SERVICE_URL:-http://agent_service:8000}/sdl',
      })
    },
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Habits', {
        endpoint: '${HABITS_SERVICE_URL:-http://habits_service:8003}/graphql',
        schemaEndpoint: '${HABITS_SERVICE_URL:-http://habits_service:8003}/sdl',
      })
    },
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Meals', {
        endpoint: '${MEALS_SERVICE_URL:-http://meals_service:8004}/graphql',
        schemaEndpoint: '${MEALS_SERVICE_URL:-http://meals_service:8004}/sdl',
      })
    },
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Movements', {
        endpoint: '${MOVEMENTS_SERVICE_URL:-http://movements_service:8005}/graphql',
        schemaEndpoint: '${MOVEMENTS_SERVICE_URL:-http://movements_service:8005}/sdl',
      })
    },
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Practices', {
        endpoint: '${PRACTICES_SERVICE_URL:-http://practices_service:8000}/graphql',
        schemaEndpoint: '${PRACTICES_SERVICE_URL:-http://practices_service:8000}/sdl',
      })
    },
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Users', {
        endpoint: '${USERS_SERVICE_URL:-http://users_service:8000}/graphql',
        schemaEndpoint: '${USERS_SERVICE_URL:-http://users_service:8000}/sdl',
      })
    },
  ]
})" > mesh.config.dynamic.ts

# Execute the main command passed to the docker container (e.g., from docker-compose or docker run).
# This allows the container to remain flexible.
exec "$@" 
