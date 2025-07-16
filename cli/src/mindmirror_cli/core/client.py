"""Qdrant client for MindMirror CLI."""

import logging
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient as QdrantClientBase
from qdrant_client.http.exceptions import ResponseHandlingException
from qdrant_client.models import (Distance, FieldCondition, Filter, MatchValue,
                                  PointStruct, Range, SearchRequest,
                                  VectorParams, PayloadSchemaType)

from .utils import get_qdrant_url, get_qdrant_api_key

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

    def __init__(self, url: str = None, api_key: str = None):
        """Initialize Qdrant client."""
        if url:
            self.url = url
        else:
            # Use environment-aware URL
            self.url = get_qdrant_url()

        if api_key:
            self.api_key = api_key
        else:
            # Use environment-aware API key
            self.api_key = get_qdrant_api_key()
        
        logger.info(f"Qdrant client initialized with URL: {self.url}")
        
        # Initialize client with API key if provided
        if self.api_key:
            self.client = QdrantClientBase(url=self.url, api_key=self.api_key)
            logger.info("Qdrant client initialized with API key authentication")
        else:
            self.client = QdrantClientBase(url=self.url)
            logger.info("Qdrant client initialized without authentication (local mode)")

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
        return self.client

    def get_knowledge_collection_name(self, tradition: str) -> str:
        """Get collection name for shared knowledge base (PDFs)."""
        return f"{tradition}_knowledge"

    def get_personal_collection_name(self, tradition: str, user_id: str) -> str:
        """Get collection name for user's personal data (journals)."""
        return f"{tradition}_{user_id}_personal"

    async def create_knowledge_collection(self, tradition: str) -> bool:
        """Create a shared collection for tradition's knowledge base (PDFs)."""
        collection_name = self.get_knowledge_collection_name(tradition)
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

            # Get vector size from environment or default to 768
            vector_size = int(os.getenv("EMBEDDING_VECTOR_SIZE", "768"))
            logger.info(f"Creating collection '{collection_name}' with vector size: {vector_size}")

            # Create new collection with vector configuration
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size, distance=Distance.COSINE
                ),
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
        collection_name = self.get_knowledge_collection_name(tradition)
        await self._create_collection(collection_name)
        return collection_name

    async def index_knowledge_documents(
        self,
        tradition: str,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[dict],
    ) -> List[str]:
        """Index multiple knowledge base documents in batch."""
        collection_name = await self.get_or_create_knowledge_collection(tradition)

        point_ids = []
        for text, embedding, metadata in zip(texts, embeddings, metadatas):
            try:
                # Ensure source_type is set for knowledge documents
                metadata = {**metadata, "source_type": "pdf"}
                
                point_id = await self.index_document(collection_name, text, embedding, metadata)
                point_ids.append(point_id)
            except Exception as e:
                logger.error(f"Failed to index document: {e}")
                continue

        return point_ids

    async def index_document(
        self,
        collection_name: str,
        text: str,
        embedding: List[float],
        metadata: Dict[str, Any],
    ) -> str:
        """Index a document with its embedding and metadata."""
        point_id = str(uuid.uuid4())

        try:
            # Debug: Log embedding dimensions
            logger.info(f"Indexing document with {len(embedding)} dimensions to collection '{collection_name}'")
            
            # Create point with embedding and metadata
            point = PointStruct(
                id=point_id, vector=embedding, payload={"text": text, **metadata}
            )

            # Upload point to collection
            self.client.upsert(collection_name=collection_name, points=[point])

            logger.debug(f"Indexed document {point_id} in collection {collection_name}")
            return point_id

        except Exception as e:
            logger.error(f"Failed to index document in {collection_name}: {e}")
            raise

    async def search_knowledge_base(
        self,
        tradition: str,
        query_embedding: List[float],
        limit: int = 10,
    ) -> List[SearchResult]:
        """Search knowledge base for a tradition."""
        collection_name = self.get_knowledge_collection_name(tradition)
        return await self.search_documents(collection_name, query_embedding, limit)

    async def search_documents(
        self,
        collection_name: str,
        query_embedding: List[float],
        limit: int = 10,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search for similar documents in a collection."""
        try:
            # Build filter if metadata filtering is requested
            search_filter = None
            if metadata_filter:
                conditions = []
                for key, value in metadata_filter.items():
                    conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
                search_filter = Filter(must=conditions)

            # Perform search
            search_results = self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=limit,
                with_payload=True,
            )

            # Convert to SearchResult objects
            results = []
            for result in search_results:
                search_result = SearchResult(
                    text=result.payload.get("text", ""),
                    score=result.score,
                    metadata={k: v for k, v in result.payload.items() if k != "text"}
                )
                results.append(search_result)

            return results

        except Exception as e:
            logger.error(f"Search failed in collection {collection_name}: {e}")
            return []

    async def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection."""
        try:
            self.client.delete_collection(collection_name=collection_name)
            logger.info(f"Deleted collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection {collection_name}: {e}")
            return False

    async def list_collections(self) -> List[str]:
        """List all collections."""
        try:
            collections = self.client.get_collections()
            return [col.name for col in collections.collections]
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return []

    async def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a collection."""
        try:
            info = self.client.get_collection(collection_name=collection_name)
            
            # Debug: Log vector configuration
            if hasattr(info, 'config') and hasattr(info.config, 'params') and hasattr(info.config.params, 'vectors'):
                vector_size = info.config.params.vectors.size
                logger.info(f"Collection '{collection_name}' has vector size: {vector_size}")
            
            return {
                "name": collection_name,
                "vectors_count": info.vectors_count if hasattr(info, "vectors_count") else 0,
                "points_count": info.points_count if hasattr(info, "points_count") else 0,
            }
        except Exception as e:
            logger.error(f"Failed to get collection info for {collection_name}: {e}")
            return None

    async def create_field_index(
        self, 
        collection_name: str, 
        field_name: str, 
        field_type: str = "keyword"
    ) -> bool:
        """Create a field index for filtering in a collection."""
        try:
            # Map field_type to PayloadSchemaType
            schema_type_map = {
                "keyword": PayloadSchemaType.KEYWORD,
                "integer": PayloadSchemaType.INTEGER,
                "float": PayloadSchemaType.FLOAT,
                "geo": PayloadSchemaType.GEO,
                "text": PayloadSchemaType.TEXT,
            }
            
            schema_type = schema_type_map.get(field_type, PayloadSchemaType.KEYWORD)
            
            # Create payload index for filtering
            self.client.create_payload_index(
                collection_name=collection_name,
                field_name=field_name,
                field_schema=schema_type
            )
            logger.info(f"Created {field_type} index on field '{field_name}' in collection '{collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to create index on field '{field_name}' in collection '{collection_name}': {e}")
            return False 