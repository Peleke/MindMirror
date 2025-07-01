"""
Application Configuration Management

Clean configuration management using pydantic-settings for environment variables
and application settings.
"""

import os
from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with environment variable support.

    Uses pydantic-settings for automatic environment variable loading
    and validation.
    """

    # Application settings
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")

    # Server settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")

    # CORS settings
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS",
    )

    # Database settings
    database_url: str = Field(env="DATABASE_URL")

    # Vector database settings
    qdrant_url: str = Field(env="QDRANT_URL")
    qdrant_api_key: str = Field(default="", env="QDRANT_API_KEY")

    # LLM settings
    llm_provider: str = Field(default="openai", env="LLM_PROVIDER")
    embedding_provider: str = Field(default="openai", env="EMBEDDING_PROVIDER")
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")

    # Ollama settings
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_chat_model: str = Field(default="llama3.2", env="OLLAMA_CHAT_MODEL")
    ollama_embedding_model: str = Field(default="nomic-embed-text", env="OLLAMA_EMBEDDING_MODEL")

    # Data directory
    data_dir: str = Field(default="./data", env="DATA_DIR")

    # Chunking settings for document processing
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")

    # Storage paths
    graph_store_path: str = Field(default="./data/graph_store", env="GRAPH_STORE_PATH")
    pdf_dir: str = Field(default="./data/pdfs", env="PDF_DIR")
    vector_store_dir: str = Field(default="./data/vector_store", env="VECTOR_STORE_DIR")

    # Logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT"
    )

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings with caching.

    Returns:
        Settings: Application settings instance
    """
    return Settings()


# Convenience function for getting settings
def get_config() -> Settings:
    """
    Convenience function to get settings.

    Returns:
        Settings: Application settings instance
    """
    return get_settings()
