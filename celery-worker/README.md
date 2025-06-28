# Celery Worker Service

Standalone Celery worker service for MindMirror that handles background tasks including journal entry indexing and tradition reindexing.

## Features

- **Journal Entry Indexing**: Index journal entries in Qdrant vector database
- **Tradition Reindexing**: Rebuild knowledge bases from GCS documents
- **Health Checks**: Monitor service health and dependencies
- **HTTP API**: Submit tasks via REST API endpoints

## Architecture

- **FastAPI**: HTTP API for task submission
- **Celery**: Background task processing
- **Redis**: Message broker and result backend
- **Qdrant**: Vector database for embeddings
- **GCS**: Document storage for traditions

## API Endpoints

### POST /tasks/index-journal-entry
Index a single journal entry.

**Request Body:**
```json
{
  "entry_id": "entry-uuid",
  "user_id": "user-uuid", 
  "tradition": "canon-default"
}
```

### POST /tasks/reindex-tradition
Rebuild a tradition's knowledge base.

**Headers:**
- `X-Reindex-Secret`: Secret key for authentication

**Request Body:**
```json
{
  "tradition": "canon-default"
}
```

### GET /health
Check service health status.

## Environment Variables

- `REDIS_URL`: Redis connection URL (default: redis://redis:6379/0)
- `QDRANT_URL`: Qdrant connection URL (default: http://qdrant:6333)
- `GCS_BUCKET_NAME`: Google Cloud Storage bucket name
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to GCS credentials file
- `REINDEX_SECRET_KEY`: Secret key for tradition reindexing

## Development

### Prerequisites
- Python 3.11+
- Poetry
- Docker & Docker Compose

### Setup
```bash
# Install dependencies
poetry install

# Run with Docker Compose
docker-compose up --build
```

### Testing
```bash
# Run tests
poetry run pytest
```

## Deployment

The service is designed to run in Docker containers with Redis and Qdrant as dependencies.

### Docker Compose
```yaml
services:
  celery-worker:
    build: ./celery-worker
    ports:
      - "8001:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
      - QDRANT_URL=http://qdrant:6333
      - GCS_BUCKET_NAME=${GCS_BUCKET_NAME}
    depends_on:
      - redis
      - qdrant
  
  celery-worker-process:
    build: ./celery-worker
    command: celery -A src.celery_app worker --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379/0
      - QDRANT_URL=http://qdrant:6333
    depends_on:
      - redis
      - celery-worker
``` 