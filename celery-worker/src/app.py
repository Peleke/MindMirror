from fastapi import FastAPI, HTTPException, Header
from fastapi.applications import FastAPI as FastAPIBase
from src.models.task_models import IndexJournalEntryRequest, ReindexTraditionRequest
from src.tasks.journal_tasks import queue_journal_entry_indexing
from src.tasks.tradition_tasks import queue_tradition_reindex
import os
import logging

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Factory function to create FastAPI app instance."""
    app = FastAPI()
    
    @app.post("/tasks/index-journal-entry")
    async def submit_index_task(
        request: IndexJournalEntryRequest, 
        x_reindex_secret: str = Header(...)
    ):
        # Validate the secret
        secret = os.getenv("REINDEX_SECRET_KEY")
        if not secret or x_reindex_secret != secret:
            raise HTTPException(status_code=401, detail="Invalid secret")
        
        try:
            logger.info(
                f"Received indexing request for entry {request.entry_id}, user {request.user_id}"
            )
            logger.info(f"Request metadata: {request.metadata}")

            # Extract tradition from metadata, default to "canon-default"
            tradition = (
                request.metadata.get("tradition", "canon-default")
                if request.metadata
                else "canon-default"
            )
            logger.info(f"Using tradition: {tradition}")

            logger.info("About to queue journal entry indexing task...")
            logger.info(
                f"Calling queue_journal_entry_indexing with args: entry_id={request.entry_id}, user_id={request.user_id}, tradition={tradition}"
            )

            task = queue_journal_entry_indexing(
                request.entry_id, request.user_id, tradition
            )
            logger.info(f"Successfully queued task with ID: {task.id}")
            logger.info(f"Task object: {task}")
            logger.info(f"Task state: {task.state}")
            return {"task_id": task.id, "status": "queued"}
        except Exception as e:
            logger.error(f"Error in submit_index_task: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/tasks/reindex-tradition")
    async def submit_reindex_task(
        request: ReindexTraditionRequest, x_reindex_secret: str = Header(...)
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

    return app

# Only create the app if we're running in web mode
# This prevents FastAPI initialization when running as Celery worker
if os.environ.get("RUN_MODE", "web") == "web":
    app = create_app()
else:
    app = None
