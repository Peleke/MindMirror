from __future__ import annotations

import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from habits_service.habits_service.app.db.repositories import HabitsReadRepository


@pytest.mark.asyncio
async def test_repo_get_lesson_template_by_id(db_session: AsyncSession, test_app):
    # Create lesson via GQL so ORM models are present
    from httpx import AsyncClient, ASGITransport
    transport = ASGITransport(app=test_app)
    client = AsyncClient(transport=transport, base_url="http://test")
    user_id = str(uuid.uuid4())

    slug = f"u-lesson-{uuid.uuid4().hex[:8]}"
    m = {
        "query": "mutation($i: LessonTemplateInput!){ createLessonTemplate(input:$i){ id slug title } }",
        "variables": {"i": {"slug": slug, "title": "Repo Lesson", "markdownContent": "# md"}},
    }
    r = await client.post("/graphql", json=m, headers={"x-internal-id": user_id})
    lid = r.json()["data"]["createLessonTemplate"]["id"]

    repo = HabitsReadRepository(db_session)
    row = await repo.get_lesson_template_by_id(lid)
    assert row is not None
    assert str(row.id) == lid
    assert row.slug == slug

    await client.aclose()


