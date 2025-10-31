from pydantic_settings import BaseSettings
from typing import Optional
import os

from shared.secrets import get_secret


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Database
    database_url: str = get_secret(
        "DATABASE_URL",
        volume_name="database-url",
        filename="database-url",
        default="postgresql+asyncpg://postgres:postgres@postgres:5432/cyborg_coach"
    )

    # Redis
    redis_url: str = get_secret(
        "REDIS_URL",
        volume_name="redis-url",
        filename="redis-url",
        default="redis://redis:6379/0"
    )

    # Celery
    celery_broker_url: str = get_secret(
        "CELERY_BROKER_URL",
        volume_name="celery-broker-url",
        filename="celery-broker-url",
        default="redis://redis:6379/0"
    )

    # Service URLs
    agent_service_url: str = os.getenv("AGENT_SERVICE_URL", "http://agent_service:8000")
    celery_worker_url: str = os.getenv("CELERY_WORKER_URL", "http://celery-worker-web:8000")
    
    # Auth
    jwt_secret: str = get_secret(
        "JWT_SECRET",
        volume_name="jwt-secret",
        filename="jwt-secret",
        default="your-secret-key"
    )
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    reindex_secret_key: str = get_secret(
        "REINDEX_SECRET_KEY",
        volume_name="reindex-secret-key",
        filename="reindex-secret-key",
        default="your-super-secret-key"
    )
    
    # Dummy UUIDs for mesh introspection and fallback users
    # These are obviously fake UUIDs (all 0s except last character)
    faux_mesh_user_id: str = os.getenv("FAUX_MESH_USER_ID", "00000000-0000-0000-0000-000000000001")
    faux_mesh_supabase_id: str = os.getenv("FAUX_MESH_SUPABASE_ID", "00000000-0000-0000-0000-000000000002")
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Supabase settings (for future use)
    supabase_url: Optional[str] = os.getenv("SUPABASE_URL")
    supabase_anon_key: Optional[str] = get_secret(
        "SUPABASE_ANON_KEY",
        volume_name="supabase-anon-key",
        filename="supabase-anon-key"
    )
    supabase_service_role_key: Optional[str] = get_secret(
        "SUPABASE_SERVICE_ROLE_KEY",
        volume_name="supabase-service-role-key",
        filename="supabase-service-role-key"
    )

    # Environment
    environment: str = get_secret("ENVIRONMENT", default="development")
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()