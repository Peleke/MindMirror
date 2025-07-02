"""
Shared journal service client for MindMirror services.

This module provides HTTP clients and authentication context managers
for communicating with the journal service.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class JournalEntryResponse(BaseModel):
    """Response model for journal entries from the journal service."""
    id: str
    user_id: str
    entry_type: str
    payload: Any
    created_at: datetime
    modified_at: Optional[datetime] = None


class AuthContext:
    """
    Context manager for authenticated HTTP requests to the journal service.
    
    This provides a standardized way to make authenticated requests
    with proper headers and error handling.
    """
    
    def __init__(self, token: Optional[str] = None, user_id: Optional[UUID] = None):
        self.token = token
        self.user_id = user_id
        self._headers = {}
        
        if token:
            self._headers["Authorization"] = f"Bearer {token}"
        if user_id:
            self._headers["x-internal-id"] = str(user_id)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get the authentication headers for requests."""
        return self._headers.copy()


class JournalServiceClient:
    """
    HTTP client for communicating with the journal service.
    
    This client provides methods to interact with the journal service's
    GraphQL API for fetching journal entries.
    """
    
    def __init__(self, base_url: str = "http://journal_service:8001"):
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        pass
    
    async def list_entries_for_user(
        self, 
        user_id: UUID, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> List[JournalEntryResponse]:
        """
        Fetch journal entries for a user, optionally filtered by date range.
        
        Args:
            user_id: The user's UUID
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            List of journal entries
        """
        # Build the GraphQL query with aliases to avoid payload field conflicts
        query = """
            query GetJournalEntries {
                journalEntries {
                    __typename
                    ... on GratitudeJournalEntry {
                        id
                        userId
                        gratitudePayload: payload {
                            gratefulFor
                            excitedAbout
                            focus
                            affirmation
                            mood
                        }
                        createdAt
                        modifiedAt
                    }
                    ... on FreeformJournalEntry {
                        id
                        userId
                        freeformPayload: payload
                        createdAt
                        modifiedAt
                    }
                    ... on ReflectionJournalEntry {
                        id
                        userId
                        reflectionPayload: payload {
                            wins
                            improvements
                            mood
                        }
                        createdAt
                        modifiedAt
                    }
                }
            }
        """
        
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as client:
                response = await client.post(
                    "/graphql",
                    json={"query": query},
                    headers={"x-internal-id": str(user_id)}
                )
                response.raise_for_status()
                
                data = response.json()
                if "errors" in data:
                    self.logger.error(f"GraphQL errors: {data['errors']}")
                    return []
                
                entries_data = data["data"]["journalEntries"]
                entries = []
                
                for entry_data in entries_data:
                    # Extract payload based on entry type
                    payload = None
                    if entry_data["__typename"] == "GratitudeJournalEntry":
                        payload = entry_data.get("gratitudePayload")
                    elif entry_data["__typename"] == "FreeformJournalEntry":
                        payload = entry_data.get("freeformPayload")
                    elif entry_data["__typename"] == "ReflectionJournalEntry":
                        payload = entry_data.get("reflectionPayload")
                    
                    # Convert GraphQL response to our standard format
                    entry = JournalEntryResponse(
                        id=entry_data["id"],
                        user_id=entry_data["userId"],
                        entry_type=entry_data["__typename"].replace("JournalEntry", "").upper(),
                        payload=payload,
                        created_at=datetime.fromisoformat(entry_data["createdAt"].replace("Z", "+00:00")),
                        modified_at=datetime.fromisoformat(entry_data["modifiedAt"].replace("Z", "+00:00")) if entry_data.get("modifiedAt") else None
                    )
                    
                    # Apply date filtering if specified
                    if start_date:
                        # Ensure both datetimes are timezone-aware for comparison
                        entry_utc = entry.created_at
                        if entry_utc.tzinfo is None:
                            entry_utc = entry_utc.replace(tzinfo=timezone.utc)
                        else:
                            entry_utc = entry_utc.astimezone(timezone.utc)
                        
                        start_utc = start_date
                        if start_utc.tzinfo is None:
                            start_utc = start_utc.replace(tzinfo=timezone.utc)
                        else:
                            start_utc = start_utc.astimezone(timezone.utc)
                        
                        if entry_utc < start_utc:
                            continue
                    if end_date:
                        # Ensure both datetimes are timezone-aware for comparison
                        entry_utc = entry.created_at
                        if entry_utc.tzinfo is None:
                            entry_utc = entry_utc.replace(tzinfo=timezone.utc)
                        else:
                            entry_utc = entry_utc.astimezone(timezone.utc)
                        
                        end_utc = end_date
                        if end_utc.tzinfo is None:
                            end_utc = end_utc.replace(tzinfo=timezone.utc)
                        else:
                            end_utc = end_utc.astimezone(timezone.utc)
                        
                        if entry_utc > end_utc:
                            continue
                    
                    entries.append(entry)
                
                return entries
                
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error fetching journal entries: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error fetching journal entries: {e}", exc_info=True)
            return []
    
    async def get_entry_by_id(self, entry_id: str, user_id: UUID) -> Optional[JournalEntryResponse]:
        """
        Fetch a specific journal entry by ID.
        
        Args:
            entry_id: The entry ID
            user_id: The user's UUID
            
        Returns:
            The journal entry if found, None otherwise
        """
        # For now, we'll fetch all entries and filter by ID
        # In a production system, the journal service would have a get-by-id endpoint
        entries = await self.list_entries_for_user(user_id)
        
        for entry in entries:
            if entry.id == entry_id:
                return entry
        
        return None


def create_journal_client(base_url: str = "http://journal_service:8001") -> JournalServiceClient:
    """
    Factory function to create a configured journal service client.
    
    Args:
        base_url: The base URL for the journal service
        
    Returns:
        A configured JournalServiceClient instance
    """
    return JournalServiceClient(base_url=base_url) 