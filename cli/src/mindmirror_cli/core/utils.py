"""Utility functions for MindMirror CLI."""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global environment setting
_current_environment = os.getenv("CLI_ENV", "local")


def set_environment(env: str) -> None:
    """Set the current environment (local, live)."""
    global _current_environment
    _current_environment = env.lower()


def get_current_environment() -> str:
    """Get the current environment setting."""
    return _current_environment


def get_qdrant_url() -> str:
    """Get Qdrant URL based on current environment."""
    if _current_environment == "live":
        return os.getenv("LIVE_QDRANT_URL", os.getenv("QDRANT_URL", "http://localhost:6333"))
    else:
        return os.getenv("QDRANT_URL", "http://localhost:6333")


def get_qdrant_api_key() -> Optional[str]:
    """Get Qdrant API key based on current environment."""
    if _current_environment == "live":
        return os.getenv("QDRANT_API_KEY")
    else:
        # No API key needed for local development
        return None


def is_live_environment() -> bool:
    """Check if we're connecting to live services."""
    return _current_environment == "live" 