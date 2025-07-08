import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from journal_service.journal_service.app.config import get_settings

logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=False,  # Set to True for SQL logging
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={
        "options": "-c search_path=journal"
    } if settings.environment != "development" else {}
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()


async def init_db():
    """Initialize database tables."""
    try:
        async with engine.begin() as conn:
            # Import models here to ensure they're registered
            from journal_service.journal_service.app.db.models.journal import JournalEntry
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
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