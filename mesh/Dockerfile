FROM node:22-slim

WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

COPY . .

# Use runtime entrypoint to compose supergraph from env and start gateway
RUN chmod +x /app/runtime-entrypoint.sh
ENTRYPOINT ["/app/runtime-entrypoint.sh"]

