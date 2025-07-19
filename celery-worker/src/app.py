from fastapi import FastAPI, HTTPException, Header
from src.clients.pubsub_client import get_pubsub_client
from src.tasks.task_processors import get_journal_processor, get_tradition_processor, get_health_processor
import logging
import os

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Factory function to create FastAPI app instance."""
    app = FastAPI()
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "celery-worker"}

    # Pub/Sub push endpoints
    @app.post("/pubsub/push/journal-indexing")
    async def handle_journal_indexing_push(request: dict):
        """Handle Pub/Sub push for journal indexing."""
        try:
            # Extract data from Pub/Sub message
            message = request.get("message", {})
            data = message.get("data", {})
            
            # Decode base64 data if present
            import base64
            if isinstance(data, str):
                data = base64.b64decode(data).decode('utf-8')
            
            # Parse JSON data
            import json
            if isinstance(data, str):
                data = json.loads(data)
            
            entry_id = data.get("entry_id")
            user_id = data.get("user_id")
            tradition = data.get("tradition", "canon-default")
            
            if not entry_id or not user_id:
                raise HTTPException(status_code=400, detail="Missing required fields")
            
            # Process the indexing
            processor = get_journal_processor()
            success = await processor.process_journal_indexing(entry_id, user_id, tradition)
            
            if success:
                return {"status": "success", "message": f"Indexed entry {entry_id}"}
            else:
                raise HTTPException(status_code=500, detail="Failed to index entry")
                
        except Exception as e:
            logger.error(f"Error processing journal indexing push: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/pubsub/push/tradition-rebuild")
    async def handle_tradition_rebuild_push(request: dict):
        """Handle Pub/Sub push for tradition rebuild."""
        try:
            # Extract data from Pub/Sub message
            message = request.get("message", {})
            data = message.get("data", {})
            
            # Decode base64 data if present
            import base64
            if isinstance(data, str):
                data = base64.b64decode(data).decode('utf-8')
            
            # Parse JSON data
            import json
            if isinstance(data, str):
                data = json.loads(data)
            
            tradition = data.get("tradition")
            
            if not tradition:
                raise HTTPException(status_code=400, detail="Missing tradition field")
            
            # Process the rebuild
            processor = get_tradition_processor()
            result = await processor.process_tradition_rebuild(tradition)
            
            return {"status": "success", "result": result}
                
        except Exception as e:
            logger.error(f"Error processing tradition rebuild push: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/pubsub/push/health-check")
    async def handle_health_check_push(request: dict):
        """Handle Pub/Sub push for health check."""
        try:
            # Process the health check
            processor = get_health_processor()
            result = await processor.process_health_check()
            
            return {"status": "success", "result": result}
                
        except Exception as e:
            logger.error(f"Error processing health check push: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # Legacy HTTP endpoints (for backward compatibility)
    @app.post("/tasks/index-journal-entry")
    async def submit_journal_indexing_task(request: dict):
        """Submit journal indexing task via HTTP (legacy)."""
        try:
            entry_id = request.get("entry_id")
            user_id = request.get("user_id")
            tradition = request.get("tradition", "canon-default")
            
            if not entry_id or not user_id:
                raise HTTPException(status_code=400, detail="Missing required fields")
            
            # Process the indexing
            processor = get_journal_processor()
            success = await processor.process_journal_indexing(entry_id, user_id, tradition)
            
            if success:
                return {"status": "success", "task_id": f"http_{entry_id}"}
            else:
                raise HTTPException(status_code=500, detail="Failed to index entry")
                
        except Exception as e:
            logger.error(f"Error processing journal indexing task: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/tasks/reindex-tradition")
    async def submit_tradition_reindex_task(
        request: dict,
        x_reindex_secret: str = Header(...)
    ):
        """Submit tradition reindex task via HTTP (legacy)."""
        try:
            # Verify secret
            secret = os.getenv("REINDEX_SECRET_KEY")
            if not secret or x_reindex_secret != secret:
                raise HTTPException(status_code=401, detail="Invalid secret")
            
            tradition = request.get("tradition")
            
            if not tradition:
                raise HTTPException(status_code=400, detail="Missing tradition field")
            
            # Process the rebuild
            processor = get_tradition_processor()
            result = await processor.process_tradition_rebuild(tradition)
            
            return {"status": "success", "task_id": f"http_{tradition}", "result": result}
                
        except Exception as e:
            logger.error(f"Error processing tradition reindex task: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    return app


# Create the FastAPI app
app = create_app()
