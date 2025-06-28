import logging
import os

from fastapi import APIRouter, Depends, Header, HTTPException, status

from agent_service.clients.task_client import TaskClient

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize TaskClient
task_client = TaskClient()


# Dependency to verify the secret header
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
    """
    Secure endpoint to trigger a tradition reindexing via celery-worker.
    """
    logger.info(f"Received re-indexing request for tradition: {tradition}")
    try:
        secret = os.getenv("REINDEX_SECRET_KEY")
        result = await task_client.queue_tradition_reindex(tradition, secret)
        return {
            "message": f"Accepted re-indexing task for tradition: {tradition}",
            "task_id": result.get("task_id"),
        }
    except Exception as e:
        logger.error(f"Failed to queue re-indexing task for {tradition}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue re-indexing task",
        )
