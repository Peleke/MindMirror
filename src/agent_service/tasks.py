import logging
from datetime import datetime
from typing import Any, Dict, List

from celery import current_app
from celery.exceptions import Retry

from agent_service.journal_indexer import (JournalIndexer,
                                           index_journal_entry_by_id)
from agent_service.app.clients.qdrant_client import get_qdrant_client

logger = logging.getLogger(__name__)

__all__ = ["index_journal_entry_by_id"]


@current_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
    retry_backoff=True,
    time_limit=300,  # 5 minutes
    name="agent_service.tasks.index_journal_entry_task",
)
async def index_journal_entry_task(
    self, entry_id: str, user_id: str, tradition: str = "canon-default"
):
    """
    Celery task to index a single journal entry.

    Args:
        entry_id: Journal entry ID to index
        user_id: User identifier
        tradition: Knowledge tradition to use

    Returns:
        True if successful, raises exception if failed
    """
    try:
        logger.info(f"Starting indexing task for entry {entry_id}, user {user_id}")

        result = await index_journal_entry_by_id(entry_id, user_id, tradition)

        if not result:
            raise Exception(f"Failed to index journal entry {entry_id}")

        logger.info(f"Successfully indexed journal entry {entry_id}")
        return True

    except Exception as exc:
        logger.error(f"Error indexing journal entry {entry_id}: {exc}")
        raise self.retry(exc=exc)


@current_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2, "countdown": 120},
    time_limit=1800,  # 30 minutes for batch operations
    name="agent_service.tasks.batch_index_journal_entries_task",
)
async def batch_index_journal_entries_task(self, entries_data: List[Dict[str, Any]]):
    """
    Celery task to index multiple journal entries in batch.

    Args:
        entries_data: List of dicts with entry_id, user_id, tradition

    Returns:
        Dict with counts of indexed and failed entries
    """
    try:
        logger.info(f"Starting batch indexing task for {len(entries_data)} entries")

        indexer = JournalIndexer()
        result = await indexer.batch_index_entries(entries_data)

        logger.info(f"Batch indexing completed: {result}")
        return result

    except Exception as exc:
        logger.error(f"Error in batch indexing task: {exc}")
        raise self.retry(exc=exc)


@current_app.task(
    bind=True, name="agent_service.tasks.health_check_task", time_limit=60
)
async def health_check_task(self):
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

        # Check Qdrant
        qdrant_client = get_qdrant_client()
        qdrant_healthy = await qdrant_client.health_check()
        health_status["services"]["qdrant"] = (
            "healthy" if qdrant_healthy else "unhealthy"
        )

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


@current_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2, "countdown": 300},
    time_limit=3600,  # 1 hour for reindexing
    name="agent_service.tasks.reindex_user_entries_task",
)
async def reindex_user_entries_task(
    self, user_id: str, tradition: str = "canon-default"
):
    """
    Celery task to reindex all entries for a user.

    Args:
        user_id: User identifier
        tradition: Knowledge tradition to use

    Returns:
        Dict with counts of indexed and failed entries
    """
    try:
        logger.info(f"Starting reindex task for user {user_id}")

        indexer = JournalIndexer()
        result = await indexer.reindex_user_entries(user_id, tradition)

        logger.info(f"Reindex completed for user {user_id}: {result}")
        return result

    except Exception as exc:
        logger.error(f"Error reindexing user {user_id}: {exc}")
        raise self.retry(exc=exc)


# Task priority settings
# These will be applied to the tasks when they are registered by the worker
current_app.conf.task_routes = {
    "agent_service.tasks.index_journal_entry_task": {
        "priority": 5,
        "routing_key": "indexing",
    },
    "agent_service.tasks.batch_index_journal_entries_task": {
        "priority": 3,
        "routing_key": "indexing",
    },
    "agent_service.tasks.health_check_task": {
        "priority": 7,
        "routing_key": "monitoring",
    },
    "agent_service.tasks.reindex_user_entries_task": {
        "priority": 2,
        "routing_key": "maintenance",
    },
}


# Convenience functions for external use
def queue_journal_entry_indexing(
    entry_id: str, user_id: str, tradition: str = "canon-default"
):
    """Queue a journal entry for indexing."""
    return current_app.send_task(
        "agent_service.tasks.index_journal_entry_task",
        args=[entry_id, user_id, tradition],
    )


def queue_batch_indexing(entries_data: List[Dict[str, Any]]):
    """Queue multiple entries for batch indexing."""
    return current_app.send_task(
        "agent_service.tasks.batch_index_journal_entries_task", args=[entries_data]
    )


def queue_user_reindex(user_id: str, tradition: str = "canon-default"):
    """Queue all user entries for reindexing."""
    return current_app.send_task(
        "agent_service.tasks.reindex_user_entries_task", args=[user_id, tradition]
    )


def queue_health_check():
    """Queue a health check task."""
    return current_app.send_task("agent_service.tasks.health_check_task")


# For testing purposes
def get_journal_entry_by_id(entry_id: str):
    """Mock function for testing - gets journal entry by ID."""
    # This would be replaced with actual database query in tests
    return None
