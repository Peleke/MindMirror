from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from sqlalchemy import Select, and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from habits.app.db.tables import (
    HabitEvent,
    HabitTemplate,
    LessonEvent,
    LessonTemplate,
    LessonSegment,
    ProgramStepTemplate,
    ProgramTemplate,
    StepDailyPlan,
    StepLessonTemplate,
    UserProgramAssignment,
)


@dataclass
class HabitStepDay:
    habit_template: HabitTemplate
    step: ProgramStepTemplate
    day_index: int


class HabitsReadRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active_assignments(self, user_id: str) -> List[UserProgramAssignment]:
        stmt: Select = select(UserProgramAssignment).where(
            and_(UserProgramAssignment.user_id == user_id, UserProgramAssignment.status == "active")
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_program_steps(self, program_template_id: str) -> List[ProgramStepTemplate]:
        stmt: Select = (
            select(ProgramStepTemplate)
            .where(ProgramStepTemplate.program_template_id == program_template_id)
            .order_by(ProgramStepTemplate.sequence_index.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_habit_template(self, habit_template_id: str) -> Optional[HabitTemplate]:
        stmt: Select = select(HabitTemplate).where(HabitTemplate.id == habit_template_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_step_lessons_for_day(self, step_id: str, day_index: int) -> List[StepLessonTemplate]:
        stmt: Select = select(StepLessonTemplate).where(
            and_(
                StepLessonTemplate.program_step_template_id == step_id,
                StepLessonTemplate.day_index == day_index,
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_lesson_templates(self, lesson_ids: List[str]) -> List[LessonTemplate]:
        if not lesson_ids:
            return []
        stmt: Select = select(LessonTemplate).where(LessonTemplate.id.in_(lesson_ids))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_lesson_segment_by_id(self, segment_id: str) -> Optional[LessonSegment]:
        stmt: Select = select(LessonSegment).where(LessonSegment.id == segment_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def find_habit_event(self, user_id: str, habit_template_id: str, on_date: date) -> Optional[HabitEvent]:
        stmt: Select = select(HabitEvent).where(
            and_(
                HabitEvent.user_id == user_id,
                HabitEvent.habit_template_id == habit_template_id,
                HabitEvent.date == on_date,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def find_lesson_events(self, user_id: str, lesson_ids: List[str], on_date: date) -> List[LessonEvent]:
        if not lesson_ids:
            return []
        stmt: Select = select(LessonEvent).where(
            and_(LessonEvent.user_id == user_id, LessonEvent.lesson_template_id.in_(lesson_ids), LessonEvent.date == on_date)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_step_daily_plan_for_day(self, step_id: str, day_index: int) -> Optional[StepDailyPlan]:
        stmt: Select = select(StepDailyPlan).where(
            and_(
                StepDailyPlan.program_step_template_id == step_id,
                StepDailyPlan.day_index == day_index,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_step_daily_plan(self, step_id: str) -> List[StepDailyPlan]:
        stmt: Select = select(StepDailyPlan).where(StepDailyPlan.program_step_template_id == step_id).order_by(StepDailyPlan.day_index.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

