#!/bin/bash

echo "Starting FastAPI web service..."

# Set environment variable for web mode
export RUN_MODE=web

# Start the FastAPI app
exec uvicorn src.app:app --host 0.0.0.0 --port 8000 