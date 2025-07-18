from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.applications import FastAPI as FastAPIBase
from src.models.task_models import IndexJournalEntryRequest, ReindexTraditionRequest
from src.tasks.journal_tasks import queue_journal_entry_indexing
from src.tasks.tradition_tasks import queue_tradition_reindex
from src.clients.pubsub_client import parse_push_message, get_pubsub_client
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

    # Pub/Sub push subscription endpoints
    @app.post("/pubsub/journal-indexing")
    async def handle_journal_indexing_message(request: Request):
        """Handle journal indexing messages from Pub/Sub push subscription."""
        try:
            # Get the raw request data
            body = await request.body()
            
            # Parse the Pub/Sub message
            message = parse_push_message(body, dict(request.headers))
            
            logger.info(f"Received journal indexing message: {message.data}")
            
            # Extract data from the message
            entry_id = message.data.get("entry_id")
            user_id = message.data.get("user_id")
            tradition = message.data.get("tradition", "canon-default")
            metadata = message.data.get("metadata", {})
            
            if not entry_id or not user_id:
                raise HTTPException(status_code=400, detail="Missing required fields")
            
            # Queue the indexing task
            task = queue_journal_entry_indexing(entry_id, user_id, tradition)
            
            logger.info(f"Successfully queued journal indexing task: {task.id}")
            return {"status": "success", "task_id": task.id}
            
        except Exception as e:
            logger.error(f"Error handling journal indexing message: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/pubsub/journal-batch-indexing")
    async def handle_journal_batch_indexing_message(request: Request):
        """Handle batch journal indexing messages from Pub/Sub push subscription."""
        try:
            body = await request.body()
            message = parse_push_message(body, dict(request.headers))
            
            logger.info(f"Received batch journal indexing message: {message.data}")
            
            entry_ids = message.data.get("entry_ids", [])
            user_id = message.data.get("user_id")
            tradition = message.data.get("tradition", "canon-default")
            
            if not entry_ids or not user_id:
                raise HTTPException(status_code=400, detail="Missing required fields")
            
            # For now, queue individual tasks (we'll optimize this later)
            task_ids = []
            for entry_id in entry_ids:
                task = queue_journal_entry_indexing(entry_id, user_id, tradition)
                task_ids.append(task.id)
            
            logger.info(f"Successfully queued {len(task_ids)} batch indexing tasks")
            return {"status": "success", "task_ids": task_ids}
            
        except Exception as e:
            logger.error(f"Error handling batch journal indexing message: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/pubsub/journal-reindex")
    async def handle_journal_reindex_message(request: Request):
        """Handle journal reindexing messages from Pub/Sub push subscription."""
        try:
            body = await request.body()
            message = parse_push_message(body, dict(request.headers))
            
            logger.info(f"Received journal reindex message: {message.data}")
            
            tradition = message.data.get("tradition", "canon-default")
            
            # Queue the reindex task
            task = queue_tradition_reindex(tradition)
            
            logger.info(f"Successfully queued journal reindex task: {task.id}")
            return {"status": "success", "task_id": task.id}
            
        except Exception as e:
            logger.error(f"Error handling journal reindex message: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/pubsub/tradition-rebuild")
    async def handle_tradition_rebuild_message(request: Request):
        """Handle tradition rebuild messages from Pub/Sub push subscription."""
        try:
            body = await request.body()
            message = parse_push_message(body, dict(request.headers))
            
            logger.info(f"Received tradition rebuild message: {message.data}")
            
            tradition = message.data.get("tradition")
            
            if not tradition:
                raise HTTPException(status_code=400, detail="Missing tradition field")
            
            # Queue the tradition rebuild task
            task = queue_tradition_reindex(tradition)
            
            logger.info(f"Successfully queued tradition rebuild task: {task.id}")
            return {"status": "success", "task_id": task.id}
            
        except Exception as e:
            logger.error(f"Error handling tradition rebuild message: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/pubsub/health-check")
    async def handle_health_check_message(request: Request):
        """Handle health check messages from Pub/Sub push subscription."""
        try:
            body = await request.body()
            message = parse_push_message(body, dict(request.headers))
            
            logger.info(f"Received health check message: {message.data}")
            
            # For now, just log the health check
            # We can add more sophisticated health checking later
            return {"status": "healthy", "message": "Health check processed"}
            
        except Exception as e:
            logger.error(f"Error handling health check message: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    return app

# Only create the app if we're running in web mode
# This prevents FastAPI initialization when running as Celery worker
if os.environ.get("RUN_MODE", "web") == "web":
    app = create_app()
else:
    app = None
