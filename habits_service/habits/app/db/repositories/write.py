from __future__ import annotations

from typing import Optional
import uuid

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from habits.app.db.tables import (
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
        subtitle: Optional[str] = None,
        hero_image_url: Optional[str] = None,
    ) -> LessonTemplate:
        fields = dict(
            slug=slug,
            title=title,
            markdown_content=markdown_content,
            summary=summary,
            tags=tags,
            est_read_minutes=est_read_minutes,
            subtitle=subtitle,
            hero_image_url=hero_image_url,
        )
        obj = LessonTemplate(**fields)
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

    async def upsert_with_version(
        self,
        *,
        slug: str,
        title: str,
        markdown_content: str,
        summary: Optional[str],
        tags: Optional[dict],
        est_read_minutes: Optional[int],
        content_hash: Optional[str],
        metadata_json: Optional[dict],
        subtitle: Optional[str] = None,
        hero_image_url: Optional[str] = None,
    ) -> LessonTemplate:
        existing = await self.get_by_slug(slug)
        if not existing:
            obj = LessonTemplate(
                slug=slug,
                title=title,
                markdown_content=markdown_content,
                summary=summary,
                tags=tags,
                est_read_minutes=est_read_minutes,
                content_hash=content_hash,
                metadata_json=metadata_json,
                subtitle=subtitle,
                hero_image_url=hero_image_url,
            )
            self.session.add(obj)
            await self.session.flush()
            return obj
        # Version bump only when content_hash changes
        update_fields = {
            "title": title,
            "markdown_content": markdown_content,
            "summary": summary,
            "tags": tags,
            "est_read_minutes": est_read_minutes,
            "metadata_json": metadata_json,
            "subtitle": subtitle,
            "hero_image_url": hero_image_url,
        }
        if content_hash and content_hash != existing.content_hash:
            update_fields["content_hash"] = content_hash
            update_fields["version"] = existing.version + 1
        await self.update(str(existing.id), **update_fields)
        return await self.get_by_id(str(existing.id))


class ProgramTemplateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, *, slug: str, title: str, description: Optional[str] = None, content_hash: Optional[str] = None, subtitle: Optional[str] = None, hero_image_url: Optional[str] = None) -> ProgramTemplate:
        fields = dict(slug=slug, title=title, description=description, subtitle=subtitle, hero_image_url=hero_image_url)
        obj = ProgramTemplate(**fields)
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

    async def get_by_id(self, id: str) -> Optional[ProgramTemplate]:
        uid = uuid.UUID(str(id))
        res = await self.session.execute(select(ProgramTemplate).where(ProgramTemplate.id == uid))
        return res.scalars().first()

    async def upsert_with_version(
        self,
        *,
        slug: str,
        title: str,
        description: Optional[str],
        content_hash: Optional[str],
        subtitle: Optional[str] = None,
        hero_image_url: Optional[str] = None,
    ) -> ProgramTemplate:
        existing = await self.get_by_slug(slug)
        if not existing:
            return await self.create(slug=slug, title=title, description=description, content_hash=content_hash, subtitle=subtitle, hero_image_url=hero_image_url)
        update_fields = {"title": title, "description": description, "subtitle": subtitle, "hero_image_url": hero_image_url}
        if content_hash and content_hash != existing.content_hash:
            update_fields["content_hash"] = content_hash
            update_fields["version"] = existing.version + 1
        await self.update(str(existing.id), **update_fields)
        return await self.get_by_id(str(existing.id))


class LessonTaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, lesson_task) -> None:
        """Add a new lesson task to the database."""
        self.session.add(lesson_task)
        await self.session.flush()

    async def get_by_id(self, id: str) -> Optional[LessonTask]:
        """Get a lesson task by ID."""
        uid = uuid.UUID(str(id))
        res = await self.session.execute(select(LessonTask).where(LessonTask.id == uid))
        return res.scalars().first()

    async def get_for_user_and_date(self, user_id: str, date: date) -> List[LessonTask]:
        """Get all lesson tasks for a user on a specific date."""
        res = await self.session.execute(
            select(LessonTask).where(
                LessonTask.user_id == user_id,
                LessonTask.date == date
            )
        )
        return list(res.scalars().all())

    async def get_for_user_date_and_lesson(
        self, user_id: str, date: date, lesson_template_id: str
    ) -> Optional[LessonTask]:
        """Get a specific lesson task for a user, date, and lesson template."""
        lid = uuid.UUID(str(lesson_template_id))
        res = await self.session.execute(
            select(LessonTask).where(
                LessonTask.user_id == user_id,
                LessonTask.date == date,
                LessonTask.lesson_template_id == lid
            )
        )
        return res.scalars().first()

    async def delete(self, id: str) -> bool:
        """Delete a lesson task by ID."""
        uid = uuid.UUID(str(id))
        res = await self.session.execute(
            delete(LessonTask).where(LessonTask.id == uid)
        )
        return res.rowcount is not None and res.rowcount > 0


