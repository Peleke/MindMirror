"""
Shared secret management utilities for Cloud Run v2 and local development.

Provides transparent secret loading from:
1. Cloud Run v2 volume mounts (/secrets/<volume-name>/<filename>)
2. Environment variables (local/staging fallback)

Usage:
    from shared.secrets import get_secret

    # Automatically reads from volume OR env
    database_url = get_secret("DATABASE_URL", volume_name="database-url", filename="database-url")
"""

import os
from pathlib import Path
from typing import Optional


def get_secret(
    env_var_name: str,
    volume_name: Optional[str] = None,
    filename: Optional[str] = None,
    default: Optional[str] = None,
) -> Optional[str]:
    """
    Get secret value from Cloud Run volume mount OR environment variable.

    Priority order:
    1. Cloud Run v2 volume mount: /secrets/<volume_name>/<filename>
    2. Environment variable: env_var_name
    3. Default value

    Args:
        env_var_name: Environment variable name (e.g., "DATABASE_URL")
        volume_name: Cloud Run volume mount name (e.g., "database-url")
        filename: Filename in the volume mount (e.g., "database-url")
        default: Default value if not found

    Returns:
        Secret value or None

    Examples:
        # Simple env var only
        api_key = get_secret("OPENAI_API_KEY")

        # With Cloud Run volume mount
        db_url = get_secret(
            "DATABASE_URL",
            volume_name="database-url",
            filename="database-url"
        )
    """
    # Try Cloud Run v2 volume mount first
    if volume_name and filename:
        secret_path = Path(f"/secrets/{volume_name}/{filename}")
        if secret_path.exists():
            try:
                value = secret_path.read_text().strip()
                if value:
                    return value
            except Exception:
                pass  # Fall through to env var

    # Fall back to environment variable
    value = os.getenv(env_var_name)
    if value:
        return value

    # Return default
    return default


def get_environment() -> str:
    """
    Get current environment (local/staging/production).

    Reads from Cloud Run v2 volume mount or environment variable.

    Returns:
        Environment string, defaults to "local"
    """
    return get_secret(
        "ENVIRONMENT",
        volume_name="environment",
        filename="environment",
        default="local"
    )


def should_auto_create_schema() -> bool:
    """
    Determine if schema should be auto-created via metadata.create_all().

    In production/staging, we use Alembic for schema management.
    Auto-creation is only for local development and testing.

    Returns:
        True if auto-creation is allowed, False otherwise
    """
    environment = get_environment()

    # Only allow auto-creation in local/test environments
    return environment in ("local", "test", "development")
