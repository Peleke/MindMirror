from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from meals.repository.uow import UnitOfWork


# Note: get_db_session might not be strictly necessary if UoW handles session creation/closing directly.
# However, keeping it for structural similarity if direct session access is ever needed outside UoW.
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency to provide a database session via UoW."""
    uow = UnitOfWork()  # New UoW for each request
    async with uow:  # Enters UoW context, session is created
        yield uow.session  # Yields the session from the active UoW
    # UoW context exit handles commit/rollback and session closing


async def get_uow() -> UnitOfWork:
    """FastAPI dependency to provide a UnitOfWork."""
    return UnitOfWork()
