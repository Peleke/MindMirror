"""
Task processors for handling business logic directly.

This module provides processors that execute business logic directly
without Celery, replacing the old task queue system.
"""

import asyncio
import logging
import tempfile
from typing import Dict, List, Any, Optional
from uuid import uuid4

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader

from src.clients.journal_client import create_celery_journal_client
from src.clients.qdrant_client import get_celery_qdrant_client
from src.clients.gcs_client import get_gcs_client
from src.utils.embedding import get_embedding, get_embeddings
from src.utils.async_utils import run_async_in_sync

logger = logging.getLogger(__name__)


class JournalIndexingProcessor:
    """Processor for journal entry indexing operations."""

    def __init__(self):
        """Initialize the processor with required clients."""
        self.journal_client = create_celery_journal_client()
        self.qdrant_client = get_celery_qdrant_client()

    def process_journal_indexing(
        self, entry_id: str, user_id: str, tradition: str = "canon-default"
    ) -> bool:
        """Process a single journal entry indexing request."""
        try:
            logger.info(f"Processing journal indexing for entry {entry_id}")
            
            # Get journal entry
            entry_data = run_async_in_sync(
                self.journal_client.get_journal_entry(entry_id)
            )
            
            if not entry_data:
                logger.warning(f"Journal entry {entry_id} not found")
                return False

            # Extract text content
            text_content = self._extract_text_from_entry(entry_data)
            if not text_content:
                logger.warning(f"No content found for entry {entry_id}")
                return False

            # Get embedding
            embedding = get_embedding(text_content)
            
            # Index in Qdrant
            self.qdrant_client.index_journal_entry(
                entry_id=entry_id,
                user_id=user_id,
                tradition=tradition,
                content=text_content,
                embedding=embedding,
                metadata=entry_data
            )
            
            logger.info(f"Successfully indexed entry {entry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing journal indexing for entry {entry_id}: {e}")
            return False

    def process_batch_indexing(self, entries_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process batch journal indexing."""
        try:
            logger.info(f"Processing batch indexing for {len(entries_data)} entries")
            
            # Use JournalIndexer for batch processing
            from src.tasks.journal_tasks import JournalIndexer
            indexer = JournalIndexer()
            
            result = run_async_in_sync(
                indexer.batch_index_entries(entries_data)
            )
            
            logger.info(f"Batch indexing completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing batch indexing: {e}")
            return {"indexed": 0, "failed": len(entries_data), "total": len(entries_data)}

    def process_user_reindex(self, user_id: str, tradition: str = "canon-default") -> Dict[str, Any]:
        """Process user reindexing."""
        try:
            logger.info(f"Processing user reindex for user {user_id}, tradition {tradition}")
            
            # Get all user entries
            entries = run_async_in_sync(
                self.journal_client.get_user_entries(user_id)
            )
            
            if not entries:
                logger.warning(f"No entries found for user {user_id}")
                return {"indexed": 0, "failed": 0, "total": 0}

            # Process each entry
            indexed = 0
            failed = 0
            
            for entry in entries:
                success = self.process_journal_indexing(
                    entry["id"], user_id, tradition
                )
                if success:
                    indexed += 1
                else:
                    failed += 1

            result = {"indexed": indexed, "failed": failed, "total": len(entries)}
            logger.info(f"User reindex completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing user reindex for user {user_id}: {e}")
            return {"indexed": 0, "failed": 1, "total": 1}

    def _extract_text_from_entry(self, entry_data: Dict[str, Any]) -> str:
        """Extract text content from journal entry data."""
        parts = []
        
        # Add title if present
        if entry_data.get("title"):
            parts.append(f"Title: {entry_data['title']}")
        
        # Add content
        if entry_data.get("content"):
            parts.append(entry_data["content"])
        
        # Add tags if present
        if entry_data.get("tags"):
            tags_str = ", ".join(entry_data["tags"])
            parts.append(f"Tags: {tags_str}")
        
        # Add summary if present
        if entry_data.get("summary"):
            parts.append(f"Summary: {entry_data['summary']}")
        
        return "\n\n".join(parts) if parts else ""


class TraditionRebuildProcessor:
    """Processor for tradition rebuild operations."""

    def __init__(self):
        """Initialize the processor with required clients."""
        self.gcs_client = get_gcs_client()
        self.qdrant_client = get_celery_qdrant_client()

    def process_tradition_rebuild(self, tradition: str) -> Dict[str, Any]:
        """Process tradition rebuild request."""
        try:
            logger.info(f"Processing tradition rebuild for {tradition}")
            
            # Get documents from GCS
            documents = self.gcs_client.list_documents(tradition)
            
            if not documents:
                logger.warning(f"No documents found for tradition {tradition}")
                return {"indexed": 0, "failed": 0, "total": 0}

            indexed = 0
            failed = 0
            
            for doc in documents:
                try:
                    # Download document
                    with tempfile.NamedTemporaryFile(suffix=".pdf") as temp_file:
                        self.gcs_client.download_document(tradition, doc["name"], temp_file.name)
                        
                        # Load and split document
                        loader = PyPDFLoader(temp_file.name)
                        pages = loader.load()
                        
                        text_splitter = RecursiveCharacterTextSplitter(
                            chunk_size=1000,
                            chunk_overlap=200
                        )
                        chunks = text_splitter.split_documents(pages)
                        
                        # Get embeddings for chunks
                        texts = [chunk.page_content for chunk in chunks]
                        embeddings = get_embeddings(texts)
                        
                        # Index chunks in Qdrant
                        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                            chunk_id = f"{doc['name']}_chunk_{i}"
                            self.qdrant_client.index_tradition_chunk(
                                chunk_id=chunk_id,
                                tradition=tradition,
                                content=chunk.page_content,
                                embedding=embedding,
                                metadata={"source": doc["name"], "page": chunk.metadata.get("page", 0)}
                            )
                        
                        indexed += len(chunks)
                        
                except Exception as e:
                    logger.error(f"Error processing document {doc['name']}: {e}")
                    failed += 1

            result = {"indexed": indexed, "failed": failed, "total": len(documents)}
            logger.info(f"Tradition rebuild completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing tradition rebuild for {tradition}: {e}")
            return {"indexed": 0, "failed": 1, "total": 1}


class HealthCheckProcessor:
    """Processor for health check operations."""

    def __init__(self):
        """Initialize the processor with required clients."""
        self.qdrant_client = get_celery_qdrant_client()

    def process_health_check(self) -> Dict[str, Any]:
        """Process health check request."""
        try:
            logger.info("Processing health check")
            
            # Check Qdrant health
            qdrant_health = self.qdrant_client.health_check()
            
            # Determine overall status
            if qdrant_health.get("status") == "healthy":
                status = "healthy"
            elif qdrant_health.get("status") == "degraded":
                status = "degraded"
            else:
                status = "unhealthy"
            
            result = {
                "status": status,
                "timestamp": "2024-01-01T00:00:00Z",
                "services": {
                    "qdrant": qdrant_health
                }
            }
            
            logger.info(f"Health check completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing health check: {e}")
            return {
                "status": "unhealthy",
                "timestamp": "2024-01-01T00:00:00Z",
                "error": str(e)
            }


# Singleton instances
_journal_processor = None
_tradition_processor = None
_health_processor = None


def get_journal_processor() -> JournalIndexingProcessor:
    """Get singleton instance of JournalIndexingProcessor."""
    global _journal_processor
    if _journal_processor is None:
        _journal_processor = JournalIndexingProcessor()
    return _journal_processor


def get_tradition_processor() -> TraditionRebuildProcessor:
    """Get singleton instance of TraditionRebuildProcessor."""
    global _tradition_processor
    if _tradition_processor is None:
        _tradition_processor = TraditionRebuildProcessor()
    return _tradition_processor


def get_health_processor() -> HealthCheckProcessor:
    """Get singleton instance of HealthCheckProcessor."""
    global _health_processor
    if _health_processor is None:
        _health_processor = HealthCheckProcessor()
    return _health_processor 