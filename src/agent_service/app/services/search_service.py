"""
Search service for orchestrating search operations.

This service coordinates search operations across different data sources,
combining embedding generation with Qdrant search capabilities.
"""

import logging
from typing import Any, Dict, List, Optional

from langchain_core.documents import Document

from agent_service.app.services.embedding_service import EmbeddingService
from agent_service.app.services.qdrant_service import QdrantService

logger = logging.getLogger(__name__)


class SearchService:
    """
    Orchestrates search operations across different data sources.

    Combines embedding generation with Qdrant search to provide
    comprehensive semantic search capabilities.
    """

    def __init__(
        self,
        qdrant_service: Optional[QdrantService] = None,
        embedding_service: Optional[EmbeddingService] = None,
    ):
        """
        Initialize the search service.

        Args:
            qdrant_service: Optional Qdrant service instance
            embedding_service: Optional embedding service instance
        """
        self.qdrant_service = qdrant_service or QdrantService()
        self.embedding_service = embedding_service or EmbeddingService()
        self.logger = logging.getLogger(f"{__name__}.SearchService")

    async def semantic_search(
        self,
        query: str,
        user_id: str,
        tradition: str = "canon-default",
        include_personal: bool = True,
        include_knowledge: bool = True,
        entry_types: Optional[List[str]] = None,
        limit: int = 10,
        score_threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search across all data sources.

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
            List of search results with metadata
        """
        try:
            self.logger.info(
                f"Performing semantic search for user {user_id}: {query[:100]}..."
            )

            # Get query embedding
            query_embedding = await self.embedding_service.get_embedding(query)
            if not query_embedding:
                self.logger.warning("Failed to generate query embedding")
                return []

            # Perform hybrid search
            documents = await self.qdrant_service.hybrid_search(
                query=query,
                user_id=user_id,
                tradition=tradition,
                include_personal=include_personal,
                include_knowledge=include_knowledge,
                entry_types=entry_types,
                limit=limit,
                score_threshold=score_threshold,
            )

            # Convert to result format
            results = []
            for doc in documents:
                result = {
                    "text": doc.page_content,
                    "score": doc.metadata.get("score", 0.0),
                    "source": doc.metadata.get("source", "unknown"),
                    "tradition": doc.metadata.get("tradition", tradition),
                    "document_type": doc.metadata.get("document_type", "unknown"),
                    "user_id": doc.metadata.get("user_id", user_id),
                }
                results.append(result)

            self.logger.info(f"Found {len(results)} results for semantic search")
            return results

        except Exception as e:
            self.logger.error(f"Semantic search failed: {e}")
            return []

    async def search_knowledge_base(
        self,
        query: str,
        tradition: str = "canon-default",
        limit: int = 10,
        score_threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Search only the knowledge base.

        Args:
            query: Search query
            tradition: Tradition to search in
            limit: Maximum number of results
            score_threshold: Minimum similarity score

        Returns:
            List of search results
        """
        try:
            self.logger.info(f"Searching knowledge base: {query[:100]}...")

            documents = await self.qdrant_service.search_knowledge_base(
                query=query,
                tradition=tradition,
                limit=limit,
                score_threshold=score_threshold,
            )

            # Convert to result format
            results = []
            for doc in documents:
                result = {
                    "text": doc.page_content,
                    "score": doc.metadata.get("score", 0.0),
                    "source": doc.metadata.get("source", "unknown"),
                    "tradition": doc.metadata.get("tradition", tradition),
                    "document_type": "knowledge",
                }
                results.append(result)

            self.logger.info(f"Found {len(results)} results in knowledge base")
            return results

        except Exception as e:
            self.logger.error(f"Knowledge base search failed: {e}")
            return []

    async def search_personal_entries(
        self,
        query: str,
        user_id: str,
        tradition: str = "canon-default",
        limit: int = 10,
        score_threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Search only personal journal entries.

        Args:
            query: Search query
            user_id: User ID to search for
            tradition: Tradition to search in
            limit: Maximum number of results
            score_threshold: Minimum similarity score

        Returns:
            List of search results
        """
        try:
            self.logger.info(f"Searching personal entries for user {user_id}")

            documents = await self.qdrant_service.search_personal_entries(
                query=query,
                user_id=user_id,
                tradition=tradition,
                limit=limit,
                score_threshold=score_threshold,
            )

            # Convert to result format
            results = []
            for doc in documents:
                result = {
                    "text": doc.page_content,
                    "score": doc.metadata.get("score", 0.0),
                    "source": doc.metadata.get("source", "unknown"),
                    "tradition": doc.metadata.get("tradition", tradition),
                    "document_type": "personal",
                    "user_id": user_id,
                }
                results.append(result)

            self.logger.info(f"Found {len(results)} personal entries")
            return results

        except Exception as e:
            self.logger.error(f"Personal entries search failed: {e}")
            return []

    async def search_by_embedding(
        self,
        embedding: List[float],
        user_id: str,
        tradition: str = "canon-default",
        include_personal: bool = True,
        include_knowledge: bool = True,
        limit: int = 10,
        score_threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Search using a pre-computed embedding vector.

        Args:
            embedding: Pre-computed embedding vector
            user_id: User ID to search for
            tradition: Tradition to search in
            include_personal: Whether to include personal entries
            include_knowledge: Whether to include knowledge base
            limit: Maximum number of results
            score_threshold: Minimum similarity score

        Returns:
            List of search results
        """
        try:
            self.logger.info(f"Searching by embedding for user {user_id}")

            # Validate embedding
            if not self.embedding_service.validate_embedding(embedding):
                self.logger.error("Invalid embedding vector provided")
                return []

            # Use Qdrant service to search by embedding
            # Note: This would require extending QdrantService to support embedding-based search
            # For now, we'll return empty results
            self.logger.warning("Embedding-based search not yet implemented")
            return []

        except Exception as e:
            self.logger.error(f"Embedding-based search failed: {e}")
            return []

    async def get_search_suggestions(
        self,
        partial_query: str,
        user_id: str,
        tradition: str = "canon-default",
        limit: int = 5,
    ) -> List[str]:
        """
        Get search suggestions based on partial query.

        Args:
            partial_query: Partial search query
            user_id: User ID to get suggestions for
            tradition: Tradition to search in
            limit: Maximum number of suggestions

        Returns:
            List of search suggestions
        """
        try:
            self.logger.debug(f"Getting search suggestions for: {partial_query}")

            # For now, return simple suggestions based on partial query
            # This could be enhanced with actual search history or autocomplete
            suggestions = [
                f"{partial_query} in {tradition}",
                f"{partial_query} personal entries",
                f"{partial_query} knowledge base",
            ]

            return suggestions[:limit]

        except Exception as e:
            self.logger.error(f"Failed to get search suggestions: {e}")
            return []

    async def health_check(self) -> Dict[str, bool]:
        """
        Check the health of search services.

        Returns:
            Dictionary with health status of each service
        """
        try:
            health_status = {
                "qdrant": await self.qdrant_service.health_check(),
                "embedding": await self.embedding_service.health_check(),
            }

            self.logger.info(f"Search service health check: {health_status}")
            return health_status

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "qdrant": False,
                "embedding": False,
            }

    def create_retriever(
        self,
        user_id: Optional[str] = None,
        tradition_id: Optional[str] = None,
        search_type: str = "hybrid",
        collection_name: str = "mindmirror",
    ):
        """
        Create a QdrantRetriever instance for LangChain integration.

        Args:
            user_id: Optional user ID for filtering
            tradition_id: Optional tradition ID for filtering
            search_type: Type of search ('vector', 'keyword', 'hybrid')
            collection_name: Name of the Qdrant collection

        Returns:
            Configured QdrantRetriever instance
        """
        from agent_service.app.clients.qdrant_retriever import QdrantRetriever

        return QdrantRetriever(
            qdrant_service=self.qdrant_service,
            embedding_service=self.embedding_service,
            collection_name=collection_name,
            user_id=user_id,
            tradition_id=tradition_id,
            search_type=search_type,
            k=5,
        )
