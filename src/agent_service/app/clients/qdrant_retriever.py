"""
Qdrant retriever for LangChain integration.

This module provides a QdrantRetriever class that integrates with
LangChain's retriever interface for document retrieval from Qdrant.
"""

import logging
from typing import Any, Dict, List, Optional
import asyncio

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import Field

from agent_service.app.services.embedding_service import EmbeddingService
from agent_service.app.services.qdrant_service import QdrantService

logger = logging.getLogger(__name__)


class QdrantRetriever(BaseRetriever):
    """
    Qdrant retriever for LangChain integration.

    This retriever provides document retrieval capabilities from Qdrant
    collections, supporting different search types and user contexts.
    """

    # Define Pydantic fields
    qdrant_service: QdrantService = Field(...)
    embedding_service: EmbeddingService = Field(...)
    collection_name: str = Field(...)
    user_id: Optional[str] = Field(default=None)
    tradition_id: Optional[str] = Field(default=None)
    search_type: str = Field(default="hybrid")
    k: int = Field(default=5)
    score_threshold: Optional[float] = Field(default=None)

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True

    def __init__(
        self,
        qdrant_service: QdrantService,
        embedding_service: EmbeddingService,
        collection_name: str,
        user_id: Optional[str] = None,
        tradition_id: Optional[str] = None,
        search_type: str = "hybrid",
        k: int = 5,
        score_threshold: Optional[float] = None,
        **kwargs,
    ):
        """
        Initialize the Qdrant retriever.

        Args:
            qdrant_service: Qdrant service instance
            embedding_service: Embedding service instance
            collection_name: Name of the Qdrant collection
            user_id: Optional user ID for filtering
            tradition_id: Optional tradition ID for filtering
            search_type: Type of search ('vector', 'keyword', 'hybrid')
            k: Number of documents to retrieve
            score_threshold: Optional minimum score threshold
        """
        super().__init__(
            qdrant_service=qdrant_service,
            embedding_service=embedding_service,
            collection_name=collection_name,
            user_id=user_id,
            tradition_id=tradition_id,
            search_type=search_type,
            k=k,
            score_threshold=score_threshold,
            **kwargs,
        )

        # Validate search type
        if search_type not in ["vector", "keyword", "hybrid"]:
            raise ValueError(f"Invalid search_type: {search_type}")

        logger.info(
            f"Initialized QdrantRetriever for collection '{collection_name}' "
            f"with search_type='{search_type}', k={k}"
        )

    async def _aget_relevant_documents(self, query: str) -> List[Document]:
        """
        Async version of get_relevant_documents.

        Args:
            query: Search query

        Returns:
            List of relevant documents
        """
        try:
            # Determine the tradition to use - use tradition_id or default
            tradition = self.tradition_id or "canon-default"

            logger.info(
                f"QdrantRetriever: Using tradition '{tradition}' for query '{query[:50]}...'"
            )

            # Perform search based on type
            if self.search_type == "vector":
                documents = await self._async_vector_search(query, tradition)
            elif self.search_type == "keyword":
                documents = await self._async_keyword_search(query, tradition)
            else:  # hybrid
                documents = await self._async_hybrid_search(query, tradition)

            logger.info(
                f"Retrieved {len(documents)} documents for query: {query[:100]}..."
            )
            return documents

        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []

    def get_relevant_documents(self, query: str) -> List[Document]:
        """
        Retrieve relevant documents for a query (sync version).

        Args:
            query: Search query

        Returns:
            List of relevant documents
        """
        # Run the async method in the current event loop or create one
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, use asyncio.create_task
                # This is a workaround for sync calls from async contexts
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run, self._aget_relevant_documents(query)
                    )
                    return future.result()
            else:
                return loop.run_until_complete(self._aget_relevant_documents(query))
        except RuntimeError:
            # No event loop running, create a new one
            return asyncio.run(self._aget_relevant_documents(query))

    async def _async_vector_search(self, query: str, tradition: str) -> List[Document]:
        """
        Perform async vector search.

        Args:
            query: Search query
            tradition: Tradition to search in

        Returns:
            List of search results
        """
        # Use knowledge base search for now
        return await self.qdrant_service.search_knowledge_base(
            query=query,
            tradition=tradition,
            limit=self.k,
            score_threshold=self.score_threshold or 0.0,
        )

    async def _async_keyword_search(self, query: str, tradition: str) -> List[Document]:
        """
        Perform async keyword search.

        Args:
            query: Search query
            tradition: Tradition to search in

        Returns:
            List of search results
        """
        # For now, use the same as vector search
        return await self._async_vector_search(query, tradition)

    async def _async_hybrid_search(self, query: str, tradition: str) -> List[Document]:
        """
        Perform async hybrid search.

        Args:
            query: Search query
            tradition: Tradition to search in

        Returns:
            List of search results
        """
        if self.user_id:
            # Use the proper hybrid search that includes both knowledge and personal data
            return await self.qdrant_service.hybrid_search(
                query=query,
                user_id=self.user_id,
                tradition=tradition,
                include_personal=True,
                include_knowledge=True,
                limit=self.k,
                score_threshold=self.score_threshold or 0.0,
            )
        else:
            # Just use knowledge base search if no user_id
            return await self._async_vector_search(query, tradition)

    def _build_search_filters(self) -> Dict[str, Any]:
        """
        Build search filters based on user and tradition context.

        Returns:
            Dictionary of search filters
        """
        filters = {}

        if self.user_id:
            filters["user_id"] = self.user_id

        if self.tradition_id:
            filters["tradition_id"] = self.tradition_id

        return filters

    def _vector_search(
        self,
        query_embedding: List[float],
        filters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Perform vector search.

        Args:
            query_embedding: Query embedding vector
            filters: Search filters

        Returns:
            List of search results
        """
        return self.qdrant_service.search_knowledge_base(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            k=self.k,
            score_threshold=self.score_threshold,
            filters=filters,
        )

    def _keyword_search(
        self,
        query: str,
        filters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Perform keyword search.

        Args:
            query: Search query
            filters: Search filters

        Returns:
            List of search results
        """
        # For now, we'll use vector search with keyword embedding
        # In the future, this could be enhanced with actual keyword search
        query_embedding = self.embedding_service.get_embedding(query)
        return self._vector_search(query_embedding, filters)

    def _hybrid_search(
        self,
        query: str,
        query_embedding: List[float],
        filters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining vector and keyword approaches.

        Args:
            query: Search query
            query_embedding: Query embedding vector
            filters: Search filters

        Returns:
            List of search results
        """
        # Get vector search results
        vector_results = self._vector_search(query_embedding, filters)

        # Get keyword search results
        keyword_results = self._keyword_search(query, filters)

        # Combine and deduplicate results
        combined_results = self._combine_search_results(vector_results, keyword_results)

        return combined_results[: self.k]

    def _combine_search_results(
        self,
        vector_results: List[Dict[str, Any]],
        keyword_results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Combine and deduplicate search results.

        Args:
            vector_results: Vector search results
            keyword_results: Keyword search results

        Returns:
            Combined and deduplicated results
        """
        # Create a map of document IDs to results
        result_map = {}

        # Add vector results with their scores
        for result in vector_results:
            doc_id = result.get("id")
            if doc_id:
                result_map[doc_id] = {
                    **result,
                    "vector_score": result.get("score", 0),
                    "keyword_score": 0,
                }

        # Add keyword results, combining scores
        for result in keyword_results:
            doc_id = result.get("id")
            if doc_id:
                if doc_id in result_map:
                    # Combine scores
                    result_map[doc_id]["keyword_score"] = result.get("score", 0)
                    # Calculate hybrid score (simple average for now)
                    vector_score = result_map[doc_id]["vector_score"]
                    keyword_score = result_map[doc_id]["keyword_score"]
                    result_map[doc_id]["score"] = (vector_score + keyword_score) / 2
                else:
                    result_map[doc_id] = {
                        **result,
                        "vector_score": 0,
                        "keyword_score": result.get("score", 0),
                    }

        # Convert back to list and sort by score
        combined_results = list(result_map.values())
        combined_results.sort(key=lambda x: x.get("score", 0), reverse=True)

        return combined_results

    def _convert_to_documents(self, results: List[Dict[str, Any]]) -> List[Document]:
        """
        Convert search results to LangChain documents.

        Args:
            results: Search results from Qdrant

        Returns:
            List of LangChain documents
        """
        documents = []

        for result in results:
            # Extract content and metadata
            content = result.get("payload", {}).get("content", "")
            metadata = result.get("payload", {}).copy()

            # Add search-specific metadata
            metadata["score"] = result.get("score")
            metadata["id"] = result.get("id")

            # Create document
            document = Document(
                page_content=content,
                metadata=metadata,
            )

            documents.append(document)

        return documents

    def set_user_id(self, user_id: str) -> None:
        """
        Set the user ID for filtering.

        Args:
            user_id: User identifier
        """
        self.user_id = user_id
        logger.debug(f"Set user_id to '{user_id}'")

    def set_tradition_id(self, tradition_id: str) -> None:
        """
        Set the tradition ID for filtering.

        Args:
            tradition_id: Tradition identifier
        """
        self.tradition_id = tradition_id
        logger.debug(f"Set tradition_id to '{tradition_id}'")

    def set_search_type(self, search_type: str) -> None:
        """
        Set the search type.

        Args:
            search_type: Type of search ('vector', 'keyword', 'hybrid')
        """
        if search_type not in ["vector", "keyword", "hybrid"]:
            raise ValueError(f"Invalid search_type: {search_type}")

        self.search_type = search_type
        logger.debug(f"Set search_type to '{search_type}'")

    def set_k(self, k: int) -> None:
        """
        Set the number of documents to retrieve.

        Args:
            k: Number of documents
        """
        if k <= 0:
            raise ValueError("k must be positive")

        self.k = k
        logger.debug(f"Set k to {k}")

    def set_score_threshold(self, score_threshold: Optional[float]) -> None:
        """
        Set the score threshold for filtering results.

        Args:
            score_threshold: Minimum score threshold or None
        """
        self.score_threshold = score_threshold
        logger.debug(f"Set score_threshold to {score_threshold}")


class QdrantRetrieverFactory:
    """
    Factory for creating QdrantRetriever instances with different configurations.
    """

    @staticmethod
    def create_default_retriever(
        collection_name: str,
        user_id: Optional[str] = None,
        tradition_id: Optional[str] = None,
    ) -> QdrantRetriever:
        """
        Create a default retriever with standard settings.

        Args:
            collection_name: Name of the Qdrant collection
            user_id: Optional user ID for filtering
            tradition_id: Optional tradition ID for filtering

        Returns:
            Configured QdrantRetriever
        """
        qdrant_service = QdrantService()
        embedding_service = EmbeddingService()

        return QdrantRetriever(
            qdrant_service=qdrant_service,
            embedding_service=embedding_service,
            collection_name=collection_name,
            user_id=user_id,
            tradition_id=tradition_id,
            search_type="hybrid",
            k=5,
        )

    @staticmethod
    def create_vector_retriever(
        collection_name: str,
        user_id: Optional[str] = None,
        tradition_id: Optional[str] = None,
        k: int = 5,
    ) -> QdrantRetriever:
        """
        Create a vector-only retriever.

        Args:
            collection_name: Name of the Qdrant collection
            user_id: Optional user ID for filtering
            tradition_id: Optional tradition ID for filtering
            k: Number of documents to retrieve

        Returns:
            Configured QdrantRetriever for vector search
        """
        qdrant_service = QdrantService()
        embedding_service = EmbeddingService()

        return QdrantRetriever(
            qdrant_service=qdrant_service,
            embedding_service=embedding_service,
            collection_name=collection_name,
            user_id=user_id,
            tradition_id=tradition_id,
            search_type="vector",
            k=k,
        )

    @staticmethod
    def create_high_precision_retriever(
        collection_name: str,
        user_id: Optional[str] = None,
        tradition_id: Optional[str] = None,
    ) -> QdrantRetriever:
        """
        Create a high-precision retriever with strict filtering.

        Args:
            collection_name: Name of the Qdrant collection
            user_id: Optional user ID for filtering
            tradition_id: Optional tradition ID for filtering

        Returns:
            Configured QdrantRetriever for high precision
        """
        qdrant_service = QdrantService()
        embedding_service = EmbeddingService()

        return QdrantRetriever(
            qdrant_service=qdrant_service,
            embedding_service=embedding_service,
            collection_name=collection_name,
            user_id=user_id,
            tradition_id=tradition_id,
            search_type="hybrid",
            k=3,
            score_threshold=0.7,
        )
