#!/bin/bash

echo "Starting Task Processor service..."

# Start the FastAPI app
exec uvicorn src.app:app --host 0.0.0.0 --port 8000 