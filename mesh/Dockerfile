FROM node:22-slim

WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

COPY . .

# Accept service URLs as build arguments (passed by build-gateway-with-urls.sh)
ARG JOURNAL_SERVICE_URL
ARG AGENT_SERVICE_URL
ARG HABITS_SERVICE_URL
ARG MEALS_SERVICE_URL
ARG MOVEMENTS_SERVICE_URL
ARG PRACTICES_SERVICE_URL
ARG USERS_SERVICE_URL
ARG VOUCHERS_WEB_BASE_URL

# Set environment variables from build args to bake URLs into the image
# This ensures the supergraph composition and runtime have access to production URLs
ENV JOURNAL_SERVICE_URL=${JOURNAL_SERVICE_URL}
ENV AGENT_SERVICE_URL=${AGENT_SERVICE_URL}
ENV HABITS_SERVICE_URL=${HABITS_SERVICE_URL}
ENV MEALS_SERVICE_URL=${MEALS_SERVICE_URL}
ENV MOVEMENTS_SERVICE_URL=${MOVEMENTS_SERVICE_URL}
ENV PRACTICES_SERVICE_URL=${PRACTICES_SERVICE_URL}
ENV USERS_SERVICE_URL=${USERS_SERVICE_URL}
ENV VOUCHERS_WEB_BASE_URL=${VOUCHERS_WEB_BASE_URL}

# Generate mesh.config.dynamic.ts from environment variables (same as entrypoint.sh)
RUN echo "Generating mesh.config.dynamic.ts with service URLs..." && \
    echo "import { defineConfig, loadGraphQLHTTPSubgraph } from '@graphql-mesh/compose-cli'" > mesh.config.dynamic.ts && \
    echo "" >> mesh.config.dynamic.ts && \
    echo "export const composeConfig = defineConfig({" >> mesh.config.dynamic.ts && \
    echo "  subgraphs: [" >> mesh.config.dynamic.ts && \
    echo "    {" >> mesh.config.dynamic.ts && \
    echo "      sourceHandler: loadGraphQLHTTPSubgraph('Users', {" >> mesh.config.dynamic.ts && \
    echo "        endpoint: '${USERS_SERVICE_URL:-http://users_service:8000}/graphql'," >> mesh.config.dynamic.ts && \
    echo "        schemaEndpoint: '${USERS_SERVICE_URL:-http://users_service:8000}/sdl'," >> mesh.config.dynamic.ts && \
    echo "      })" >> mesh.config.dynamic.ts && \
    echo "    }," >> mesh.config.dynamic.ts && \
    echo "    {" >> mesh.config.dynamic.ts && \
    echo "      sourceHandler: loadGraphQLHTTPSubgraph('Practices', {" >> mesh.config.dynamic.ts && \
    echo "        endpoint: '${PRACTICES_SERVICE_URL:-http://practices_service:8000}/graphql'," >> mesh.config.dynamic.ts && \
    echo "        schemaEndpoint: '${PRACTICES_SERVICE_URL:-http://practices_service:8000}/sdl'," >> mesh.config.dynamic.ts && \
    echo "      })" >> mesh.config.dynamic.ts && \
    echo "    }," >> mesh.config.dynamic.ts && \
    echo "    {" >> mesh.config.dynamic.ts && \
    echo "      sourceHandler: loadGraphQLHTTPSubgraph('Movements', {" >> mesh.config.dynamic.ts && \
    echo "        endpoint: '${MOVEMENTS_SERVICE_URL:-http://movements_service:8005}/graphql'," >> mesh.config.dynamic.ts && \
    echo "        schemaEndpoint: '${MOVEMENTS_SERVICE_URL:-http://movements_service:8005}/sdl'," >> mesh.config.dynamic.ts && \
    echo "      })" >> mesh.config.dynamic.ts && \
    echo "    }," >> mesh.config.dynamic.ts && \
    echo "    {" >> mesh.config.dynamic.ts && \
    echo "      sourceHandler: loadGraphQLHTTPSubgraph('Meals', {" >> mesh.config.dynamic.ts && \
    echo "        endpoint: '${MEALS_SERVICE_URL:-http://meals_service:8004}/graphql'," >> mesh.config.dynamic.ts && \
    echo "        schemaEndpoint: '${MEALS_SERVICE_URL:-http://meals_service:8004}/sdl'," >> mesh.config.dynamic.ts && \
    echo "      })" >> mesh.config.dynamic.ts && \
    echo "    }," >> mesh.config.dynamic.ts && \
    echo "    {" >> mesh.config.dynamic.ts && \
    echo "      sourceHandler: loadGraphQLHTTPSubgraph('Habits', {" >> mesh.config.dynamic.ts && \
    echo "        endpoint: '${HABITS_SERVICE_URL:-http://habits_service:8003}/graphql'," >> mesh.config.dynamic.ts && \
    echo "        schemaEndpoint: '${HABITS_SERVICE_URL:-http://habits_service:8003}/sdl'," >> mesh.config.dynamic.ts && \
    echo "      })" >> mesh.config.dynamic.ts && \
    echo "    }," >> mesh.config.dynamic.ts && \
    echo "    {" >> mesh.config.dynamic.ts && \
    echo "      sourceHandler: loadGraphQLHTTPSubgraph('Agent', {" >> mesh.config.dynamic.ts && \
    echo "        endpoint: '${AGENT_SERVICE_URL:-http://agent_service:8000}/graphql'," >> mesh.config.dynamic.ts && \
    echo "        schemaEndpoint: '${AGENT_SERVICE_URL:-http://agent_service:8000}/sdl'," >> mesh.config.dynamic.ts && \
    echo "      })" >> mesh.config.dynamic.ts && \
    echo "    }," >> mesh.config.dynamic.ts && \
    echo "    {" >> mesh.config.dynamic.ts && \
    echo "      sourceHandler: loadGraphQLHTTPSubgraph('Journal', {" >> mesh.config.dynamic.ts && \
    echo "        endpoint: '${JOURNAL_SERVICE_URL:-http://journal_service:8001}/graphql'," >> mesh.config.dynamic.ts && \
    echo "        schemaEndpoint: '${JOURNAL_SERVICE_URL:-http://journal_service:8001}/sdl'," >> mesh.config.dynamic.ts && \
    echo "      })" >> mesh.config.dynamic.ts && \
    echo "    }" >> mesh.config.dynamic.ts && \
    echo "  ]" >> mesh.config.dynamic.ts && \
    echo "})" >> mesh.config.dynamic.ts && \
    cat mesh.config.dynamic.ts && \
    echo "Composing supergraph with production service URLs..." && \
    mkdir -p build && \
    npx mesh-compose -c mesh.config.dynamic.ts -o build/supergraph.graphql && \
    echo "Supergraph composition complete!"

# Use runtime entrypoint to start gateway with pre-composed supergraph
RUN chmod +x /app/runtime-entrypoint.sh
ENTRYPOINT ["/app/runtime-entrypoint.sh"]
