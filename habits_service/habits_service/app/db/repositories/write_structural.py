from __future__ import annotations

import uuid
from typing import Iterable, List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from habits_service.habits_service.app.db.tables import (
    ProgramStepTemplate,
    StepLessonTemplate,
    UserProgramAssignment,
)


class ProgramStepTemplateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def bulk_create(self, *, program_template_id: str, steps: Iterable[dict]) -> List[ProgramStepTemplate]:
        created: List[ProgramStepTemplate] = []
        pid = uuid.UUID(str(program_template_id))
        for s in steps:
            obj = ProgramStepTemplate(
                program_template_id=pid,
                sequence_index=s["sequence_index"],
                habit_template_id=uuid.UUID(str(s["habit_template_id"])),
                duration_days=s["duration_days"],
            )
            self.session.add(obj)
            created.append(obj)
        await self.session.flush()
        return created

    async def delete_by_program(self, program_template_id: str) -> int:
        pid = uuid.UUID(str(program_template_id))
        # Delete step-lesson mappings first to avoid FK violations, then steps
        res_steps = await self.session.execute(select(ProgramStepTemplate).where(ProgramStepTemplate.program_template_id == pid))
        steps = list(res_steps.scalars().all())
        deleted = 0
        for st in steps:
            await self.session.execute(delete(StepLessonTemplate).where(StepLessonTemplate.program_step_template_id == st.id))
            deleted += 1
        await self.session.execute(delete(ProgramStepTemplate).where(ProgramStepTemplate.program_template_id == pid))
        return deleted


class StepLessonTemplateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def bulk_create(self, *, step_id: str, lessons: Iterable[dict]) -> List[StepLessonTemplate]:
        created: List[StepLessonTemplate] = []
        sid = uuid.UUID(str(step_id))
        for l in lessons:
            obj = StepLessonTemplate(
                program_step_template_id=sid,
                day_index=l["day_index"],
                lesson_template_id=uuid.UUID(str(l["lesson_template_id"])),
            )
            self.session.add(obj)
            created.append(obj)
        await self.session.flush()
        return created

    async def delete_by_step(self, step_id: str) -> int:
        sid = uuid.UUID(str(step_id))
        res = await self.session.execute(delete(StepLessonTemplate).where(StepLessonTemplate.program_step_template_id == sid))
        return res.rowcount or 0


class UserProgramAssignmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, *, user_id: str, program_template_id: str, start_date) -> UserProgramAssignment:
        obj = UserProgramAssignment(
            user_id=user_id,
            program_template_id=uuid.UUID(str(program_template_id)),
            start_date=start_date,
            status="active",
        )
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def set_status(self, id: str, status: str) -> Optional[UserProgramAssignment]:
        aid = uuid.UUID(str(id))
        res = await self.session.execute(select(UserProgramAssignment).where(UserProgramAssignment.id == aid))
        obj = res.scalars().first()
        if not obj:
            return None
        obj.status = status
        await self.session.flush()
        return obj


