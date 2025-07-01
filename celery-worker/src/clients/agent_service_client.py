import logging
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)


class AgentServiceClient:
    """Base client for communicating with the agent service."""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv(
            "AGENT_SERVICE_URL", "http://agent_service:8000"
        )
        self.client = httpx.AsyncClient()
        logger.info(f"Initialized AgentServiceClient with base_url: {self.base_url}")

    async def list_journal_entries_by_user_for_period(
        self, user_id: str, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        List journal entries for a user within a specific time period.

        Args:
            user_id: The user ID
            start_date: Start of the time period
            end_date: End of the time period

        Returns:
            List of journal entry dictionaries
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/journal/entries",
                params={
                    "user_id": user_id,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to list journal entries for user {user_id}: {e}")
            return []

    async def get_journal_entry_by_id(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific journal entry by ID.

        Args:
            entry_id: The journal entry ID

        Returns:
            Journal entry dictionary if found, None otherwise
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/journal/entries/{entry_id}"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get journal entry {entry_id}: {e}")
            return None

    async def create_journal_entry(
        self, user_id: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new journal entry.

        Args:
            user_id: The user ID
            content: The journal entry content
            metadata: Optional metadata

        Returns:
            Created journal entry dictionary
        """
        try:
            payload = {
                "user_id": user_id,
                "content": content,
                "metadata": metadata or {},
            }
            response = await self.client.post(
                f"{self.base_url}/api/journal/entries", json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create journal entry for user {user_id}: {e}")
            return None

    async def update_journal_entry(
        self, entry_id: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing journal entry.

        Args:
            entry_id: The journal entry ID
            content: The updated content
            metadata: Optional updated metadata

        Returns:
            Updated journal entry dictionary
        """
        try:
            payload = {"content": content, "metadata": metadata or {}}
            response = await self.client.put(
                f"{self.base_url}/api/journal/entries/{entry_id}", json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to update journal entry {entry_id}: {e}")
            return None

    async def delete_journal_entry(self, entry_id: str) -> bool:
        """
        Delete a journal entry.

        Args:
            entry_id: The journal entry ID

        Returns:
            True if successful, False otherwise
        """
        try:
            response = await self.client.delete(
                f"{self.base_url}/api/journal/entries/{entry_id}"
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to delete journal entry {entry_id}: {e}")
            return False

    async def health_check(self) -> bool:
        """Check if the agent service is healthy."""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Agent service health check failed: {e}")
            return False
