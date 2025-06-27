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


@strawberry.type
class GratitudeJournalEntry:
    id: str
    user_id: str
    entry_type: str = "GRATITUDE"
    payload: GratitudePayloadType
    created_at: datetime
    modified_at: Optional[datetime] = None


@strawberry.type
class ReflectionJournalEntry:
    id: str
    user_id: str
    entry_type: str = "REFLECTION"
    payload: ReflectionPayloadType
    created_at: datetime
    modified_at: Optional[datetime] = None


# A GraphQL Union to represent the different kinds of journal entries
JournalEntryType = strawberry.union(
    "JournalEntryType",
    (FreeformJournalEntry, GratitudeJournalEntry, ReflectionJournalEntry),
    description="A journal entry, which can be freeform, gratitude, or reflection.",
)
