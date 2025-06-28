"""
Embedding service for centralized embedding operations.

This service provides a clean interface for embedding operations,
abstracting away the underlying embedding client implementation.
"""

import logging
from typing import List, Optional

from agent_service.app.clients.embedding_client import EmbeddingClient

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Centralized embedding operations service.

    Provides a clean interface for getting embeddings from text,
    with proper error handling and logging.
    """

    def __init__(self, embedding_client: Optional[EmbeddingClient] = None):
        """
        Initialize the embedding service.

        Args:
            embedding_client: Optional embedding client instance
        """
        self.embedding_client = embedding_client or EmbeddingClient()
        self.logger = logging.getLogger(f"{__name__}.EmbeddingService")

    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Get embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector or None if failed
        """
        try:
            self.logger.debug(f"Getting embedding for text: {text[:100]}...")

            embedding = await self.embedding_client.get_embedding(text)

            if embedding:
                self.logger.debug(
                    f"Successfully generated embedding of length {len(embedding)}"
                )
                return embedding
            else:
                self.logger.warning("Embedding client returned None")
                return None

        except Exception as e:
            self.logger.error(f"Failed to get embedding: {e}")
            return None

    async def get_embeddings(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Get embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors (None for failed embeddings)
        """
        try:
            self.logger.debug(f"Getting embeddings for {len(texts)} texts")

            embeddings = await self.embedding_client.get_embeddings(texts)

            if embeddings:
                self.logger.debug(
                    f"Successfully generated {len(embeddings)} embeddings"
                )
                return embeddings
            else:
                self.logger.warning("Embedding client returned None for batch request")
                return [None] * len(texts)

        except Exception as e:
            self.logger.error(f"Failed to get embeddings: {e}")
            return [None] * len(texts)

    async def get_embedding_safe(
        self, text: str, fallback_vector: Optional[List[float]] = None
    ) -> List[float]:
        """
        Get embedding with fallback to zero vector or provided fallback.

        Args:
            text: Text to embed
            fallback_vector: Optional fallback vector to use on failure

        Returns:
            Embedding vector (never None)
        """
        embedding = await self.get_embedding(text)

        if embedding:
            return embedding

        # Use fallback or zero vector
        if fallback_vector:
            self.logger.warning(f"Using fallback vector for text: {text[:100]}...")
            return fallback_vector
        else:
            self.logger.warning(f"Using zero vector for text: {text[:100]}...")
            return [0.0] * 1536  # Default embedding size

    def validate_embedding(self, embedding: List[float]) -> bool:
        """
        Validate that an embedding vector is properly formatted.

        Args:
            embedding: Embedding vector to validate

        Returns:
            True if valid, False otherwise
        """
        if not embedding:
            return False

        if not isinstance(embedding, list):
            return False

        if not all(isinstance(x, (int, float)) for x in embedding):
            return False

        # Check for reasonable embedding size (1536 is common for OpenAI)
        if len(embedding) not in [1536, 768, 384, 1024]:
            self.logger.warning(f"Unexpected embedding size: {len(embedding)}")

        return True
