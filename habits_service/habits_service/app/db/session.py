from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from habits_service.habits_service.app.config import get_settings
import uuid


settings = get_settings()
connect_args = {
    "statement_cache_size": 0,
    "prepared_statement_cache_size": 0,
    "prepared_statement_name_func": lambda: f"__asyncpg_{uuid.uuid4()}__",
}
engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_recycle=settings.db_pool_recycle,
    pool_pre_ping=settings.db_pool_pre_ping,
    pool_timeout=settings.db_pool_timeout,
    connect_args=connect_args,
)
async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
