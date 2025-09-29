from __future__ import annotations

from typing import AsyncGenerator
import os
import ssl

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

from ..web.config import Config


class Base(DeclarativeBase):
    metadata = MetaData(schema="movements")


# SSL/connect args for cloud DBs
connect_args: dict = {"timeout": 30}
try:
    url_lc = (Config.DATABASE_URL or "").lower()
    if "localhost" not in url_lc and "127.0.0.1" not in url_lc:
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        connect_args["ssl"] = ssl_ctx  # type: ignore[assignment]
except Exception:
    pass

_engine = create_async_engine(
    Config.DATABASE_URL,
    pool_pre_ping=True,
    future=True,
    pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
    pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "10")),
    pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "1800")),
    connect_args=connect_args,
)
_async_session_factory = async_sessionmaker(bind=_engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with _async_session_factory() as session:
        yield session


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return _async_session_factory 