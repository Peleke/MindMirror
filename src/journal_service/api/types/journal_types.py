from datetime import datetime
from typing import List, Optional, Union

import strawberry

# --- Input types for Mutations ---


@strawberry.input
class GratitudeEntryInput:
    grateful_for: List[str]
    excited_about: List[str]
    focus: str
    affirmation: str
    mood: Optional[str] = None


@strawberry.input
class ReflectionEntryInput:
    wins: List[str]
    improvements: List[str]
    mood: Optional[str] = None


@strawberry.input
class FreeformEntryInput:
    content: str


# --- Output types for Queries ---


@strawberry.type
class GratitudePayloadType:
    grateful_for: List[str]
    excited_about: List[str]
    focus: str
    affirmation: str
    mood: Optional[str] = None


@strawberry.type
class ReflectionPayloadType:
    wins: List[str]
    improvements: List[str]
    mood: Optional[str] = None


@strawberry.type
class FreeformJournalEntry:
    id: str
    user_id: str
    entry_type: str = "FREEFORM"
    payload: str
    created_at: datetime
    modified_at: Optional[datetime] = None

    @classmethod
    def from_pydantic(cls, entry):
        return cls(
            id=str(entry.id),
            user_id=str(entry.user_id),
            payload=entry.payload,
            created_at=entry.created_at,
            modified_at=entry.modified_at,
        )


@strawberry.type
class GratitudeJournalEntry:
    id: str
    user_id: str
    entry_type: str = "GRATITUDE"
    payload: GratitudePayloadType
    created_at: datetime
    modified_at: Optional[datetime] = None

    @classmethod
    def from_pydantic(cls, entry):
        return cls(
            id=str(entry.id),
            user_id=str(entry.user_id),
            payload=GratitudePayloadType(**entry.payload.model_dump()),
            created_at=entry.created_at,
            modified_at=entry.modified_at,
        )


@strawberry.type
class ReflectionJournalEntry:
    id: str
    user_id: str
    entry_type: str = "REFLECTION"
    payload: ReflectionPayloadType
    created_at: datetime
    modified_at: Optional[datetime] = None

    @classmethod
    def from_pydantic(cls, entry):
        return cls(
            id=str(entry.id),
            user_id=str(entry.user_id),
            payload=ReflectionPayloadType(**entry.payload.model_dump()),
            created_at=entry.created_at,
            modified_at=entry.modified_at,
        )


# A GraphQL Union to represent the different kinds of journal entries
JournalEntryType = strawberry.union(
    "JournalEntryType",
    (FreeformJournalEntry, GratitudeJournalEntry, ReflectionJournalEntry),
    description="A journal entry, which can be freeform, gratitude, or reflection.",
)
