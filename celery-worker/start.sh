#!/bin/bash

echo "Starting celery-worker service..."

# Start the FastAPI app
echo "Starting FastAPI app..."
uvicorn src.app:app --host 0.0.0.0 --port 8000 &

# Start the Celery worker
echo "Starting Celery worker..."
celery -A src.celery_app.celery_app worker -l info -Q indexing,maintenance &

# Wait for all background processes
wait 