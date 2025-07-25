import logging
import os
import asyncio
import httpx
from typing import List, Protocol
from abc import ABC, abstractmethod

from ..config import Config

logger = logging.getLogger(__name__)


class EmbeddingService(Protocol):
    """Protocol for embedding services."""

    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        ...

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        ...


class OllamaEmbeddingService:
    """Ollama-based embedding service."""

    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or os.getenv(
            "OLLAMA_BASE_URL", "http://host.docker.internal:11434"
        )
        self.model = model or os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
        self.client = httpx.AsyncClient()

    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Ollama."""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": text},
            )
            response.raise_for_status()
            result = response.json()
            embedding = result["embedding"]

            logger.debug(f"Generated embedding for text (length: {len(text)})")
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding with Ollama: {e}")
            # Return zero vector as fallback
            return [0.0] * Config.VECTOR_SIZE

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        try:
            embeddings = []
            for text in texts:
                embedding = await self.get_embedding(text)
                embeddings.append(embedding)
            return embeddings
        except Exception as e:
            logger.error(f"Failed to generate embeddings with Ollama: {e}")
            return [[0.0] * Config.VECTOR_SIZE for _ in texts]


class OpenAIEmbeddingService:
    """OpenAI-based embedding service."""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        self.client = httpx.AsyncClient()

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI."""
        try:
            response = await self.client.post(
                "https://api.openai.com/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={"model": self.model, "input": text},
            )
            response.raise_for_status()
            return response.json()["data"][0]["embedding"]
        except Exception as e:
            logger.error(f"Failed to generate embedding with OpenAI: {e}")
            return [0.0] * 1536  # OpenAI embeddings are typically 1536-dimensional

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        try:
            response = await self.client.post(
                "https://api.openai.com/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={"model": self.model, "input": texts},
            )
            response.raise_for_status()
            return [item["embedding"] for item in response.json()["data"]]
        except Exception as e:
            logger.error(f"Failed to generate embeddings with OpenAI: {e}")
            return [[0.0] * 1536 for _ in texts]


class SentenceTransformersEmbeddingService:
    """Local Sentence Transformers embedding service."""

    def __init__(self, model_name: str = None, **kwargs):
        # Handle both direct parameter and config dict
        if isinstance(model_name, dict):
            config = model_name
            self.model_name = config.get("model_name") or os.getenv(
                "SENTENCE_TRANSFORMERS_MODEL", "all-MiniLM-L6-v2"
            )
        else:
            self.model_name = model_name or os.getenv(
                "SENTENCE_TRANSFORMERS_MODEL", "all-MiniLM-L6-v2"
            )

        self._model = None

        # Check if sentence_transformers is available at initialization
        try:
            import sentence_transformers
        except ImportError:
            raise ImportError(
                "sentence_transformers package is required but not installed. Run: pip install sentence-transformers"
            )

    def _load_model(self):
        """Lazy load the model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self.model_name)
                logger.info(f"Loaded Sentence Transformers model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to load Sentence Transformers model: {e}")
                raise

    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Sentence Transformers (synchronous)."""
        try:
            self._load_model()
            # SentenceTransformers expects a list of texts
            embedding = self._model.encode([text])
            return embedding[0].tolist()
        except Exception as e:
            logger.error(
                f"Failed to generate embedding with Sentence Transformers: {e}"
            )
            raise

    async def get_embedding_async(self, text: str) -> List[float]:
        """Generate embedding for text using Sentence Transformers (async wrapper)."""
        try:
            self._load_model()
            # Note: SentenceTransformers is synchronous, so we run it in a thread
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(None, self._model.encode, [text])
            return embedding[0].tolist()
        except Exception as e:
            logger.error(
                f"Failed to generate embedding with Sentence Transformers: {e}"
            )
            return [0.0] * 384  # Default dimension for all-MiniLM-L6-v2

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (synchronous)."""
        try:
            self._load_model()
            embeddings = self._model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            logger.error(
                f"Failed to generate embeddings with Sentence Transformers: {e}"
            )
            raise

    async def get_embeddings_async(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (async wrapper)."""
        try:
            self._load_model()
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(None, self._model.encode, texts)
            return embeddings.tolist()
        except Exception as e:
            logger.error(
                f"Failed to generate embeddings with Sentence Transformers: {e}"
            )
            return [[0.0] * 384 for _ in texts]


class MockEmbeddingService:
    """Mock embedding service for testing."""

    def __init__(self, dimension: int = None):
        self.dimension = dimension or Config.VECTOR_SIZE

    async def get_embedding(self, text: str) -> List[float]:
        """Generate mock embedding."""
        import random

        return [random.uniform(-1, 1) for _ in range(self.dimension)]

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate mock embeddings."""
        return [await self.get_embedding(text) for text in texts]


class EmbeddingServiceFactory:
    """Factory for creating embedding services."""

    @staticmethod
    def create(service_type: str = None) -> EmbeddingService:
        """Create an embedding service based on configuration."""
        service_type = service_type or os.getenv("EMBEDDING_SERVICE", "ollama")

        if service_type == "ollama":
            return OllamaEmbeddingService()
        elif service_type == "openai":
            return OpenAIEmbeddingService()
        elif service_type == "sentence-transformers":
            return SentenceTransformersEmbeddingService()
        elif service_type == "mock":
            return MockEmbeddingService()
        else:
            raise ValueError(f"Unknown embedding service type: {service_type}")


# Global embedding service instance
_embedding_service: EmbeddingService = None


def get_embedding_service() -> EmbeddingService:
    """Get the global embedding service instance."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingServiceFactory.create()
    return _embedding_service


def set_embedding_service(service: EmbeddingService):
    """Set the global embedding service instance (for testing)."""
    global _embedding_service
    _embedding_service = service


# Convenience functions for backward compatibility
async def get_embedding(text: str) -> List[float]:
    """
    Generate embedding for a single text using the configured service.

    Args:
        text: The text to embed

    Returns:
        List of floats representing the embedding vector
    """
    try:
        service = get_embedding_service()
        embedding = await service.get_embedding(text)
        logger.debug(f"Generated embedding for text (length: {len(text)})")
        return embedding

    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        # Return zero vector as fallback
        return [0.0] * Config.VECTOR_SIZE


async def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts using the configured service.

    Args:
        texts: List of texts to embed

    Returns:
        List of embedding vectors
    """
    try:
        service = get_embedding_service()
        embeddings = await service.get_embeddings(texts)
        logger.info(f"Generated {len(embeddings)} embeddings")
        return embeddings

    except Exception as e:
        logger.error(f"Failed to generate embeddings: {e}")
        # Return zero vectors as fallback
        return [[0.0] * Config.VECTOR_SIZE for _ in texts]
