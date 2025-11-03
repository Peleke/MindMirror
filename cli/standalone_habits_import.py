#!/usr/bin/env python3
"""Standalone habits/programs importer - no CLI dependencies."""

import asyncio
import sys
import os
import hashlib
import yaml
import json
from pathlib import Path
from dataclasses import asdict

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "habits_service"))
sys.path.insert(0, str(Path(__file__).parent.parent / "tools" / "content_parser"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from content_parser.parser import parse_markdown
from habits.app.db.models import Base
from habits.app.db.repositories.write import (
    LessonTemplateRepository,
    ProgramTemplateRepository,
    HabitTemplateRepository,
)
from habits.app.db.repositories.write_structural import (
    ProgramStepTemplateRepository,
    LessonSegmentRepository,
    StepDailyPlanRepository,
    StepLessonTemplateRepository,
)
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.exc import IntegrityError


def _hash_content(*parts: str) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update((p or "").encode("utf-8"))
    return h.hexdigest()


async def main():
    if len(sys.argv) < 3:
        print("Usage: python standalone_habits_import.py <database_url> <program_dir>")
        print("\nExample:")
        print("  python standalone_habits_import.py \\")
        print("    'postgresql+asyncpg://user:pass@host:5432/postgres' \\")
        print("    /workspace/data/habits/programs/unfck-your-eating")
        sys.exit(1)

    db_url = sys.argv[1]
    program_dir = Path(sys.argv[2])

    print(f"Database: {db_url}")
    print(f"Program directory: {program_dir}")
    print()

    # Validate program directory
    if not program_dir.exists():
        print(f"ERROR: Directory does not exist: {program_dir}")
        sys.exit(1)

    program_yaml = program_dir / "program.yaml"
    if not program_yaml.exists():
        print(f"ERROR: program.yaml not found in {program_dir}")
        sys.exit(1)

    # Create engine
    engine = create_async_engine(db_url, echo=False, poolclass=NullPool)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    # Load program manifest
    with open(program_yaml, "r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)

    program_slug = manifest["slug"]
    program_title = manifest.get("title", program_slug)

    print(f"Program: {program_title}")
    print(f"Slug: {program_slug}")
    print()

    async with session_maker() as session:
        # Repos
        program_repo = ProgramTemplateRepository(session)
        lesson_repo = LessonTemplateRepository(session)
        habit_repo = HabitTemplateRepository(session)
        step_repo = ProgramStepTemplateRepository(session)
        segment_repo = LessonSegmentRepository(session)
        daily_plan_repo = StepDailyPlanRepository(session)
        step_lesson_repo = StepLessonTemplateRepository(session)

        # Hash for idempotency
        program_hash = _hash_content(json.dumps(manifest, sort_keys=True))

        try:
            # Upsert program using CLI pattern
            program = await program_repo.upsert_with_version(
                slug=program_slug,
                title=program_title,
                description=manifest.get("description"),
                content_hash=program_hash,
                subtitle=manifest.get("subtitle"),
                hero_image_url=manifest.get("heroImageUrl"),
            )
            await session.commit()
            program_id = program.id

            print(f"Program ID: {program_id}")

            # Load and upsert lessons from markdown files
            lessons_dir = program_dir
            lesson_files = [f for f in os.listdir(lessons_dir) if f.endswith("_lesson.md")]
            slug_to_lesson_id = {}

            print(f"Found {len(lesson_files)} lesson files")
            for fname in lesson_files:
                fpath = lessons_dir / fname
                with open(fpath, "r", encoding="utf-8") as f:
                    md = f.read()
                parsed = parse_markdown(md)
                metadata = {
                    "flags": parsed.flags,
                    "outline": [asdict(o) for o in parsed.outline],
                }
                subtitle = parsed.raw_frontmatter.get("subtitle") if hasattr(parsed, "raw_frontmatter") else None
                hero_image_url = parsed.raw_frontmatter.get("heroImageUrl") if hasattr(parsed, "raw_frontmatter") else None
                content_hash = _hash_content(parsed.slug, parsed.title, parsed.markdown, subtitle or "", hero_image_url or "", json.dumps(metadata, sort_keys=True))

                lt = await lesson_repo.upsert_with_version(
                    slug=parsed.slug,
                    title=parsed.title or parsed.slug,
                    markdown_content=parsed.markdown,
                    summary=parsed.summary,
                    tags=parsed.tags,
                    est_read_minutes=None,
                    content_hash=content_hash,
                    metadata_json=metadata,
                    subtitle=subtitle,
                    hero_image_url=hero_image_url,
                )
                slug_to_lesson_id[parsed.slug] = lt.id
                print(f"  ✓ Lesson: {parsed.title}")

            await session.commit()
            print(f"✓ Imported {len(lesson_files)} lessons")

        except Exception as e:
            await session.rollback()
            print(f"\n❌ Error during import: {str(e)}")
            raise

    print("\n✓ Import complete!")


if __name__ == "__main__":
    asyncio.run(main())
