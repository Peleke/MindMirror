"""Seed habits/lessons/programs into habits_service DB from local data.

Uses content_parser to parse lessons and a program manifest to upsert templates.
"""

from __future__ import annotations

import sys
from pathlib import Path

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
from mindmirror_cli.core.utils import (
    set_environment,
    get_current_environment,
    is_live_environment,
    is_production_environment,
    get_database_url,
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
    env: Optional[str] = typer.Option(None, "--env", "-e", help="Environment (local, staging, production)"),
):
    """Seed the specified program into the current DB."""

    async def _run():
        # Set CLI environment if provided
        if env:
            set_environment(env)
            console.print(f"[blue]Environment: {get_current_environment()}[/blue]")

        # Production safety check
        if is_production_environment():
            confirm = typer.confirm(
                "⚠️  You are seeding PRODUCTION habits/programs. Continue?",
                default=False
            )
            if not confirm:
                console.print("[yellow]Cancelled[/yellow]")
                raise typer.Exit(0)

        nonlocal database_url
        if not database_url:
            try:
                database_url = get_database_url('main')
            except ValueError as e:
                console.print(f"[red]{e}[/red]")
                raise typer.Exit(1)

        console.print(f"[cyan]Target DB:[/cyan] {database_url.split('@')[-1]}")

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
            segrepo = LessonSegmentRepository(session)
            dprepo = StepDailyPlanRepository(session)

            # Load program manifest
            manifest_path = os.path.join(program_dir, "program.yaml")
            import yaml

            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = yaml.safe_load(f)

            program_slug = manifest["slug"]
            program_title = manifest.get("title", program_slug)
            program_hash = _hash_content(json.dumps(manifest, sort_keys=True))
            program = await prepo.upsert_with_version(
                slug=program_slug,
                title=program_title,
                description=manifest.get("description"),
                content_hash=program_hash,
                subtitle=manifest.get("subtitle"),
                hero_image_url=manifest.get("heroImageUrl"),
            )
            await session.commit()

            # Seed lessons
            lessons_dir = program_dir
            lesson_files = [f for f in os.listdir(lessons_dir) if f.endswith("_lesson.md")]
            slug_to_lesson_id: dict[str, str] = {}
            slug_to_file_path: dict[str, str] = {}
            for fname in lesson_files:
                fpath = os.path.join(lessons_dir, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    md = f.read()
                parsed = parse_markdown(md)
                metadata = {
                    "flags": parsed.flags,
                    "outline": [asdict(o) for o in parsed.outline],
                }
                # Support subtitle and hero image
                subtitle = parsed.raw_frontmatter.get("subtitle") if hasattr(parsed, "raw_frontmatter") else None
                hero_image_url = parsed.raw_frontmatter.get("heroImageUrl") if hasattr(parsed, "raw_frontmatter") else None
                content_hash = _hash_content(parsed.slug, parsed.title, parsed.markdown, subtitle or "", hero_image_url or "", json.dumps(metadata, sort_keys=True))
                lt = await lrepo.upsert_with_version(
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
                slug_to_lesson_id[parsed.slug] = str(lt.id)
                slug_to_file_path[parsed.slug] = fpath
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
                # Delete step-lesson mappings first to avoid FK violations
                for st in existing_steps:
                    await slrepo.delete_by_step(str(st.id))
                await session.commit()
                await srepo.delete_by_program(str(program.id))
                await session.commit()

            created_steps = await srepo.bulk_create(
                program_template_id=str(program.id),
                steps=[
                    {
                        "sequence_index": idx,
                        "habit_template_id": (
                            habit_slug_to_id.get(step.get("habitTemplateSlug"))
                            if step.get("habitTemplateSlug") else None
                        ),
                        "duration_days": int(step.get("durationDays", 7)),
                    }
                    for idx, step in enumerate(manifest.get("sequence", []))
                ],
            )
            await session.commit()

            # Map lessons to steps (optional day mapping via step.yaml);
            # also seed lesson segments and daily plan when sidecars provided
            for idx, step in enumerate(manifest.get("sequence", [])):
                step_obj = created_steps[idx]
                # Default: if lessonSlugs, attach them to day 0 unless overridden by step.yaml
                default_lessons = []
                for slug in step.get("lessonSlugs", []) or []:
                    if slug in slug_to_lesson_id:
                        default_lessons.append({"day_index": 0, "lesson_template_id": slug_to_lesson_id[slug]})

                # Sidecar step.yaml support (extract-only segmentation)
                step_dir = program_dir
                sidecar_path = os.path.join(step_dir, f"step_{idx:02d}.yaml")
                daily_plan_items = []
                if os.path.exists(sidecar_path):
                    with open(sidecar_path, "r", encoding="utf-8") as f:
                        step_cfg = yaml.safe_load(f)
                    # Segments sidecar keyed by lesson slug (optional)
                    segments_cfg = step_cfg.get("lesson_segments") or {}
                    for lesson_slug, segs in segments_cfg.items():
                        lesson_id = slug_to_lesson_id.get(lesson_slug)
                        if not lesson_id:
                            continue
                        # Clear existing per-lesson segments for idempotency
                        await segrepo.delete_by_lesson(lesson_id)
                        seg_payloads = []
                        for seg in segs or []:
                            extract_cfg = seg.get("extract") or {}
                            # Load full lesson markdown to support extraction
                            # This CLI already parsed lessons, but we reload file here to keep it simple
                            # Infer lesson filename by slug (convention: <slug>_lesson.md within program_dir)
                            candidate_md = slug_to_file_path.get(lesson_slug) or os.path.join(program_dir, f"{lesson_slug}_lesson.md")
                            segment_md = seg.get("content") or ""
                            if not segment_md and os.path.exists(candidate_md):
                                with open(candidate_md, "r", encoding="utf-8") as lf:
                                    full_md = lf.read()
                                t = (extract_cfg.get("type") or "").lower()
                                if t == "heading":
                                    match = extract_cfg.get("match")
                                    segment_md = _extract_heading(full_md, match) if match else ""
                                elif t == "heading_range":
                                    from_h = extract_cfg.get("from")
                                    to_h = extract_cfg.get("to")
                                    segment_md = _extract_heading_range(full_md, from_h, to_h)
                                else:
                                    segment_md = ""
                                # Support extra extracts appended sequentially
                                extras = extract_cfg.get("extra") or []
                                for ex in extras:
                                    et = (ex.get("type") or "").lower()
                                    if et == "heading":
                                        mm = ex.get("match")
                                        if mm:
                                            segment_md += "\n\n" + _extract_heading(full_md, mm)
                                    elif et == "heading_range":
                                        fh = ex.get("from")
                                        th = ex.get("to")
                                        segment_md += "\n\n" + _extract_heading_range(full_md, fh, th)
                            seg_payloads.append({
                                "lesson_template_id": lesson_id,
                                "day_index_within_step": seg.get("day_index"),
                                "title": seg.get("title") or lesson_slug,
                                "subtitle": seg.get("subtitle"),
                                "markdown_content": segment_md,
                                "summary": seg.get("summary"),
                                "metadata_json": {"extract": extract_cfg} if extract_cfg else seg.get("metadata"),
                            })
                        created_segs = await segrepo.bulk_upsert(seg_payloads)
                        # Optionally map segments to daily plan by day index for this step
                        if created_segs:
                            for cs in created_segs:
                                if cs.day_index_within_step is not None:
                                    daily_plan_items.append({
                                        "day_index": int(cs.day_index_within_step),
                                        "lesson_segment_id": str(cs.id),
                                    })

                    # Daily plan entries (habit variants + journal prompts)
                    for item in step_cfg.get("daily_plan", []) or []:
                        dp = {
                            "day_index": int(item.get("day_index", 0)),
                            "habit_variant_text": item.get("habit_variant_text"),
                            "journal_prompt_text": item.get("journal_prompt_text"),
                        }
                        # Link a segment by lesson slug if provided
                        seg_slug = item.get("lesson_segment_slug")
                        if seg_slug and isinstance(seg_slug, str):
                            # Best-effort: find the first created segment with matching title
                            # (authoring can ensure unique titles or extend schema to include slug)
                            pass
                        daily_plan_items.append(dp)

                # Persist daily plan (merge duplicates by day_index), then lessons
                if daily_plan_items:
                    merged: dict[int, dict] = {}
                    for p in daily_plan_items:
                        di = int(p.get("day_index", 0))
                        if di not in merged:
                            merged[di] = {
                                "day_index": di,
                                "habit_variant_text": None,
                                "journal_prompt_text": None,
                                "lesson_segment_id": None,
                                "metadata_json": None,
                            }
                        tgt = merged[di]
                        # Prefer non-empty values; keep existing if new is falsy
                        if p.get("habit_variant_text"):
                            tgt["habit_variant_text"] = p.get("habit_variant_text")
                        if p.get("journal_prompt_text"):
                            tgt["journal_prompt_text"] = p.get("journal_prompt_text")
                        if p.get("lesson_segment_id"):
                            tgt["lesson_segment_id"] = p.get("lesson_segment_id")
                        if p.get("metadata_json"):
                            tgt["metadata_json"] = p.get("metadata_json")
                    await dprepo.bulk_upsert(step_id=str(step_obj.id), plans=list(merged.values()))

                if default_lessons:
                    await slrepo.bulk_create(step_id=str(step_obj.id), lessons=default_lessons)
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

    # --- simple markdown extract helpers ---
    def _extract_heading(md: str, heading_text: str) -> str:
        """Extract a section starting at a heading until the next heading of same or higher level."""
        if not heading_text:
            return ""
        lines = md.splitlines()
        start = -1
        start_level = None
        for i, line in enumerate(lines):
            if line.strip().startswith("#") and heading_text.strip() in line:
                start = i
                start_level = line.count("#", 0, line.find(" ")) or line.count("#")
                break
        if start == -1:
            return ""
        out = [lines[start]]
        for j in range(start + 1, len(lines)):
            l = lines[j]
            if l.strip().startswith("#"):
                lvl = l.count("#", 0, l.find(" ")) or l.count("#")
                if start_level is not None and lvl <= start_level:
                    break
            out.append(l)
        return "\n".join(out).strip()

    def _extract_heading_range(md: str, from_heading: str, to_heading: str | None) -> str:
        """Extract content from one heading to another (exclusive of the ending heading)."""
        if not from_heading:
            return ""
        lines = md.splitlines()
        start = -1
        for i, line in enumerate(lines):
            if line.strip().startswith("#") and from_heading.strip() in line:
                start = i
                break
        if start == -1:
            return ""
        out = [lines[start]]
        for j in range(start + 1, len(lines)):
            l = lines[j]
            if to_heading and l.strip().startswith("#") and to_heading.strip() in l:
                break
            out.append(l)
        return "\n".join(out).strip()

    asyncio.run(_run())
