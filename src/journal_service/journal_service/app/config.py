from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/cyborg_coach"
    
    # Redis
    redis_url: str = "redis://redis:6379/0"
    
    # Celery
    celery_broker_url: str = "redis://redis:6379/0"
    
    # Service URLs
    agent_service_url: str = "http://agent_service:8000"
    
    # Auth
    jwt_secret: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings() 