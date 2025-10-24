from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional
import os

from shared.secrets import get_secret


class Settings(BaseSettings):
    """Habits service settings (aligned with journal_service)."""

    # Database
    database_url: str = get_secret(
        "DATABASE_URL",
        volume_name="database-url",
        filename="database-url",
        default="postgresql+asyncpg://postgres:postgres@postgres:5432/cyborg_coach"
    )
    database_schema: str = os.getenv("DATABASE_SCHEMA", "habits")
    # Connection pool tuning
    db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "15"))
    db_max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "30"))
    db_pool_recycle: int = int(os.getenv("DB_POOL_RECYCLE", "1800"))
    db_pool_pre_ping: bool = os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"
    db_pool_timeout: int = int(os.getenv("DB_POOL_TIMEOUT", "10"))

    # Auth
    jwt_secret: str = get_secret(
        "JWT_SECRET",
        volume_name="jwt-secret",
        filename="jwt-secret",
        default="your-secret-key"
    )
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    require_auth: bool = os.getenv("REQUIRE_AUTH", "true").lower() == "true"

    # Dummy UUIDs for mesh introspection and fallback users
    faux_mesh_user_id: str = os.getenv("FAUX_MESH_USER_ID", "00000000-0000-0000-0000-000000000001")
    faux_mesh_supabase_id: str = os.getenv("FAUX_MESH_SUPABASE_ID", "00000000-0000-0000-0000-000000000002")

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Supabase (kept for symmetry/future use)
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

    # Vouchers/web integration
    vouchers_web_base_url: Optional[str] = os.getenv("VOUCHERS_WEB_BASE_URL")

    # Campaign -> Program mapping
    uye_program_template_id: Optional[str] = os.getenv("UYE_PROGRAM_TEMPLATE_ID")
    mindmirror_program_template_id: Optional[str] = os.getenv("MINDMIRROR_PROGRAM_TEMPLATE_ID")
    # Add-on programs
    daily_journaling_program_template_id: Optional[str] = os.getenv("DAILY_JOURNALING_PROGRAM_TEMPLATE_ID")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()

