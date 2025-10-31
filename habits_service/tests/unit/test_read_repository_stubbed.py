from __future__ import annotations

import uuid
import pytest

from habits_service.habits_service.app.db.repositories.read import HabitsReadRepository


class DummySession:
    """A minimal AsyncSession-like stub for shape checking.
    We won't execute here; integration tests will cover real DB.
    """

    async def execute(self, *_args, **_kwargs):
        raise NotImplementedError


@pytest.mark.asyncio
async def test_repository_shape_instantiation():
    repo = HabitsReadRepository(DummySession())
    assert repo is not None


