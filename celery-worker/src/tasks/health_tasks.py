import logging
from datetime import datetime
from celery import current_app
import asyncio

from src.celery_app import celery_app
from src.clients.qdrant_client import get_celery_qdrant_client

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True, name="celery_worker.tasks.health_check_task", time_limit=60
)
def health_check_task(self):
    """
    Health check task for monitoring system status.

    Returns:
        Dict with health status of various services
    """
    try:
        logger.info("Running health check task")

        health_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy",
            "services": {},
        }

        # Create event loop for async operations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Check Qdrant
            qdrant_client = get_celery_qdrant_client()
            qdrant_healthy = loop.run_until_complete(qdrant_client.health_check())
            health_status["services"]["qdrant"] = (
                "healthy" if qdrant_healthy else "unhealthy"
            )
        finally:
            loop.close()

        # Check Redis (Celery broker)
        try:
            with current_app.connection_for_read() as conn:
                conn.ensure_connection(max_retries=1)
            health_status["services"]["redis"] = "healthy"
        except Exception:
            health_status["services"]["redis"] = "unhealthy"

        # Overall status
        if any(status == "unhealthy" for status in health_status["services"].values()):
            health_status["status"] = "degraded"

        return health_status
    except Exception as exc:
        logger.error(f"Health check task failed: {exc}")
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "unhealthy",
            "error": str(exc),
            "services": {},
        }


def queue_health_check():
    """Queue a health check task."""
    return current_app.send_task("celery_worker.tasks.health_check_task") 