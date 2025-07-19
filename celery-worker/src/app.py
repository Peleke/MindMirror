from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.applications import FastAPI as FastAPIBase
from src.models.task_models import IndexJournalEntryRequest, ReindexTraditionRequest
from src.tasks.task_processors import get_journal_processor, get_tradition_processor, get_health_processor
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
        # DEPRECATED: This endpoint will be removed in a future version.
        # Use direct Pub/Sub publishing instead.
        logger.warning(
            "DEPRECATED: /tasks/index-journal-entry endpoint is deprecated. "
            "Use direct Pub/Sub publishing to journal-indexing topic instead."
        )
        
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

            # Process directly using task processor
            journal_processor = get_journal_processor()
            success = journal_processor.process_journal_indexing(request.entry_id, request.user_id, tradition)
            
            if success:
                logger.info(f"Successfully processed journal indexing for entry: {request.entry_id}")
                return {"status": "success", "entry_id": request.entry_id}
            else:
                logger.error(f"Failed to process journal indexing for entry: {request.entry_id}")
                raise HTTPException(status_code=500, detail="Failed to process journal indexing")
        except Exception as e:
            logger.error(f"Error in submit_index_task: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/tasks/reindex-tradition")
    async def submit_reindex_task(
        request: ReindexTraditionRequest, x_reindex_secret: str = Header(...)
    ):
        # DEPRECATED: This endpoint will be removed in a future version.
        # Use direct Pub/Sub publishing instead.
        logger.warning(
            "DEPRECATED: /tasks/reindex-tradition endpoint is deprecated. "
            "Use direct Pub/Sub publishing to tradition-rebuild topic instead."
        )
        
        secret = os.getenv("REINDEX_SECRET_KEY")
        if not secret or x_reindex_secret != secret:
            raise HTTPException(status_code=401, detail="Invalid secret")

        try:
            # Process directly using task processor
            tradition_processor = get_tradition_processor()
            result = tradition_processor.process_tradition_rebuild(request.tradition)
            
            logger.info(f"Successfully processed tradition rebuild: {result}")
            return {"status": "success", "result": result}
        except Exception as e:
            logger.error(f"Error in submit_reindex_task: {e}", exc_info=True)
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
            
            # Process the indexing task directly
            journal_processor = get_journal_processor()
            success = journal_processor.process_journal_indexing(entry_id, user_id, tradition)
            
            if success:
                logger.info(f"Successfully processed journal indexing for entry: {entry_id}")
                return {"status": "success", "entry_id": entry_id}
            else:
                logger.error(f"Failed to process journal indexing for entry: {entry_id}")
                raise HTTPException(status_code=500, detail="Failed to process journal indexing")
            
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
            
            # Process batch indexing directly
            journal_processor = get_journal_processor()
            
            # Convert to the format expected by the processor
            entries_data = [
                {"entry_id": entry_id, "user_id": user_id, "tradition": tradition}
                for entry_id in entry_ids
            ]
            
            result = journal_processor.process_batch_indexing(entries_data)
            
            logger.info(f"Successfully processed batch indexing: {result}")
            return {"status": "success", "result": result}
            
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
            
            # Process the reindex task directly
            journal_processor = get_journal_processor()
            result = journal_processor.process_user_reindex("all", tradition)
            
            logger.info(f"Successfully processed journal reindex: {result}")
            return {"status": "success", "result": result}
            
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
            
            # Process the tradition rebuild task directly
            tradition_processor = get_tradition_processor()
            result = tradition_processor.process_tradition_rebuild(tradition)
            
            logger.info(f"Successfully processed tradition rebuild: {result}")
            return {"status": "success", "result": result}
            
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
            
            # Process the health check directly
            health_processor = get_health_processor()
            result = health_processor.process_health_check()
            
            logger.info(f"Health check result: {result}")
            return {"status": "success", "result": result}
            
        except Exception as e:
            logger.error(f"Error handling health check message: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    return app


# Create the FastAPI app
app = create_app()
