from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from journal_service.journal_service.app.db.repositories.base import BaseRepository
from journal_service.journal_service.app.db.models.journal import JournalEntry


class JournalRepository(BaseRepository[JournalEntry]):
    """Repository for journal entries."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, JournalEntry)
    
    async def get_entries_for_user(
        self, 
        user_id: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[JournalEntry]:
        """Get journal entries for specific user."""
        result = await self.session.execute(
            select(JournalEntry)
            .where(JournalEntry.user_id == user_id)
            .order_by(JournalEntry.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def check_for_entry_today(
        self, 
        user_id: str, 
        entry_type: str
    ) -> bool:
        """Check if user has entry of specific type today."""
        today = datetime.utcnow().date()
        result = await self.session.execute(
            select(JournalEntry)
            .where(
                JournalEntry.user_id == user_id,
                JournalEntry.entry_type == entry_type,
                func.date(JournalEntry.created_at) == today
            )
        )
        return result.scalar_one_or_none() is not None
    
    async def get_entries_by_type(
        self,
        user_id: str,
        entry_type: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[JournalEntry]:
        """Get journal entries by type for user."""
        result = await self.session.execute(
            select(JournalEntry)
            .where(
                JournalEntry.user_id == user_id,
                JournalEntry.entry_type == entry_type
            )
            .order_by(JournalEntry.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all() 