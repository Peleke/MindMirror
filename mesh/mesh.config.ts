import { defineConfig, loadGraphQLHTTPSubgraph, loadOpenAPISubgraph } from '@graphql-mesh/compose-cli'

export const composeConfig = defineConfig({
  subgraphs: [
    // NOTE: This file is only used if you run the static mesh compose. In docker-compose, we use
    // entrypoint.sh to generate mesh.config.dynamic.ts at runtime with HABITS_SERVICE_URL, etc.
    // Keeping Habits here for local direct runs as well.
    { sourceHandler: loadGraphQLHTTPSubgraph('Journal', { endpoint: 'http://journal_service:8001/graphql' }) },
    { sourceHandler: loadGraphQLHTTPSubgraph('Agent', { endpoint: 'http://agent_service:8000/graphql' }) },
    { sourceHandler: loadGraphQLHTTPSubgraph('Habits', { endpoint: 'http://habits_service:8003/graphql' }) },
    { sourceHandler: loadGraphQLHTTPSubgraph('Meals', { endpoint: 'http://meals_service:8004/graphql' }) },
    // Voucher REST endpoints exposed via OpenAPI (simple wrapper)
    {
      sourceHandler: loadOpenAPISubgraph('Vouchers', {
        source: {
          openapi: {
            document: {
              openapi: '3.0.0',
              info: { title: 'Vouchers API', version: '1.0.0' },
              servers: [{ url: process.env.WEB_BASE_URL || process.env.NEXT_PUBLIC_BASE_URL || 'http://web:3000' }],
              paths: {
                '/api/vouchers/autoenroll': {
                  post: {
                    operationId: 'autoEnroll',
                    responses: { '200': { description: 'Auto enroll result' } },
                  }
                }
              }
            }
          }
        }
      })
    }
  ]
})

