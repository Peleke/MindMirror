from datetime import datetime
from typing import List, Literal, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, Field


class GratitudePayload(BaseModel):
    """Data for a morning gratitude entry."""

    grateful_for: List[str]
    excited_about: List[str]
    focus: str
    affirmation: str
    mood: Optional[str] = None


class ReflectionPayload(BaseModel):
    """Data for an evening reflection entry."""

    wins: List[str]
    improvements: List[str]
    mood: Optional[str] = None


class JournalEntry(BaseModel):
    """
    A Pydantic model representing a single journal entry for the agent service.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    entry_type: Literal["GRATITUDE", "REFLECTION", "FREEFORM"]
    payload: Union[str, GratitudePayload, ReflectionPayload]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        } 