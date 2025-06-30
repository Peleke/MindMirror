from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID


class GratitudePayload(BaseModel):
    """Gratitude journal entry payload."""
    grateful_for: str = Field(..., min_length=1, max_length=500)
    impact: str = Field(..., min_length=1, max_length=500)
    reflection: Optional[str] = Field(None, max_length=1000)


class ReflectionPayload(BaseModel):
    """Reflection journal entry payload."""
    prompt: str = Field(..., min_length=1, max_length=200)
    response: str = Field(..., min_length=1, max_length=2000)
    insights: Optional[str] = Field(None, max_length=1000)


class JournalEntryResponse(BaseModel):
    """Journal entry response model."""
    id: UUID
    user_id: UUID
    entry_type: str
    payload: Dict[str, Any]
    created_at: datetime
    modified_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CreateJournalEntryRequest(BaseModel):
    """Request model for creating journal entries."""
    entry_type: str = Field(..., pattern="^(GRATITUDE|REFLECTION|FREEFORM)$")
    payload: Dict[str, Any] 