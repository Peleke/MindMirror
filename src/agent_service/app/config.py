"""
Application Configuration Management

Clean configuration management using pydantic-settings for environment variables
and application settings. NO defaults - fail fast if required config is missing.
"""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, validator, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with environment variable support.

    Uses pydantic-settings for automatic environment variable loading
    and validation. NO defaults for critical settings - fail fast if missing.
    """

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # extra="ignore",  # Allow extra fields but ignore them
    )

    # Application settings
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")

    # Server settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    api_port: Optional[str] = Field(default=None, env="API_PORT")

    # CORS settings
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS",
    )

    # Database settings - REQUIRED
    database_url: str = Field(env="DATABASE_URL")

    # PostgreSQL settings
    postgres_user: Optional[str] = Field(default=None, env="POSTGRES_USER")
    postgres_password: Optional[str] = Field(default=None, env="POSTGRES_PASSWORD")
    postgres_db: Optional[str] = Field(default=None, env="POSTGRES_DB")

    # Redis settings
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")

    # Vector database settings - REQUIRED
    qdrant_url: str = Field(env="QDRANT_URL")
    qdrant_api_key: str = Field(default="", env="QDRANT_API_KEY")

    # LLM Provider Configuration - REQUIRED
    llm_provider: str = Field(env="LLM_PROVIDER")
    llm_temperature: float = Field(default=0.7, env="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=1000, env="LLM_MAX_TOKENS")
    llm_streaming: bool = Field(default=False, env="LLM_STREAMING")

    # Provider-specific settings - loaded as-is from env
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: Optional[str] = Field(default=None, env="OPENAI_MODEL")

    ollama_base_url: Optional[str] = Field(default=None, env="OLLAMA_BASE_URL")
    ollama_chat_model: Optional[str] = Field(default=None, env="OLLAMA_CHAT_MODEL")
    ollama_embedding_model: Optional[str] = Field(
        default=None, env="OLLAMA_EMBEDDING_MODEL"
    )

    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    google_model: Optional[str] = Field(default=None, env="GOOGLE_MODEL")

    # Embedding provider - REQUIRED
    embedding_provider: str = Field(env="EMBEDDING_PROVIDER")

    # Embedding vector size - REQUIRED
    embedding_vector_size: int = Field(env="EMBEDDING_VECTOR_SIZE")

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

    # Frontend/Next.js settings
    next_public_app_mode: Optional[str] = Field(
        default=None, env="NEXT_PUBLIC_APP_MODE"
    )
    next_public_insight_timeout: Optional[str] = Field(
        default=None, env="NEXT_PUBLIC_INSIGHT_TIMEOUT"
    )
    next_public_supabase_url: Optional[str] = Field(
        default=None, env="NEXT_PUBLIC_SUPABASE_URL"
    )
    next_public_supabase_anon_key: Optional[str] = Field(
        default=None, env="NEXT_PUBLIC_SUPABASE_ANON_KEY"
    )

    # Supabase settings
    supabase_url: Optional[str] = Field(default=None, env="SUPABASE_URL")
    supabase_anon_key: Optional[str] = Field(default=None, env="SUPABASE_ANON_KEY")
    supabase_service_role_key: Optional[str] = Field(
        default=None, env="SUPABASE_SERVICE_ROLE_KEY"
    )
    supabase_jwt_secret: Optional[str] = Field(default=None, env="SUPABASE_JWT_SECRET")

    # External service settings
    resend_api_key: Optional[str] = Field(default=None, env="RESEND_API_KEY")

    # Docker/deployment settings
    uvicorn_reload: Optional[str] = Field(default=None, env="UVICORN_RELOAD")
    i_am_in_a_docker_container: Optional[str] = Field(
        default=None, env="I_AM_IN_A_DOCKER_CONTAINER"
    )

    # Security settings
    jwt_secret: Optional[str] = Field(default=None, env="JWT_SECRET")
    reindex_secret_key: Optional[str] = Field(default=None, env="REINDEX_SECRET_KEY")

    # Service URLs
    celery_worker_url: Optional[str] = Field(default=None, env="CELERY_WORKER_URL")
    journal_service_url: Optional[str] = Field(default=None, env="JOURNAL_SERVICE_URL")

    # Storage settings
    prompt_storage_type: Optional[str] = Field(default=None, env="PROMPT_STORAGE_TYPE")
    use_gcs_emulator: Optional[str] = Field(default=None, env="USE_GCS_EMULATOR")
    gcs_bucket_name: Optional[str] = Field(default=None, env="GCS_BUCKET_NAME")
    gcs_emulator_host: Optional[str] = Field(default=None, env="GCS_EMULATOR_HOST")
    storage_emulator_host: Optional[str] = Field(
        default=None, env="STORAGE_EMULATOR_HOST"
    )

    @validator("llm_provider")
    def validate_llm_provider(cls, v):
        """Validate LLM provider is supported."""
        supported = ["openai", "ollama", "gemini"]
        if v not in supported:
            raise ValueError(f"LLM provider must be one of {supported}, got: {v}")
        return v

    @validator("embedding_provider")
    def validate_embedding_provider(cls, v):
        """Validate embedding provider is supported."""
        supported = ["openai", "ollama", "gemini"]
        if v not in supported:
            raise ValueError(f"Embedding provider must be one of {supported}, got: {v}")
        return v

    # Provider-aware properties that fail fast if config is missing

    @property
    def llm_model(self) -> str:
        """Get the chat model for the configured LLM provider."""
        if self.llm_provider == "openai":
            if not self.openai_model:
                raise ValueError(
                    "OPENAI_MODEL environment variable is required when using OpenAI provider"
                )
            return self.openai_model
        elif self.llm_provider == "ollama":
            if not self.ollama_chat_model:
                raise ValueError(
                    "OLLAMA_CHAT_MODEL environment variable is required when using Ollama provider"
                )
            return self.ollama_chat_model
        elif self.llm_provider == "gemini":
            if not self.google_model:
                raise ValueError(
                    "GOOGLE_MODEL environment variable is required when using Gemini provider"
                )
            return self.google_model
        else:
            raise ValueError(f"Unknown LLM provider: {self.llm_provider}")

    @property
    def embedding_model(self) -> str:
        """Get the embedding model for the configured embedding provider."""
        if self.embedding_provider == "openai":
            # OpenAI embeddings use a different model naming
            return "text-embedding-3-small"  # This is their standard embedding model
        elif self.embedding_provider == "ollama":
            if not self.ollama_embedding_model:
                raise ValueError(
                    "OLLAMA_EMBEDDING_MODEL environment variable is required when using Ollama embedding provider"
                )
            return self.ollama_embedding_model
        elif self.embedding_provider == "gemini":
            return "models/embedding-001"  # Standard Gemini embedding model
        else:
            raise ValueError(f"Unknown embedding provider: {self.embedding_provider}")

    @property
    def llm_api_key(self) -> Optional[str]:
        """Get the API key for the configured LLM provider."""
        if self.llm_provider == "openai":
            if not self.openai_api_key:
                raise ValueError(
                    "OPENAI_API_KEY environment variable is required when using OpenAI provider"
                )
            return self.openai_api_key
        elif self.llm_provider == "gemini":
            if not self.google_api_key:
                raise ValueError(
                    "GOOGLE_API_KEY environment variable is required when using Gemini provider"
                )
            return self.google_api_key
        elif self.llm_provider == "ollama":
            return None  # Ollama doesn't require API key
        else:
            raise ValueError(f"Unknown LLM provider: {self.llm_provider}")

    @property
    def embedding_api_key(self) -> Optional[str]:
        """Get the API key for the configured embedding provider."""
        if self.embedding_provider == "openai":
            if not self.openai_api_key:
                raise ValueError(
                    "OPENAI_API_KEY environment variable is required when using OpenAI embedding provider"
                )
            return self.openai_api_key
        elif self.embedding_provider == "gemini":
            if not self.google_api_key:
                raise ValueError(
                    "GOOGLE_API_KEY environment variable is required when using Gemini embedding provider"
                )
            return self.google_api_key
        elif self.embedding_provider == "ollama":
            return None  # Ollama doesn't require API key
        else:
            raise ValueError(f"Unknown embedding provider: {self.embedding_provider}")

    @property
    def llm_base_url(self) -> Optional[str]:
        """Get the base URL for the configured LLM provider."""
        if self.llm_provider == "ollama":
            if not self.ollama_base_url:
                raise ValueError(
                    "OLLAMA_BASE_URL environment variable is required when using Ollama provider"
                )
            return self.ollama_base_url
        return None

    @property
    def embedding_base_url(self) -> Optional[str]:
        """Get the base URL for the configured embedding provider."""
        if self.embedding_provider == "ollama":
            if not self.ollama_base_url:
                raise ValueError(
                    "OLLAMA_BASE_URL environment variable is required when using Ollama embedding provider"
                )
            return self.ollama_base_url
        return None


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
