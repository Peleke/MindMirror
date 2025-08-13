from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "local"
    log_level: str = "INFO"
    database_url: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/cyborg_coach"
    database_schema: str = "habits"
    require_auth: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()

