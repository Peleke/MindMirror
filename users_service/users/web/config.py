import os


class Config:
    """Configuration settings for the users service."""

    API_VERSION = "0.1.0"
    DEBUG_GRAPHQL_SERVER = os.getenv("DEBUG_GRAPHQL_SERVER", "True").lower() == "true"
    DB_ECHO = os.getenv("DB_ECHO", "False").lower() == "true"

    # Prefer a fully-formed DATABASE_URL if provided (e.g., from Cloud Run secret)
    _RAW_DATABASE_URL = os.getenv("DATABASE_URL", "")

    # Database settings (fallback components)
    DB_USER = os.getenv("DB_USER", "users_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "users_password")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5433")  # Default for local dev; Docker may override to 5432
    DB_NAME = os.getenv("DB_NAME", "users_db")
    DB_DRIVER = os.getenv("DB_DRIVER", "asyncpg")

    if _RAW_DATABASE_URL:
        DATABASE_URL = _RAW_DATABASE_URL
    else:
        # Construct DATABASE_URL from individual parts for local/dev
        DATABASE_URL = f"postgresql+{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Service URLs for cross-service communication
    PRACTICES_SERVICE_URL = os.getenv("PRACTICES_SERVICE_URL", "http://practices:8000/graphql")
    MEALS_SERVICE_URL = os.getenv("MEALS_SERVICE_URL", "http://meals:8000/graphql")
    JOURNAL_SERVICE_URL = os.getenv("JOURNAL_SERVICE_URL", "http://journal:8000/graphql")
    MOVEMENTS_SERVICE_URL = os.getenv("MOVEMENTS_SERVICE_URL", "http://movements:8000/graphql")
    AGENT_SERVICE_URL = os.getenv("AGENT_SERVICE_URL", "http://agent:8000/graphql")
    # FITNESS_SEVICE_URL superseded by MOVEMENTS_SERVICE_URL
    FITNESS_SERVICE_URL = os.getenv("FITNESS_SERVICE_URL", "http://movements:8000/graphql")
    # SHADOW_BOXING_SERVICE_URL does not yet exist
    SHADOW_BOXING_SERVICE_URL = os.getenv("SHADOW_BOXING_SERVICE_URL", "http://boxing:8000/graphql")

    # Supabase settings
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
