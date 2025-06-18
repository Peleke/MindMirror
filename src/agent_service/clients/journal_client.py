"""
Real Journal Service Client for Agent Service.

This module replaces the previous mock with a real HTTP client
that communicates with the journal service over the network.
"""

from datetime import datetime
from typing import List
from uuid import UUID

from agent_service.models.journal import JournalEntry
from shared.clients import (AuthContext, JournalServiceClient,
                            create_journal_client)


class JournalClient:
    """
    A client to interact with the external journal service using HTTP.

    This client adapts our shared HTTP client to the agent service's
    expected interface and data models.
    """

    def __init__(self, base_url: str = "http://journal_service:8001"):
        self._http_client = create_journal_client(base_url=base_url)

    async def list_by_user_for_period(
        self, user_id: str, start_date: datetime, end_date: datetime
    ) -> List[JournalEntry]:
        """
        Retrieves journal entries for a user within a date range.

        This method adapts the shared client's response to the agent service's
        JournalEntry model for compatibility with existing code.
        """
        async with self._http_client as client:
            # Convert string user_id to UUID for the shared client
            user_uuid = UUID(user_id)

            # Get all entries for the user and filter by date range
            shared_entries = await client.list_entries_for_user(
                user_id=user_uuid, start_date=start_date, end_date=end_date
            )

            # Convert shared client entries to agent service model
            agent_entries = []
            for shared_entry in shared_entries:
                agent_entry = JournalEntry(
                    id=shared_entry.id,
                    user_id=shared_entry.user_id,
                    entry_type=shared_entry.entry_type,
                    payload=shared_entry.payload,
                    created_at=shared_entry.created_at,
                    modified_at=shared_entry.modified_at,
                )
                agent_entries.append(agent_entry)

            return agent_entries

    async def get_entry_by_id(self, entry_id: str, user_id: str) -> dict:
        """
        Get a single journal entry by ID.

        This method is used by the journal indexer and returns a dictionary
        format that matches the existing integration expectations.
        """
        async with self._http_client as client:
            user_uuid = UUID(user_id)

            # Get all entries and find the specific one
            # In a real implementation, the journal service would have a get-by-id endpoint
            shared_entries = await client.list_entries_for_user(user_id=user_uuid)

            for entry in shared_entries:
                if entry.id == entry_id:
                    return {
                        "id": entry.id,
                        "user_id": entry.user_id,
                        "entry_type": entry.entry_type,
                        "payload": entry.payload,
                        "created_at": entry.created_at.isoformat(),
                        "modified_at": (
                            entry.modified_at.isoformat() if entry.modified_at else None
                        ),
                    }

            # Entry not found
            return None
