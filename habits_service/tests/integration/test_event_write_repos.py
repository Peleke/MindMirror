from __future__ import annotations

from datetime import date
import pytest

from habits_service.habits_service.app.db.repositories.write import (
    HabitTemplateRepository,
    LessonTemplateRepository,
)
from habits_service.habits_service.app.db.repositories.write_events import (
    HabitEventRepository,
    LessonEventRepository,
)


@pytest.mark.asyncio
async def test_habit_and_lesson_event_upserts(db_session):
    ht_repo = HabitTemplateRepository(db_session)
    lt_repo = LessonTemplateRepository(db_session)
    he_repo = HabitEventRepository(db_session)
    le_repo = LessonEventRepository(db_session)

    import uuid
    habit = await ht_repo.create(slug=f"event-habit-{uuid.uuid4().hex[:8]}", title="Event Habit")
    lesson = await lt_repo.create(slug="event-lesson", title="Event Lesson", markdown_content="# md")
    await db_session.commit()

    # Habit event upsert
    e1 = await he_repo.upsert(user_id="u1", habit_template_id=str(habit.id), on_date=date(2025, 8, 1), response="no")
    await db_session.commit()
    assert e1 and e1.response == "no"
    e2 = await he_repo.upsert(user_id="u1", habit_template_id=str(habit.id), on_date=date(2025, 8, 1), response="yes")
    await db_session.commit()
    assert e2.response == "yes"

    # Lesson event upsert (opened -> completed)
    l1 = await le_repo.upsert(user_id="u1", lesson_template_id=str(lesson.id), on_date=date(2025, 8, 1), event_type="opened")
    await db_session.commit()
    assert l1.event_type == "opened"
    l2 = await le_repo.upsert(user_id="u1", lesson_template_id=str(lesson.id), on_date=date(2025, 8, 1), event_type="completed")
    await db_session.commit()
    assert l2.event_type == "completed"


