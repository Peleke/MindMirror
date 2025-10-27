import logging
from types import TracebackType
from typing import AsyncGenerator, Optional, Type

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker as AsyncSessionMakerType

from users.repository.database import (
    async_session_factory as global_async_session_factory,  # Ensure this is the correct name
)

logger = logging.getLogger(__name__)


class UnitOfWork:
    def __init__(self, session_factory: Optional[AsyncSessionMakerType] = None):
        self.session_factory = session_factory or global_async_session_factory
        if not self.session_factory:
            raise RuntimeError("Session factory not configured. Ensure database.py has async_session_factory.")
        self._session: Optional[AsyncSession] = None
        logger.debug(f"UnitOfWork initialized with session factory: {self.session_factory}.")

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            logger.error("Session accessed before __aenter__ or after __aexit__.")
            raise RuntimeError("Session is not available. Ensure 'async with uow:' is used.")
        return self._session

    async def __aenter__(self) -> "UnitOfWork":
        self._session = self.session_factory()
        logger.debug(f"Session {self._session} created and __aenter__ called.")
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],  # Changed to BaseException for broader compatibility
        exc_val: Optional[BaseException],
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
                await self.commit()  # Commit if no exceptions
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
    """Provides a UnitOfWork instance as a FastAPI dependency."""
    # Ensure global_async_session_factory is initialized before get_uow is first called.
    # This typically happens during app startup (e.g., in lifespan or by importing database.py).
    if global_async_session_factory is None:
        logger.error("Global session factory not initialized when get_uow was called.")
        # Depending on strictness, could raise an error or try to initialize.
        # For now, relying on app startup to call init_db().
        raise RuntimeError("Global session factory not initialized.")

    uow = UnitOfWork()
    logger.debug(f"UoW instance {uow} created by get_uow.")
    try:
        yield uow
    finally:
        if uow._session:
            logger.debug(f"Ensuring UoW {uow} session {uow._session} is closed by get_uow finally block.")
            await uow.close()
        logger.debug(f"UoW instance {uow} cleaned up by get_uow.")


__all__ = ["UnitOfWork", "get_uow"]
