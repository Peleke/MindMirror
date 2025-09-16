import pytest
from sqlalchemy import text
from movements.repository.database import get_session_factory, Base
from movements.repository.movements_repo import MovementsRepoPg
from uuid import uuid4


@pytest.mark.asyncio
async def test_idempotent_import_path_via_repo_helper():
    session_factory = get_session_factory()
    async with session_factory() as s:
        await s.execute(text('CREATE SCHEMA IF NOT EXISTS "movements"'))
        await s.commit()
    async with session_factory().bind.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    created_id = None
    external = f"exr_{uuid4().hex[:10]}"
    # Create
    async with session_factory() as s:
        repo = MovementsRepoPg(s)
        suffix = uuid4().hex[:8]
        name = f"X {suffix}"
        slug = f"x-{suffix}"
        first = await repo.create(user_id=None, data={"name": name, "slug": slug, "source": "exercise-db", "externalId": external})
        created_id = first["id_"]
        await s.commit()
    try:
        async with session_factory() as s:
            repo = MovementsRepoPg(s)
            found = await repo.get_by_external("exercise-db", external)
            assert found is not None
            assert found["id_"] == created_id
    finally:
        if created_id:
            async with session_factory() as s:
                repo = MovementsRepoPg(s)
                try:
                    await repo.delete(created_id)
                    await s.commit()
                except Exception:
                    pass 