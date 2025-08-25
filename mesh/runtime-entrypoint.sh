#!/bin/sh
set -e

echo "--- HIVE GATEWAY RUNTIME ENTRYPOINT ---"
echo "JOURNAL_SERVICE_URL=${JOURNAL_SERVICE_URL}"
echo "AGENT_SERVICE_URL=${AGENT_SERVICE_URL}"
echo "HABITS_SERVICE_URL=${HABITS_SERVICE_URL}"
echo "MEALS_SERVICE_URL=${MEALS_SERVICE_URL}"
echo "MOVEMENTS_SERVICE_URL=${MOVEMENTS_SERVICE_URL}"
echo "VOUCHERS_WEB_BASE_URL=${VOUCHERS_WEB_BASE_URL}"

# Generate dynamic mesh config from env or use docker fallbacks for local
cat > mesh.config.dynamic.ts <<'EOF'
import { defineConfig, loadGraphQLHTTPSubgraph } from '@graphql-mesh/compose-cli'

export const composeConfig = defineConfig({
  subgraphs: [
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Journal', {
        endpoint: `${process.env.JOURNAL_SERVICE_URL || 'http://journal_service:8001'}/graphql`,
      }),
    },
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Agent', {
        endpoint: `${process.env.AGENT_SERVICE_URL || 'http://agent_service:8000'}/graphql`,
      })
    },
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Habits', {
        endpoint: `${process.env.HABITS_SERVICE_URL || 'http://habits_service:8003'}/graphql`,
      })
    },
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Meals', {
        endpoint: `${process.env.MEALS_SERVICE_URL || 'http://meals_service:8004'}/graphql`,
      })
    },
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Movements', {
        endpoint: `${process.env.MOVEMENTS_SERVICE_URL || 'http://movements_service:8005'}/graphql`,
      })
    },
  ]
})
EOF

echo "Composing supergraph from mesh.config.dynamic.ts"
npx mesh-compose -c mesh.config.dynamic.ts -o build/supergraph.graphql

echo "Starting Hive Gateway with generated supergraph on PORT=${PORT:-4000}"
exec npx hive-gateway supergraph ./build/supergraph.graphql --host 0.0.0.0 --port ${PORT:-4000}
