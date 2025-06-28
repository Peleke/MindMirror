"""
Journal Client Retriever

Implements retriever that wraps JournalClient for real journal data access.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from langchain_core.documents import Document

from .base import Retriever, RetrieverMetadata


class JournalRetriever(Retriever):
    """Retriever that wraps JournalClient for real journal data access."""

    def __init__(self, journal_client, user_id: str):
        self.journal_client = journal_client
        self.user_id = user_id
        self._context: Dict[str, Any] = {}

    async def retrieve(self, query: str) -> List[Document]:
        """Retrieve journal entries based on query."""
        # Parse query to determine what to retrieve
        query_lower = query.lower()

        # Determine time period from query
        end_date = datetime.now()
        if "week" in query_lower or "recent" in query_lower:
            start_date = end_date - timedelta(days=7)
        elif "month" in query_lower:
            start_date = end_date - timedelta(days=30)
        elif "quarter" in query_lower:
            start_date = end_date - timedelta(days=90)
        elif "year" in query_lower:
            start_date = end_date - timedelta(days=365)
        else:
            # Default to last month
            start_date = end_date - timedelta(days=30)

        # Get entries from journal client
        entries = await self.journal_client.list_by_user_for_period(
            self.user_id, start_date, end_date
        )

        # Convert entries to documents
        documents = []
        for entry in entries:
            # Create document content based on entry type
            content = self._format_entry_content(entry)

            document = Document(
                page_content=content,
                metadata={
                    "source": "journal",
                    "entry_id": str(entry.id),
                    "user_id": str(entry.user_id),
                    "entry_type": entry.entry_type,
                    "created_at": entry.created_at.isoformat(),
                    "modified_at": (
                        entry.modified_at.isoformat() if entry.modified_at else None
                    ),
                    "query": query,
                },
            )
            documents.append(document)

        return documents

    def _format_entry_content(self, entry) -> str:
        """Format journal entry as document content."""
        if entry.entry_type == "text":
            return entry.payload.get("content", "")
        elif entry.entry_type == "mood":
            mood = entry.payload.get("mood", "unknown")
            note = entry.payload.get("note", "")
            return f"Mood: {mood}\nNote: {note}"
        elif entry.entry_type == "goal":
            title = entry.payload.get("title", "")
            description = entry.payload.get("description", "")
            status = entry.payload.get("status", "unknown")
            return f"Goal: {title}\nDescription: {description}\nStatus: {status}"
        else:
            # Generic format for unknown types
            return str(entry.payload)

    def get_metadata(self) -> RetrieverMetadata:
        """Get journal retriever metadata."""
        return RetrieverMetadata(
            name=f"journal_retriever_{self.user_id}",
            type="http",
            backend="journal_service",
            description="Retriever for journal entries via HTTP client",
            capabilities=["time_based_query", "entry_type_filtering", "user_specific"],
            latency_ms=100.0,  # Estimated HTTP latency
            cost_per_query=0.0,
        )

    def set_context(self, context: Dict[str, Any]) -> None:
        """Set context for the retriever."""
        self._context.update(context)

    async def get_entries_by_type(
        self, entry_type: str, days_back: int = 30
    ) -> List[Document]:
        """Get entries of a specific type."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        entries = await self.journal_client.list_by_user_for_period(
            self.user_id, start_date, end_date
        )
        filtered_entries = [e for e in entries if e.entry_type == entry_type]

        return [
            Document(
                page_content=self._format_entry_content(entry),
                metadata={
                    "source": "journal",
                    "entry_id": str(entry.id),
                    "entry_type": entry.entry_type,
                    "created_at": entry.created_at.isoformat(),
                },
            )
            for entry in filtered_entries
        ]


class JournalRetrieverFactory:
    """Factory for creating journal retrievers."""

    def __init__(self, journal_client):
        self.journal_client = journal_client

    def create_retriever(self, user_id: str) -> JournalRetriever:
        """Create a journal retriever for a specific user."""
        return JournalRetriever(self.journal_client, user_id)
