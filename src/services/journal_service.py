import uuid
from datetime import date, datetime
from typing import List, Optional, Union

from shared.auth import CurrentUser
from src.models.journal import (GratitudePayload, JournalEntry,
                                ReflectionPayload)
from src.repositories.journal_repository import JournalRepository


class JournalService:
    """
    Provides business logic for managing journal entries.
    """

    def __init__(self, repository: JournalRepository):
        self._repository = repository

    async def create_freeform_entry(
        self, current_user: CurrentUser, content: str
    ) -> JournalEntry:
        """Creates a simple, freeform text journal entry."""
        entry = JournalEntry(
            user_id=str(current_user.id), entry_type="FREEFORM", payload=content
        )
        return await self._repository.create(entry)

    async def create_gratitude_entry(
        self, current_user: CurrentUser, payload: GratitudePayload
    ) -> JournalEntry:
        """Creates a structured gratitude journal entry."""
        entry = JournalEntry(
            user_id=str(current_user.id), entry_type="GRATITUDE", payload=payload
        )
        return await self._repository.create(entry)

    async def create_reflection_entry(
        self, current_user: CurrentUser, payload: ReflectionPayload
    ) -> JournalEntry:
        """Creates a structured reflection journal entry."""
        entry = JournalEntry(
            user_id=str(current_user.id), entry_type="REFLECTION", payload=payload
        )
        return await self._repository.create(entry)

    def get_entry(self, entry_id: str) -> Optional[JournalEntry]:
        """Retrieves a single journal entry."""
        return self._repository.get_by_id(entry_id)

    async def get_entries_for_user(self, user_id: str) -> List[JournalEntry]:
        """Retrieves all journal entries for a user."""
        return await self._repository.list_by_user(user_id)

    async def check_for_entry_today(self, user_id: str, entry_type: str) -> bool:
        """Checks if an entry of a specific type exists for the user today."""
        today = date.today()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())

        entries_today = await self._repository.list_by_user_for_period(
            user_id, start_of_day, end_of_day
        )

        return any(entry.entry_type == entry_type for entry in entries_today)

    def update_entry_payload(
        self, entry_id: str, payload: Union[str, GratitudePayload, ReflectionPayload]
    ) -> Optional[JournalEntry]:
        """Updates the payload of an existing journal entry."""
        return self._repository.update(entry_id, {"payload": payload})

    async def delete_entry(self, entry_id: str) -> bool:
        """Deletes a journal entry."""
        return await self._repository.delete(uuid.UUID(entry_id))
