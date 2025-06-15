from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class GratitudeJournalEntry(BaseModel):
    id: UUID
    user_id: UUID
    created_at: datetime
    gratitude_items: List[str]

    class Config:
        orm_mode = True


class ReflectionJournalEntry(BaseModel):
    id: UUID
    user_id: UUID
    created_at: datetime
    reflection: str

    class Config:
        orm_mode = True


class JournalEntryModel(BaseModel):
    """
    A Pydantic model representing a journal entry fetched from the database.
    """
    id: UUID
    user_id: str
    entry_type: str
    payload: dict
    created_at: datetime
    modified_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True 