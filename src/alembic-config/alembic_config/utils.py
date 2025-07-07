"""Database utilities for Alembic configuration."""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global environment setting
_current_environment = os.getenv("ALEMBIC_ENV", "supabase")


def set_environment(env: str) -> None:
    """Set the current environment (supabase, local)."""
    global _current_environment
    _current_environment = env.lower()


def get_current_environment() -> str:
    """Get the current environment setting."""
    return _current_environment


def get_database_url() -> str:
    """Get database URL from environment variables."""
    # Check for explicit DATABASE_URL first
    if database_url := os.getenv("DATABASE_URL"):
        return database_url
    
    # Check current environment setting
    if _current_environment == "local":
        return os.getenv("LOCAL_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/cyborg_coach")
    
    # Default to Supabase - check for individual variables first
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "postgres")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")
    
    if db_host and db_user and db_pass:
        # URL encode the password to handle special characters
        import urllib.parse
        encoded_pass = urllib.parse.quote_plus(db_pass)
        return f"postgresql://{db_user}:{encoded_pass}@{db_host}:{db_port}/{db_name}"
    
    # Fallback to SUPABASE_URL/SUPABASE_KEY format
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if supabase_url and supabase_key:
        # Extract host from Supabase URL
        # Format: https://project-ref.supabase.co
        host = supabase_url.replace("https://", "").replace("http://", "")
        return f"postgresql://postgres:{supabase_key}@{host}:5432/postgres"
    
    # Final fallback to local
    return os.getenv("LOCAL_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/cyborg_coach")


def get_driver() -> str:
    """Get appropriate database driver based on environment."""
    # Allow override via environment variable
    if driver := os.getenv("DB_DRIVER"):
        return driver
    
    # Use asyncpg for Supabase, psycopg2 for local
    if _current_environment == "local":
        return "psycopg2"
    else:
        return "asyncpg"


def is_supabase_environment() -> bool:
    """Check if we're connecting to Supabase."""
    return _current_environment != "local"


def get_schema_name() -> str:
    """Get the schema name for migrations."""
    return os.getenv("DB_SCHEMA", "mindmirror") 