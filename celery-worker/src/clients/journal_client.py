import logging
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import httpx

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


class CeleryJournalClient:
    """Celery-specific journal client that uses GraphQL to talk to journal service."""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("JOURNAL_SERVICE_URL", "http://journal_service:8001")
        self.graphql_url = f"{self.base_url}/graphql"
        self.client = httpx.AsyncClient()
        logger.info(f"Initialized CeleryJournalClient with GraphQL URL: {self.graphql_url}")

    async def _execute_query(self, query: str, variables: Dict[str, Any] = None, user_id: str = None) -> Dict[str, Any]:
        """Execute a GraphQL query."""
        payload = {
            "query": query,
            "variables": variables or {}
        }
        
        headers = {"Content-Type": "application/json"}
        
        # Add user context for authentication if user_id is provided
        if user_id:
            # The journal service uses x-internal-id header to identify the user
            headers["x-internal-id"] = user_id
        
        response = await self.client.post(
            self.graphql_url,
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        
        result = response.json()
        if "errors" in result:
            raise Exception(f"GraphQL errors: {result['errors']}")
        
        return result.get("data", {})

    async def get_entry_by_id(self, entry_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific journal entry by ID using GraphQL.

        Args:
            entry_id: The journal entry ID
            user_id: The user ID (for validation)

        Returns:
            Journal entry dictionary if found, None otherwise
        """
        try:
            from .queries import GET_JOURNAL_ENTRY_BY_ID
            
            variables = {
                "entryId": entry_id
            }
            
            logger.info(f"Executing GraphQL query for entry {entry_id} with variables: {variables}")
            
            # Note: GraphQL context will handle user validation
            data = await self._execute_query(GET_JOURNAL_ENTRY_BY_ID, variables, user_id)
            
            logger.info(f"GraphQL response data: {data}")
            
            entry_data = data.get("journalEntry")
            if not entry_data:
                logger.warning(f"Journal entry {entry_id} not found - GraphQL returned: {data}")
                return None

            logger.info(f"Raw entry data from GraphQL: {entry_data}")

            # Convert GraphQL response to the format expected by indexing code
            result = {
                "id": entry_data["id"],
                "user_id": entry_data["userId"],
                "entry_type": entry_data["entryType"],
                "payload": self._extract_payload_from_entry(entry_data),
                "created_at": entry_data["createdAt"],
                "updated_at": entry_data.get("modifiedAt", entry_data["createdAt"]),
                "metadata": {}
            }

            logger.info(f"Converted result: {result}")
            logger.info(f"Retrieved journal entry {entry_id} for user {user_id}")
            return result

        except Exception as e:
            logger.error(f"Failed to get journal entry {entry_id}: {e}")
            return None

    def _extract_payload_from_entry(self, entry_data: Dict[str, Any]) -> Any:
        """Extract payload from GraphQL entry data based on entry type."""
        entry_type = entry_data.get("entryType", "")
        
        if entry_type == "GRATITUDE":
            payload = entry_data.get("payload", {})
            if isinstance(payload, dict):
                return {
                    "grateful_for": payload.get("gratefulFor", []),
                    "excited_about": payload.get("excitedAbout", []),
                    "focus": payload.get("focus", ""),
                    "affirmation": payload.get("affirmation", ""),
                    "mood": payload.get("mood", "")
                }
        elif entry_type == "REFLECTION":
            payload = entry_data.get("payload", {})
            if isinstance(payload, dict):
                return {
                    "wins": payload.get("wins", []),
                    "improvements": payload.get("improvements", []),
                    "mood": payload.get("mood", "")
                }
        elif entry_type == "FREEFORM":
            # For freeform, the content comes from the 'content' field
            content = entry_data.get("content", "")
            return {"content": content if isinstance(content, str) else str(content)}
        
        return entry_data.get("payload", {})

    async def list_by_user_for_period(
        self, user_id: str, start_date: datetime, end_date: datetime
    ) -> List[JournalEntry]:
        """
        List journal entries for a user within a specific time period using GraphQL.

        Args:
            user_id: The user ID
            start_date: Start of the time period
            end_date: End of the time period

        Returns:
            List of journal entries
        """
        try:
            from .queries import GET_JOURNAL_ENTRIES
            
            # Note: We'll need to filter by date on the client side since the schema
            # doesn't seem to have date filtering built in
            data = await self._execute_query(GET_JOURNAL_ENTRIES, {"limit": 100}, user_id)
            
            entries_data = data.get("journalEntries", [])
            
            # Convert to JournalEntry objects and filter by date
            entries = []
            for entry_data in entries_data:
                entry_created_at = datetime.fromisoformat(entry_data["createdAt"].replace("Z", "+00:00"))
                
                # Filter by date range
                if start_date <= entry_created_at <= end_date:
                    payload = self._extract_payload_from_entry(entry_data)
                    content = self._extract_content_from_payload(payload, entry_data.get("entryType", ""))
                    
                    entry = JournalEntry(
                        id=entry_data["id"],
                        user_id=entry_data["userId"],
                        content=content,
                        created_at=entry_created_at,
                        updated_at=datetime.fromisoformat(entry_data.get("modifiedAt", entry_data["createdAt"]).replace("Z", "+00:00")),
                        metadata={}
                    )
                    entries.append(entry)

            logger.info(f"Retrieved {len(entries)} journal entries for user {user_id}")
            return entries

        except Exception as e:
            logger.error(f"Failed to list journal entries for user {user_id}: {e}")
            raise

    def _extract_content_from_payload(self, payload: Any, entry_type: str) -> str:
        """Extract text content from payload for different entry types."""
        if entry_type == "FREEFORM":
            return payload.get("content", "") if isinstance(payload, dict) else str(payload)
        elif entry_type == "GRATITUDE":
            parts = []
            if payload.get("grateful_for"):
                parts.append(f"Grateful for: {', '.join(payload['grateful_for'])}")
            if payload.get("excited_about"):
                parts.append(f"Excited about: {', '.join(payload['excited_about'])}")
            if payload.get("focus"):
                parts.append(f"Focus: {payload['focus']}")
            if payload.get("affirmation"):
                parts.append(f"Affirmation: {payload['affirmation']}")
            return " ".join(parts)
        elif entry_type == "REFLECTION":
            parts = []
            if payload.get("wins"):
                parts.append(f"Wins: {', '.join(payload['wins'])}")
            if payload.get("improvements"):
                parts.append(f"Improvements: {', '.join(payload['improvements'])}")
            if payload.get("mood"):
                parts.append(f"Mood: {payload['mood']}")
            return " ".join(parts)
        
        return str(payload) if payload else ""


# Global client instance
_celery_journal_client: Optional[CeleryJournalClient] = None


def create_celery_journal_client() -> CeleryJournalClient:
    """Create or get the global Celery journal client instance."""
    global _celery_journal_client
    if _celery_journal_client is None:
        _celery_journal_client = CeleryJournalClient()
    return _celery_journal_client 