import os


class Config:
    """Configuration settings for the users service."""

    API_VERSION = "0.1.0"
    DEBUG_GRAPHQL_SERVER = os.getenv("DEBUG_GRAPHQL_SERVER", "True").lower() == "true"
    DB_ECHO = os.getenv("DB_ECHO", "False").lower() == "true"

    # Database settings
    DB_USER = os.getenv("DB_USER", "users_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "users_password")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5433")  # Default for local dev; Docker will override to 5432 for internal
    DB_NAME = os.getenv("DB_NAME", "users_db")
    DB_DRIVER = os.getenv("DB_DRIVER", "asyncpg")

    # Always construct DATABASE_URL from the specific environment variables
    # to ensure this service uses its dedicated settings from docker-compose.yml
    DATABASE_URL = f"postgresql+{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Service URLs for cross-service communication
    PRACTICES_SERVICE_URL = os.getenv("PRACTICES_SERVICE_URL", "http://practices:8000/graphql")
    FITNESS_SERVICE_URL = os.getenv("FITNESS_SERVICE_URL", "http://movements:8000/graphql")
    MEALS_SERVICE_URL = os.getenv("MEALS_SERVICE_URL", "http://meals:8000/graphql")
    SHADOW_BOXING_SERVICE_URL = os.getenv("SHADOW_BOXING_SERVICE_URL", "http://boxing:8000/graphql")

    # Supabase settings
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
