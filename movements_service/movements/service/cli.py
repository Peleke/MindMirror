import argparse
import asyncio
from sqlalchemy import text

from movements.repository.database import get_session_factory, Base
from .csv_importer import import_movements_csv


async def _ensure_schema_and_tables():
    sf = get_session_factory()
    async with sf() as s:
        await s.execute(text('CREATE SCHEMA IF NOT EXISTS "movements"'))
        await s.commit()
    async with sf().bind.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def _cmd_import_csv(path: str):
    await _ensure_schema_and_tables()
    sf = get_session_factory()
    async with sf() as s:
        n = await import_movements_csv(s, path)
        print(f"Imported {n} rows from {path}")


def main():
    parser = argparse.ArgumentParser(prog="movements-cli")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_import = sub.add_parser("import-csv", help="Import movements from CSV file")
    p_import.add_argument("--path", required=True, help="Path to CSV inside container")

    args = parser.parse_args()

    if args.cmd == "import-csv":
        asyncio.run(_cmd_import_csv(args.path))
    else:
        parser.error("Unknown command")


if __name__ == "__main__":
    main() 