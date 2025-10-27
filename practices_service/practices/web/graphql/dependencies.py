from typing import Any, AsyncGenerator, Dict, cast
from uuid import UUID

from fastapi import Depends
from shared.auth import CurrentUser, get_current_user
from shared.data_models import UserRole
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.websockets import WebSocket
from strawberry.fastapi import BaseContext

from practices.repository.database import async_session_maker
from practices.repository.uow import UnitOfWork


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency to provide a database session."""
    session = async_session_maker()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_uow(session: AsyncSession = Depends(get_db_session)) -> UnitOfWork:
    """FastAPI dependency to provide a Unit of Work."""
    return UnitOfWork(session)


class CustomContext(BaseContext):
    def __init__(
        self,
        uow: UnitOfWork = Depends(get_uow),
        current_user: CurrentUser | None = Depends(get_current_user),
    ):
        self.uow = uow
        self.current_user = current_user

    def __getitem__(self, key: str) -> Any:
        """Allows context to be accessed like a dictionary for backward compatibility."""
        return getattr(self, key)

    def get(self, key: str, default: Any = None) -> Any:
        """Allows context to be accessed like a dictionary for backward compatibility."""
        return getattr(self, key, default)


async def get_context(
    custom_context: CustomContext = Depends(CustomContext),
) -> CustomContext:
    return custom_context
