"""
Qdrant service for high-level Qdrant operations.

This service provides a clean interface for Qdrant operations,
abstracting away the underlying Qdrant client implementation.
"""

import logging
from typing import Any, Dict, List, Optional

from langchain_core.documents import Document

from agent_service.app.clients.qdrant_client import QdrantClient

logger = logging.getLogger(__name__)


class QdrantService:
    """
    High-level Qdrant operations service.

    Provides a clean interface for Qdrant operations including
    search, indexing, and collection management.
    """

    def __init__(self, qdrant_client: Optional[QdrantClient] = None):
        """
        Initialize the Qdrant service.

        Args:
            qdrant_client: Optional Qdrant client instance
        """
        self.qdrant_client = qdrant_client or QdrantClient()
        self.logger = logging.getLogger(f"{__name__}.QdrantService")

    async def search_knowledge_base(
        self, query: str, tradition: str, limit: int = 10, score_threshold: float = 0.7
    ) -> List[Document]:
        """
        Search knowledge base using Qdrant.

        Args:
            query: Search query
            tradition: Tradition to search in
            limit: Maximum number of results
            score_threshold: Minimum similarity score

        Returns:
            List of relevant documents
        """
        try:
            self.logger.debug(f"Searching knowledge base for query: {query[:100]}...")

            # Get query embedding first
            from agent_service.app.services.embedding_service import EmbeddingService

            embedding_service = EmbeddingService()

            # Get embedding for the query
            query_embedding = await embedding_service.get_embedding(query)
            if not query_embedding:
                self.logger.warning("Failed to get query embedding")
                return []

            results = self.qdrant_client.search_knowledge_base(
                tradition=tradition,
                query_embedding=query_embedding,
                limit=limit,
            )

            # Filter results by score threshold if specified
            if score_threshold > 0:
                results = [r for r in results if r.score >= score_threshold]

            # Convert to LangChain documents
            documents = []
            for result in results:
                doc = Document(
                    page_content=result.text,
                    metadata={
                        "source": result.metadata.get("source_id", "unknown"),
                        "score": result.score,
                        "tradition": tradition,
                        "document_type": "knowledge",
                    },
                )
                documents.append(doc)

            self.logger.debug(f"Found {len(documents)} documents in knowledge base")
            return documents

        except Exception as e:
            self.logger.error(f"Failed to search knowledge base: {e}")
            return []

    async def search_personal_entries(
        self,
        query: str,
        user_id: str,
        tradition: str,
        limit: int = 10,
        score_threshold: float = 0.7,
    ) -> List[Document]:
        """
        Search personal journal entries using Qdrant.

        Args:
            query: Search query
            user_id: User ID to search for
            tradition: Tradition to search in
            limit: Maximum number of results
            score_threshold: Minimum similarity score

        Returns:
            List of relevant documents
        """
        try:
            self.logger.debug(f"Searching personal entries for user {user_id}")

            results = await self.qdrant_client.search_personal_entries(
                query=query,
                user_id=user_id,
                tradition=tradition,
                limit=limit,
                score_threshold=score_threshold,
            )

            # Convert to LangChain documents
            documents = []
            for result in results:
                doc = Document(
                    page_content=result.text,
                    metadata={
                        "source": result.metadata.get("source_id", "unknown"),
                        "score": result.score,
                        "tradition": tradition,
                        "user_id": user_id,
                        "document_type": "personal",
                    },
                )
                documents.append(doc)

            self.logger.debug(f"Found {len(documents)} personal documents")
            return documents

        except Exception as e:
            self.logger.error(f"Failed to search personal entries: {e}")
            return []

    async def hybrid_search(
        self,
        query: str,
        user_id: str,
        tradition: str,
        include_personal: bool = True,
        include_knowledge: bool = True,
        entry_types: Optional[List[str]] = None,
        limit: int = 10,
        score_threshold: float = 0.7,
    ) -> List[Document]:
        """
        Combined search across knowledge and personal data.

        Args:
            query: Search query
            user_id: User ID to search for
            tradition: Tradition to search in
            include_personal: Whether to include personal entries
            include_knowledge: Whether to include knowledge base
            entry_types: Types of entries to include
            limit: Maximum number of results
            score_threshold: Minimum similarity score

        Returns:
            List of relevant documents
        """
        try:
            self.logger.debug(f"Performing hybrid search for user {user_id}")

            # Get query embedding first
            from agent_service.app.services.embedding_service import EmbeddingService

            embedding_service = EmbeddingService()

            # Get embedding for the query
            query_embedding = await embedding_service.get_embedding(query)
            if not query_embedding:
                self.logger.warning("Failed to get query embedding")
                return []

            results = await self.qdrant_client.hybrid_search(
                query=query,
                user_id=user_id,
                tradition=tradition,
                query_embedding=query_embedding,
                include_personal=include_personal,
                include_knowledge=include_knowledge,
                entry_types=entry_types,
                limit=limit,
            )

            # Filter results by score threshold if specified
            if score_threshold > 0:
                results = [r for r in results if r.score >= score_threshold]

            # Convert to LangChain documents
            documents = []
            for result in results:
                doc = Document(
                    page_content=result.text,
                    metadata={
                        "source": result.metadata.get("source_id", "unknown"),
                        "score": result.score,
                        "tradition": tradition,
                        "user_id": user_id,
                        "document_type": result.metadata.get(
                            "document_type", "unknown"
                        ),
                    },
                )
                documents.append(doc)

            self.logger.debug(f"Found {len(documents)} documents in hybrid search")
            return documents

        except Exception as e:
            self.logger.error(f"Failed to perform hybrid search: {e}")
            return []

    async def index_knowledge_documents(
        self,
        tradition: str,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
    ) -> List[str]:
        """
        Index knowledge documents to Qdrant.

        Args:
            tradition: Tradition to index for
            texts: List of text contents
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries

        Returns:
            List of point IDs
        """
        try:
            self.logger.debug(
                f"Indexing {len(texts)} knowledge documents for tradition {tradition}"
            )

            point_ids = await self.qdrant_client.index_knowledge_documents(
                tradition=tradition,
                texts=texts,
                embeddings=embeddings,
                metadatas=metadatas,
            )

            self.logger.debug(f"Successfully indexed {len(point_ids)} documents")
            return point_ids

        except Exception as e:
            self.logger.error(f"Failed to index knowledge documents: {e}")
            return []

    async def index_personal_documents(
        self,
        user_id: str,
        tradition: str,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
    ) -> List[str]:
        """
        Index personal documents to Qdrant.

        Args:
            user_id: User ID to index for
            tradition: Tradition to index for
            texts: List of text contents
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries

        Returns:
            List of point IDs
        """
        try:
            self.logger.debug(
                f"Indexing {len(texts)} personal documents for user {user_id}"
            )

            point_ids = await self.qdrant_client.index_personal_documents(
                user_id=user_id,
                tradition=tradition,
                texts=texts,
                embeddings=embeddings,
                metadatas=metadatas,
            )

            self.logger.debug(
                f"Successfully indexed {len(point_ids)} personal documents"
            )
            return point_ids

        except Exception as e:
            self.logger.error(f"Failed to index personal documents: {e}")
            return []

    async def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a Qdrant collection.

        Args:
            collection_name: Name of collection to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.debug(f"Deleting collection: {collection_name}")

            await self.qdrant_client.delete_collection(collection_name)

            self.logger.debug(f"Successfully deleted collection: {collection_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete collection {collection_name}: {e}")
            return False

    async def health_check(self) -> bool:
        """
        Check if Qdrant is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            health = await self.qdrant_client.health_check()
            if health:
                self.logger.debug("Qdrant health check passed")
            else:
                self.logger.warning("Qdrant health check failed")
            return health
        except Exception as e:
            self.logger.error(f"Qdrant health check error: {e}")
            return False
