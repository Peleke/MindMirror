"""Alembic configuration setup."""

import os
import sys
from pathlib import Path
from typing import Any, Dict

from alembic.config import Config

from .utils import get_database_url, get_driver, get_schema_name


def get_alembic_config() -> Config:
    """Get configured Alembic config object."""
    # Get the directory containing this file
    current_dir = Path(__file__).parent.parent
    
    # Create Alembic config
    config = Config()
    
    # Set the alembic.ini file location
    config.set_main_option("script_location", str(current_dir / "alembic"))
    
    # Set database URL
    database_url = get_database_url()
    config.set_main_option("sqlalchemy.url", database_url)
    
    # Set driver
    driver = get_driver()
    if driver == "asyncpg":
        config.set_main_option("sqlalchemy.url", database_url.replace("postgresql://", "postgresql+asyncpg://"))
    
    # Add src to Python path for model imports
    src_path = current_dir.parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    return config


def get_metadata():
    """Get SQLAlchemy metadata from central aggregator."""
    try:
        from models import metadata
        return metadata
    except ImportError as e:
        raise ImportError(f"Could not import models metadata: {e}") 