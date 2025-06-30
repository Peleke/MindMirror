from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class CurrentUser(BaseModel):
    """Current user model for authentication."""
    id: UUID
    email: str
    role: str
    is_active: bool = True


class CreateFreeformEntryRequest(BaseModel):
    """Request for creating a freeform journal entry."""
    content: str


class CreateGratitudeEntryRequest(BaseModel):
    """Request for creating a gratitude journal entry."""
    grateful_for: str
    impact: str
    reflection: Optional[str] = None


class CreateReflectionEntryRequest(BaseModel):
    """Request for creating a reflection journal entry."""
    prompt: str
    response: str
    insights: Optional[str] = None


class DeleteEntryRequest(BaseModel):
    """Request for deleting a journal entry."""
    entry_id: UUID 