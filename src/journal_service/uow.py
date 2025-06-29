from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from journal_service.database import async_session_maker
from journal_service.repository import JournalRepository


class UnitOfWork:
    """
    Unit of Work pattern implementation for the journal service.
    Manages database transactions and repository access.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self._journal_repository = None

    @property
    def journal_repository(self) -> JournalRepository:
        """Lazy-loaded journal repository."""
        if self._journal_repository is None:
            self._journal_repository = JournalRepository(self.session)
        return self._journal_repository

    async def commit(self):
        """Commit the current transaction."""
        await self.session.commit()

    async def rollback(self):
        """Rollback the current transaction."""
        await self.session.rollback()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()


async def get_uow() -> AsyncGenerator[UnitOfWork, None]:
    """
    Dependency injection function to provide UnitOfWork instances.
    Creates a database session and returns a UnitOfWork instance.
    """
    async with async_session_maker() as session:
        uow = UnitOfWork(session)
        try:
            yield uow
        finally:
            await session.close()
