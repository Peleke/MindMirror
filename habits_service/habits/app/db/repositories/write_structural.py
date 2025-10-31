from __future__ import annotations

import uuid
from typing import Iterable, List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from habits.app.db.tables import (
    ProgramStepTemplate,
    LessonSegment,
    StepDailyPlan,
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
            habit_id = s.get("habit_template_id")
            obj = ProgramStepTemplate(
                program_template_id=pid,
                sequence_index=s["sequence_index"],
                habit_template_id=(uuid.UUID(str(habit_id)) if habit_id else None),
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
            # Remove daily plans for the step (FK to program_step_templates)
            await self.session.execute(delete(StepDailyPlan).where(StepDailyPlan.program_step_template_id == st.id))
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


class LessonSegmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def bulk_upsert(self, segments: Iterable[dict]) -> list[LessonSegment]:
        created: list[LessonSegment] = []
        for seg in segments:
            obj = LessonSegment(
                id=uuid.UUID(seg["id"]) if seg.get("id") else uuid.uuid4(),
                lesson_template_id=uuid.UUID(str(seg["lesson_template_id"])),
                day_index_within_step=seg.get("day_index_within_step"),
                title=seg["title"],
                subtitle=seg.get("subtitle"),
                markdown_content=seg["markdown_content"],
                summary=seg.get("summary"),
                metadata_json=seg.get("metadata_json"),
            )
            self.session.add(obj)
            created.append(obj)
        await self.session.flush()
        return created

    async def delete_by_lesson(self, lesson_template_id: str) -> int:
        lid = uuid.UUID(str(lesson_template_id))
        res = await self.session.execute(delete(LessonSegment).where(LessonSegment.lesson_template_id == lid))
        return res.rowcount or 0


class StepDailyPlanRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def bulk_upsert(self, *, step_id: str, plans: Iterable[dict]) -> list[StepDailyPlan]:
        created: list[StepDailyPlan] = []
        sid = uuid.UUID(str(step_id))
        # Delete existing plans for idempotency
        await self.session.execute(delete(StepDailyPlan).where(StepDailyPlan.program_step_template_id == sid))
        for p in plans:
            obj = StepDailyPlan(
                program_step_template_id=sid,
                day_index=int(p["day_index"]),
                habit_variant_text=p.get("habit_variant_text"),
                journal_prompt_text=p.get("journal_prompt_text"),
                lesson_segment_id=uuid.UUID(str(p["lesson_segment_id"])) if p.get("lesson_segment_id") else None,
                metadata_json=p.get("metadata_json"),
            )
            self.session.add(obj)
            created.append(obj)
        await self.session.flush()
        return created


