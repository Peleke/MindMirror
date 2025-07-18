"""
Task processors for MindMirror celery-worker service.

This module contains the extracted business logic from Celery tasks,
allowing them to be executed directly by Pub/Sub message handlers.
"""

import logging
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
import tempfile
import os
import json

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

from src.clients.journal_client import create_celery_journal_client
from src.clients.qdrant_client import get_celery_qdrant_client
from src.clients.gcs_client import get_gcs_client
from src.utils.embedding import get_embedding, get_embeddings
from src.tasks.journal_tasks import JournalIndexer

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


class JournalIndexingProcessor:
    """Processor for journal indexing tasks."""
    
    def __init__(self):
        self.journal_client = create_celery_journal_client()
        self.qdrant_client = get_celery_qdrant_client()
    
    def process_journal_indexing(
        self, 
        entry_id: str, 
        user_id: str, 
        tradition: str = "canon-default"
    ) -> bool:
        """Process a single journal entry indexing task.
        
        Args:
            entry_id: Journal entry ID to index
            user_id: User identifier
            tradition: Knowledge tradition to use
            
        Returns:
            True if successful, False if failed
        """
        try:
            logger.info(f"Processing journal indexing for entry {entry_id}, user {user_id}")
            
            # Use our helper function to run the async code
            result = run_async_in_sync(
                self._index_journal_entry_by_id(entry_id, user_id, tradition)
            )
            
            if not result:
                logger.error(f"Failed to index journal entry {entry_id}")
                return False
            
            logger.info(f"Successfully indexed journal entry {entry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing journal indexing for entry {entry_id}: {e}", exc_info=True)
            return False
    
    async def _index_journal_entry_by_id(
        self, entry_id: str, user_id: str, tradition: str
    ) -> bool:
        """Index a single journal entry by ID.
        
        Args:
            entry_id: Journal entry ID
            user_id: User identifier
            tradition: Knowledge tradition to use
            
        Returns:
            True if successful, False if failed
        """
        try:
            # Get the journal entry
            entry_data = await self.journal_client.get_journal_entry(entry_id)
            if not entry_data:
                logger.error(f"Journal entry {entry_id} not found")
                return False
            
            # Extract text from the entry
            text = self._extract_text_from_entry(entry_data)
            if not text:
                logger.warning(f"No text content found in journal entry {entry_id}")
                return False
            
            # Generate embedding
            embedding = await get_embedding(text)
            
            # Prepare metadata
            metadata = {
                "entry_id": entry_id,
                "user_id": user_id,
                "source_type": "journal_entry",
                "document_type": "journal",
                "created_at": entry_data.get("created_at"),
                "updated_at": entry_data.get("updated_at"),
                "tradition": tradition,
            }
            
            # Index in Qdrant
            self.qdrant_client.index_journal_entry(
                tradition=tradition,
                entry_id=entry_id,
                user_id=user_id,
                text=text,
                embedding=embedding,
                metadata=metadata,
            )
            
            logger.info(f"Successfully indexed journal entry {entry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error indexing journal entry {entry_id}: {e}", exc_info=True)
            return False
    
    def _extract_text_from_entry(self, entry_data: Dict[str, Any]) -> str:
        """Extract text content from a journal entry.
        
        Args:
            entry_data: Journal entry data
            
        Returns:
            Extracted text content
        """
        # Extract text from various possible fields
        text_parts = []
        
        # Check for content field
        if entry_data.get("content"):
            text_parts.append(entry_data["content"])
        
        # Check for title field
        if entry_data.get("title"):
            text_parts.append(f"Title: {entry_data['title']}")
        
        # Check for summary field
        if entry_data.get("summary"):
            text_parts.append(f"Summary: {entry_data['summary']}")
        
        # Check for tags
        if entry_data.get("tags"):
            tags_text = ", ".join(entry_data["tags"])
            text_parts.append(f"Tags: {tags_text}")
        
        return " ".join(text_parts).strip()
    
    def process_batch_indexing(self, entries_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process batch journal indexing.
        
        Args:
            entries_data: List of dicts with entry_id, user_id, tradition
            
        Returns:
            Dict with counts of indexed and failed entries
        """
        try:
            logger.info(f"Processing batch indexing for {len(entries_data)} entries")
            
            async def batch_index():
                indexer = JournalIndexer()
                return await indexer.batch_index_entries(entries_data)
            
            result = run_async_in_sync(batch_index())
            
            logger.info(f"Batch indexing completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in batch indexing: {e}", exc_info=True)
            return {"indexed": 0, "failed": len(entries_data), "errors": [str(e)]}
    
    def process_user_reindex(self, user_id: str, tradition: str = "canon-default") -> Dict[str, Any]:
        """Process user reindexing.
        
        Args:
            user_id: User identifier
            tradition: Knowledge tradition to use
            
        Returns:
            Dict with counts of indexed and failed entries
        """
        try:
            logger.info(f"Processing reindex for user {user_id}")
            
            async def reindex_user():
                indexer = JournalIndexer()
                return await indexer.reindex_user_entries(user_id, tradition)
            
            result = run_async_in_sync(reindex_user())
            
            logger.info(f"Reindex completed for user {user_id}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error reindexing user {user_id}: {e}", exc_info=True)
            return {"indexed": 0, "failed": 0, "errors": [str(e)]}


class TraditionRebuildProcessor:
    """Processor for tradition rebuild tasks."""
    
    def __init__(self):
        self.gcs_client = get_gcs_client()
        self.qdrant_client = get_celery_qdrant_client()
    
    def process_tradition_rebuild(self, tradition: str) -> Dict[str, Any]:
        """Process tradition knowledge base rebuild.
        
        Args:
            tradition: Tradition to rebuild
            
        Returns:
            Dict with rebuild status and results
        """
        try:
            logger.info(f"Processing knowledge base rebuild for tradition: {tradition}")
            
            # Clear existing knowledge data
            knowledge_collection_name = self.qdrant_client.get_knowledge_collection_name(tradition)
            try:
                self.qdrant_client.delete_collection(knowledge_collection_name)
                logger.info(f"Deleted existing collection: {knowledge_collection_name}")
            except Exception as e:
                logger.warning(f"Could not delete collection {knowledge_collection_name}: {e}")
            
            self.qdrant_client.get_or_create_knowledge_collection(tradition)
            
            # Process documents
            doc_prefix = f"{tradition}/"
            doc_blobs = self.gcs_client.list_files(prefix=doc_prefix)
            
            if not doc_blobs:
                logger.warning(f"No documents found for tradition '{tradition}'")
                return {"status": "success", "message": "No documents to process."}
            
            processed_files = []
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            
            for blob in doc_blobs:
                if not blob.name.endswith(".pdf"):
                    continue
                
                logger.info(f"Processing document: {blob.name}")
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                        temp_file_path = temp_file.name
                    
                    self.gcs_client.download_to_filename(blob.name, temp_file_path)
                    loader = PyPDFLoader(temp_file_path)
                    docs = loader.load_and_split(text_splitter)
                    os.remove(temp_file_path)
                    
                    texts = [doc.page_content for doc in docs]
                    
                    # Generate embeddings using async function
                    embeddings = run_async_in_sync(get_embeddings(texts))
                    
                    metadatas = [
                        {
                            "source_type": "pdf",
                            "source_id": blob.name,
                            "document_type": "knowledge",
                            "page": doc.metadata.get("page", 0) + 1,
                        }
                        for doc in docs
                    ]
                    
                    self.qdrant_client.index_knowledge_documents(
                        tradition=tradition,
                        texts=texts,
                        embeddings=embeddings,
                        metadatas=metadatas,
                    )
                    processed_files.append(blob.name)
                    logger.info(f"Successfully processed {len(docs)} chunks from {blob.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to process document {blob.name}: {e}")
                    if "temp_file_path" in locals() and os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
            
            # Update manifest
            manifest = {
                "last_updated": datetime.utcnow().isoformat(),
                "processed_files": processed_files,
                "tradition": tradition,
            }
            manifest_path = f"{tradition}/metadata/manifest.json"
            self.gcs_client.upload_from_string(manifest_path, json.dumps(manifest, indent=2))
            
            logger.info(f"Knowledge base rebuild complete for tradition: {tradition}")
            return {"status": "success", "processed_files": len(processed_files)}
            
        except Exception as e:
            logger.error(f"Error rebuilding tradition {tradition}: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}


class HealthCheckProcessor:
    """Processor for health check tasks."""
    
    def __init__(self):
        self.qdrant_client = get_celery_qdrant_client()
    
    def process_health_check(self) -> Dict[str, Any]:
        """Process health check task.
        
        Returns:
            Dict with health status of various services
        """
        try:
            logger.info("Processing health check")
            
            health_status = {
                "timestamp": datetime.utcnow().isoformat(),
                "status": "healthy",
                "services": {},
            }
            
            # Check Qdrant
            try:
                qdrant_healthy = run_async_in_sync(self.qdrant_client.health_check())
                health_status["services"]["qdrant"] = (
                    "healthy" if qdrant_healthy else "unhealthy"
                )
            except Exception as e:
                logger.error(f"Qdrant health check failed: {e}")
                health_status["services"]["qdrant"] = "unhealthy"
            
            # Overall status
            if any(status == "unhealthy" for status in health_status["services"].values()):
                health_status["status"] = "degraded"
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}", exc_info=True)
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "status": "unhealthy",
                "error": str(e),
                "services": {},
            }


# Global processor instances
_journal_processor: Optional[JournalIndexingProcessor] = None
_tradition_processor: Optional[TraditionRebuildProcessor] = None
_health_processor: Optional[HealthCheckProcessor] = None


def get_journal_processor() -> JournalIndexingProcessor:
    """Get or create the global journal processor instance."""
    global _journal_processor
    if _journal_processor is None:
        _journal_processor = JournalIndexingProcessor()
    return _journal_processor


def get_tradition_processor() -> TraditionRebuildProcessor:
    """Get or create the global tradition processor instance."""
    global _tradition_processor
    if _tradition_processor is None:
        _tradition_processor = TraditionRebuildProcessor()
    return _tradition_processor


def get_health_processor() -> HealthCheckProcessor:
    """Get or create the global health processor instance."""
    global _health_processor
    if _health_processor is None:
        _health_processor = HealthCheckProcessor()
    return _health_processor 