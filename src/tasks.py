import logging
from datetime import datetime
from typing import Dict, Any, List
from celery.exceptions import Retry

from src.celery_app import celery_app
from src.journal_indexer import index_journal_entry_by_id, JournalIndexer

logger = logging.getLogger(__name__)

__all__ = ["celery_app", "index_journal_entry_by_id"]


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
    retry_backoff=True,
    name="index_journal_entry_task"
)
def index_journal_entry_task(self, entry_id: str, user_id: str, tradition: str = "canon-default"):
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
        
        # Since Celery tasks run in sync context, we need to run the async function
        import asyncio
        
        # Create new event loop for this task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                index_journal_entry_by_id(entry_id, user_id, tradition)
            )
        finally:
            loop.close()
        
        if not result:
            raise Exception(f"Failed to index journal entry {entry_id}")
        
        logger.info(f"Successfully indexed journal entry {entry_id}")
        return True
        
    except Exception as exc:
        logger.error(f"Error indexing journal entry {entry_id}: {exc}")
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying task for entry {entry_id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60 * (2 ** self.request.retries), exc=exc)
        else:
            logger.error(f"Max retries exceeded for entry {entry_id}")
            raise exc


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2, "countdown": 120},
    time_limit=1800,  # 30 minutes for batch operations
    name="batch_index_journal_entries_task"
)
def batch_index_journal_entries_task(self, entries_data: List[Dict[str, Any]]):
    """
    Celery task to index multiple journal entries in batch.
    
    Args:
        entries_data: List of dicts with entry_id, user_id, tradition
        
    Returns:
        Dict with counts of indexed and failed entries
    """
    try:
        logger.info(f"Starting batch indexing task for {len(entries_data)} entries")
        
        import asyncio
        
        # Create new event loop for this task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            indexer = JournalIndexer()
            result = loop.run_until_complete(
                indexer.batch_index_entries(entries_data)
            )
        finally:
            loop.close()
        
        logger.info(f"Batch indexing completed: {result}")
        return result
        
    except Exception as exc:
        logger.error(f"Error in batch indexing task: {exc}")
        
        # Retry logic for batch operations
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying batch task (attempt {self.request.retries + 1})")
            raise self.retry(countdown=120 * (2 ** self.request.retries), exc=exc)
        else:
            logger.error("Max retries exceeded for batch indexing task")
            raise exc


@celery_app.task(
    bind=True,
    name="health_check_task",
    time_limit=60
)
def health_check_task(self):
    """
    Health check task for monitoring system status.
    
    Returns:
        Dict with health status of various services
    """
    try:
        import asyncio
        from src.vector_stores.qdrant_client import get_qdrant_client
        
        logger.info("Running health check task")
        
        # Create new event loop for this task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        health_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy",
            "services": {}
        }
        
        try:
            # Check Qdrant
            qdrant_client = get_qdrant_client()
            qdrant_healthy = loop.run_until_complete(qdrant_client.health_check())
            health_status["services"]["qdrant"] = "healthy" if qdrant_healthy else "unhealthy"
            
            # Check Redis (Celery broker)
            try:
                from celery import current_app
                conn = current_app.broker_connection()
                conn.ensure_connection(max_retries=1)
                health_status["services"]["redis"] = "healthy"
            except Exception:
                health_status["services"]["redis"] = "unhealthy"
            
            # Overall status
            if any(status == "unhealthy" for status in health_status["services"].values()):
                health_status["status"] = "degraded"
            
        finally:
            loop.close()
        
        logger.info(f"Health check completed: {health_status}")
        return health_status
        
    except Exception as exc:
        logger.error(f"Health check task failed: {exc}")
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "unhealthy",
            "error": str(exc),
            "services": {}
        }


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2, "countdown": 300},
    time_limit=3600,  # 1 hour for reindexing
    name="reindex_user_entries_task"
)
def reindex_user_entries_task(self, user_id: str, tradition: str = "canon-default"):
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
        
        import asyncio
        
        # Create new event loop for this task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            indexer = JournalIndexer()
            result = loop.run_until_complete(
                indexer.reindex_user_entries(user_id, tradition)
            )
        finally:
            loop.close()
        
        logger.info(f"Reindex completed for user {user_id}: {result}")
        return result
        
    except Exception as exc:
        logger.error(f"Error reindexing user {user_id}: {exc}")
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying reindex for user {user_id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=300 * (2 ** self.request.retries), exc=exc)
        else:
            logger.error(f"Max retries exceeded for reindex user {user_id}")
            raise exc


# Task priority settings
index_journal_entry_task.priority = 5  # High priority for real-time indexing
batch_index_journal_entries_task.priority = 3  # Medium priority for batch operations
health_check_task.priority = 7  # Highest priority for monitoring
reindex_user_entries_task.priority = 2  # Low priority for maintenance operations

# Task routing settings
index_journal_entry_task.routing_key = "indexing"
batch_index_journal_entries_task.routing_key = "indexing"
health_check_task.routing_key = "monitoring"
reindex_user_entries_task.routing_key = "maintenance"


# Convenience functions for external use
def queue_journal_entry_indexing(entry_id: str, user_id: str, tradition: str = "canon-default"):
    """Queue a journal entry for indexing."""
    return index_journal_entry_task.delay(entry_id, user_id, tradition)


def queue_batch_indexing(entries_data: List[Dict[str, Any]]):
    """Queue multiple entries for batch indexing."""
    return batch_index_journal_entries_task.delay(entries_data)


def queue_user_reindex(user_id: str, tradition: str = "canon-default"):
    """Queue all user entries for reindexing."""
    return reindex_user_entries_task.delay(user_id, tradition)


def queue_health_check():
    """Queue a health check task."""
    return health_check_task.delay()


# For testing purposes
def get_journal_entry_by_id(entry_id: str):
    """Mock function for testing - gets journal entry by ID."""
    # This would be replaced with actual database query in tests
    return None 