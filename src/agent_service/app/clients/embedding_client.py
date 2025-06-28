"""
Embedding client for HTTP communication with embedding service.

This client provides a clean interface for getting embeddings
from the embedding service via HTTP.
"""

import asyncio
import logging
from typing import List, Optional

import httpx

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """
    HTTP client for embedding service communication.

    Provides methods to get embeddings from the embedding service
    via HTTP requests.
    """

    def __init__(self, base_url: str = "http://ollama:11434"):
        """
        Initialize the embedding client.

        Args:
            base_url: Base URL for the embedding service
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.logger = logging.getLogger(f"{__name__}.EmbeddingClient")

    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Get embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector or None if failed
        """
        try:
            self.logger.debug(f"Requesting embedding for text: {text[:100]}...")

            response = await self.client.post(
                f"{self.base_url}/api/embeddings",
                json={"model": "llama2", "prompt": text},
            )

            response.raise_for_status()
            data = response.json()

            if "embedding" in data:
                embedding = data["embedding"]
                self.logger.debug(f"Received embedding of length {len(embedding)}")
                return embedding
            else:
                self.logger.error("No embedding in response")
                return None

        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error getting embedding: {e.response.status_code}")
            return None
        except httpx.RequestError as e:
            self.logger.error(f"Request error getting embedding: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error getting embedding: {e}")
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
            self.logger.debug(f"Requesting embeddings for {len(texts)} texts")

            # Process texts in parallel
            tasks = [self.get_embedding(text) for text in texts]
            embeddings = await asyncio.gather(*tasks, return_exceptions=True)

            # Convert exceptions to None
            result = []
            for i, embedding in enumerate(embeddings):
                if isinstance(embedding, Exception):
                    self.logger.error(
                        f"Failed to get embedding for text {i}: {embedding}"
                    )
                    result.append(None)
                else:
                    result.append(embedding)

            self.logger.debug(
                f"Successfully processed {len([e for e in result if e is not None])} embeddings"
            )
            return result

        except Exception as e:
            self.logger.error(f"Failed to get embeddings: {e}")
            return [None] * len(texts)

    async def health_check(self) -> bool:
        """
        Check if the embedding service is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Embedding service health check failed: {e}")
            return False

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
