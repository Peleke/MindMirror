from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database
    database_url: str = os.getenv('DATABASE_URL', "postgresql+asyncpg://postgres:postgres@postgres:5432/cyborg_coach")
    
    # Redis
    redis_url: str = os.getenv('REDIS_URL', "redis://redis:6379/0")
    
    # Celery
    celery_broker_url: str = os.getenv('CELERY_BROKER_URL', "redis://redis:6379/0")
    
    # Service URLs
    agent_service_url: str = os.getenv('AGENT_SERVICE_URL', "http://agent_service:8000")
    
    # Auth
    jwt_secret: str = os.getenv('JWT_SECRET', "your-secret-key")
    jwt_algorithm: str = os.getenv('JWT_ALGORITHM', "HS256")
    
    # Dummy UUIDs for mesh introspection and fallback users
    # These are obviously fake UUIDs (all 0s except last character)
    faux_mesh_user_id: str = os.getenv('FAUX_MESH_USER_ID', "00000000-0000-0000-0000-000000000001")
    faux_mesh_supabase_id: str = os.getenv('FAUX_MESH_SUPABASE_ID', "00000000-0000-0000-0000-000000000002")
    
    # Logging
    log_level: str = os.getenv('LOG_LEVEL', "INFO")
    
    # Supabase settings (for future use)
    supabase_url: Optional[str] = os.getenv('SUPABASE_URL')
    supabase_anon_key: Optional[str] = os.getenv('SUPABASE_ANON_KEY')
    supabase_service_role_key: Optional[str] = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    # Environment
    environment: str = os.getenv('ENVIRONMENT', "development")
    debug: bool = os.getenv('DEBUG', "False").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()