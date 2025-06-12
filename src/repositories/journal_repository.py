import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.journal import JournalEntry as PydanticJournalEntry
from src.models.sql.journal import JournalEntryModel


class JournalRepository:
    """
    Manages CRUD operations for journal entries using SQLAlchemy.
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, entry: PydanticJournalEntry) -> PydanticJournalEntry:
        """Adds a new journal entry to the database."""
        db_entry = JournalEntryModel(
            id=uuid.UUID(entry.id),
            user_id=entry.user_id,
            entry_type=entry.entry_type,
            payload=(
                entry.payload.model_dump()
                if hasattr(entry.payload, "model_dump")
                else entry.payload
            ),
            created_at=entry.created_at,
        )
        self._session.add(db_entry)
        await self._session.flush()
        await self._session.refresh(db_entry)
        return db_entry.to_pydantic()

    async def get_by_id(self, entry_id: uuid.UUID) -> Optional[PydanticJournalEntry]:
        """Retrieves a journal entry by its ID."""
        result = await self._session.get(JournalEntryModel, entry_id)
        return result.to_pydantic() if result else None

    async def list_by_user(self, user_id: str) -> List[PydanticJournalEntry]:
        """Retrieves all journal entries for a specific user."""
        stmt = (
            select(JournalEntryModel)
            .where(JournalEntryModel.user_id == user_id)
            .order_by(JournalEntryModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return [entry.to_pydantic() for entry in result.scalars().all()]

    async def list_by_user_for_period(
        self, user_id: str, start_date: datetime, end_date: datetime
    ) -> List[PydanticJournalEntry]:
        """Retrieves all journal entries for a user within a specific date range."""
        stmt = (
            select(JournalEntryModel)
            .where(
                JournalEntryModel.user_id == user_id,
                JournalEntryModel.created_at >= start_date,
                JournalEntryModel.created_at <= end_date,
            )
            .order_by(JournalEntryModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return [entry.to_pydantic() for entry in result.scalars().all()]

    async def delete(self, entry_id: uuid.UUID) -> bool:
        """Deletes a journal entry by its ID."""
        entry = await self._session.get(JournalEntryModel, entry_id)
        if entry:
            await self._session.delete(entry)
            await self._session.flush()
            return True
        return False
