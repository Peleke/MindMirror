"""Utility functions for MindMirror CLI."""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global environment setting
_current_environment = os.getenv("CLI_ENV", "local")


def set_environment(env: str) -> None:
    """Set the current environment (local, staging, production)."""
    global _current_environment
    env_lower = env.lower()
    valid_envs = {"local", "staging", "production"}

    if env_lower not in valid_envs:
        raise ValueError(
            f"Invalid environment: {env}. Must be one of: {', '.join(sorted(valid_envs))}"
        )

    _current_environment = env_lower


def get_current_environment() -> str:
    """Get the current environment setting (local, staging, or production)."""
    return _current_environment


def is_production_environment() -> bool:
    """Check if targeting production environment (extra safety checks)."""
    return _current_environment == "production"


def is_staging_environment() -> bool:
    """Check if targeting staging environment."""
    return _current_environment == "staging"


def is_live_environment() -> bool:
    """Check if we're connecting to live services (staging or production).

    Deprecated: Use is_staging_environment() or is_production_environment() instead.
    Kept for backwards compatibility.
    """
    return _current_environment in ("staging", "production")


def get_database_url(service: str = "main") -> str:
    """
    Get database URL for service based on current environment.

    Args:
        service: Database service name (only used for local Docker containers)
            - 'main': habits, journal, agent services (default)
            - 'movements': movements service
            - 'practices': practices service
            - 'users': users service

    Returns:
        Database URL string

    Raises:
        ValueError: If required environment variable is not set

    Environment Variables:
        Local (Docker Compose - separate containers per service):
            - LOCAL_DATABASE_URL (optional override for main)
            - LOCAL_MOVEMENTS_DATABASE_URL (optional override for movements)
            - LOCAL_PRACTICES_DATABASE_URL (optional override for practices)
            - LOCAL_USERS_DATABASE_URL (optional override for users)

        Staging/Production (single database, different schemas):
            - STAGING_DATABASE_URL (required)
            - PRODUCTION_DATABASE_URL (required)
            Note: Schema is specified via --schema flag in commands

    Examples:
        >>> set_environment('staging')
        >>> get_database_url('movements')
        'postgresql+asyncpg://...'  # from STAGING_DATABASE_URL
        # Schema controlled by --schema flag (e.g., --schema movements)

        >>> set_environment('local')
        >>> get_database_url('movements')
        'postgresql+asyncpg://movements_user:movements_password@movements_postgres:5432/swae_movements'
    """
    env = _current_environment.upper()

    # For staging/production: single database URL, schema specified via --schema flag
    if env in ['STAGING', 'PRODUCTION']:
        env_var = f'{env}_DATABASE_URL'
        url = os.getenv(env_var)

        # Fallback to legacy SUPABASE_DATABASE_URL for backwards compatibility
        if not url:
            url = os.getenv('SUPABASE_DATABASE_URL')

        if not url:
            raise ValueError(
                f"Missing database URL for {_current_environment} environment.\n"
                f"Please set the {env_var} environment variable.\n"
                f"Example: export {env_var}='postgresql+asyncpg://postgres:password@host:5432/postgres'\n"
                f"Note: Schema is specified via --schema flag (e.g., --schema movements)"
            )

        return url

    # For local: separate Docker containers with different URLs per service
    if env == 'LOCAL':
        # Check for service-specific override first
        service_env_var = f'LOCAL_{service.upper()}_DATABASE_URL' if service != 'main' else 'LOCAL_DATABASE_URL'
        url = os.getenv(service_env_var)

        if url:
            return url

        # Docker Compose defaults
        local_defaults = {
            'main': "postgresql+asyncpg://postgres:postgres@postgres:5432/cyborg_coach",
            'movements': "postgresql+asyncpg://movements_user:movements_password@movements_postgres:5432/swae_movements",
            'practices': "postgresql+asyncpg://practices_user:practices_password@practices_postgres:5432/swae_practices",
            'users': "postgresql+asyncpg://users_user:users_password@users_postgres:5432/swae_users",
        }
        return local_defaults.get(service, local_defaults['main'])

    # Should not reach here, but provide helpful error
    raise ValueError(
        f"Unsupported environment: {_current_environment}. Must be local, staging, or production."
    )


def get_qdrant_url() -> str:
    """Get Qdrant URL based on current environment."""
    if is_live_environment():
        return os.getenv("LIVE_QDRANT_URL", os.getenv("QDRANT_URL", "http://localhost:6333"))
    else:
        return os.getenv("QDRANT_URL", "http://localhost:6333")


def get_qdrant_api_key() -> Optional[str]:
    """Get Qdrant API key based on current environment."""
    if is_live_environment():
        return os.getenv("QDRANT_API_KEY")
    else:
        # No API key needed for local development
        return None 