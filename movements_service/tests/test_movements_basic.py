import asyncio
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from movements.repository.database import get_session_factory, Base
from movements.repository.movements_repo import MovementsRepoPg
from uuid import uuid4


@pytest.mark.asyncio
async def test_create_get_search_basic():
    session_factory = get_session_factory()

    # Ensure schema/tables exist
    async with session_factory() as s:  # type: AsyncSession
        await s.execute(text('CREATE SCHEMA IF NOT EXISTS "movements"'))
        await s.commit()
    async with session_factory().bind.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    created_id = None
    # Create
    async with session_factory() as s:
        repo = MovementsRepoPg(s)
        suffix = uuid4().hex[:8]
        name = f"Bodyweight Glute Bridge {suffix}"
        slug = f"bodyweight-glute-bridge-{suffix}"
        created = await repo.create(user_id="test-user", data={
            "name": name,
            "slug": slug,
            "bodyRegion": "Lower Body",
            "difficulty": "Beginner",
            "primeMoverMuscle": "Gluteus Maximus",
            "secondaryMuscles": ["Biceps Femoris", "Erector Spinae"],
            "primaryEquipment": ["Bodyweight"],
            "movementPatterns": ["Hip Extension"],
            "planesOfMotion": ["Sagittal Plane"],
        })
        assert created["id_"]
        created_id = created["id_"]
        # Ensure visibility to subsequent sessions
        await s.commit()

    try:
        # Get
        async with session_factory() as s:
            repo = MovementsRepoPg(s)
            fetched = await repo.get(created_id)
            assert fetched is not None
            assert fetched["name"].startswith("Bodyweight Glute Bridge")
            assert "Hip Extension" in fetched["movementPatterns"]

        # Search
        async with session_factory() as s:
            repo = MovementsRepoPg(s)
            results = await repo.search(searchTerm="Glute", bodyRegion="Lower Body", pattern="Hip Extension")
            assert any(r["id_"] == created_id for r in results)
    finally:
        # Cleanup created row to keep tests idempotent
        if created_id:
            async with session_factory() as s:
                repo = MovementsRepoPg(s)
                try:
                    await repo.delete(created_id)
                    await s.commit()
                except Exception:
                    pass 