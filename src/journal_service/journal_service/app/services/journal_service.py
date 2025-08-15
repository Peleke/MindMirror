import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from journal_service.journal_service.app.db.repositories.journal import JournalRepository
from journal_service.journal_service.app.models.domain import (
    GratitudePayload, ReflectionPayload, JournalEntryResponse
)
from journal_service.journal_service.app.models.requests import CurrentUser
from journal_service.journal_service.app.clients.task_client import TaskClient
from datetime import datetime

logger = logging.getLogger(__name__)


class JournalService:
    """Service for journal entry operations."""
    
    def __init__(self, repository: JournalRepository):
        self.repository = repository
        self.task_client = TaskClient()
    
    async def _trigger_reindexing(self, entry_id: str, user_id: str, content: str, created_at: datetime, tradition: str = "canon-default"):
        """Trigger reindexing for a journal entry (fire-and-forget)."""
        try:
            await self.task_client.queue_journal_indexing(
                entry_id=entry_id,
                user_id=user_id,
                content=content,
                created_at=created_at,
                metadata={"tradition": tradition}
            )
            logger.info(f"Triggered reindexing for entry {entry_id}")
        except Exception as e:
            logger.error(f"Failed to trigger reindexing for entry {entry_id}: {e}")
            # Don't raise - this is fire-and-forget
    
    def _prepare_reindexing_callback(self, entry_id: str, user_id: str, content: str, created_at: datetime, tradition: str = "canon-default"):
        """Prepare a callback for reindexing that can be executed after transaction commit."""
        async def _reindex_callback():
            await self._trigger_reindexing(entry_id, user_id, content, created_at, tradition)
        return _reindex_callback
    
    def _extract_content_for_reindexing(self, entry_type: str, payload: Dict[str, Any]) -> str:
        """Extract text content from journal entry payload for reindexing."""
        if entry_type == "FREEFORM":
            return payload.get("content", "")
        
        elif entry_type == "GRATITUDE":
            content_parts = []
            content_parts.extend(payload.get("gratefulFor", []))
            content_parts.extend(payload.get("excitedAbout", []))
            if payload.get("focus"):
                content_parts.append(payload["focus"])
            if payload.get("affirmation"):
                content_parts.append(payload["affirmation"])
            if payload.get("mood"):
                content_parts.append(payload["mood"])
            return " ".join(content_parts)
        
        elif entry_type == "REFLECTION":
            content_parts = []
            content_parts.extend(payload.get("wins", []))
            content_parts.extend(payload.get("improvements", []))
            if payload.get("mood"):
                content_parts.append(payload["mood"])
            return " ".join(content_parts)
        
        else:
            # Fallback: convert payload to string
            return str(payload)
    
    async def create_freeform_entry(
        self, 
        user: CurrentUser, 
        content: str,
        habit_template_id: Optional[str] = None,
    ) -> tuple[JournalEntryResponse, callable]:
        """Create a freeform journal entry."""
        payload = {"content": content}
        extra: Dict[str, Any] = {}
        if habit_template_id:
            extra["habit_template_id"] = habit_template_id
        entry = await self.repository.create(
            user_id=user.id,
            entry_type="FREEFORM",
            payload=payload,
            **extra,
        )
        
        logger.info(f"Created freeform entry {entry.id} for user {user.id}")
        
        # Prepare reindexing callback (to be executed after transaction commit)
        reindex_callback = self._prepare_reindexing_callback(
            entry_id=str(entry.id),
            user_id=str(user.id),
            content=content,
            created_at=entry.created_at
        )
        
        return JournalEntryResponse.from_orm(entry), reindex_callback
    
    async def create_gratitude_entry(
        self, 
        user_id: str,
        gratefulFor: List[str],
        excitedAbout: List[str],
        focus: Optional[str] = None,
        affirmation: Optional[str] = None,
        mood: Optional[str] = None,
        habit_template_id: Optional[str] = None,
    ) -> tuple[JournalEntryResponse, callable]:
        """Create a gratitude journal entry."""
        payload = {
            "gratefulFor": gratefulFor,
            "excitedAbout": excitedAbout,
            "focus": focus,
            "affirmation": affirmation,
            "mood": mood,
        }
        extra: Dict[str, Any] = {}
        if habit_template_id:
            extra["habit_template_id"] = habit_template_id
        entry = await self.repository.create(
            user_id=user_id,
            entry_type="GRATITUDE",
            payload=payload,
            **extra,
        )
        
        logger.info(f"Created gratitude entry {entry.id} for user {user_id}")
        
        # Extract content for reindexing
        content = self._extract_content_for_reindexing("GRATITUDE", payload)
        
        # Prepare reindexing callback (to be executed after transaction commit)
        reindex_callback = self._prepare_reindexing_callback(
            entry_id=str(entry.id),
            user_id=user_id,
            content=content,
            created_at=entry.created_at
        )
        
        return JournalEntryResponse.from_orm(entry), reindex_callback
    
    async def create_reflection_entry(
        self,
        user_id: str,
        wins: List[str],
        improvements: List[str],
        mood: Optional[str] = None,
        habit_template_id: Optional[str] = None,
    ) -> tuple[JournalEntryResponse, callable]:
        """Create a reflection journal entry."""
        payload = {
            "wins": wins,
            "improvements": improvements,
            "mood": mood,
        }
        extra: Dict[str, Any] = {}
        if habit_template_id:
            extra["habit_template_id"] = habit_template_id
        entry = await self.repository.create(
            user_id=user_id,
            entry_type="REFLECTION",
            payload=payload,
            **extra,
        )
        
        logger.info(f"Created reflection entry {entry.id} for user {user_id}")
        
        # Extract content for reindexing
        content = self._extract_content_for_reindexing("REFLECTION", payload)
        
        # Prepare reindexing callback (to be executed after transaction commit)
        reindex_callback = self._prepare_reindexing_callback(
            entry_id=str(entry.id),
            user_id=user_id,
            content=content,
            created_at=entry.created_at
        )
        
        return JournalEntryResponse.from_orm(entry), reindex_callback
    
    async def get_entries_for_user(
        self, 
        user_id: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[JournalEntryResponse]:
        """Get journal entries for user."""
        entries = await self.repository.get_entries_for_user(
            user_id, limit, offset
        )
        return [JournalEntryResponse.from_orm(entry) for entry in entries]

    async def get_entries_for_habit(
        self,
        user_id: str,
        habit_template_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[JournalEntryResponse]:
        entries = await self.repository.get_entries_for_habit(user_id, habit_template_id, limit, offset)
        return [JournalEntryResponse.from_orm(entry) for entry in entries]
    
    async def count_entries_for_user(self, user_id: str) -> int:
        """Count journal entries for user."""
        return await self.repository.count_entries_for_user(user_id)
    
    async def check_for_entry_today(
        self, 
        user_id: str, 
        entry_type: str
    ) -> bool:
        """Check if user has entry of specific type today."""
        return await self.repository.check_for_entry_today(user_id, entry_type)
    
    async def delete_entry(self, entry_id: UUID, user_id: str) -> bool:
        """Delete a journal entry."""
        entry = await self.repository.get(str(entry_id))
        if entry and str(entry.user_id) == user_id:
            success = await self.repository.delete(str(entry_id))
            if success:
                logger.info(f"Deleted journal entry {entry_id} for user {user_id}")
            return success
        logger.warning(f"User {user_id} attempted to delete entry {entry_id} but was denied")
        return False
    
    async def get_entry(self, entry_id: UUID, user_id: str) -> Optional[JournalEntryResponse]:
        """Get a specific journal entry."""
        entry = await self.repository.get(str(entry_id))
        if entry and str(entry.user_id) == user_id:
            return JournalEntryResponse.from_orm(entry)
        return None
    
    async def get_entry_system(self, entry_id: UUID) -> Optional[JournalEntryResponse]:
        """Get a specific journal entry (system-level, no user permission check)."""
        entry = await self.repository.get(str(entry_id))
        if entry:
            return JournalEntryResponse.from_orm(entry)
        return None 