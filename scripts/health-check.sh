#!/bin/bash

# Health check script for MindMirror application
# This script checks the health of all services

set -e

echo "Running health checks..."

# Check if application is responding
echo "Checking application health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Application is healthy"
else
    echo "❌ Application health check failed"
    exit 1
fi

# Check storage service health
echo "Checking storage service health..."
if curl -f http://localhost:8000/health/storage > /dev/null 2>&1; then
    echo "✅ Storage service is healthy"
else
    echo "❌ Storage service health check failed"
    exit 1
fi

# Check GCS emulator if in development
if [ "$ENVIRONMENT" = "development" ]; then
    echo "Checking GCS emulator..."
    if curl -s http://${GCS_EMULATOR_HOST:-gcs-emulator:4443}/storage/v1/b > /dev/null 2>&1; then
        echo "✅ GCS emulator is healthy"
    else
        echo "❌ GCS emulator health check failed"
        exit 1
    fi
fi

# Check local GCS bucket
if [ -d "/app/local_gcs_bucket" ]; then
    echo "Checking local GCS bucket..."
    if [ -d "/app/local_gcs_bucket/prompts" ]; then
        echo "✅ Local GCS bucket is accessible"
    else
        echo "❌ Local GCS bucket is not accessible"
        exit 1
    fi
fi

echo "🎉 All health checks passed!" 