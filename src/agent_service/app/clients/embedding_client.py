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

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the embedding client.

        Args:
            base_url: Base URL for the embedding service (uses config if None)
        """
        if base_url is None:
            # Get base URL from configuration
            from agent_service.app.config import get_settings

            settings = get_settings()
            base_url = settings.embedding_base_url

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

            # Get the embedding model from config
            from agent_service.app.config import get_settings

            settings = get_settings()
            model = settings.embedding_model
            provider = settings.embedding_provider

            if provider == "openai":
                # Use OpenAI's embedding API
                headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
                response = await self.client.post(
                    "https://api.openai.com/v1/embeddings",
                    headers=headers,
                    json={"model": model, "input": text},
                )
            elif provider == "ollama":
                # Use Ollama's embedding API
                response = await self.client.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": model, "prompt": text},
                )
            else:
                self.logger.error(f"Unsupported embedding provider: {provider}")
                return None

            response.raise_for_status()
            data = response.json()

            # Extract embedding based on provider
            if provider == "openai":
                if "data" in data and len(data["data"]) > 0:
                    embedding = data["data"][0]["embedding"]
                else:
                    self.logger.error("No embedding data in OpenAI response")
                    return None
            elif provider == "ollama":
                if "embedding" in data:
                    embedding = data["embedding"]
                else:
                    self.logger.error("No embedding in Ollama response")
                    return None
            else:
                self.logger.error(f"Unsupported embedding provider: {provider}")
                return None

            self.logger.debug(f"Received embedding of length {len(embedding)}")
            return embedding

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
            from agent_service.app.config import get_settings
            settings = get_settings()
            provider = settings.embedding_provider

            if provider == "openai":
                # For OpenAI, we can't easily health check without making an API call
                # Just return True since the API key validation will happen on actual requests
                return True
            elif provider == "ollama":
                # Check Ollama's health endpoint
                response = await self.client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                return True
            else:
                self.logger.error(f"Unsupported embedding provider for health check: {provider}")
                return False
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
