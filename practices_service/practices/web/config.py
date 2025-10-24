import os
from shared.secrets import get_secret


class Config:
    API_VERSION = os.getenv("API_VERSION", "0.1.0")
    DEBUG_GRAPHQL_SERVER = os.getenv("DEBUG_GRAPHQL_SERVER", "true").lower() == "true"

    # Database Configuration - loaded from environment variables
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")  # Default to 5432, can be overridden by tests
    DB_NAME = os.getenv("DB_NAME", "swae")

    DATABASE_URL = get_secret(
        "DATABASE_URL",
        volume_name="database-url",
        filename="database-url",
        default=f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "swae-aa835-test")
    GCP_PROJECT_ID = os.getenv("GCS_PROJECT_ID", "swae-aa835")
