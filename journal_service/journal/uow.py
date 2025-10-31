from __future__ import annotations
import abc
from typing import Self, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from .app.db.database import async_session_maker
from .app.db.repositories.journal import JournalRepository


class IUnitOfWork(abc.ABC):
    session: AsyncSession
    journal_repository: JournalRepository

    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()

    @abc.abstractmethod
    async def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def rollback(self):
        raise NotImplementedError


class UnitOfWork(IUnitOfWork):
    """
    Unit of Work pattern implementation for the journal service.
    Manages database transactions and repository access.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self._journal_repository = None

    @property
    def journal_repository(self) -> JournalRepository:
        """Lazy-loaded journal repository."""
        if self._journal_repository is None:
            self._journal_repository = JournalRepository(self.session)
        return self._journal_repository

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()


async def get_uow() -> AsyncGenerator[UnitOfWork, None]:
    async with async_session_maker() as session:
        uow = UnitOfWork(session)
        try:
            yield uow
        finally:
            await uow.rollback()
