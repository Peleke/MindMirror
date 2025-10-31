"""
Journal Service Client - Focused, functional client for journal data.

This client provides ONLY the methods actually needed by the agent service,
avoiding the complexity of mirroring the entire GraphQL API.
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from shared.clients.base import AuthContext, BaseServiceClient, ServiceConfig


class JournalEntry:
    """Lightweight journal entry data transfer object."""
    
    def __init__(
        self,
        id: str,
        user_id: str,
        entry_type: str,
        payload: any,
        created_at: datetime,
        modified_at: Optional[datetime] = None
    ):
        self.id = id
        self.user_id = user_id
        self.entry_type = entry_type
        self.payload = payload
        self.created_at = created_at
        self.modified_at = modified_at
    
    @classmethod
    def from_graphql_response(cls, data: Dict) -> "JournalEntry":
        """Create JournalEntry from GraphQL response data."""
        # Handle union types from GraphQL response
        entry_type = data.get("__typename", "").replace("JournalEntry", "").upper()
        
        # Extract payload based on entry type
        payload = None
        if entry_type == "GRATITUDE":
            payload = data.get("gratitudePayload") or data.get("payload")
        elif entry_type == "REFLECTION":
            payload = data.get("reflectionPayload") or data.get("payload")
        elif entry_type == "FREEFORM":
            payload = data.get("freeformPayload") or data.get("payload")
        else:
            payload = data.get("payload")
        
        created_at = datetime.fromisoformat(data["createdAt"].replace("Z", "+00:00"))
        modified_at = None
        if data.get("modifiedAt"):
            modified_at = datetime.fromisoformat(data["modifiedAt"].replace("Z", "+00:00"))
        
        return cls(
            id=data["id"],
            user_id=data["userId"],
            entry_type=entry_type,
            payload=payload,
            created_at=created_at,
            modified_at=modified_at
        )


class JournalServiceClient(BaseServiceClient):
    """
    Client for the Journal Service.
    
    Provides focused methods for retrieving journal data needed by the agent service.
    Does NOT mirror the entire GraphQL API - only what's actually used.
    """
    
    # GraphQL queries used by this client
    _JOURNAL_ENTRIES_QUERY = """
        query GetJournalEntries {
            journalEntries {
                __typename
                ... on GratitudeJournalEntry {
                    id
                    userId
                    createdAt
                    modifiedAt
                    gratitudePayload: payload {
                        gratefulFor
                        excitedAbout
                        focus
                        affirmation
                        mood
                    }
                }
                ... on FreeformJournalEntry {
                    id
                    userId
                    createdAt
                    modifiedAt
                    freeformPayload: payload
                }
                ... on ReflectionJournalEntry {
                    id
                    userId
                    createdAt
                    modifiedAt
                    reflectionPayload: payload {
                        wins
                        improvements
                        mood
                    }
                }
            }
        }
    """
    
    _ENTRY_EXISTS_TODAY_QUERY = """
        query JournalEntryExistsToday($entryType: String!) {
            journalEntryExistsToday(entryType: $entryType)
        }
    """
    
    async def list_entries_for_user(
        self, 
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[JournalEntry]:
        """
        Retrieve journal entries for a user.
        
        Note: The current journal service API doesn't support date filtering,
        so we retrieve all entries and filter client-side if dates are provided.
        This is acceptable for MVP but should be optimized later.
        """
        auth = AuthContext(user_id=user_id)
        
        data = await self.execute_query(
            auth=auth,
            query=self._JOURNAL_ENTRIES_QUERY,
            operation_name="GetJournalEntries"
        )
        
        entries = [
            JournalEntry.from_graphql_response(entry_data)
            for entry_data in data.get("journalEntries", [])
        ]
        
        # Client-side date filtering if needed
        if start_date or end_date:
            filtered_entries = []
            for entry in entries:
                include_entry = True
                if start_date and entry.created_at < start_date:
                    include_entry = False
                if end_date and entry.created_at > end_date:
                    include_entry = False
                if include_entry:
                    filtered_entries.append(entry)
            return filtered_entries
        
        return entries
    
    async def check_entry_exists_today(
        self, 
        user_id: UUID, 
        entry_type: str
    ) -> bool:
        """Check if a journal entry of a specific type exists for today."""
        auth = AuthContext(user_id=user_id)
        
        data = await self.execute_query(
            auth=auth,
            query=self._ENTRY_EXISTS_TODAY_QUERY,
            variables={"entryType": entry_type},
            operation_name="JournalEntryExistsToday"
        )
        
        return data.get("journalEntryExistsToday", False)


def create_journal_client(base_url: str = "http://localhost:8001") -> JournalServiceClient:
    """Factory function to create a journal service client with standard config."""
    config = ServiceConfig(
        base_url=base_url,
        service_name="journal-service",
        timeout=15.0,  # Journal queries should be fast
        max_retries=2,  # Fewer retries for non-critical data
    )
    return JournalServiceClient(config) 