import os
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from uuid import uuid4

from qdrant_client import QdrantClient as QdrantClientBase
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchRequest
)
from qdrant_client.http.exceptions import ResponseHandlingException

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Result from a vector search operation."""
    text: str
    score: float
    metadata: Dict[str, Any]
    
    def is_personal_content(self) -> bool:
        """Check if this result is from personal journal content."""
        return self.metadata.get("source_type") == "journal"


class QdrantClient:
    """Production-ready Qdrant client for vector operations."""
    
    def __init__(self, qdrant_url: Optional[str] = None):
        self.client = None
        self.qdrant_url = qdrant_url or os.getenv("QDRANT_URL", "http://localhost:6333")
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Qdrant client with environment configuration."""
        try:
            self.client = QdrantClientBase(url=self.qdrant_url)
            logger.info(f"Qdrant client initialized with URL: {self.qdrant_url}")
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant client: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check if Qdrant is healthy and reachable."""
        try:
            # Get collections info as a health check
            collections = self.client.get_collections()
            return collections is not None
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False
    
    def get_client(self) -> QdrantClientBase:
        """Get the underlying Qdrant client."""
        if self.client is None:
            self._initialize_client()
        return self.client

    def _get_knowledge_collection_name(self, tradition: str) -> str:
        """Get collection name for shared knowledge base (PDFs)."""
        return f"{tradition}_knowledge"
    
    def _get_personal_collection_name(self, tradition: str, user_id: str) -> str:
        """Get collection name for user's personal data (journals)."""
        return f"{tradition}_{user_id}_personal"

    async def create_knowledge_collection(self, tradition: str) -> bool:
        """Create a shared collection for tradition's knowledge base (PDFs)."""
        collection_name = self._get_knowledge_collection_name(tradition)
        return await self._create_collection(collection_name)
    
    async def create_personal_collection(self, tradition: str, user_id: str) -> bool:
        """Create a personal collection for user's journal entries."""
        collection_name = self._get_personal_collection_name(tradition, user_id)
        return await self._create_collection(collection_name)

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
                vectors_config=VectorParams(
                    size=384,  # nomic-embed-text dimension
                    distance=Distance.COSINE
                )
            )
            
            logger.info(f"Created collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection {collection_name}: {e}")
            return False

    async def get_or_create_knowledge_collection(self, tradition: str) -> str:
        """
        Ensures a knowledge collection exists for a tradition and returns its name.
        """
        collection_name = self._get_knowledge_collection_name(tradition)
        await self._create_collection_if_not_exists(collection_name)
        return collection_name

    async def get_or_create_personal_collection(self, tradition: str, user_id: str) -> str:
        """Get or create personal collection for user's data."""
        await self.create_personal_collection(tradition, user_id)
        return self._get_personal_collection_name(tradition, user_id)

    async def index_knowledge_document(
        self,
        tradition: str,
        text: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> str:
        """Index a knowledge base document (PDF) in shared collection."""
        collection_name = await self.get_or_create_knowledge_collection(tradition)
        
        # Ensure source_type is set for knowledge documents
        metadata = {**metadata, "source_type": "pdf"}
        
        return await self.index_document(collection_name, text, embedding, metadata)
    
    async def index_personal_document(
        self,
        tradition: str,
        user_id: str,
        text: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> str:
        """Index a personal document (journal entry) in user's collection."""
        collection_name = await self.get_or_create_personal_collection(tradition, user_id)
        
        # Ensure source_type and user_id are set for personal documents
        metadata = {**metadata, "source_type": "journal", "user_id": user_id}
        
        return await self.index_document(collection_name, text, embedding, metadata)

    async def index_document(
        self,
        collection_name: str,
        text: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> str:
        """Index a document with its embedding and metadata."""
        point_id = str(uuid4())
        
        try:
            # Create point with embedding and metadata
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "text": text,
                    **metadata
                }
            )
            
            # Upload point to collection
            self.client.upsert(
                collection_name=collection_name,
                points=[point]
            )
            
            logger.debug(f"Indexed document {point_id} in collection {collection_name}")
            return point_id
            
        except Exception as e:
            logger.error(f"Failed to index document in {collection_name}: {e}")
            raise

    async def search_documents(
        self,
        collection_name: str,
        query_embedding: List[float],
        limit: int = 10,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar documents in a collection."""
        try:
            # Build filter if metadata filtering is requested
            search_filter = None
            if metadata_filter:
                conditions = []
                for key, value in metadata_filter.items():
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )
                search_filter = Filter(must=conditions)
            
            # Perform search
            search_results = self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=limit,
                with_payload=True
            )
            
            # Convert to SearchResult objects
            results = []
            for hit in search_results:
                payload = hit.payload or {}
                text = payload.pop("text", "")
                
                result = SearchResult(
                    text=text,
                    score=hit.score,
                    metadata=payload
                )
                results.append(result)
            
            logger.debug(f"Found {len(results)} results in collection {collection_name}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search in collection {collection_name}: {e}")
            return []

    async def hybrid_search(
        self,
        query: str,
        user_id: str,
        tradition: str,
        query_embedding: List[float],
        include_personal: bool = True,
        include_knowledge: bool = True,
        date_range: Optional[tuple] = None,
        entry_types: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[SearchResult]:
        """
        Perform hybrid search across knowledge base and/or personal content.
        
        Args:
            query: The search query text
            user_id: User identifier
            tradition: Knowledge tradition (e.g., "canon-default")
            query_embedding: Embedding vector for the query
            include_personal: Whether to include personal journal entries
            include_knowledge: Whether to include shared knowledge base
            date_range: Optional tuple of (start_date, end_date) for filtering
            entry_types: Optional list of entry types to filter by
            limit: Maximum number of results to return
        
        Returns:
            List of SearchResult objects ranked by relevance
        """
        all_results = []
        
        # Search shared knowledge base
        if include_knowledge:
            knowledge_collection = await self.get_or_create_knowledge_collection(tradition)
            knowledge_filter = {"source_type": "pdf"}
            
            knowledge_results = await self.search_documents(
                collection_name=knowledge_collection,
                query_embedding=query_embedding,
                limit=limit,
                metadata_filter=knowledge_filter
            )
            all_results.extend(knowledge_results)
        
        # Search personal content
        if include_personal:
            personal_collection = await self.get_or_create_personal_collection(tradition, user_id)
            personal_filter = {"source_type": "journal"}
            
            if entry_types:
                personal_filter["document_type"] = entry_types[0]  # Simplified for now
            
            personal_results = await self.search_documents(
                collection_name=personal_collection,
                query_embedding=query_embedding,
                limit=limit,
                metadata_filter=personal_filter
            )
            all_results.extend(personal_results)
        
        # Apply hybrid ranking and return top results
        ranked_results = self._apply_hybrid_ranking(all_results, query)
        return ranked_results[:limit]

    async def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection and all its documents."""
        try:
            self.client.delete_collection(collection_name=collection_name)
            logger.info(f"Deleted collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection {collection_name}: {e}")
            return False

    async def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a collection."""
        try:
            collection_info = self.client.get_collection(collection_name=collection_name)
            return {
                "name": collection_info.config.params.vectors.distance,
                "vector_count": collection_info.points_count,
                "indexed_vector_count": collection_info.indexed_vectors_count,
                "payload_schema": collection_info.payload_schema
            }
        except Exception as e:
            logger.error(f"Failed to get collection info for {collection_name}: {e}")
            return None

    def _apply_hybrid_ranking(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        """
        Apply hybrid ranking combining semantic similarity, recency, and personal relevance.
        
        Ranking weights:
        - Semantic similarity: 0.7
        - Recency bonus: 0.2 (for journal entries)
        - Personal relevance: 0.1
        """
        for result in results:
            base_score = result.score
            
            # Recency bonus for journal entries
            recency_bonus = 0.0
            if result.is_personal_content():
                try:
                    timestamp = datetime.fromisoformat(result.metadata.get("timestamp", ""))
                    days_ago = (datetime.now(timezone.utc) - timestamp).days
                    # Decay bonus over time (max 0.2 bonus for today, 0.1 for week old, 0 for month old)
                    recency_bonus = max(0, 0.2 * (1 - days_ago / 30))
                except (ValueError, TypeError):
                    recency_bonus = 0.0
            
            # Personal relevance bonus
            personal_bonus = 0.1 if result.is_personal_content() else 0.0
            
            # Combine scores
            result.score = (0.7 * base_score) + recency_bonus + personal_bonus
        
        # Sort by final score
        return sorted(results, key=lambda r: r.score, reverse=True)

    def get_knowledge_collection_name(self, tradition: str) -> str:
        """Returns the standardized name for a tradition's knowledge collection."""
        return f"{tradition}_knowledge"

    async def get_or_create_knowledge_collection(self, tradition: str) -> str:
        """
        Ensures a knowledge collection exists for a tradition and returns its name.
        """
        collection_name = self.get_knowledge_collection_name(tradition)
        await self._create_collection_if_not_exists(collection_name)
        return collection_name

    async def index_knowledge_documents(
        self,
        tradition: str,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[dict]
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
                payload={**metadata, "text": text}
            )
            for text, embedding, metadata in zip(texts, embeddings, metadatas)
        ]
        
        if not points:
            return []

        operation_info = await self.client.upsert(
            collection_name=collection_name,
            wait=True,
            points=points
        )
        logger.info(f"Upserted {len(points)} points to {collection_name}. Status: {operation_info.status}")
        
        return [point.id for point in points]


# Global client instance
_qdrant_client = None


def get_qdrant_client() -> QdrantClient:
    """Get or create the global Qdrant client instance."""
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient()
    return _qdrant_client 