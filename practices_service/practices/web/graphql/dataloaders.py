import asyncio
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from practices.domain.models import DomainPractice
from practices.repository.repositories import PracticeRepository


class PracticeLoader:
    """
    Data loader for efficient loading of Practice entities in GraphQL resolvers.
    Uses a batching approach to reduce N+1 query problems.
    """

    def __init__(self, session_factory):
        self.session_factory = session_factory
        self._batch_load_practice_cache: Dict[UUID, DomainPractice] = {}
        self._batch_load_futures: Dict[UUID, asyncio.Future] = {}
        self._pending_practice_ids: List[UUID] = []

    async def load_practice(self, practice_id: UUID) -> Optional[DomainPractice]:
        """
        Load a practice by ID, using batch loading for efficiency.
        Returns a Future that will be resolved with the practice once loaded.
        """
        # If already loaded, return from cache
        if practice_id in self._batch_load_practice_cache:
            return self._batch_load_practice_cache[practice_id]

        # If a load is already pending for this ID, return the existing future
        if practice_id in self._batch_load_futures:
            return await self._batch_load_futures[practice_id]

        # Create a future for this practice ID
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        self._batch_load_futures[practice_id] = future

        # Add to pending IDs
        self._pending_practice_ids.append(practice_id)

        # Schedule batch load if this is the first ID in the batch
        if len(self._pending_practice_ids) == 1:
            loop.create_task(self._schedule_batch_load())

        # Return the future, which will be resolved later
        return await future

    async def _schedule_batch_load(self):
        """
        Wait a small amount of time to collect more IDs before executing the batch load.
        This allows multiple resolvers to request practices before we query the database.
        """
        await asyncio.sleep(0.01)  # Small delay to collect more IDs

        # Copy pending IDs and clear the list
        practice_ids = self._pending_practice_ids.copy()
        self._pending_practice_ids = []

        if not practice_ids:
            return

        try:
            # Load practices in batch
            practices = await self._batch_load_practices(practice_ids)

            # Update cache and resolve futures
            for practice in practices:
                practice_id = practice.id_
                self._batch_load_practice_cache[practice_id] = practice

                if practice_id in self._batch_load_futures:
                    future = self._batch_load_futures[practice_id]
                    if not future.done():
                        future.set_result(practice)
                    del self._batch_load_futures[practice_id]

            # Set None for missing practices
            for practice_id in practice_ids:
                if practice_id not in self._batch_load_practice_cache and practice_id in self._batch_load_futures:
                    future = self._batch_load_futures[practice_id]
                    if not future.done():
                        future.set_result(None)
                    del self._batch_load_futures[practice_id]

        except Exception as e:
            # Set exception for all pending futures
            for practice_id in practice_ids:
                if practice_id in self._batch_load_futures:
                    future = self._batch_load_futures[practice_id]
                    if not future.done():
                        future.set_exception(e)
                    del self._batch_load_futures[practice_id]

    async def _batch_load_practices(self, practice_ids: List[UUID]) -> List[DomainPractice]:
        """
        Load multiple practices by ID in a single database query.
        """
        async with self.session_factory() as session:
            practice_repo = PracticeRepository(session)
            return await practice_repo.get_practices_by_ids(practice_ids)

    def clear_cache(self):
        """
        Clear the loader cache.
        """
        self._batch_load_practice_cache.clear()
