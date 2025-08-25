from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

from ..web.config import Config


class Base(DeclarativeBase):
    metadata = MetaData(schema="movements")


_engine = create_async_engine(Config.DATABASE_URL, pool_pre_ping=True, future=True)
_async_session_factory = async_sessionmaker(bind=_engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with _async_session_factory() as session:
        yield session


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return _async_session_factory 