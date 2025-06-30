import strawberry
from datetime import datetime
from typing import Optional, List


@strawberry.type
class GratitudePayloadType:
    """GraphQL type for gratitude payload."""
    grateful_for: str
    impact: str
    reflection: Optional[str] = None


@strawberry.type
class ReflectionPayloadType:
    """GraphQL type for reflection payload."""
    prompt: str
    response: str
    insights: Optional[str] = None


@strawberry.type
class JournalEntryType:
    """Base GraphQL type for journal entries."""
    id: str
    user_id: str
    entry_type: str
    created_at: datetime
    modified_at: Optional[datetime] = None


@strawberry.type
class GratitudeJournalEntry(JournalEntryType):
    """GraphQL type for gratitude journal entries."""
    payload: GratitudePayloadType


@strawberry.type
class ReflectionJournalEntry(JournalEntryType):
    """GraphQL type for reflection journal entries."""
    payload: ReflectionPayloadType


@strawberry.type
class FreeformJournalEntry(JournalEntryType):
    """GraphQL type for freeform journal entries."""
    payload: str


# Input types
@strawberry.input
class GratitudeEntryInput:
    """Input type for creating gratitude entries."""
    grateful_for: str
    impact: str
    reflection: Optional[str] = None


@strawberry.input
class ReflectionEntryInput:
    """Input type for creating reflection entries."""
    prompt: str
    response: str
    insights: Optional[str] = None


@strawberry.input
class FreeformEntryInput:
    """Input type for creating freeform entries."""
    content: str 