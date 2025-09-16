import pytest
from sqlalchemy import text
from movements.repository.database import get_session_factory, Base
from movements.repository.movements_repo import MovementsRepoPg


@pytest.mark.asyncio
async def test_idempotent_import_path_via_repo_helper():
    session_factory = get_session_factory()
    async with session_factory() as s:
        await s.execute(text('CREATE SCHEMA IF NOT EXISTS "movements"'))
        await s.commit()
    async with session_factory().bind.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as s:
        repo = MovementsRepoPg(s)
        # Simulate two create calls with same external tuple
        first = await repo.create(user_id=None, data={"name": "X", "slug": "x", "source": "exercise-db", "externalId": "exr_same"})
        await s.commit()
    async with session_factory() as s:
        repo = MovementsRepoPg(s)
        found = await repo.get_by_external("exercise-db", "exr_same")
        assert found is not None
        assert found["id_"] == first["id_"] 