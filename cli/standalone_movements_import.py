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

            # Map CSV columns to model fields
            movement_data = {
                'name': name,
                'slug': slug,
                'difficulty': row.get('Difficulty Level'),
                'body_region': row.get('Body Region'),
                'target_muscle_group': row.get('Target Muscle Group'),
                'prime_mover_muscle': row.get('Prime Mover Muscle'),
                'posture': row.get('Posture'),
                'arm_mode': row.get('Single or Double Arm'),
                'arm_pattern': row.get('Continuous or Alternating Arms'),
                'grip': row.get('Grip'),
                'load_position': row.get('Load Position (Ending)'),
                'leg_pattern': row.get('Continuous or Alternating Legs'),
                'foot_elevation': row.get('Foot Elevation'),
                'combo_type': row.get('Combination Exercises'),
                'mechanics': row.get('Mechanics'),
                'laterality': row.get('Laterality'),
                'primary_classification': row.get('Primary Exercise Classification'),
                'force_type': row.get('Force Type'),
                'short_video_url': row.get('Short YouTube Demonstration'),
                'long_video_url': row.get('In-Depth YouTube Explanation'),
                'source': 'exercisedb_csv',
                'metadata_': {
                    'secondary_muscle': row.get('Secondary Muscle'),
                    'tertiary_muscle': row.get('Tertiary Muscle'),
                    'primary_equipment': row.get('Primary Equipment'),
                    'secondary_equipment': row.get('Secondary Equipment'),
                    'movement_pattern_1': row.get('Movement Pattern #1'),
                    'movement_pattern_2': row.get('Movement Pattern #2'),
                    'movement_pattern_3': row.get('Movement Pattern #3'),
                    'plane_of_motion_1': row.get('Plane Of Motion #1'),
                    'plane_of_motion_2': row.get('Plane Of Motion #2'),
                    'plane_of_motion_3': row.get('Plane Of Motion #3'),
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
