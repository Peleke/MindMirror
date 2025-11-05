#!/usr/bin/env python3
"""Standalone movements CSV importer - no CLI dependencies."""

import asyncio
import sys
import csv
import uuid  # Required for pgbouncer compatibility (unique prepared statement names)
from pathlib import Path
from typing import Optional

# Add movements_service and shared to path
sys.path.insert(0, str(Path(__file__).parent.parent / "movements_service"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from movements.repository.models import MovementModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


def _slugify(name: str) -> str:
    """Convert name to URL-safe slug."""
    import re
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = re.sub(r'^-+|-+$', '', slug)
    return slug


def _is_valid_url(value: Optional[str]) -> bool:
    """Check if value is a valid URL (not placeholder text)."""
    if not value or not isinstance(value, str):
        return False
    value = value.strip()
    # Must start with http:// or https://
    return value.startswith('http://') or value.startswith('https://')


def _clean_value(value: Optional[str]) -> Optional[str]:
    """Clean CSV value: strip whitespace, convert empty/None-like strings to None."""
    if value is None:
        return None
    if not isinstance(value, str):
        return value
    value = value.strip()
    # Treat empty strings, 'None', 'null', etc. as None
    if value in ('', 'None', 'none', 'NULL', 'null', 'N/A', 'n/a'):
        return None
    return value


async def import_movements_csv(
    session,
    csv_path: str,
    update_existing: bool = True
) -> tuple[int, int, int]:
    """Import movements from ExerciseDB-style CSV."""
    created = 0
    updated = 0
    skipped = 0

    with open(csv_path, 'r', encoding='utf-8') as f:
        # Skip header rows (lines before actual headers)
        content = f.read()
        lines = content.split('\n')

        # Find the header row (contains "Exercise" as first column)
        header_idx = None
        for i, line in enumerate(lines):
            if line.strip().startswith(',Exercise,'):
                header_idx = i
                break

        if header_idx is None:
            print("ERROR: Could not find header row in CSV")
            return 0, 0, 0

        # Parse CSV starting from header
        csv_lines = '\n'.join(lines[header_idx:])
        reader = csv.DictReader(csv_lines.split('\n'))

        for row in reader:
            # Skip empty rows
            if not row.get('Exercise') or row.get('Exercise').strip() == '':
                continue

            name = row.get('Exercise').strip()
            slug = _slugify(name)

            # Check if exists by SLUG (the unique constraint)
            stmt = select(MovementModel).where(MovementModel.slug == slug)
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            # Get and validate video URLs (filter out placeholder text like "Video Demonstration")
            short_video = _clean_value(row.get('Short YouTube Demonstration'))
            long_video = _clean_value(row.get('In-Depth YouTube Explanation'))
            short_video_url = short_video if _is_valid_url(short_video) else None
            long_video_url = long_video if _is_valid_url(long_video) else None

            # Map CSV columns to model fields (clean all values)
            movement_data = {
                'name': name,
                'slug': slug,
                'difficulty': _clean_value(row.get('Difficulty Level')),
                'body_region': _clean_value(row.get('Body Region')),
                'target_muscle_group': _clean_value(row.get('Target Muscle Group')),
                'prime_mover_muscle': _clean_value(row.get('Prime Mover Muscle')),
                'posture': _clean_value(row.get('Posture')),
                'arm_mode': _clean_value(row.get('Single or Double Arm')),
                'arm_pattern': _clean_value(row.get('Continuous or Alternating Arms')),
                'grip': _clean_value(row.get('Grip')),
                'load_position': _clean_value(row.get('Load Position (Ending)')),
                'leg_pattern': _clean_value(row.get('Continuous or Alternating Legs')),
                'foot_elevation': _clean_value(row.get('Foot Elevation')),
                'combo_type': _clean_value(row.get('Combination Exercises')),
                'mechanics': _clean_value(row.get('Mechanics')),
                'laterality': _clean_value(row.get('Laterality')),
                'primary_classification': _clean_value(row.get('Primary Exercise Classification')),
                'force_type': _clean_value(row.get('Force Type')),
                'short_video_url': short_video_url,
                'long_video_url': long_video_url,
                'source': 'exercisedb_csv',
                'metadata_': {
                    'secondary_muscle': _clean_value(row.get('Secondary Muscle')),
                    'tertiary_muscle': _clean_value(row.get('Tertiary Muscle')),
                    'primary_equipment': _clean_value(row.get('Primary Equipment')),
                    'secondary_equipment': _clean_value(row.get('Secondary Equipment')),
                    'movement_pattern_1': _clean_value(row.get('Movement Pattern #1')),
                    'movement_pattern_2': _clean_value(row.get('Movement Pattern #2')),
                    'movement_pattern_3': _clean_value(row.get('Movement Pattern #3')),
                    'plane_of_motion_1': _clean_value(row.get('Plane Of Motion #1')),
                    'plane_of_motion_2': _clean_value(row.get('Plane Of Motion #2')),
                    'plane_of_motion_3': _clean_value(row.get('Plane Of Motion #3')),
                }
            }

            # Remove empty values
            movement_data = {k: v for k, v in movement_data.items() if v not in [None, '', 'None', 0]}
            # Clean metadata
            if 'metadata_' in movement_data:
                movement_data['metadata_'] = {k: v for k, v in movement_data['metadata_'].items() if v not in [None, '', 'None', 0]}

            try:
                if existing:
                    if update_existing:
                        # Update existing movement
                        for key, value in movement_data.items():
                            if key != 'slug':  # Don't update slug
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
                print(f"  ⚠️  Skipping '{name}': {str(e.orig)[:100]}")
                skipped += 1
                continue

        await session.commit()

    return created, updated, skipped


async def main():
    if len(sys.argv) < 3:
        print("Usage: python standalone_movements_import.py <database_url> <csv_path>")
        print("\nExample:")
        print("  python standalone_movements_import.py \\")
        print("    'postgresql+asyncpg://user:pass@host:5432/postgres' \\")
        print("    exercises.csv")
        sys.exit(1)

    db_url = sys.argv[1]
    csv_path = sys.argv[2]
    update_existing = True

    print(f"Database: {db_url}")
    print(f"CSV: {csv_path}")
    print(f"Update existing: {update_existing}")
    print()

    # Create engine
    engine = create_async_engine(db_url, echo=False)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async with session_maker() as session:
        created, updated, skipped = await import_movements_csv(
            session=session,
            csv_path=csv_path,
            update_existing=update_existing,
        )

        print(f"\n✓ Import complete!")
        print(f"  Created: {created}")
        print(f"  Updated: {updated}")
        print(f"  Skipped: {skipped}")
        print(f"  Total:   {created + updated + skipped}")


if __name__ == "__main__":
    asyncio.run(main())
