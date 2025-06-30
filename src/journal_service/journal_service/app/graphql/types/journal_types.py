import strawberry
from datetime import datetime
from typing import Optional, List, Union


@strawberry.type
class GratitudePayloadType:
    """GraphQL type for gratitude payload."""
    gratefulFor: List[str]
    excitedAbout: List[str]
    focus: Optional[str] = None
    affirmation: Optional[str] = None
    mood: Optional[str] = None


@strawberry.type
class ReflectionPayloadType:
    """GraphQL type for reflection payload."""
    wins: List[str]
    improvements: List[str]
    mood: Optional[str] = None


@strawberry.interface
class JournalEntryInterface:
    """Base interface for journal entries."""
    id: str
    userId: str
    entryType: str
    createdAt: datetime
    modifiedAt: Optional[datetime] = None


@strawberry.type
class GratitudeJournalEntry(JournalEntryInterface):
    """GraphQL type for gratitude journal entries."""
    payload: GratitudePayloadType


@strawberry.type
class ReflectionJournalEntry(JournalEntryInterface):
    """GraphQL type for reflection journal entries."""
    payload: ReflectionPayloadType


@strawberry.type
class FreeformJournalEntry(JournalEntryInterface):
    """GraphQL type for freeform journal entries."""
    payload: str


# Input types
@strawberry.input
class GratitudeEntryInput:
    """Input type for creating gratitude entries."""
    gratefulFor: List[str]
    excitedAbout: List[str]
    focus: Optional[str] = None
    affirmation: Optional[str] = None
    mood: Optional[str] = None


@strawberry.input
class ReflectionEntryInput:
    """Input type for creating reflection entries."""
    wins: List[str]
    improvements: List[str]
    mood: Optional[str] = None


@strawberry.input
class FreeformEntryInput:
    """Input type for creating freeform entries."""
    content: str 