import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import UUID

from src.models.sql.journal import JournalEntryModel
from src.models.journal import JournalEntry as PydanticJournalEntry, GratitudePayload, ReflectionPayload
from src.vector_stores.qdrant_client import get_qdrant_client

logger = logging.getLogger(__name__)


class JournalIndexer:
    """Handles indexing journal entries into the vector store."""
    
    def __init__(self):
        self.qdrant_client = get_qdrant_client()
    
    async def index_entry(
        self,
        entry: PydanticJournalEntry,
        user_id: str,
        tradition: str = "canon-default"
    ) -> bool:
        """
        Index a single journal entry.
        
        Args:
            entry: The journal entry to index
            user_id: User identifier
            tradition: Knowledge tradition/collection to use
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract text content based on entry type
            text_content = self._extract_text_content(entry)
            if not text_content.strip():
                logger.warning(f"No text content extracted from entry {entry.id}")
                return False
            
            # Generate embedding for the content
            from src.embedding import get_embedding
            embedding = await get_embedding(text_content)
            if not embedding:
                logger.error(f"Failed to generate embedding for entry {entry.id}")
                return False
            
            # Prepare metadata
            metadata = self._prepare_metadata(entry, user_id)
            
            # Index the document in the user's personal collection
            point_id = await self.qdrant_client.index_personal_document(
                tradition=tradition,
                user_id=user_id,
                text=text_content,
                embedding=embedding,
                metadata=metadata
            )
            
            logger.info(f"Successfully indexed journal entry {entry.id} as point {point_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index journal entry {entry.id}: {e}")
            return False

    async def batch_index_entries(self, entries_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Index multiple journal entries in batch.
        
        Args:
            entries_data: List of dicts with entry_id, user_id, tradition
            
        Returns:
            Dict with counts of indexed and failed entries
        """
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

    async def reindex_user_entries(self, user_id: str, tradition: str = "canon-default") -> Dict[str, int]:
        """
        Reindex all entries for a user.
        
        Args:
            user_id: User identifier
            tradition: Knowledge tradition to use
            
        Returns:
            Dict with counts of indexed and failed entries
        """
        try:
            # Get all journal entries for the user from database
            from src.uow import UnitOfWork
            from src.repositories.journal_repository import JournalRepository
            
            async with UnitOfWork() as uow:
                repo = JournalRepository(uow.session)
                entries = await repo.list_by_user(user_id)
            
            # Clear existing entries from vector store
            try:
                personal_collection = await self.qdrant_client.get_or_create_personal_collection(tradition, user_id)
                # Delete and recreate collection to clear all user's entries
                await self.qdrant_client.delete_collection(personal_collection)
                await self.qdrant_client.get_or_create_personal_collection(tradition, user_id)
                logger.info(f"Cleared existing entries for user {user_id}")
            except Exception as e:
                logger.warning(f"Failed to clear existing entries for user {user_id}: {e}")
            
            # Index all entries
            indexed_count = 0
            failed_count = 0
            
            for entry in entries:
                try:
                    success = await self.index_entry(entry, user_id, tradition)
                    if success:
                        indexed_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    logger.error(f"Failed to reindex entry {entry.id}: {e}")
                    failed_count += 1
            
            return {
                "indexed": indexed_count,
                "failed": failed_count,
                "total": len(entries)
            }
            
        except Exception as e:
            logger.error(f"Failed to reindex entries for user {user_id}: {e}")
            return {"indexed": 0, "failed": 0, "total": 0, "error": str(e)}
    
    def _extract_text_content(self, entry: PydanticJournalEntry) -> str:
        """Extract searchable text content from different journal entry types."""
        if entry.entry_type == "GRATITUDE":
            # Handle gratitude payload
            if isinstance(entry.payload, dict):
                payload = GratitudePayload(**entry.payload)
            else:
                payload = entry.payload
            
            if hasattr(payload, 'grateful_for') and payload.grateful_for:
                gratitude_text = ". ".join(payload.grateful_for)
                excited_text = ". ".join(payload.excited_about) if hasattr(payload, 'excited_about') and payload.excited_about else ""
                focus_text = payload.focus if hasattr(payload, 'focus') and payload.focus else ""
                affirmation_text = payload.affirmation if hasattr(payload, 'affirmation') and payload.affirmation else ""
                
                content_parts = [f"Gratitude: {gratitude_text}"]
                if excited_text:
                    content_parts.append(f"Excited about: {excited_text}")
                if focus_text:
                    content_parts.append(f"Focus: {focus_text}")
                if affirmation_text:
                    content_parts.append(f"Affirmation: {affirmation_text}")
                
                return ". ".join(content_parts)
            return ""
        
        elif entry.entry_type == "REFLECTION":
            # Handle reflection payload
            if isinstance(entry.payload, dict):
                payload = ReflectionPayload(**entry.payload)
            else:
                payload = entry.payload
            
            if hasattr(payload, 'wins') and payload.wins:
                wins_text = ". ".join(payload.wins)
                improvements_text = ". ".join(payload.improvements) if hasattr(payload, 'improvements') and payload.improvements else ""
                
                content_parts = [f"Wins: {wins_text}"]
                if improvements_text:
                    content_parts.append(f"Improvements: {improvements_text}")
                
                return f"Reflection: {'. '.join(content_parts)}"
            return ""
        
        elif entry.entry_type == "FREEFORM":
            # Use the freeform content directly
            content = entry.payload if isinstance(entry.payload, str) else str(entry.payload)
            return f"Journal: {content}"
        
        else:
            # Fallback for unknown entry types
            logger.warning(f"Unknown journal entry type: {entry.entry_type}")
            return str(entry.payload)
    
    def _prepare_metadata(self, entry: PydanticJournalEntry, user_id: str) -> Dict[str, Any]:
        """Prepare metadata for the journal entry."""
        return {
            "source_type": "journal",
            "source_id": entry.id,
            "user_id": user_id,
            "timestamp": entry.created_at.isoformat() if entry.created_at else datetime.utcnow().isoformat(),
            "document_type": entry.entry_type.lower(),
            "entry_type": entry.entry_type.lower()  # Duplicate for backwards compatibility
        }


async def index_journal_entry_by_id(entry_id: str, user_id: str, tradition: str = "canon-default") -> bool:
    """
    Index a journal entry by its ID.
    
    Args:
        entry_id: Journal entry ID
        user_id: User identifier  
        tradition: Knowledge tradition to use
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get the journal entry from database
        from src.uow import UnitOfWork
        from src.repositories.journal_repository import JournalRepository
        from uuid import UUID
        
        async with UnitOfWork() as uow:
            repo = JournalRepository(uow.session)
            entry = await repo.get_by_id(UUID(entry_id))
        
        if not entry:
            logger.error(f"Journal entry {entry_id} not found")
            return False
        
        # Index the entry
        indexer = JournalIndexer()
        return await indexer.index_entry(entry, user_id, tradition)
        
    except Exception as e:
        logger.error(f"Failed to index journal entry {entry_id}: {e}")
        return False


async def delete_user_collection(user_id: str, tradition: str = "canon-default") -> bool:
    """Delete all indexed entries for a user."""
    try:
        qdrant_client = get_qdrant_client()
        collection_name = f"{tradition}_{user_id}_personal"
        return await qdrant_client.delete_collection(collection_name)
    except Exception as e:
        logger.error(f"Failed to delete collection for user {user_id}: {e}")
        return False 