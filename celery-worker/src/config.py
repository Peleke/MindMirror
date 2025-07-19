"""
Configuration settings for the Celery worker.
"""

import os
from typing import Optional


class Config:
    """Configuration class for Celery worker settings."""

    # Vector embedding configuration
    VECTOR_SIZE: int = int(
        os.getenv("EMBEDDING_VECTOR_SIZE", "1536")
    )  # text-embedding-3-small dimension

    # Database configuration
    POSTGRES_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://user:password@postgres:5432/mindmirror"
    )

    # Redis configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")

    # Qdrant configuration
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://qdrant:6333")
    QDRANT_API_KEY: Optional[str] = os.getenv("QDRANT_API_KEY")

    # Journal service configuration
    JOURNAL_SERVICE_URL: str = os.getenv(
        "JOURNAL_SERVICE_URL", "http://journal_service:8001"
    )

    # Agent service configuration
    AGENT_SERVICE_URL: str = os.getenv(
        "AGENT_SERVICE_URL", "http://agent_service:8000"
    )

    # Embedding service configuration
    EMBEDDING_SERVICE: str = os.getenv("EMBEDDING_SERVICE", "ollama")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    OLLAMA_BASE_URL: str = os.getenv(
        "OLLAMA_BASE_URL", "http://host.docker.internal:11434"
    )
    OLLAMA_EMBEDDING_MODEL: str = os.getenv(
        "OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"
    )

    # Task configuration
    TASK_DEFAULT_RETRY_DELAY: int = int(os.getenv("TASK_DEFAULT_RETRY_DELAY", "60"))
    TASK_MAX_RETRIES: int = int(os.getenv("TASK_MAX_RETRIES", "3"))
    TASK_TIME_LIMIT: int = int(os.getenv("TASK_TIME_LIMIT", "300"))

    # Testing configuration - only "true" (lowercase) should enable testing
    TESTING: bool = os.getenv("TESTING", "false").lower() == "true"

    @classmethod
    def get_qdrant_url(cls) -> str:
        """Get the full Qdrant URL."""
        return cls.QDRANT_URL

    @classmethod
    def is_testing(cls) -> bool:
        """Check if we're in testing mode."""
        return cls.TESTING


# Global config instance
config = Config()
