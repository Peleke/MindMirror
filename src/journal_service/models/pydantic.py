from datetime import datetime
from typing import List, Literal, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, Field


def a_uuid():
    return str(uuid4())


# --- Payload Models for Structured Entries ---


class GratitudePayload(BaseModel):
    """Data for a morning gratitude entry."""

    grateful_for: List[str] = Field(..., min_length=3, max_length=3)
    excited_about: List[str] = Field(..., min_length=3, max_length=3)
    focus: str
    affirmation: str
    mood: Optional[str] = None


class ReflectionPayload(BaseModel):
    """Data for an evening reflection entry."""

    wins: List[str] = Field(..., min_length=3, max_length=3)
    improvements: List[str] = Field(..., min_length=2, max_length=2)
    mood: Optional[str] = None


# --- Main Journal Entry Model ---


class JournalEntry(BaseModel):
    """
    A polymorphic Pydantic model representing a single journal entry.
    The `entry_type` determines the structure of the `payload`.
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
