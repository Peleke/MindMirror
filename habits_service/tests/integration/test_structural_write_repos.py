from __future__ import annotations

from datetime import date
import pytest

from habits_service.habits_service.app.db.repositories.write import (
    HabitTemplateRepository,
    ProgramTemplateRepository,
)
from habits_service.habits_service.app.db.repositories.write_structural import (
    ProgramStepTemplateRepository,
    StepLessonTemplateRepository,
    UserProgramAssignmentRepository,
)


@pytest.mark.asyncio
async def test_structural_repos_flow(db_session):
    # Create base templates
    hrepo = HabitTemplateRepository(db_session)
    prepo = ProgramTemplateRepository(db_session)
    srepo = ProgramStepTemplateRepository(db_session)
    lrepo = StepLessonTemplateRepository(db_session)
    arepo = UserProgramAssignmentRepository(db_session)

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

    # Step lessons: none for now (we can add after we have a lesson template wired)
    deleted = await lrepo.delete_by_step(str(steps[0].id))
    assert deleted == 0

    # Assignment
    assignment = await arepo.create(user_id="u-test", program_template_id=str(program.id), start_date=date(2025, 8, 1))
    await db_session.commit()
    assert assignment.id is not None and assignment.status == "active"

    # Pause
    paused = await arepo.set_status(str(assignment.id), "paused")
    await db_session.commit()
    assert paused and paused.status == "paused"
