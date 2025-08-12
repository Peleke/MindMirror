from __future__ import annotations

from datetime import date
import pytest

from habits_service.habits_service.app.db.repositories.write import (
    HabitTemplateRepository,
    ProgramTemplateRepository,
    LessonTemplateRepository,
)
from habits_service.habits_service.app.db.repositories.write_structural import (
    ProgramStepTemplateRepository,
    StepLessonTemplateRepository,
    UserProgramAssignmentRepository,
)
from habits_service.habits_service.app.db.repositories.read import HabitsReadRepository
from habits_service.habits_service.app.services.planner import plan_daily_tasks


@pytest.mark.asyncio
async def test_structural_repos_flow(db_session):
    # Create base templates
    hrepo = HabitTemplateRepository(db_session)
    prepo = ProgramTemplateRepository(db_session)
    srepo = ProgramStepTemplateRepository(db_session)
    lrepo = StepLessonTemplateRepository(db_session)
    arepo = UserProgramAssignmentRepository(db_session)
    ltrepo = LessonTemplateRepository(db_session)

    habit = await hrepo.create(slug="hydrate", title="Hydrate")
    program = await prepo.create(slug="water-week", title="Water Week")
    await db_session.commit()

    # Steps
    steps = await srepo.bulk_create(
        program_template_id=str(program.id),
        steps=[
            {
                "sequence_index": 0,
                "habit_template_id": str(habit.id),
                "duration_days": 7,
            }
        ],
    )
    await db_session.commit()
    assert steps and steps[0].program_template_id == program.id

    # Step lessons: create two lessons and associate on different days
    lesson1 = await ltrepo.create(slug="why-water", title="Why water?", markdown_content="# md1", summary="w1")
    lesson2 = await ltrepo.create(slug="how-much", title="How much?", markdown_content="# md2", summary="w2")
    await db_session.commit()

    created_step_lessons = await lrepo.bulk_create(
        step_id=str(steps[0].id),
        lessons=[
            {"day_index": 0, "lesson_template_id": str(lesson1.id)},
            {"day_index": 2, "lesson_template_id": str(lesson2.id)},
        ],
    )
    await db_session.commit()
    assert len(created_step_lessons) == 2

    # Verify via read repo
    rrepo = HabitsReadRepository(db_session)
    d0 = await rrepo.get_step_lessons_for_day(str(steps[0].id), 0)
    d2 = await rrepo.get_step_lessons_for_day(str(steps[0].id), 2)
    assert len(d0) == 1 and str(d0[0].lesson_template_id) == str(lesson1.id)
    assert len(d2) == 1 and str(d2[0].lesson_template_id) == str(lesson2.id)

    # Assignment
    assignment = await arepo.create(user_id="u-test", program_template_id=str(program.id), start_date=date(2025, 8, 1))
    await db_session.commit()
    assert assignment.id is not None and assignment.status == "active"

    # Keep active to allow planner to emit tasks (paused assignment would be skipped in active-only calls)

    # Planner integration sanity: on day 3 (offset 2), lesson2 should appear
    tasks = await plan_daily_tasks("u-test", date(2025, 8, 3), rrepo)
    lesson_titles = [getattr(t, "title", None) for t in tasks]
    assert "How much?" in lesson_titles
