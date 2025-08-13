from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Habits service settings (aligned with journal_service)."""

    # Database
    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@postgres:5432/cyborg_coach"
    )
    database_schema: str = os.getenv("DATABASE_SCHEMA", "habits")

    # Auth
    jwt_secret: str = os.getenv("JWT_SECRET", "your-secret-key")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    require_auth: bool = os.getenv("REQUIRE_AUTH", "true").lower() == "true"

    # Dummy UUIDs for mesh introspection and fallback users
    faux_mesh_user_id: str = os.getenv("FAUX_MESH_USER_ID", "00000000-0000-0000-0000-000000000001")
    faux_mesh_supabase_id: str = os.getenv("FAUX_MESH_SUPABASE_ID", "00000000-0000-0000-0000-000000000002")

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Supabase (kept for symmetry/future use)
    supabase_url: Optional[str] = os.getenv("SUPABASE_URL")
    supabase_anon_key: Optional[str] = os.getenv("SUPABASE_ANON_KEY")
    supabase_service_role_key: Optional[str] = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()

