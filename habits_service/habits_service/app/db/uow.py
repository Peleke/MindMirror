from typing import AsyncGenerator, Optional
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from habits_service.habits_service.app.db.session import async_session_maker


logger = logging.getLogger(__name__)


class UnitOfWork:
    def __init__(self, session_factory: Optional[callable] = None):
        self.session_factory = session_factory or async_session_maker
        self._session: Optional[AsyncSession] = None

    async def __aenter__(self) -> "UnitOfWork":
        self._session = self.session_factory()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        assert self._session is not None
        if exc:
            await self._session.rollback()
        else:
            await self._session.commit()
        await self._session.close()
        self._session = None

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("UnitOfWork session accessed outside of context")
        return self._session


async def get_uow() -> AsyncGenerator[UnitOfWork, None]:
    async with UnitOfWork() as uow:
        yield uow


