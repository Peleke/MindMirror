import logging
import os

from fastapi import APIRouter, Depends, Header, HTTPException, status

from agent_service.celery_app import celery_app

logger = logging.getLogger(__name__)
router = APIRouter()


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
    Secure endpoint to trigger a Celery task that rebuilds the knowledge base
    for a specific tradition from its source (e.g., GCS bucket).

    This is intended to be called by an automated process, like a Cloud Function.
    """
    logger.info(f"Received re-indexing request for tradition: {tradition}")
    try:
        # Note: The task name must match what's registered in Celery.
        celery_app.send_task(
            "rebuild_tradition_knowledge_base",
            args=[tradition],
        )
        return {"message": f"Accepted re-indexing task for tradition: {tradition}"}
    except Exception as e:
        logger.error(f"Failed to queue re-indexing task for {tradition}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue re-indexing task",
        )
