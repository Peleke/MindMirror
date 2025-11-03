#!/usr/bin/env python3
"""Standalone PN movements importer - no CLI dependencies."""

import asyncio
import sys
import os
import uuid
from pathlib import Path

# Add movements_service and shared to path
sys.path.insert(0, str(Path(__file__).parent.parent / "movements_service"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import from cli/ directory (same directory as this script)
from pn_csv_importer import import_pn_movements_csv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


async def main():
    # Parse args
    if len(sys.argv) < 3:
        print("Usage: python standalone_pn_import.py <database_url> <jen_csv> [craig_csv]")
        print("\nExample (Jen only - RECOMMENDED):")
        print("  python standalone_pn_import.py \\")
        print("    'postgresql+asyncpg://user:pass@host:5432/postgres' \\")
        print("    jen_export.csv")
        print("\nExample (Both coaches):")
        print("  python standalone_pn_import.py \\")
        print("    'postgresql+asyncpg://user:pass@host:5432/postgres' \\")
        print("    jen_export.csv \\")
        print("    craig_export.csv")
        sys.exit(1)

    db_url = sys.argv[1]
    jen_csv = sys.argv[2]
    craig_csv = sys.argv[3] if len(sys.argv) > 3 else None
    update_existing = True

    print(f"Database: {db_url}")
    print(f"Jen CSV: {jen_csv}")
    print(f"Craig CSV: {craig_csv or '(not provided - Jen only)'}")
    print(f"Update existing: {update_existing}")
    print()

    # Create engine
    engine = create_async_engine(db_url, echo=False)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    # If craig_csv not provided, create empty temp file
    import tempfile
    temp_craig = None
    if not craig_csv:
        temp_craig = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
        temp_craig.write('Exercise,URL,Description\n')  # Empty CSV with headers
        temp_craig.close()
        craig_csv = temp_craig.name

    try:
        async with session_maker() as session:
            result = await import_pn_movements_csv(
                session=session,
                jen_csv_path=jen_csv,
                craig_csv_path=craig_csv,
                update_existing=update_existing,
            )
            created = result['created']
            updated = result['updated']
            skipped = result['skipped']
    finally:
        # Clean up temp file
        if temp_craig:
            import os
            os.unlink(temp_craig.name)

        print(f"\n✓ Import complete!")
        print(f"  Created: {created}")
        print(f"  Updated: {updated}")
        print(f"  Skipped: {skipped}")
        print(f"  Total:   {created + updated + skipped}")


if __name__ == "__main__":
    asyncio.run(main())
