# CELERY_PLAN.md

## Architecture Overview

Extract Celery components from `agent-service` into standalone `celery-worker` service with HTTP API for task submission, decoupling `journal-service` from direct imports. Handle both journal entry indexing and tradition reindexing triggered by GCS bucket events. Leverage existing shared clients library for consistent service communication.

## Directory Structure

```
celery-worker/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── app.py                 # FastAPI app for task submission
│   ├── celery_app.py          # Celery configuration
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── journal_tasks.py   # Journal indexing tasks
│   │   ├── health_tasks.py    # Health check tasks
│   │   └── tradition_tasks.py # Tradition reindexing tasks
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── qdrant_client.py   # Qdrant client (extends shared)
│   │   ├── journal_client.py  # Journal client (extends shared)
│   │   └── gcs_client.py      # GCS client for tradition documents
│   ├── models/
│   │   ├── __init__.py
│   │   └── task_models.py     # Pydantic models for task requests
│   └── utils/
│       ├── __init__.py
│       ├── config.py          # Configuration management
│       └── embedding.py       # Embedding utilities
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # pytest-celery configuration
│   ├── test_app.py            # FastAPI endpoint tests
│   ├── test_tasks.py          # Task execution tests
│   └── test_integration.py    # End-to-end tests
└── README.md

journal-service/
├── src/
│   ├── clients/
│   │   ├── __init__.py
│   │   └── task_client.py     # HTTP client for celery-worker
│   └── web/
│       └── app.py             # Updated to use TaskClient
```

## Implementation Plan

### Phase 1: Extract Celery Components

#### 1.1 Create celery-worker service structure
```bash
mkdir celery-worker
cd celery-worker
# Create directory structure as above
```

#### 1.2 Extract tasks from agent-service
- Move `agent_service/tasks.py` → `celery-worker/src/tasks/journal_tasks.py`
- Move `agent_service/celery_app.py` → `celery-worker/src/celery_app.py`
- Move `ingestion/tasks/rebuild_tradition.py` → `celery-worker/src/tasks/tradition_tasks.py`
- Extract Qdrant client → `celery-worker/src/clients/qdrant_client.py`
- Extract GCS client → `celery-worker/src/clients/gcs_client.py`
- Extract embedding utilities → `celery-worker/src/utils/embedding.py`

#### 1.3 Create FastAPI task submission API
```python
# celery-worker/src/app.py
from fastapi import FastAPI, HTTPException, Header
from .models.task_models import IndexJournalEntryRequest, ReindexTraditionRequest
from .tasks.journal_tasks import queue_journal_entry_indexing
from .tasks.tradition_tasks import queue_tradition_reindex
import os

app = FastAPI()

@app.post("/tasks/index-journal-entry")
async def submit_index_task(request: IndexJournalEntryRequest):
    try:
        task = queue_journal_entry_indexing(
            request.entry_id, 
            request.user_id, 
            request.tradition
        )
        return {"task_id": task.id, "status": "queued"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tasks/reindex-tradition")
async def submit_reindex_task(
    request: ReindexTraditionRequest,
    x_reindex_secret: str = Header(...)
):
    secret = os.getenv("REINDEX_SECRET_KEY")
    if not secret or x_reindex_secret != secret:
        raise HTTPException(status_code=401, detail="Invalid secret")
    
    try:
        task = queue_tradition_reindex(request.tradition)
        return {"task_id": task.id, "status": "queued"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "celery-worker"}
```

#### 1.4 Create Pydantic models
```python
# celery-worker/src/models/task_models.py
from pydantic import BaseModel
from typing import Optional

class IndexJournalEntryRequest(BaseModel):
    entry_id: str
    user_id: str
    tradition: str = "canon-default"

class ReindexTraditionRequest(BaseModel):
    tradition: str
```

#### 1.5 Create shared client extensions
```python
# celery-worker/src/clients/journal_client.py
from shared.clients import JournalServiceClient, create_journal_client
from agent_service.models.journal import JournalEntry
from typing import List
from datetime import datetime
from uuid import UUID

class CeleryJournalClient(JournalServiceClient):
    """
    Extended journal client for celery-worker with agent service compatibility.
    
    This extends the shared JournalServiceClient to provide the interface
    expected by the agent service's journal indexer.
    """
    
    async def list_by_user_for_period(
        self, user_id: str, start_date: datetime, end_date: datetime
    ) -> List[JournalEntry]:
        """
        Retrieves journal entries for a user within a date range.
        
        This method adapts the shared client's response to the agent service's
        JournalEntry model for compatibility with existing code.
        """
        user_uuid = UUID(user_id)
        shared_entries = await self.list_entries_for_user(
            user_id=user_uuid, start_date=start_date, end_date=end_date
        )

        # Convert shared client entries to agent service model
        agent_entries = []
        for shared_entry in shared_entries:
            agent_entry = JournalEntry(
                id=shared_entry.id,
                user_id=shared_entry.user_id,
                entry_type=shared_entry.entry_type,
                payload=shared_entry.payload,
                created_at=shared_entry.created_at,
                modified_at=shared_entry.modified_at,
            )
            agent_entries.append(agent_entry)

        return agent_entries

    async def get_entry_by_id(self, entry_id: str, user_id: str) -> dict:
        """
        Get a single journal entry by ID.
        
        This method is used by the journal indexer and returns a dictionary
        format that matches the existing integration expectations.
        """
        user_uuid = UUID(user_id)
        shared_entries = await self.list_entries_for_user(user_id=user_uuid)

        for entry in shared_entries:
            if entry.id == entry_id:
                return {
                    "id": entry.id,
                    "user_id": entry.user_id,
                    "entry_type": entry.entry_type,
                    "payload": entry.payload,
                    "created_at": entry.created_at.isoformat(),
                    "modified_at": (
                        entry.modified_at.isoformat() if entry.modified_at else None
                    ),
                }

        return None

def create_celery_journal_client(base_url: str = "http://journal_service:8001") -> CeleryJournalClient:
    """Factory function to create a celery-specific journal client."""
    return CeleryJournalClient(base_url=base_url)
```

```python
# celery-worker/src/clients/qdrant_client.py
from agent_service.app.clients.qdrant_client import QdrantClient as AgentQdrantClient

class CeleryQdrantClient(AgentQdrantClient):
    """
    Extended Qdrant client for celery-worker.
    
    This reuses the existing agent service Qdrant client implementation
    to maintain consistency and avoid duplication.
    """
    
    def __init__(self, url: str = None):
        super().__init__(url=url)
    
    # All methods inherited from AgentQdrantClient
    # Additional celery-specific methods can be added here if needed

def get_celery_qdrant_client() -> CeleryQdrantClient:
    """Get or create the global Qdrant client instance for celery-worker."""
    global _celery_qdrant_client
    if _celery_qdrant_client is None:
        _celery_qdrant_client = CeleryQdrantClient()
    return _celery_qdrant_client

# Global client instance
_celery_qdrant_client = None
```

#### 1.6 Update tradition reindexing task
```python
# celery-worker/src/tasks/tradition_tasks.py
import json
import logging
import os
import tempfile
from datetime import datetime
from celery import current_app
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

from ..clients.qdrant_client import get_celery_qdrant_client
from ..clients.gcs_client import get_gcs_client
from ..utils.embedding import get_embedding

logger = logging.getLogger(__name__)

@current_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2, "countdown": 300},
    time_limit=3600,
    name="celery_worker.tasks.rebuild_tradition_knowledge_base"
)
def rebuild_tradition_knowledge_base(self, tradition: str):
    """Celery task to rebuild a tradition's knowledge base from documents in GCS."""
    logger.info(f"Starting knowledge base rebuild for tradition: {tradition}")

    gcs_client = get_gcs_client()
    qdrant_client = get_celery_qdrant_client()

    # Clear existing knowledge data
    knowledge_collection_name = qdrant_client.get_knowledge_collection_name(tradition)
    try:
        qdrant_client.delete_collection(knowledge_collection_name)
        logger.info(f"Deleted existing collection: {knowledge_collection_name}")
    except Exception as e:
        logger.warning(f"Could not delete collection {knowledge_collection_name}: {e}")

    qdrant_client.get_or_create_knowledge_collection(tradition)
    
    # Process documents
    doc_prefix = f"{tradition}/documents/"
    doc_blobs = gcs_client.list_files(prefix=doc_prefix)
    
    if not doc_blobs:
        logger.warning(f"No documents found for tradition '{tradition}'")
        return {"status": "success", "message": "No documents to process."}

    processed_files = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    for blob in doc_blobs:
        if not blob.name.endswith(".pdf"):
            continue

        logger.info(f"Processing document: {blob.name}")
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file_path = temp_file.name

            gcs_client.download_to_filename(blob.name, temp_file_path)
            loader = PyPDFLoader(temp_file_path)
            docs = loader.load_and_split(text_splitter)
            os.remove(temp_file_path)

            texts = [doc.page_content for doc in docs]
            embeddings = [get_embedding(text) for text in texts]

            metadatas = [
                {
                    "source_type": "pdf",
                    "source_id": blob.name,
                    "document_type": "knowledge",
                    "page": doc.metadata.get("page", 0) + 1,
                }
                for doc in docs
            ]

            qdrant_client.index_knowledge_documents(
                tradition=tradition,
                texts=texts,
                embeddings=embeddings,
                metadatas=metadatas,
            )
            processed_files.append(blob.name)
            logger.info(f"Successfully processed {len(docs)} chunks from {blob.name}")

        except Exception as e:
            logger.error(f"Failed to process document {blob.name}: {e}")
            if "temp_file_path" in locals() and os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    # Update manifest
    manifest = {
        "last_updated": datetime.utcnow().isoformat(),
        "processed_files": processed_files,
        "tradition": tradition,
    }
    manifest_path = f"{tradition}/metadata/manifest.json"
    gcs_client.upload_from_string(manifest_path, json.dumps(manifest, indent=2))

    logger.info(f"Knowledge base rebuild complete for tradition: {tradition}")
    return {"status": "success", "processed_files": len(processed_files)}
```

### Phase 2: Create TaskClient for journal-service

#### 2.1 Implement HTTP client
```python
# journal-service/src/clients/task_client.py
import httpx
from typing import Optional

class TaskClient:
    def __init__(self, base_url: str = "http://celery-worker:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def queue_journal_indexing(
        self, 
        entry_id: str, 
        user_id: str, 
        tradition: str = "canon-default"
    ) -> dict:
        response = await self.client.post(
            f"{self.base_url}/tasks/index-journal-entry",
            json={
                "entry_id": entry_id,
                "user_id": user_id,
                "tradition": tradition
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def queue_tradition_reindex(
        self, 
        tradition: str,
        secret: str
    ) -> dict:
        response = await self.client.post(
            f"{self.base_url}/tasks/reindex-tradition",
            json={"tradition": tradition},
            headers={"X-Reindex-Secret": secret}
        )
        response.raise_for_status()
        return response.json()
```

#### 2.2 Update journal-service app.py
```python
# journal-service/src/web/app.py
from ..clients.task_client import TaskClient

task_client = TaskClient()

# Replace direct import calls with:
await task_client.queue_journal_indexing(
    entry_id=str(new_entry.id),
    user_id=user_id,
    tradition="canon-default"
)
```

### Phase 3: Update agent-service web hooks

#### 3.1 Update hooks.py to use TaskClient
```python
# agent_service/web/hooks.py
import logging
import os
from fastapi import APIRouter, Depends, Header, HTTPException, status
from journal_service.clients.task_client import TaskClient

logger = logging.getLogger(__name__)
router = APIRouter()

task_client = TaskClient()

async def verify_secret(x_reindex_secret: str = Header(...)):
    """Dependency to verify the secret re-indexing header."""
    secret = os.getenv("REINDEX_SECRET_KEY")
    if not secret or x_reindex_secret != secret:
        logger.warning("Invalid or missing re-indexing secret.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing secret key",
        )

@router.post(
    "/triggers/reindex-tradition",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(verify_secret)],
    summary="Trigger a knowledge base rebuild for a tradition",
)
async def trigger_reindex(tradition: str):
    """Secure endpoint to trigger tradition reindexing via celery-worker."""
    logger.info(f"Received re-indexing request for tradition: {tradition}")
    try:
        secret = os.getenv("REINDEX_SECRET_KEY")
        result = await task_client.queue_tradition_reindex(tradition, secret)
        return {"message": f"Accepted re-indexing task for tradition: {tradition}", "task_id": result.get("task_id")}
    except Exception as e:
        logger.error(f"Failed to queue re-indexing task for {tradition}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue re-indexing task",
        )
```

### Phase 4: Docker Configuration

#### 4.1 Create celery-worker Dockerfile
```dockerfile
# celery-worker/Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY tests/ ./tests/

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 4.2 Create celery-worker requirements.txt
```txt
# celery-worker/requirements.txt
fastapi>=0.104.0
uvicorn>=0.24.0
celery>=5.3.0
redis>=5.0.0
httpx>=0.24.0
pydantic>=2.0.0
langchain>=0.1.0
langchain-community>=0.0.10
google-cloud-storage>=2.10.0
qdrant-client>=1.6.0
pytest>=7.4.0
pytest-celery>=0.0.0
pytest-asyncio>=0.21.0
shared-clients>=0.1.0  # Shared clients library
```

#### 4.3 Create celery-worker docker-compose.yml
```yaml
# celery-worker/docker-compose.yml
version: '3.8'
services:
  celery-worker:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
      - QDRANT_URL=http://qdrant:6333
      - GCS_BUCKET_NAME=${GCS_BUCKET_NAME}
      - GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json
    volumes:
      - ${GOOGLE_APPLICATION_CREDENTIALS}:/app/credentials.json:ro
    depends_on:
      - redis
      - qdrant
  
  celery-worker-process:
    build: .
    command: celery -A src.celery_app worker --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379/0
      - QDRANT_URL=http://qdrant:6339
      - GCS_BUCKET_NAME=${GCS_BUCKET_NAME}
      - GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json
    volumes:
      - ${GOOGLE_APPLICATION_CREDENTIALS}:/app/credentials.json:ro
    depends_on:
      - redis
      - celery-worker

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

#### 4.4 Update main docker-compose.yml
```yaml
# Add to existing docker-compose.yml
services:
  celery-worker:
    build: ./celery-worker
    ports:
      - "8001:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
      - QDRANT_URL=http://qdrant:6333
      - GCS_BUCKET_NAME=${GCS_BUCKET_NAME}
      - GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json
    volumes:
      - ${GOOGLE_APPLICATION_CREDENTIALS}:/app/credentials.json:ro
    depends_on:
      - redis
      - qdrant
  
  celery-worker-process:
    build: ./celery-worker
    command: celery -A src.celery_app worker --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379/0
      - QDRANT_URL=http://qdrant:6333
      - GCS_BUCKET_NAME=${GCS_BUCKET_NAME}
      - GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json
    volumes:
      - ${GOOGLE_APPLICATION_CREDENTIALS}:/app/credentials.json:ro
    depends_on:
      - redis
      - celery-worker
```

### Phase 5: Update Cloud Function

#### 5.1 Update ingestion cloud function
```python
# ingestion/cloud_function/main.py
import logging
import os
from typing import Any, Dict

import functions_framework
import requests

logging.basicConfig(level=logging.INFO)

@functions_framework.cloud_event
def trigger_reindex_on_gcs_upload(cloud_event):
    """Cloud Function triggered by new file upload to GCS bucket."""
    api_webhook_url = os.environ.get("API_WEBHOOK_URL")
    reindex_secret = os.environ.get("REINDEX_SECRET_KEY")

    if not all([api_webhook_url, reindex_secret]):
        logging.error("Missing required environment variables")
        return ("Configuration error", 500)

    data = cloud_event.data
    bucket = data.get("bucket")
    file_name = data.get("name")

    if not all([bucket, file_name]):
        logging.error("Invalid CloudEvent payload")
        return ("Bad Request", 400)

    logging.info(f"Received event for file: gs://{bucket}/{file_name}")

    try:
        tradition = file_name.split("/")[0]
    except IndexError:
        logging.error(f"Could not determine tradition from file path: {file_name}")
        return ("Bad Request", 400)

    logging.info(f"Triggering re-indexing for tradition: {tradition}")

    headers = {"X-Reindex-Secret": reindex_secret}
    params = {"tradition": tradition}

    try:
        response = requests.post(
            api_webhook_url, headers=headers, params=params, timeout=10
        )
        response.raise_for_status()

        logging.info(f"Successfully triggered webhook. Status: {response.status_code}")
        return ("Webhook triggered successfully", 200)

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to call webhook: {e}")
        return ("Webhook call failed", 500)
```

### Phase 6: Migration Steps

#### 6.1 Remove Celery from agent-service
- Delete `agent_service/celery_app.py`
- Delete `agent_service/tasks.py`
- Remove Celery dependencies from agent-service requirements.txt

#### 6.2 Remove tradition tasks from ingestion
- Delete `ingestion/tasks/rebuild_tradition.py`
- Remove Celery dependencies from ingestion requirements.txt

#### 6.3 Update journal-service dependencies
```txt
# journal-service/requirements.txt
httpx>=0.24.0  # For TaskClient
shared-clients>=0.1.0  # Shared clients library
```

#### 6.4 Update environment variables
```bash
# journal-service/.env
TASK_WORKER_URL=http://celery-worker:8000

# celery-worker/.env
REDIS_URL=redis://redis:6379/0
QDRANT_URL=http://qdrant:6333
GCS_BUCKET_NAME=your-gcs-bucket
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
REINDEX_SECRET_KEY=your-secret-key

# agent-service/.env
TASK_WORKER_URL=http://celery-worker:8000
```

### Phase 7: Validation

#### 7.1 Test journal entry indexing flow
```bash
# Test journal entry creation triggers indexing
curl -X POST http://localhost:8000/journal/entries \
  -H "Content-Type: application/json" \
  -d '{"content": "test entry", "user_id": "test-user"}'

# Verify task is queued
curl http://localhost:8001/tasks/status/{task_id}
```

#### 7.2 Test tradition reindexing flow
```bash
# Test tradition reindexing via webhook
curl -X POST http://localhost:8000/triggers/reindex-tradition \
  -H "X-Reindex-Secret: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"tradition": "canon-default"}'

# Verify task is queued
curl http://localhost:8001/tasks/status/{task_id}
```

#### 7.3 Test cloud function integration
```bash
# Simulate GCS upload event
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{"data": {"bucket": "test-bucket", "name": "canon-default/documents/test.pdf"}}'
```

## File Dependencies

### celery-worker/src/tasks/journal_tasks.py
- Depends on: `src/clients/qdrant_client.py`, `src/clients/journal_client.py`
- Imports: `celery`, `logging`, `datetime`, `shared.clients`

### celery-worker/src/tasks/tradition_tasks.py
- Depends on: `src/clients/qdrant_client.py`, `src/clients/gcs_client.py`, `src/utils/embedding.py`
- Imports: `celery`, `logging`, `langchain`, `tempfile`

### celery-worker/src/app.py
- Depends on: `src/models/task_models.py`, `src/tasks/journal_tasks.py`, `src/tasks/tradition_tasks.py`
- Imports: `fastapi`, `httpx`, `os`

### celery-worker/src/clients/journal_client.py
- Depends on: `shared.clients`, `agent_service.models.journal`
- Extends: `shared.clients.JournalServiceClient`
- Imports: `uuid`, `datetime`, `typing`

### celery-worker/src/clients/qdrant_client.py
- Depends on: `agent_service.app.clients.qdrant_client`
- Extends: `agent_service.app.clients.qdrant_client.QdrantClient`
- Imports: Inherited from parent

### journal-service/src/clients/task_client.py
- Depends on: `httpx`
- No internal dependencies

### journal-service/src/web/app.py
- Depends on: `src/clients/task_client.py`
- Removes: `agent_service.tasks` import

### agent_service/web/hooks.py
- Depends on: `journal_service.clients.task_client`
- Removes: `agent_service.celery_app` import

## Configuration Requirements

### Environment Variables
```bash
# celery-worker
REDIS_URL=redis://redis:6379/0
QDRANT_URL=http://qdrant:6333
GCS_BUCKET_NAME=your-gcs-bucket
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json
REINDEX_SECRET_KEY=your-secret-key

# journal-service
TASK_WORKER_URL=http://celery-worker:8000

# agent-service
TASK_WORKER_URL=http://celery-worker:8000
REINDEX_SECRET_KEY=your-secret-key

# cloud-function
API_WEBHOOK_URL=http://agent-service:8000/triggers/reindex-tradition
REINDEX_SECRET_KEY=your-secret-key
```

### Network Configuration
- celery-worker:8000 (FastAPI)
- celery-worker:6379 (Redis)
- journal-service:8000 (existing)
- agent-service:8000 (existing)
- cloud-function:8080 (existing)

## Rollback Plan

1. Keep agent-service and ingestion Celery code in feature branch
2. Deploy celery-worker alongside existing services
3. Switch journal-service to use TaskClient
4. Update agent-service hooks to use TaskClient
5. Monitor for 24 hours
6. Remove agent-service and ingestion Celery code
7. If issues arise, revert to direct imports 