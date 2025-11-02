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
# This ensures runtime-entrypoint.sh has access to production URLs
ENV JOURNAL_SERVICE_URL=${JOURNAL_SERVICE_URL}
ENV AGENT_SERVICE_URL=${AGENT_SERVICE_URL}
ENV HABITS_SERVICE_URL=${HABITS_SERVICE_URL}
ENV MEALS_SERVICE_URL=${MEALS_SERVICE_URL}
ENV MOVEMENTS_SERVICE_URL=${MOVEMENTS_SERVICE_URL}
ENV PRACTICES_SERVICE_URL=${PRACTICES_SERVICE_URL}
ENV USERS_SERVICE_URL=${USERS_SERVICE_URL}
ENV VOUCHERS_WEB_BASE_URL=${VOUCHERS_WEB_BASE_URL}

# Use runtime entrypoint to compose supergraph from env and start gateway
RUN chmod +x /app/runtime-entrypoint.sh
ENTRYPOINT ["/app/runtime-entrypoint.sh"]
