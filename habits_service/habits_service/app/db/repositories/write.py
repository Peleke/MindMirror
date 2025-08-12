from __future__ import annotations

from typing import Optional
import uuid

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from habits_service.habits_service.app.db.tables import (
    HabitTemplate,
    LessonTemplate,
    ProgramTemplate,
    ProgramStepTemplate,
    StepLessonTemplate,
    UserProgramAssignment,
)


class HabitTemplateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        *,
        slug: str,
        title: str,
        short_description: Optional[str] = None,
        description: Optional[str] = None,
        level: Optional[int] = None,
        default_duration_days: int = 7,
        tags: Optional[dict] = None,
    ) -> HabitTemplate:
        obj = HabitTemplate(
            slug=slug,
            title=title,
            short_description=short_description,
            description=description,
            level=level,
            default_duration_days=default_duration_days,
            tags=tags,
        )
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def update(self, id: str, **fields) -> Optional[HabitTemplate]:
        uid = uuid.UUID(str(id))
        await self.session.execute(
            update(HabitTemplate).where(HabitTemplate.id == uid).values(**fields)
        )
        await self.session.flush()
        return await self.get_by_id(str(uid))

    async def delete(self, id: str) -> bool:
        uid = uuid.UUID(str(id))
        res = await self.session.execute(
            delete(HabitTemplate).where(HabitTemplate.id == uid)
        )
        return res.rowcount is not None and res.rowcount > 0

    async def get_by_slug(self, slug: str) -> Optional[HabitTemplate]:
        res = await self.session.execute(select(HabitTemplate).where(HabitTemplate.slug == slug))
        return res.scalars().first()

    async def get_by_id(self, id: str) -> Optional[HabitTemplate]:
        uid = uuid.UUID(str(id))
        res = await self.session.execute(select(HabitTemplate).where(HabitTemplate.id == uid))
        return res.scalars().first()


class LessonTemplateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        *,
        slug: str,
        title: str,
        markdown_content: str,
        summary: Optional[str] = None,
        tags: Optional[dict] = None,
        est_read_minutes: Optional[int] = None,
    ) -> LessonTemplate:
        obj = LessonTemplate(
            slug=slug,
            title=title,
            markdown_content=markdown_content,
            summary=summary,
            tags=tags,
            est_read_minutes=est_read_minutes,
        )
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def update(self, id: str, **fields) -> Optional[LessonTemplate]:
        uid = uuid.UUID(str(id))
        await self.session.execute(
            update(LessonTemplate).where(LessonTemplate.id == uid).values(**fields)
        )
        await self.session.flush()
        return await self.get_by_id(str(uid))

    async def delete(self, id: str) -> bool:
        uid = uuid.UUID(str(id))
        res = await self.session.execute(
            delete(LessonTemplate).where(LessonTemplate.id == uid)
        )
        return res.rowcount is not None and res.rowcount > 0

    async def get_by_slug(self, slug: str) -> Optional[LessonTemplate]:
        res = await self.session.execute(select(LessonTemplate).where(LessonTemplate.slug == slug))
        return res.scalars().first()

    async def get_by_id(self, id: str) -> Optional[LessonTemplate]:
        uid = uuid.UUID(str(id))
        res = await self.session.execute(select(LessonTemplate).where(LessonTemplate.id == uid))
        return res.scalars().first()


class ProgramTemplateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, *, slug: str, title: str, description: Optional[str] = None) -> ProgramTemplate:
        obj = ProgramTemplate(slug=slug, title=title, description=description)
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def update(self, id: str, **fields) -> Optional[ProgramTemplate]:
        uid = uuid.UUID(str(id))
        await self.session.execute(
            update(ProgramTemplate).where(ProgramTemplate.id == uid).values(**fields)
        )
        await self.session.flush()
        return await self.get_by_id(str(uid))

    async def delete(self, id: str) -> bool:
        uid = uuid.UUID(str(id))
        res = await self.session.execute(
            delete(ProgramTemplate).where(ProgramTemplate.id == uid)
        )
        return res.rowcount is not None and res.rowcount > 0

    async def get_by_slug(self, slug: str) -> Optional[ProgramTemplate]:
        res = await self.session.execute(select(ProgramTemplate).where(ProgramTemplate.slug == slug))
        return res.scalars().first()

        uid = uuid.UUID(str(id))
        res = await self.session.execute(select(ProgramTemplate).where(ProgramTemplate.id == uid))
        return res.scalars().first()


