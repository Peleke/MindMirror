import os


class Config:
    API_VERSION = os.getenv("API_VERSION", "0.1.0")
    DEBUG_GRAPHQL_SERVER = os.getenv("DEBUG_GRAPHQL_SERVER", "true").lower() == "true"

    # Database Configuration - loaded from environment variables
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5433")  # Changed port to avoid conflict with practices
    DB_NAME = os.getenv("DB_NAME", "swae_meals")  # Using a different DB name

    DATABASE_URL = os.getenv(
        "DATABASE_URL", f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Add any other meals-specific configurations here
    # For example, if you had external service URLs, API keys, etc.
