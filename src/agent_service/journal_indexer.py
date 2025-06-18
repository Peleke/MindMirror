import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from agent_service.embedding import get_embedding
from agent_service.vector_stores.qdrant_client import get_qdrant_client
from shared.clients import AuthContext, create_journal_client

logger = logging.getLogger(__name__)


class JournalServiceClient:
    """
    Real client to interact with the Journal Service using HTTP.

    This replaces the previous mock implementation with actual network calls.
    """

    def __init__(self, base_url: str = "http://journal_service:8001"):
        self._http_client = create_journal_client(base_url=base_url)

    async def get_entry_by_id(
        self, entry_id: str, user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Fetches a single journal entry by its ID from the journal service."""
        async with self._http_client as client:
            user_uuid = UUID(user_id)

            # Get all entries and find the specific one
            # Note: In a production system, the journal service would have a get-by-id endpoint
            shared_entries = await client.list_entries_for_user(user_id=user_uuid)

            for entry in shared_entries:
                if entry.id == entry_id:
                    return {
                        "id": entry.id,
                        "user_id": entry.user_id,
                        "created_at": entry.created_at.isoformat(),
                        "entry_type": entry.entry_type,
                        "payload": entry.payload,
                    }

            # Entry not found
            logger.warning(f"Journal entry {entry_id} not found for user {user_id}")
            return None

    async def get_all_entries_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Fetches all journal entries for a user from the journal service."""
        async with self._http_client as client:
            user_uuid = UUID(user_id)
            shared_entries = await client.list_entries_for_user(user_id=user_uuid)

            # Convert to the expected dictionary format
            return [
                {
                    "id": entry.id,
                    "user_id": entry.user_id,
                    "created_at": entry.created_at.isoformat(),
                    "entry_type": entry.entry_type,
                    "payload": entry.payload,
                }
                for entry in shared_entries
            ]


class JournalIndexer:
    """Handles indexing journal entries into the vector store."""

    def __init__(self):
        self.qdrant_client = get_qdrant_client()
        self.journal_service_client = JournalServiceClient()

    async def index_entry(
        self, entry_data: Dict[str, Any], user_id: str, tradition: str = "canon-default"
    ) -> bool:
        """
        Index a single journal entry from its dictionary representation.

        Args:
            entry_data: The journal entry data as a dictionary
            user_id: User identifier
            tradition: Knowledge tradition/collection to use

        Returns:
            True if successful, False otherwise
        """
        try:
            entry_id = entry_data.get("id")
            if not entry_id:
                logger.error("Cannot index entry without an ID.")
                return False

            text_content = self._extract_text_content(entry_data)
            if not text_content or not text_content.strip():
                logger.warning(f"No text content extracted from entry {entry_id}")
                return False

            embedding = await get_embedding(text_content)
            if not embedding:
                logger.error(f"Failed to generate embedding for entry {entry_id}")
                return False

            metadata = self._prepare_metadata(entry_data, user_id)

            point_id = await self.qdrant_client.index_personal_document(
                tradition=tradition,
                user_id=user_id,
                text=text_content,
                embedding=embedding,
                metadata=metadata,
            )

            logger.info(
                f"Successfully indexed journal entry {entry_id} as point {point_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to index journal entry {entry_data.get('id')}: {e}")
            return False

    async def batch_index_entries(
        self, entries_data: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Index multiple journal entries in batch.

        Args:
            entries_data: List of dicts, each must contain 'id' and 'user_id'.

        Returns:
            Dict with counts of indexed and failed entries
        """
        indexed_count = 0
        failed_count = 0

        for entry_data in entries_data:
            try:
                user_id = entry_data.get("user_id")
                tradition = entry_data.get("tradition", "canon-default")
                if not user_id:
                    logger.error(
                        f"Missing user_id for entry in batch indexing: {entry_data.get('id')}"
                    )
                    failed_count += 1
                    continue

                success = await self.index_entry(entry_data, user_id, tradition)
                if success:
                    indexed_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(
                    f"Failed to index entry {entry_data.get('id')} in batch: {e}"
                )
                failed_count += 1

        return {
            "indexed": indexed_count,
            "failed": failed_count,
            "total": len(entries_data),
        }

    async def reindex_user_entries(
        self, user_id: str, tradition: str = "canon-default"
    ) -> Dict[str, int]:
        """
        Reindex all entries for a user by fetching them from the journal_service.

        Args:
            user_id: User identifier
            tradition: Knowledge tradition to use

        Returns:
            Dict with counts of indexed and failed entries
        """
        try:
            entries = await self.journal_service_client.get_all_entries_by_user(user_id)
            if not entries:
                logger.warning(
                    f"No journal entries found for user {user_id} to reindex."
                )
                return {"indexed": 0, "failed": 0, "total": 0}

            collection_name = self.qdrant_client._get_personal_collection_name(
                tradition, user_id
            )
            await self.qdrant_client.recreate_collection(collection_name)
            logger.info(
                f"Cleared and recreated collection {collection_name} for user {user_id}"
            )

            # Add tradition to each entry for batch processing
            for entry in entries:
                entry["tradition"] = tradition

            return await self.batch_index_entries(entries)

        except Exception as e:
            logger.error(f"Failed to reindex entries for user {user_id}: {e}")
            return {"indexed": 0, "failed": 0, "total": 0, "error": str(e)}

    def _extract_text_content(self, entry_data: Dict[str, Any]) -> str:
        """Extract searchable text content from a journal entry dictionary."""
        entry_type = entry_data.get("entry_type", "").upper()
        payload = entry_data.get("payload", {})

        if entry_type == "GRATITUDE":
            grateful_for = payload.get("grateful_for", [])
            excited_about = payload.get("excited_about", [])
            focus = payload.get("focus", "")
            affirmation = payload.get("affirmation", "")

            content_parts = []
            if grateful_for:
                content_parts.append(f"Gratitude: {'. '.join(grateful_for)}")
            if excited_about:
                content_parts.append(f"Excited about: {'. '.join(excited_about)}")
            if focus:
                content_parts.append(f"Focus: {focus}")
            if affirmation:
                content_parts.append(f"Affirmation: {affirmation}")
            return ". ".join(content_parts)

        elif entry_type == "REFLECTION":
            wins = payload.get("wins", [])
            improvements = payload.get("improvements", [])

            content_parts = []
            if wins:
                content_parts.append(f"Wins: {'. '.join(wins)}")
            if improvements:
                content_parts.append(f"Improvements: {'. '.join(improvements)}")

            if not content_parts:
                return ""
            return f"Reflection: {'. '.join(content_parts)}"

        elif entry_type == "FREEFORM":
            return f"Journal: {payload if isinstance(payload, str) else str(payload)}"

        else:
            logger.warning(f"Unknown journal entry type: {entry_type}")
            return str(payload)

    def _prepare_metadata(
        self, entry_data: Dict[str, Any], user_id: str
    ) -> Dict[str, Any]:
        """Prepare metadata for the journal entry."""
        entry_type = entry_data.get("entry_type", "unknown").lower()
        return {
            "source_type": "journal",
            "source_id": str(entry_data.get("id")),
            "user_id": user_id,
            "timestamp": entry_data.get("created_at", datetime.utcnow().isoformat()),
            "document_type": entry_type,
            "entry_type": entry_type,  # Duplicate for backwards compatibility
        }


async def index_journal_entry_by_id(
    entry_id: str, user_id: str, tradition: str = "canon-default"
) -> bool:
    """
    Fetches a journal entry from the journal_service by its ID and indexes it.

    Args:
        entry_id: Journal entry ID
        user_id: User identifier
        tradition: Knowledge tradition to use

    Returns:
        True if successful, False otherwise
    """
    try:
        indexer = JournalIndexer()
        entry_data = await indexer.journal_service_client.get_entry_by_id(
            entry_id, user_id
        )

        if not entry_data:
            logger.error(f"Journal entry {entry_id} not found in journal service.")
            return False

        return await indexer.index_entry(entry_data, user_id, tradition)

    except Exception as e:
        logger.error(f"Failed to index journal entry {entry_id}: {e}")
        return False


async def delete_user_collection(
    user_id: str, tradition: str = "canon-default"
) -> bool:
    """Delete all indexed entries for a user."""
    try:
        qdrant_client = get_qdrant_client()
        collection_name = qdrant_client._get_personal_collection_name(
            tradition, user_id
        )
        return await qdrant_client.delete_collection(collection_name)
    except Exception as e:
        logger.error(f"Failed to delete collection for user {user_id}: {e}")
        return False
