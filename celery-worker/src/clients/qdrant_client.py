# Import the Qdrant client from agent service
# We'll need to copy the implementation or create a local version
import logging
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient as QdrantClientBase
from qdrant_client.http.exceptions import ResponseHandlingException
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    SearchRequest,
    VectorParams,
    Range,
)
from qdrant_client.http import models

from ..config import Config

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Result from a vector search operation."""

    id: str
    score: float
    payload: Dict[str, Any]
    vector: Optional[List[float]] = None

    def is_personal_content(self) -> bool:
        """Check if this result is from personal journal content."""
        return self.payload.get("source_type") == "journal"


class CeleryQdrantClient:
    """Qdrant client for celery-worker operations."""

    def __init__(self, url: str = None, api_key: str = None):
        """Initialize Qdrant client."""
        self.url = url or Config.QDRANT_URL
        self.api_key = api_key or Config.QDRANT_API_KEY
        
        # Debug logging
        logger.debug(f"Qdrant URL: {self.url}")
        logger.debug(f"Qdrant API key present: {bool(self.api_key)}")
        
        # Initialize client with API key if provided
        if self.api_key:
            self.client = QdrantClientBase(url=self.url, api_key=self.api_key)
            logger.info(f"Initialized CeleryQdrantClient with {self.url} (with API key)")
        else:
            self.client = QdrantClientBase(url=self.url)
            logger.warning(f"Initialized CeleryQdrantClient with {self.url} (no API key - may cause auth issues)")

    async def health_check(self) -> bool:
        """Check if Qdrant is healthy and reachable."""
        try:
            # Get collections info as a health check
            collections = self.client.get_collections()
            logger.debug("Qdrant health check successful")
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False

    def get_knowledge_collection_name(self, tradition: str) -> str:
        """Returns the standardized name for a tradition's knowledge collection."""
        return f"{tradition}_knowledge"

    async def get_or_create_knowledge_collection(self, tradition: str) -> str:
        """
        Ensures a knowledge collection exists for a tradition and returns its name.
        """
        collection_name = self.get_knowledge_collection_name(tradition)
        await self._create_collection(collection_name)
        return collection_name

    async def _create_collection(self, collection_name: str) -> bool:
        """Internal method to create a collection with standard configuration."""
        try:
            # Check if collection already exists
            collections = self.client.get_collections()
            existing_names = [col.name for col in collections.collections]

            if collection_name in existing_names:
                logger.info(f"Collection {collection_name} already exists")
                return True

            # Create new collection with vector configuration
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=Config.VECTOR_SIZE, distance=Distance.COSINE
                ),
            )

            logger.info(f"Created collection: {collection_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to create collection {collection_name}: {e}")
            return False

    async def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection and all its documents."""
        try:
            self.client.delete_collection(collection_name=collection_name)
            logger.info(f"Deleted collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection {collection_name}: {e}")
            return False

    async def index_knowledge_documents(
        self,
        tradition: str,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[dict],
    ) -> List[str]:
        """
        Indexes a batch of document chunks into a tradition's knowledge collection.

        Returns:
            A list of the point IDs for the indexed documents.
        """
        collection_name = self.get_knowledge_collection_name(tradition)
        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={**metadata, "text": text},
            )
            for text, embedding, metadata in zip(texts, embeddings, metadatas)
        ]

        if not points:
            return []

        operation_info = self.client.upsert(
            collection_name=collection_name, wait=True, points=points
        )
        logger.info(
            f"Upserted {len(points)} points to {collection_name}. Status: {operation_info.status}"
        )

        return [point.id for point in points]

    async def search_knowledge_base(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: float = 0.7,
    ) -> List[SearchResult]:
        """Search the knowledge base with a query vector."""
        try:
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
            )

            search_results = []
            for result in results:
                search_results.append(
                    SearchResult(
                        id=result.id,
                        score=result.score,
                        payload=result.payload,
                        vector=result.vector,
                    )
                )

            logger.debug(
                f"Found {len(search_results)} results in collection {collection_name}"
            )
            return search_results
        except Exception as e:
            logger.error(f"Failed to search collection {collection_name}: {e}")
            return []

    async def get_collection_info(
        self, collection_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get information about a collection."""
        try:
            info = self.client.get_collection(collection_name=collection_name)
            return {
                "name": info.name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status,
            }
        except Exception as e:
            logger.error(f"Failed to get collection info for {collection_name}: {e}")
            return None

    def get_personal_collection_name(self, tradition: str, user_id: str) -> str:
        """Get collection name for user's personal data (journals)."""
        return f"{tradition}_{user_id}_personal"

    async def get_or_create_personal_collection(
        self, tradition: str, user_id: str
    ) -> str:
        """Get or create personal collection for user's data."""
        collection_name = self.get_personal_collection_name(tradition, user_id)
        await self._create_collection(collection_name)
        return collection_name

    async def index_personal_document(
        self,
        tradition: str,
        user_id: str,
        text: str,
        embedding: List[float],
        metadata: Dict[str, Any],
    ) -> str:
        """Index a personal document (journal entry) in user's collection."""
        collection_name = await self.get_or_create_personal_collection(
            tradition, user_id
        )

        # Ensure source_type and user_id are set for personal documents
        metadata = {**metadata, "source_type": "journal", "user_id": user_id}

        return await self.index_document(collection_name, text, embedding, metadata)

    async def index_document(
        self,
        collection_name: str,
        text: str,
        embedding: List[float],
        metadata: Dict[str, Any],
    ) -> str:
        """Index a document in the specified collection."""
        try:
            # Generate unique ID for the document
            doc_id = str(uuid.uuid4())

            # Add text to metadata
            metadata["text"] = text

            # Create point for insertion
            point = PointStruct(id=doc_id, vector=embedding, payload=metadata)

            # Insert into collection
            self.client.upsert(collection_name=collection_name, points=[point])

            logger.info(
                f"Successfully indexed document {doc_id} in collection {collection_name}"
            )
            return doc_id

        except Exception as e:
            logger.error(
                f"Failed to index document in collection {collection_name}: {e}"
            )
            raise


# Global client instance
_celery_qdrant_client: Optional[CeleryQdrantClient] = None


def get_celery_qdrant_client() -> CeleryQdrantClient:
    """Create or get the global Celery Qdrant client instance."""
    global _celery_qdrant_client
    if _celery_qdrant_client is None:
        _celery_qdrant_client = CeleryQdrantClient()  # Will use Config.QDRANT_URL and Config.QDRANT_API_KEY
    return _celery_qdrant_client
