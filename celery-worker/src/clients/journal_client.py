import logging
import os
import re
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
        self.graphql_endpoint = f"{self.base_url}/graphql"
        self.client = httpx.AsyncClient()
        logger.info(f"Initialized CeleryJournalClient with GraphQL URL: {self.graphql_endpoint}")

    def _camel_to_snake(self, name: str) -> str:
        """Convert camelCase to snake_case."""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def _convert_to_snake_case(self, data: Any) -> Any:
        """Recursively convert camelCase keys to snake_case."""
        if isinstance(data, dict):
            return {
                self._camel_to_snake(k): self._convert_to_snake_case(v)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [self._convert_to_snake_case(item) for item in data]
        else:
            return data

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
            self.graphql_endpoint,
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
            # Simple GraphQL query for journal entry
            query = """
                query GetJournalEntry($id: UUID!) {
                    journalEntry(entryId: $id) {
                        id
                        content
                        entryType
                        createdAt
                        modifiedAt
                        user {
                            id
                        }
                    }
                }
            """
            
            variables = {"id": entry_id}
            
            logger.info(f"Executing GraphQL query for entry {entry_id} with variables: {variables}")
            
            data = await self._execute_query(query, variables, user_id)
            
            logger.info(f"GraphQL response data: {data}")
            
            entry_data = data.get("journalEntry")
            if not entry_data:
                logger.warning(f"Journal entry {entry_id} not found - GraphQL returned: {data}")
                return None

            logger.info(f"Raw entry data from GraphQL: {entry_data}")

            # Convert to snake_case and add user_id for convenience
            converted_data = self._convert_to_snake_case(entry_data)
            if "user" in converted_data and "id" in converted_data["user"]:
                converted_data["user_id"] = converted_data["user"]["id"]

            logger.info(f"Retrieved journal entry {entry_id} for user {user_id}")
            return converted_data

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
        
        return entry_data.get("payload", entry_data)

    async def list_by_user_for_period(
        self, user_id: str, start_date: str, end_date: str
    ) -> List[Dict[str, Any]]:
        """
        List journal entries for a user within a specific time period using GraphQL.

        Args:
            user_id: The user ID
            start_date: Start of the time period (ISO string)
            end_date: End of the time period (ISO string)

        Returns:
            List of journal entry dictionaries
        """
        try:
            # Simple GraphQL query for journal entries
            query = """
                query GetJournalEntries($userId: UUID!, $startDate: DateTime!, $endDate: DateTime!) {
                    journalEntries(userId: $userId, startDate: $startDate, endDate: $endDate) {
                        id
                        content
                        entryType
                        createdAt
                        modifiedAt
                    }
                }
            """
            
            variables = {
                "userId": user_id,
                "startDate": start_date,
                "endDate": end_date
            }
            
            data = await self._execute_query(query, variables, user_id)
            
            entries_data = data.get("journalEntries", [])

            # Convert to snake_case
            converted_entries = self._convert_to_snake_case(entries_data)

            logger.info(f"Retrieved {len(converted_entries)} journal entries for user {user_id}")
            return converted_entries

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
            if payload.get("mood"):
                parts.append(f"Mood: {payload['mood']}")
            return "\n".join(parts)
        elif entry_type == "REFLECTION":
            parts = []
            if payload.get("wins"):
                parts.append(f"Wins: {', '.join(payload['wins'])}")
            if payload.get("improvements"):
                parts.append(f"Improvements: {', '.join(payload['improvements'])}")
            if payload.get("mood"):
                parts.append(f"Mood: {payload['mood']}")
            return "\n".join(parts)
        
        return str(payload) if payload else ""


# Global instance
_celery_journal_client = None


def get_celery_journal_client() -> CeleryJournalClient:
    """Get the global CeleryJournalClient instance."""
    global _celery_journal_client
    if _celery_journal_client is None:
        _celery_journal_client = CeleryJournalClient()
    return _celery_journal_client


def create_celery_journal_client() -> CeleryJournalClient:
    """Create a new CeleryJournalClient instance."""
    return CeleryJournalClient() 