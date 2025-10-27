import logging
from types import TracebackType
from typing import AsyncGenerator, Optional, Type

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker as AsyncSessionMakerType

# Import the existing async_session_maker from database.py
# This UoW will use the application's centrally configured engine and session factory.
from practices.repository.database import (
    async_session_maker as global_async_session_maker,
)

logger = logging.getLogger(__name__)


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        """Initializes the Unit of Work with an externally managed session."""
        self._session = session
        logger.debug(f"UnitOfWork initialized with provided session: {self._session}.")

    @property
    def session(self) -> AsyncSession:
        return self._session

    async def __aenter__(self) -> "UnitOfWork":
        """Enters the context for the unit of work. The session is already active."""
        logger.debug(f"Session {self._session} entering UoW context.")
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[Exception]],
        exc_val: Optional[Exception],
        exc_tb: Optional[TracebackType],
    ) -> None:
        if self._session is None:
            logger.warning("__aexit__ called on UoW without an active session.")
            return

        try:
            if exc_type is not None:
                logger.warning(f"Exception occurred in UoW block: {exc_val}, rolling back session {self._session}.")
                await self.rollback()
            else:
                logger.debug(f"UoW block exited successfully for session {self._session}. Committing.")
                await self.commit()
        finally:
            logger.debug(f"Closing session {self._session} in __aexit__.")
            await self.close()
            self._session = None

    async def commit(self) -> None:
        if self._session and self._session.is_active:
            logger.debug(f"Committing session {self._session}.")
            await self._session.commit()
        else:
            logger.warning(f"Attempted to commit on an inactive or None session: {self._session}")

    async def rollback(self) -> None:
        if self._session and self._session.is_active:
            logger.debug(f"Rolling back session {self._session}.")
            await self._session.rollback()
        else:
            logger.warning(f"Attempted to rollback on an inactive or None session: {self._session}")

    async def close(self) -> None:
        if self._session and self._session.is_active:
            logger.debug(f"Closing session {self._session} from UoW.close().")
            await self._session.close()
        else:
            logger.debug(f"Session {self._session} already closed or None in UoW.close().")


async def get_uow() -> AsyncGenerator[UnitOfWork, None]:
    """
    Dependency to provide a UoW that manages its own session lifecycle.
    """
    session = global_async_session_maker()
    uow = UnitOfWork(session)
    try:
        yield uow
        await uow.commit()
    except Exception:
        await uow.rollback()
        raise
    finally:
        await session.close()


__all__ = ["UnitOfWork", "get_uow"]
