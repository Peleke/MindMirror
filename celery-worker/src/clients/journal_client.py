import logging
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass

from src.clients.agent_service_client import AgentServiceClient

logger = logging.getLogger(__name__)


@dataclass
class JournalEntry:
    """Journal entry model for Celery operations."""
    id: str
    user_id: str
    content: str
    created_at: datetime
    updated_at: datetime
    metadata: Optional[dict] = None


class CeleryJournalClient(AgentServiceClient):
    """Celery-specific journal client for background operations."""

    def __init__(self, base_url: str = None):
        super().__init__(base_url)
        logger.info(f"Initialized CeleryJournalClient with base_url: {self.base_url}")

    async def list_by_user_for_period(
        self, user_id: str, start_date: datetime, end_date: datetime
    ) -> List[JournalEntry]:
        """
        List journal entries for a user within a specific time period.

        Args:
            user_id: The user ID
            start_date: Start of the time period
            end_date: End of the time period

        Returns:
            List of journal entries
        """
        try:
            # Use the parent class method to get raw data
            entries_data = await super().list_journal_entries_by_user_for_period(
                user_id, start_date, end_date
            )

            # Convert to JournalEntry objects
            entries = []
            for entry_data in entries_data:
                entry = JournalEntry(
                    id=entry_data["id"],
                    user_id=entry_data["user_id"],
                    content=entry_data["content"],
                    created_at=datetime.fromisoformat(entry_data["created_at"]),
                    updated_at=datetime.fromisoformat(entry_data["updated_at"]),
                    metadata=entry_data.get("metadata"),
                )
                entries.append(entry)

            logger.info(f"Retrieved {len(entries)} journal entries for user {user_id}")
            return entries

        except Exception as e:
            logger.error(f"Failed to list journal entries for user {user_id}: {e}")
            raise

    async def get_entry_by_id(self, entry_id: str) -> Optional[JournalEntry]:
        """
        Get a specific journal entry by ID.

        Args:
            entry_id: The journal entry ID

        Returns:
            Journal entry if found, None otherwise
        """
        try:
            # Use the parent class method to get raw data
            entry_data = await super().get_journal_entry_by_id(entry_id)

            if not entry_data:
                logger.warning(f"Journal entry {entry_id} not found")
                return None

            # Convert to JournalEntry object
            entry = JournalEntry(
                id=entry_data["id"],
                user_id=entry_data["user_id"],
                content=entry_data["content"],
                created_at=datetime.fromisoformat(entry_data["created_at"]),
                updated_at=datetime.fromisoformat(entry_data["updated_at"]),
                metadata=entry_data.get("metadata"),
            )

            logger.info(f"Retrieved journal entry {entry_id}")
            return entry

        except Exception as e:
            logger.error(f"Failed to get journal entry {entry_id}: {e}")
            raise


# Global client instance
_celery_journal_client: Optional[CeleryJournalClient] = None


def create_celery_journal_client() -> CeleryJournalClient:
    """Create or get the global Celery journal client instance."""
    global _celery_journal_client
    if _celery_journal_client is None:
        _celery_journal_client = CeleryJournalClient()
    return _celery_journal_client 