from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from habits_service.habits_service.app.config import get_settings


settings = get_settings()
engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
    pool_size=5,
    max_overflow=0,
    pool_recycle=1800,
    pool_pre_ping=True,
)
async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


