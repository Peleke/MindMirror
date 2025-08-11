import { defineConfig, loadGraphQLHTTPSubgraph } from '@graphql-mesh/compose-cli'

export const composeConfig = defineConfig({
  subgraphs: [
    // NOTE: This file is only used if you run the static mesh compose. In docker-compose, we use
    // entrypoint.sh to generate mesh.config.dynamic.ts at runtime with HABITS_SERVICE_URL, etc.
    // Keeping Habits here for local direct runs as well.
    { sourceHandler: loadGraphQLHTTPSubgraph('Journal', { endpoint: 'http://journal_service:8001/graphql' }) },
    { sourceHandler: loadGraphQLHTTPSubgraph('Agent', { endpoint: 'http://agent_service:8000/graphql' }) },
    { sourceHandler: loadGraphQLHTTPSubgraph('Habits', { endpoint: 'http://habits_service:8003/graphql' }) },
  ]
})

