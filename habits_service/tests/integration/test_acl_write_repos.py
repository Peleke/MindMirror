from __future__ import annotations

import pytest

from habits_service.habits_service.app.db.repositories.write import HabitTemplateRepository
from habits_service.habits_service.app.db.repositories.write_acl import (
    TemplateAccessRepository,
    TemplateProvenanceRepository,
)


@pytest.mark.asyncio
async def test_acl_and_provenance(db_session):
    hrepo = HabitTemplateRepository(db_session)
    aclrepo = TemplateAccessRepository(db_session)
    provrepo = TemplateProvenanceRepository(db_session)

    habit = await hrepo.create(slug="share-me", title="Share Me")
    await db_session.commit()

    # Upsert public view and owner
    pub = await aclrepo.upsert_public_view(kind="habit", template_id=str(habit.id))
    own = await aclrepo.grant(kind="habit", template_id=str(habit.id), permission="owner", user_id="u1")
    await db_session.commit()
    assert pub and own

    # List accessible for user u2 should include via public
    ids = await aclrepo.list_accessible_template_ids(kind="habit", user_id="u2")
    assert str(habit.id) in ids

    # Provenance
    p = await provrepo.upsert(kind="habit", template_id=str(habit.id), origin="user", origin_user_id="u1")
    await db_session.commit()
    assert p.origin == "user" and p.origin_user_id == "u1"


