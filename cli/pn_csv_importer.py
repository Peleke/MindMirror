"""Precision Nutrition CSV importer for movements with coach video support."""
from __future__ import annotations

import csv
import re
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

# Assumes movements_service is in sys.path (added by calling scripts)
from movements.repository.models import MovementModel


def _slugify(name: str) -> str:
    """Convert name to URL-safe slug."""
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = re.sub(r'^-+|-+$', '', slug)
    return slug


def parse_description_to_steps(raw_description: str) -> str:
    """
    Parse numbered instructions into newline-separated steps.

    Example:
        "1. Lock ribs. 2. Tuck tailbone. 3. Don't sag."
        -> "1. Lock ribs.\n2. Tuck tailbone.\n3. Don't sag."
    """
    if not raw_description or not raw_description.strip():
        return ""

    # Split by pattern: number followed by period and space
    # Use positive lookahead to keep the delimiter
    steps = re.split(r'(?=\d+\.\s+)', raw_description.strip())

    # Clean and filter empty steps
    cleaned_steps = [step.strip() for step in steps if step.strip()]

    # Join with newlines
    return '\n'.join(cleaned_steps)


async def import_pn_movements_csv(
    session: AsyncSession,
    jen_csv_path: str,
    craig_csv_path: str,
    update_existing: bool = True
) -> dict:
    """
    Import Precision Nutrition movements from Jen and Craig CSVs.

    Both CSVs have the same exercises but different coach videos:
    - Jen (female coach) -> short_video_url (PRIMARY - shown in UI)
    - Craig (male coach) -> long_video_url (ALTERNATE - detailed version)

    Args:
        session: Async SQLAlchemy session
        jen_csv_path: Path to jen_export.csv
        craig_csv_path: Path to craig_export.csv
        update_existing: If True, update existing movements; if False, skip duplicates

    Returns:
        dict with counts: {"created": int, "updated": int, "skipped": int}
    """
    # Parse both CSVs into memory
    jen_exercises = {}
    with open(jen_csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get('Exercise') or '').strip()
            if name and name != 'Exercise':  # Skip header duplicates
                jen_exercises[name] = {
                    'url': (row.get('URL') or '').strip(),
                    'description': (row.get('Description') or '').strip()
                }

    craig_exercises = {}
    with open(craig_csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get('Exercise') or '').strip()
            if name and name != 'Exercise':
                craig_exercises[name] = {
                    'url': (row.get('URL') or '').strip(),
                    'description': (row.get('Description') or '').strip()
                }

    # Merge exercises (should have same names)
    all_exercise_names = set(jen_exercises.keys()) | set(craig_exercises.keys())

    created = 0
    updated = 0
    skipped = 0

    for exercise_name in sorted(all_exercise_names):
        jen_data = jen_exercises.get(exercise_name, {})
        craig_data = craig_exercises.get(exercise_name, {})

        # Get URLs (prefer data from both sources)
        jen_url = jen_data.get('url', '')
        craig_url = craig_data.get('url', '')

        # Get description (prefer jen, fallback to craig)
        raw_description = jen_data.get('description') or craig_data.get('description', '')
        cleaned_description = parse_description_to_steps(raw_description)

        # Build metadata
        metadata = {
            'video_coaches': {},
            'source_details': {
                'program': 'precision_nutrition',
                'import_version': 'v1'
            }
        }

        if jen_url:
            metadata['video_coaches']['female'] = jen_url
        if craig_url:
            metadata['video_coaches']['male'] = craig_url

        # Check if movement exists by SLUG (the unique constraint)
        slug = _slugify(exercise_name)
        stmt = select(MovementModel).where(MovementModel.slug == slug)
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()

        movement_data = {
            'name': exercise_name,
            'slug': slug,
            'description': cleaned_description,
            'short_video_url': jen_url or None,    # female coach (PRIMARY)
            'long_video_url': craig_url or None,   # male coach (ALTERNATE)
            'source': 'precision_nutrition',
            'metadata': metadata
        }

        try:
            if existing:
                if update_existing:
                    # Update existing movement
                    for key, value in movement_data.items():
                        if key not in ['slug', 'name']:  # Don't update slug or name
                            setattr(existing, key, value)
                    await session.flush()
                    updated += 1
                else:
                    skipped += 1
            else:
                # Create new movement
                movement = MovementModel(**movement_data)
                session.add(movement)
                await session.flush()
                created += 1
        except IntegrityError as e:
            # Handle duplicate slug or other integrity errors
            await session.rollback()
            print(f"  ⚠️  Skipping '{exercise_name}': {str(e.orig)[:100]}")
            skipped += 1
            continue

    await session.commit()

    return {
        'created': created,
        'updated': updated,
        'skipped': skipped,
        'total': len(all_exercise_names)
    }
