from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from habits.app.db.tables import HabitEvent, LessonEvent


class HabitEventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert(
        self,
        *,
        user_id: str,
        habit_template_id: str,
        on_date: date,
        response: str,
        source: Optional[str] = None,
    ) -> HabitEvent:
        hid = uuid.UUID(str(habit_template_id))
        res = await self.session.execute(
            select(HabitEvent).where(
                and_(
                    HabitEvent.user_id == user_id,
                    HabitEvent.habit_template_id == hid,
                    HabitEvent.date == on_date,
                )
            )
        )
        existing = res.scalars().first()
        if existing:
            existing.response = response
            existing.source = source
            await self.session.flush()
            return existing
        obj = HabitEvent(
            user_id=user_id,
            habit_template_id=hid,
            date=on_date,
            response=response,
            source=source,
        )
        self.session.add(obj)
        await self.session.flush()
        return obj


class LessonEventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert(
        self,
        *,
        user_id: str,
        lesson_template_id: str,
        on_date: date,
        event_type: str,  # opened|completed
    ) -> LessonEvent:
        lid = uuid.UUID(str(lesson_template_id))
        res = await self.session.execute(
            select(LessonEvent).where(
                and_(
                    LessonEvent.user_id == user_id,
                    LessonEvent.lesson_template_id == lid,
                    LessonEvent.date == on_date,
                )
            )
        )
        existing = res.scalars().first()
        if existing:
            # Promote state if needed (opened -> completed), else set provided
            if existing.event_type != "completed":
                existing.event_type = event_type
            await self.session.flush()
            return existing
        obj = LessonEvent(
            user_id=user_id,
            lesson_template_id=lid,
            date=on_date,
            event_type=event_type,
        )
        self.session.add(obj)
        await self.session.flush()
        return obj


