import os
from shared.secrets import get_secret

class Config:
    SERVICE_NAME = os.getenv("SERVICE_NAME", "movements_service")

    # HTTP
    DEFAULT_HTTP_PORT = 8005
    PORT = int(os.getenv("PORT") or os.getenv("MOVEMENTS_HTTP_PORT") or DEFAULT_HTTP_PORT)
    DEBUG_GRAPHQL_SERVER = os.getenv("DEBUG_GRAPHQL_SERVER", "true").lower() == "true"

    # Database
    # Prefer full DATABASE_URL; else construct from parts
    DATABASE_URL = get_secret(
        "DATABASE_URL",
        volume_name="database-url",
        filename="database-url"
    )
    if not DATABASE_URL:
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_PORT = int(os.getenv("DB_PORT", "5432"))
        DB_USER = os.getenv("DB_USER", "postgres")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
        DB_NAME = os.getenv("DB_NAME", "swae_movements")
        DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # External sources
    EXERCISEDB_BASE_URL = os.getenv("EXERCISEDB_BASE_URL", "https://v2.exercisedb.io")
    EXERCISEDB_API_KEY = get_secret(
        "EXERCISEDB_API_KEY",
        volume_name="exercisedb-api-key",
        filename="exercisedb-api-key",
        default=""
    )

    # Auth
    REQUIRE_AUTH = os.getenv("REQUIRE_AUTH", "true").lower() == "true" 