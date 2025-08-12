from __future__ import annotations

import asyncio
import uuid
import pytest

from habits_service.habits_service.app.db.session import async_session_maker, engine
from habits_service.habits_service.app.db.models import Base
from habits_service.habits_service.app.db.repositories.write import (
    HabitTemplateRepository,
    LessonTemplateRepository,
    ProgramTemplateRepository,
)


@pytest.mark.asyncio
async def test_template_write_repos_crud():
    # Create tables if not present (dev convenience)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        hrepo = HabitTemplateRepository(session)
        lrepo = LessonTemplateRepository(session)
        prepo = ProgramTemplateRepository(session)

        habit_slug = f"eat-slowly-{uuid.uuid4().hex[:8]}"
        lesson_slug = f"slow-eating-1-{uuid.uuid4().hex[:8]}"
        program_slug = f"eating-7x7-{uuid.uuid4().hex[:8]}"

        habit = await hrepo.create(slug=habit_slug, title="Eat Slowly")
        lesson = await lrepo.create(slug=lesson_slug, title="Why slow?", markdown_content="# md")
        program = await prepo.create(slug=program_slug, title="Eating 7x7")

        await session.commit()

        assert habit.id is not None
        assert lesson.id is not None
        assert program.id is not None

        # get_by_slug
        found_habit = await hrepo.get_by_slug(habit_slug)
        assert found_habit and found_habit.title == "Eat Slowly"

        # update
        await hrepo.update(str(habit.id), title="Eat Slowly v2")
        await session.commit()
        again = await hrepo.get_by_id(str(habit.id))
        assert again and again.title == "Eat Slowly v2"


