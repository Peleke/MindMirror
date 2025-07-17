#!/bin/bash

echo "Starting Celery worker service..."

# Set environment variable for worker mode
export RUN_MODE=worker

# Start the Celery worker
exec celery -A src.celery_app worker -l info -Q indexing,maintenance 