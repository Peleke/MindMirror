"""Seed habits/lessons/programs into habits_service DB from local data.

Uses content_parser to parse lessons and a program manifest to upsert templates.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
from dataclasses import asdict
from typing import Optional

import typer
from rich.console import Console
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from content_parser.parser import parse_markdown

from habits_service.habits_service.app.db.models import Base
from habits_service.habits_service.app.db.repositories.write import (
    LessonTemplateRepository,
    ProgramTemplateRepository,
    HabitTemplateRepository,
)
from habits_service.habits_service.app.db.repositories.write_structural import (
    ProgramStepTemplateRepository,
    StepLessonTemplateRepository,
)

console = Console()
app = typer.Typer(name="seed-habits", help="Seed habits/lessons/programs into DB")


def _hash_content(*parts: str) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update((p or "").encode("utf-8"))
    return h.hexdigest()


@app.command()
def run(
    program_dir: str = typer.Argument("/workspace/data/habits/programs/unfck-your-eating", help="Program directory"),
    database_url: Optional[str] = typer.Option(None, "--db-url", envvar="DATABASE_URL"),
    schema: Optional[str] = typer.Option("habits", "--schema", envvar="DATABASE_SCHEMA"),
):
    """Seed the specified program into the current DB."""

    async def _run():
        nonlocal database_url
        if not database_url:
            # fall back to compose default
            database_url = "postgresql+asyncpg://postgres:postgres@postgres:5432/cyborg_coach"

        engine = create_async_engine(
            database_url,
            future=True,
            poolclass=NullPool,
            execution_options={"schema_translate_map": {"habits": schema}},
        )
        async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

        # Ensure tables exist
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with async_session() as session:
            hrepo = HabitTemplateRepository(session)
            lrepo = LessonTemplateRepository(session)
            prepo = ProgramTemplateRepository(session)
            srepo = ProgramStepTemplateRepository(session)
            slrepo = StepLessonTemplateRepository(session)

            # Load program manifest
            manifest_path = os.path.join(program_dir, "program.yaml")
            import yaml

            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = yaml.safe_load(f)

            program_slug = manifest["slug"]
            program_title = manifest.get("title", program_slug)
            program_hash = _hash_content(json.dumps(manifest, sort_keys=True))
            program = await prepo.upsert_with_version(
                slug=program_slug, title=program_title, description=manifest.get("description"), content_hash=program_hash
            )
            await session.commit()

            # Seed lessons
            lessons_dir = program_dir
            lesson_files = [f for f in os.listdir(lessons_dir) if f.endswith("_lesson.md")]
            slug_to_lesson_id: dict[str, str] = {}
            for fname in lesson_files:
                fpath = os.path.join(lessons_dir, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    md = f.read()
                parsed = parse_markdown(md)
                metadata = {
                    "flags": parsed.flags,
                    "outline": [asdict(o) for o in parsed.outline],
                }
                content_hash = _hash_content(parsed.slug, parsed.title, parsed.markdown, json.dumps(metadata, sort_keys=True))
                lt = await lrepo.upsert_with_version(
                    slug=parsed.slug,
                    title=parsed.title or parsed.slug,
                    markdown_content=parsed.markdown,
                    summary=parsed.summary,
                    tags=parsed.tags,
                    est_read_minutes=None,
                    content_hash=content_hash,
                    metadata_json=metadata,
                )
                slug_to_lesson_id[parsed.slug] = str(lt.id)
            await session.commit()

            # Build or upsert HabitTemplates needed by steps
            # Map habitTemplateSlug -> id
            habit_slug_to_id: dict[str, str] = {}
            for idx, step in enumerate(manifest.get("sequence", [])):
                habit_slug = step.get("habitTemplateSlug")
                habit_title = step.get("title") or habit_slug
                if not habit_slug:
                    continue
                existing = await hrepo.get_by_slug(habit_slug)
                if not existing:
                    created = await hrepo.create(
                        slug=habit_slug,
                        title=habit_title,
                        short_description=None,
                        description=None,
                        level=None,
                        default_duration_days=int(step.get("durationDays", 7)),
                        tags=None,
                    )
                    habit_slug_to_id[habit_slug] = str(created.id)
                else:
                    habit_slug_to_id[habit_slug] = str(existing.id)
            await session.commit()

            # Build program steps and step-lessons
            # Delete old to keep idempotent
            from sqlalchemy import select
            from habits_service.habits_service.app.db.tables import ProgramStepTemplate
            existing_steps = await session.execute(
                select(ProgramStepTemplate).where(ProgramStepTemplate.program_template_id == program.id)
            )
            existing_steps = list(existing_steps.scalars())
            if existing_steps:
                await srepo.delete_by_program(str(program.id))
                await session.commit()

            created_steps = await srepo.bulk_create(
                program_template_id=str(program.id),
                steps=[
                    {
                        "sequence_index": idx,
                        "habit_template_id": habit_slug_to_id.get(step.get("habitTemplateSlug", "")) or uuid_from_slug(step.get("habitTemplateSlug", "")),
                        "duration_days": int(step.get("durationDays", 7)),
                    }
                    for idx, step in enumerate(manifest.get("sequence", []))
                ],
            )
            await session.commit()

            # Map lessons to steps
            for idx, step in enumerate(manifest.get("sequence", [])):
                if not step.get("lessonSlugs"):
                    continue
                step_obj = created_steps[idx]
                lessons = [
                    {"day_index": 0, "lesson_template_id": slug_to_lesson_id[slug]} for slug in step["lessonSlugs"] if slug in slug_to_lesson_id
                ]
                if lessons:
                    await slrepo.bulk_create(step_id=str(step_obj.id), lessons=lessons)
            await session.commit()

        await engine.dispose()
        console.print("[green]✅ Seeded program and lessons[/green]")

    # Helper to convert habit slugs to a deterministic UUID namespace (placeholder; to be wired to actual HabitTemplates later)
    import uuid

    def uuid_from_slug(slug: str) -> str:
        if not slug:
            return str(uuid.uuid4())
        ns = uuid.UUID("00000000-0000-0000-0000-000000000001")
        return str(uuid.uuid5(ns, slug))

    asyncio.run(_run())


