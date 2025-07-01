import logging
from datetime import datetime
from typing import Any, Dict, List
import asyncio
from celery import current_app

from celery.exceptions import Retry

from src.celery_app import celery_app
from src.clients.journal_client import create_celery_journal_client
from src.clients.qdrant_client import get_celery_qdrant_client
from src.utils.embedding import get_embedding

logger = logging.getLogger(__name__)


def run_async_in_sync(coro):
    """Run an async coroutine in a sync context, handling existing event loops."""
    try:
        # Try to get the current event loop
        loop = asyncio.get_running_loop()
        # If we get here, an event loop is already running
        # We need to run the coroutine in a different way
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    except RuntimeError:
        # No event loop is running, we can create one
        return asyncio.run(coro)


# NOTE: Use task routes instead of queue kwarg: <https://docs.celeryq.dev/en/stable/userguide/configuration.html#task-routes>
@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
    time_limit=300,  # 5 minutes
    name="celery_worker.tasks.index_journal_entry_task",
)
def index_journal_entry_task(
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
        
        # Use our helper function to run the async code
        result = run_async_in_sync(index_journal_entry_by_id(entry_id, user_id, tradition))
        
        if not result:
            logger.error(f"Failed to index journal entry {entry_id}")
            raise Exception("Failed to index journal entry")
        
        logger.info(f"Successfully indexed journal entry {entry_id}")
        return True
        
    except Exception as exc:
        logger.error(f"Error indexing journal entry {entry_id}: {exc}")
        # Retry the task
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2, "countdown": 120},
    time_limit=1800,  # 30 minutes for batch operations
    name="celery_worker.tasks.batch_index_journal_entries_task",
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
        
        async def batch_index():
            indexer = JournalIndexer()
            return await indexer.batch_index_entries(entries_data)
        
        # Use our helper function to run the async code
        result = run_async_in_sync(batch_index())
        
        logger.info(f"Batch indexing completed: {result}")
        return result
        
    except Exception as exc:
        logger.error(f"Error in batch indexing task: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2, "countdown": 300},
    time_limit=3600,  # 1 hour for reindexing
    name="celery_worker.tasks.reindex_user_entries_task",
)
def reindex_user_entries_task(
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
        
        async def reindex_user():
            indexer = JournalIndexer()
            return await indexer.reindex_user_entries(user_id, tradition)
        
        # Use our helper function to run the async code
        result = run_async_in_sync(reindex_user())
        
        logger.info(f"Reindex completed for user {user_id}: {result}")
        return result
        
    except Exception as exc:
        logger.error(f"Error reindexing user {user_id}: {exc}")
        raise self.retry(exc=exc)


# Convenience functions for external use
def queue_journal_entry_indexing(
    entry_id: str, user_id: str, tradition: str = "canon-default"
):
    """Queue a journal entry for indexing."""
    logger.info(f"queue_journal_entry_indexing called with entry_id={entry_id}, user_id={user_id}, tradition={tradition}")
    try:
        logger.info("About to send task to celery...")
        logger.info(f"Task name: celery_worker.tasks.index_journal_entry_task")
        logger.info(f"Task args: [{entry_id}, {user_id}, {tradition}]")
        
        task = current_app.send_task(
            "celery_worker.tasks.index_journal_entry_task",
            args=[entry_id, user_id, tradition],
        )
        logger.info(f"Successfully sent task to celery: {task.id}")
        logger.info(f"Task state: {task.state}")
        logger.info(f"Task info: {task.info}")
        return task
    except Exception as e:
        logger.error(f"Error in queue_journal_entry_indexing: {e}", exc_info=True)
        raise


def queue_batch_indexing(entries_data: List[Dict[str, Any]]):
    """Queue multiple entries for batch indexing."""
    return current_app.send_task(
        "celery_worker.tasks.batch_index_journal_entries_task", 
        args=[entries_data]
    )


def queue_user_reindex(user_id: str, tradition: str = "canon-default"):
    """Queue all user entries for reindexing."""
    return current_app.send_task(
        "celery_worker.tasks.reindex_user_entries_task", 
        args=[user_id, tradition]
    )


# Helper functions for journal indexing
async def index_journal_entry_by_id(entry_id: str, user_id: str, tradition: str) -> bool:
    """
    Index a single journal entry by ID.
    
    Args:
        entry_id: Journal entry ID
        user_id: User identifier
        tradition: Knowledge tradition
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get journal entry
        journal_client = create_celery_journal_client()
        entry_data = await journal_client.get_entry_by_id(entry_id, user_id)
        
        if not entry_data:
            logger.warning(f"Journal entry {entry_id} not found")
            return False
        
        # Extract text from entry
        text = extract_text_from_entry(entry_data)
        if not text:
            logger.warning(f"No text content found in entry {entry_id}")
            return False
        
        # Generate embedding
        embedding = await get_embedding(text)
        
        # Index in Qdrant
        qdrant_client = get_celery_qdrant_client()
        collection_name = await qdrant_client.get_or_create_personal_collection(tradition, user_id)
        
        metadata = {
            "source_type": "journal",
            "user_id": user_id,
            "entry_id": entry_id,
            "entry_type": entry_data["entry_type"],
            "created_at": entry_data["created_at"],
            "document_type": "journal_entry",
        }
        
        await qdrant_client.index_personal_document(
            tradition=tradition,
            user_id=user_id,
            text=text,
            embedding=embedding,
            metadata=metadata,
        )
        
        logger.info(f"Successfully indexed journal entry {entry_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to index journal entry {entry_id}: {e}")
        return False


def extract_text_from_entry(entry_data: Dict[str, Any]) -> str:
    """
    Extract text content from journal entry data.
    
    Args:
        entry_data: Journal entry data
        
    Returns:
        Extracted text content
    """
    entry_type = entry_data.get("entry_type", "").upper()
    payload = entry_data.get("payload", {})
    
    if entry_type == "FREEFORM":
        return str(payload) if payload else ""
    
    elif entry_type == "GRATITUDE":
        if isinstance(payload, dict):
            parts = []
            if payload.get("grateful_for"):
                parts.append(f"Grateful for: {', '.join(payload['grateful_for'])}")
            if payload.get("excited_about"):
                parts.append(f"Excited about: {', '.join(payload['excited_about'])}")
            if payload.get("focus"):
                parts.append(f"Focus: {payload['focus']}")
            if payload.get("affirmation"):
                parts.append(f"Affirmation: {payload['affirmation']}")
            return " ".join(parts)
        return str(payload) if payload else ""
    
    elif entry_type == "REFLECTION":
        if isinstance(payload, dict):
            parts = []
            if payload.get("wins"):
                parts.append(f"Wins: {', '.join(payload['wins'])}")
            if payload.get("improvements"):
                parts.append(f"Improvements: {', '.join(payload['improvements'])}")
            if payload.get("mood"):
                parts.append(f"Mood: {payload['mood']}")
            return " ".join(parts)
        return str(payload) if payload else ""
    
    return str(payload) if payload else ""


class JournalIndexer:
    """Journal indexing service."""
    
    def __init__(self):
        self.journal_client = create_celery_journal_client()
        self.qdrant_client = get_celery_qdrant_client()
    
    async def batch_index_entries(self, entries_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Index multiple journal entries in batch."""
        indexed_count = 0
        failed_count = 0
        
        for entry_data in entries_data:
            try:
                success = await index_journal_entry_by_id(
                    entry_data["entry_id"],
                    entry_data["user_id"],
                    entry_data.get("tradition", "canon-default")
                )
                if success:
                    indexed_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Failed to index entry {entry_data.get('entry_id')}: {e}")
                failed_count += 1
        
        return {
            "indexed": indexed_count,
            "failed": failed_count,
            "total": len(entries_data)
        }
    
    async def reindex_user_entries(self, user_id: str, tradition: str) -> Dict[str, Any]:
        """Reindex all entries for a user."""
        try:
            # Get all entries for user in last 30 days
            end_date = datetime.utcnow()
            start_date = datetime(end_date.year, end_date.month - 1, end_date.day)
            
            entries = await self.journal_client.list_by_user_for_period(
                user_id, start_date, end_date
            )
            
            # Clear existing personal collection
            collection_name = self.qdrant_client._get_personal_collection_name(tradition, user_id)
            await self.qdrant_client.delete_collection(collection_name)
            
            # Reindex all entries
            indexed_count = 0
            for entry in entries:
                try:
                    text = extract_text_from_entry({
                        "entry_type": entry.entry_type,
                        "payload": entry.payload
                    })
                    
                    if text:
                        embedding = await get_embedding(text)
                        metadata = {
                            "source_type": "journal",
                            "user_id": user_id,
                            "entry_id": entry.id,
                            "entry_type": entry.entry_type,
                            "created_at": entry.created_at.isoformat(),
                            "document_type": "journal_entry",
                        }
                        
                        await self.qdrant_client.index_personal_document(
                            tradition=tradition,
                            user_id=user_id,
                            text=text,
                            embedding=embedding,
                            metadata=metadata,
                        )
                        indexed_count += 1
                        
                except Exception as e:
                    logger.error(f"Failed to reindex entry {entry.id}: {e}")
            
            return {
                "indexed": indexed_count,
                "total_entries": len(entries),
                "user_id": user_id,
                "tradition": tradition
            }
            
        except Exception as e:
            logger.error(f"Failed to reindex user {user_id}: {e}")
            return {
                "indexed": 0,
                "total_entries": 0,
                "error": str(e),
                "user_id": user_id,
                "tradition": tradition
            } 