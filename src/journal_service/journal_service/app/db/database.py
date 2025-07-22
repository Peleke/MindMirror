import logging
import os
import ssl
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from journal_service.journal_service.app.config import get_settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Get settings
settings = get_settings()

# Initialize connect_args
connect_args = {}

# --- Environment-Specific SSL Configuration ---
# Only apply SSL settings for non-local environments (like production).
# Your local Docker postgres does not use SSL.
if settings.environment != "local":
    # In a real production setup, you would want to use your cloud provider's CA cert
    # and not disable hostname checking or verification.
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connect_args["ssl"] = ssl_context

# Create async engine
engine = create_async_engine(
    str(settings.database_url), # Ensure URL is a string
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args=connect_args,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()

# Set the schema for all tables
Base.metadata.schema = "journal"


async def init_db():
    """Initialize database tables."""
    try:
        async with engine.begin() as conn:
            # Create the journal schema if it doesn't exist
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS journal"))
            
            # Import models here to ensure they're registered
            from journal_service.journal_service.app.db.models.journal import JournalEntry
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        raise


async def get_session() -> AsyncSession:
    """Get database session."""
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_db():
    """Close database connections."""
    await engine.dispose()
    logger.info("Database connections closed") 