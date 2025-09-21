from __future__ import annotations

from datetime import date
from typing import List, Optional

from sqlalchemy import Select, and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from habits_service.habits_service.app.db.tables import (
    HabitEvent,
    HabitTemplate,
    LessonEvent,
    LessonTemplate,
    ProgramTemplate,
    ProgramStepTemplate,
    StepLessonTemplate,
    UserProgramAssignment,
    # Newly required models for daily planning
    StepDailyPlan,
    LessonSegment,
)


class HabitsReadRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active_assignments(self, user_id: str) -> List[UserProgramAssignment]:
        stmt: Select = select(UserProgramAssignment).where(
            and_(UserProgramAssignment.user_id == user_id, UserProgramAssignment.status == "active")
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_assignments(self, user_id: str, status: Optional[str] = None) -> List[UserProgramAssignment]:
        stmt: Select = select(UserProgramAssignment).where(UserProgramAssignment.user_id == user_id)
        if status:
            stmt = stmt.where(UserProgramAssignment.status == status)
        result = await self.session.execute(stmt.order_by(UserProgramAssignment.created_at.desc()))
        return list(result.scalars().all())

    async def get_program_steps(self, program_template_id: str) -> List[ProgramStepTemplate]:
        stmt: Select = (
            select(ProgramStepTemplate)
            .where(ProgramStepTemplate.program_template_id == program_template_id)
            .order_by(ProgramStepTemplate.sequence_index.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_program_templates(self) -> List[ProgramTemplate]:
        stmt: Select = select(ProgramTemplate).order_by(ProgramTemplate.created_at.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_program_template_by_slug(self, slug: str) -> Optional[ProgramTemplate]:
        stmt: Select = select(ProgramTemplate).where(ProgramTemplate.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalars().first()

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

    async def get_step_lessons(self, step_id: str) -> List[StepLessonTemplate]:
        stmt: Select = select(StepLessonTemplate).where(
            StepLessonTemplate.program_step_template_id == step_id
        ).order_by(StepLessonTemplate.day_index.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_lesson_templates(self, lesson_ids: List[str]) -> List[LessonTemplate]:
        if not lesson_ids:
            return []
        stmt: Select = select(LessonTemplate).where(LessonTemplate.id.in_(lesson_ids))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_lesson_template_by_id(self, lesson_id: str) -> Optional[LessonTemplate]:
        stmt: Select = select(LessonTemplate).where(LessonTemplate.id == lesson_id)
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

    async def list_recent_lesson_completions(self, user_id: str, limit: int = 50) -> List[LessonEvent]:
        stmt: Select = (
            select(LessonEvent)
            .where(and_(LessonEvent.user_id == user_id, LessonEvent.event_type == "completed"))
            .order_by(LessonEvent.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # --- Daily Plan & Lesson Segment helpers (used by planner) ---
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
        stmt: Select = select(StepDailyPlan).where(
            StepDailyPlan.program_step_template_id == step_id
        ).order_by(StepDailyPlan.day_index.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_lesson_segment_by_id(self, segment_id: str) -> Optional[LessonSegment]:
        stmt: Select = select(LessonSegment).where(LessonSegment.id == segment_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_lesson_segments_by_lesson(self, lesson_template_id: str) -> List[LessonSegment]:
        stmt: Select = select(LessonSegment).where(
            LessonSegment.lesson_template_id == lesson_template_id
        ).order_by(LessonSegment.day_index_within_step.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_lesson_tasks_for_user_and_date(self, user_id: str, date: date) -> List[LessonTask]:
        """Get all lesson tasks for a user on a specific date."""
        stmt: Select = select(LessonTask).where(
            LessonTask.user_id == user_id,
            LessonTask.date == date
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


