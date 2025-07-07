"""
Central Models Aggregator for MindMirror

This module aggregates SQLAlchemy models from all services into a single
metadata object for use by Alembic and other tools.

Usage:
    from src.models import metadata
    # Use metadata for Alembic target_metadata
"""

import logging
from typing import Dict, List, Optional

# Try to import SQLAlchemy, but don't fail if it's not available
try:
    from sqlalchemy import MetaData
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    MetaData = None

logger = logging.getLogger(__name__)

# Create a combined metadata object if SQLAlchemy is available
if SQLALCHEMY_AVAILABLE:
    metadata = MetaData()
else:
    metadata = None

# Track which services have been loaded
_loaded_services: List[str] = []

def _load_journal_service_models() -> bool:
    """Load models from journal service."""
    if not SQLALCHEMY_AVAILABLE:
        logger.warning("SQLAlchemy not available, skipping model loading")
        return False
        
    try:
        from journal_service.models.sql.base import Base as JournalBase
        from journal_service.models.sql.journal import JournalEntryModel
        
        # Reflect all tables from journal service into our metadata
        for table_name, table in JournalBase.metadata.tables.items():
            if table_name not in metadata.tables:
                # Create a copy of the table with our metadata
                table_copy = table.tometadata(metadata)
                logger.debug(f"Loaded journal service table: {table_name}")
            else:
                logger.warning(f"Table {table_name} already exists in metadata (from journal service)")
        
        _loaded_services.append("journal_service")
        logger.info("Successfully loaded journal service models")
        return True
        
    except ImportError as e:
        logger.warning(f"Could not import journal service models: {e}")
        return False
    except Exception as e:
        logger.error(f"Error loading journal service models: {e}")
        return False

def _load_agent_service_models() -> bool:
    """Load models from agent service."""
    if not SQLALCHEMY_AVAILABLE:
        logger.warning("SQLAlchemy not available, skipping model loading")
        return False
        
    try:
        from agent_service.models.sql.base import Base as AgentBase
        
        # Check if agent service has any models
        if not hasattr(AgentBase.metadata, 'tables') or not AgentBase.metadata.tables:
            logger.info("Agent service has no models to load")
            return True
        
        # Reflect all tables from agent service into our metadata
        for table_name, table in AgentBase.metadata.tables.items():
            if table_name not in metadata.tables:
                # Create a copy of the table with our metadata
                table_copy = table.tometadata(metadata)
                logger.debug(f"Loaded agent service table: {table_name}")
            else:
                logger.warning(f"Table {table_name} already exists in metadata (from agent service)")
        
        _loaded_services.append("agent_service")
        logger.info("Successfully loaded agent service models")
        return True
        
    except ImportError as e:
        logger.warning(f"Could not import agent service models: {e}")
        return False
    except Exception as e:
        logger.error(f"Error loading agent service models: {e}")
        return False

def _load_shared_models() -> bool:
    """Load models from shared package."""
    try:
        # Import any shared models if they exist
        # This is a placeholder for future shared models
        logger.debug("No shared models to load")
        return True
        
    except ImportError as e:
        logger.warning(f"Could not import shared models: {e}")
        return False
    except Exception as e:
        logger.error(f"Error loading shared models: {e}")
        return False

def load_all_models() -> bool:
    """Load models from all available services."""
    logger.info("Loading models from all services...")
    
    success = True
    
    # Load models from each service
    success &= _load_journal_service_models()
    success &= _load_agent_service_models()
    success &= _load_shared_models()
    
    if success:
        logger.info(f"Successfully loaded models from services: {_loaded_services}")
        logger.info(f"Total tables in metadata: {len(metadata.tables)}")
        
        # Log all tables for debugging
        for table_name in metadata.tables.keys():
            logger.debug(f"  - {table_name}")
    else:
        logger.warning("Some services failed to load")
    
    return success

def get_loaded_services() -> List[str]:
    """Get list of services that were successfully loaded."""
    return _loaded_services.copy()

def get_table_names() -> List[str]:
    """Get list of all table names in the metadata."""
    if metadata is None:
        return []
    return list(metadata.tables.keys())

# Auto-load models when module is imported
load_all_models()

# Export the metadata for use by Alembic and other tools
__all__ = ['metadata', 'load_all_models', 'get_loaded_services', 'get_table_names'] 