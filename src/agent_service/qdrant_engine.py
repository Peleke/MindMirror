"""
Qdrant-based RAG engine for the coaching assistant.

This module provides a modern RAG engine that uses Qdrant vector store
instead of the legacy FAISS system.
"""

import asyncio
import logging
from typing import List, Optional

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables.base import Runnable
from pydantic import Field

from agent_service.chain import create_rag_chain
from agent_service.embedding import get_embedding
from agent_service.vector_stores.qdrant_client import QdrantClient

logger = logging.getLogger(__name__)


class QdrantRetriever(BaseRetriever):
    """
    Custom retriever that uses Qdrant for vector similarity search.
    """

    # Declare Pydantic fields
    qdrant_client: QdrantClient = Field(...)
    tradition: str = Field(...)
    user_id: str = Field(default="demo")

    def __init__(
        self, qdrant_client: QdrantClient, tradition: str, user_id: str = "demo"
    ):
        super().__init__(
            qdrant_client=qdrant_client, tradition=tradition, user_id=user_id
        )

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
    ) -> List[Document]:
        """Retrieve relevant documents using Qdrant search (sync wrapper)."""
        try:
            # Run the async method in a new event loop
            return asyncio.run(
                self._aget_relevant_documents(query, run_manager=run_manager)
            )
        except Exception as e:
            logger.error(f"Error in sync document retrieval: {e}")
            return []

    async def _aget_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
    ) -> List[Document]:
        """Retrieve relevant documents using Qdrant search (async)."""
        try:
            # Generate query embedding (async)
            query_embedding = await get_embedding(query)
            if not query_embedding:
                logger.error("Failed to generate embedding for query")
                return []

            # Perform knowledge base search (sync)
            results = self.qdrant_client.search_knowledge_base(
                tradition=self.tradition, query_embedding=query_embedding, limit=5
            )

            # Convert search results to LangChain documents
            documents = []
            for result in results:
                doc = Document(
                    page_content=result.text,
                    metadata={
                        "source": result.metadata.get("source_id", "unknown"),
                        "score": result.score,
                        "source_type": result.metadata.get("source_type", "unknown"),
                        **result.metadata,
                    },
                )
                documents.append(doc)

            logger.info(
                f"Retrieved {len(documents)} documents for query: {query[:50]}..."
            )
            return documents

        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []


class QdrantCoachingEngine:
    """
    Modern RAG-based coaching engine using Qdrant vector store.

    This engine replaces the legacy FAISS-based system with a more
    scalable and production-ready Qdrant implementation.
    """

    def __init__(self, tradition: str = "canon-default", user_id: str = "demo"):
        self.tradition = tradition
        self.user_id = user_id
        self.qdrant_client = QdrantClient()
        self.retriever = None
        self.rag_chain = None
        self._initialize()

    def _initialize(self):
        """Initialize the engine with Qdrant-based retriever and RAG chain."""
        try:
            # Check if Qdrant is available by trying to get collections
            try:
                self.qdrant_client.client.get_collections()
            except Exception as e:
                raise RuntimeError(f"Qdrant is not available: {e}")

            # Initialize retriever
            self.retriever = QdrantRetriever(
                qdrant_client=self.qdrant_client,
                tradition=self.tradition,
                user_id=self.user_id,
            )

            # Initialize RAG chain
            self.rag_chain = create_rag_chain(retrievers=[self.retriever])

            logger.info(
                f"QdrantCoachingEngine initialized for tradition: {self.tradition}"
            )

        except Exception as e:
            logger.error(f"Failed to initialize QdrantCoachingEngine: {e}")
            raise

    def ask(self, query: str) -> str:
        """Ask a question using the RAG chain."""
        if not self.rag_chain:
            raise ValueError("RAG chain is not initialized")

        try:
            response = self.rag_chain.invoke(query)
            logger.info(f"Generated response for query: {query[:50]}...")
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I apologize, but I encountered an error while processing your question: {str(e)}"

    def get_rag_chain(self) -> Runnable:
        """Get the underlying RAG chain."""
        if not self.rag_chain:
            raise ValueError("RAG chain is not initialized")
        return self.rag_chain

    def check_knowledge_base(self) -> bool:
        """Check if the knowledge base has documents for this tradition."""
        try:
            collection_name = self.qdrant_client.get_knowledge_collection_name(
                self.tradition
            )

            # Try to get collection info
            info = self.qdrant_client.client.get_collection(collection_name)
            if info and hasattr(info, "points_count"):
                return info.points_count > 0
            elif info and isinstance(info, dict):
                return info.get("points_count", 0) > 0
            return False

        except Exception as e:
            logger.warning(f"Could not check knowledge base: {e}")
            return False

    def reload(self):
        """Reload the engine."""
        logger.info("Reloading QdrantCoachingEngine...")
        self._initialize()


# --- Engine Cache ---
# Cache for engine instances to avoid re-initialization
qdrant_engine_cache = {}


def get_qdrant_engine_for_tradition(
    tradition: str, user_id: str = "demo"
) -> Optional[QdrantCoachingEngine]:
    """
    Get or create a QdrantCoachingEngine instance for a tradition.

    Returns None if the knowledge base is not available.
    """
    cache_key = f"{tradition}_{user_id}"

    if cache_key not in qdrant_engine_cache:
        logger.info(f"Creating new QdrantEngine for tradition '{tradition}'")

        try:
            engine = QdrantCoachingEngine(tradition=tradition, user_id=user_id)

            # Check if knowledge base has content
            if not engine.check_knowledge_base():
                logger.warning(
                    f"No documents found in knowledge base for tradition '{tradition}'"
                )
                return None

            qdrant_engine_cache[cache_key] = engine
            logger.info(f"QdrantEngine for '{tradition}' initialized and cached")

        except Exception as e:
            logger.error(f"Failed to initialize QdrantEngine for '{tradition}': {e}")
            return None

    return qdrant_engine_cache[cache_key]


def clear_engine_cache():
    """Clear the engine cache."""
    global qdrant_engine_cache
    qdrant_engine_cache.clear()
    logger.info("Engine cache cleared")
