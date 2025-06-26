#!/bin/bash

# Initialize GCS bucket and upload default prompts
# This script is used in Docker environment to set up GCS storage

set -e

echo "Initializing GCS bucket..."

# Wait for GCS emulator to be ready
echo "Waiting for GCS emulator..."
until curl -s http://${GCS_EMULATOR_HOST:-gcs-emulator:4443}/storage/v1/b > /dev/null 2>&1; do
    echo "GCS emulator not ready, waiting..."
    sleep 2
done

echo "GCS emulator is ready!"

# Set up GCS environment
export STORAGE_EMULATOR_HOST=${GCS_EMULATOR_HOST:-gcs-emulator:4443}

# Create bucket if it doesn't exist
BUCKET_NAME=${GCS_BUCKET_NAME:-local_gcs_bucket}
echo "Creating bucket: $BUCKET_NAME"

# Use gsutil to create bucket
gsutil mb -p local-project gs://$BUCKET_NAME || echo "Bucket already exists"

# Upload default prompts if they exist
if [ -d "/app/prompts" ]; then
    echo "Uploading default prompts to GCS..."
    gsutil -m cp -r /app/prompts/* gs://$BUCKET_NAME/prompts/ || echo "No prompts to upload"
fi

echo "GCS bucket initialization complete!"
echo "Bucket: gs://$BUCKET_NAME"
echo "Storage emulator: $STORAGE_EMULATOR_HOST" 