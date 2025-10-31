#!/bin/sh
set -e

echo "--- HIVE GATEWAY RUNTIME ENTRYPOINT ---"
echo "Gateway will use supergraph pre-composed by mesh-compose service"

echo "Using pre-composed supergraph from mesh-compose service"
if [ ! -f build/supergraph.graphql ]; then
  echo "ERROR: No supergraph.graphql found! Make sure mesh-compose service completed successfully."
  exit 1
fi

echo "Starting Hive Gateway with pre-composed supergraph on PORT=${PORT:-4000}"
exec npx hive-gateway supergraph ./build/supergraph.graphql --host 0.0.0.0 --port ${PORT:-4000}
