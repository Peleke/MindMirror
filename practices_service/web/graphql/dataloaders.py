import asyncio
import uuid
from typing import Any, Callable, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload  # For eager loading if needed
from strawberry.dataloader import DataLoader

from ..repository.models.practice import PracticeModel

# Define a type for an async session factory
AsyncSessionFactory = Callable[
    [], AsyncSession
]  # More precisely, this is what async_sessionmaker returns for its instances
# Or, if you pass the async_sessionmaker itself: AsyncSessionFactory = async_sessionmaker[AsyncSession]


class PracticeLoader(DataLoader[uuid.UUID, Optional[PracticeModel]]):
    # Loader will use the provided factory to create sessions for its batch operations.
    def __init__(
        self, session_factory: async_sessionmaker[AsyncSession], loop: Optional[asyncio.AbstractEventLoop] = None
    ):
        super().__init__(load_fn=None, loop=loop)
        self.session_factory: async_sessionmaker[AsyncSession] = session_factory

    async def batch_load_fn(self, keys: List[uuid.UUID]) -> List[Optional[PracticeModel]]:
        """
        Batch loads PracticeModels for the given list of practice IDs.
        Ensures the returned list of practices is in the same order as the input keys.
        """
        if not keys:
            return []

        # print(f"PracticeLoader: Batch loading practices for IDs: {keys}") # For debugging

        async with self.session_factory() as session:  # Create a new session for this batch
            stmt = (
                select(PracticeModel).where(PracticeModel.id_.in_(keys))
                # .options(selectinload(PracticeModel.prescriptions)...) # Optional eager loading
            )
            result = await session.execute(stmt)
            practices_db = result.scalars().all()

        practices_by_id = {p.id: p for p in practices_db}
        # print(f"PracticeLoader: Found practices: {practices_by_id.keys()}") # For debugging

        return [practices_by_id.get(key) for key in keys]
