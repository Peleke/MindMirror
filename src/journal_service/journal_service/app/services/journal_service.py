import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from journal_service.journal_service.app.db.repositories.journal import JournalRepository
from journal_service.journal_service.app.models.domain import (
    GratitudePayload, ReflectionPayload, JournalEntryResponse
)
from journal_service.journal_service.app.models.requests import CurrentUser

logger = logging.getLogger(__name__)


class JournalService:
    """Service for journal entry operations."""
    
    def __init__(self, repository: JournalRepository):
        self.repository = repository
    
    async def create_freeform_entry(
        self, 
        user: CurrentUser, 
        content: str
    ) -> JournalEntryResponse:
        """Create a freeform journal entry."""
        payload = {"content": content}
        entry = await self.repository.create(
            user_id=user.id,
            entry_type="FREEFORM",
            payload=payload
        )
        
        logger.info(f"Created freeform entry {entry.id} for user {user.id}")
        return JournalEntryResponse.from_orm(entry)
    
    async def create_gratitude_entry(
        self, 
        user: CurrentUser, 
        payload: GratitudePayload
    ) -> JournalEntryResponse:
        """Create a gratitude journal entry."""
        entry = await self.repository.create(
            user_id=user.id,
            entry_type="GRATITUDE",
            payload=payload.model_dump()
        )
        
        logger.info(f"Created gratitude entry {entry.id} for user {user.id}")
        return JournalEntryResponse.from_orm(entry)
    
    async def create_reflection_entry(
        self,
        user: CurrentUser,
        payload: ReflectionPayload
    ) -> JournalEntryResponse:
        """Create a reflection journal entry."""
        entry = await self.repository.create(
            user_id=user.id,
            entry_type="REFLECTION",
            payload=payload.model_dump()
        )
        
        logger.info(f"Created reflection entry {entry.id} for user {user.id}")
        return JournalEntryResponse.from_orm(entry)
    
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
    
    async def check_for_entry_today(
        self, 
        user_id: str, 
        entry_type: str
    ) -> bool:
        """Check if user has entry of specific type today."""
        return await self.repository.check_for_entry_today(user_id, entry_type)
    
    async def delete_entry(self, entry_id: UUID) -> bool:
        """Delete a journal entry."""
        success = await self.repository.delete(str(entry_id))
        if success:
            logger.info(f"Deleted journal entry {entry_id}")
        return success
    
    async def get_entry(self, entry_id: UUID) -> Optional[JournalEntryResponse]:
        """Get a specific journal entry."""
        entry = await self.repository.get(str(entry_id))
        if entry:
            return JournalEntryResponse.from_orm(entry)
        return None 