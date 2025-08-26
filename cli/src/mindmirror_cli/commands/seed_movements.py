from __future__ import annotations

import asyncio
import os
from typing import Optional

import typer
from rich.console import Console
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from sqlalchemy import text

from mindmirror_cli.core.utils import (
    set_environment,
    get_current_environment,
    is_live_environment,
)

console = Console()
app = typer.Typer(name="seed-movements", help="Seed movements into DB from CSV", invoke_without_command=True)


async def _execute(from_csv: str, database_url: Optional[str], schema: str, env: Optional[str]):
    if env:
        set_environment(env)
        console.print(f"[blue]Using environment: {get_current_environment()}[/blue]")

    if not database_url:
        if is_live_environment():
            supabase_db_url = os.getenv("SUPABASE_DATABASE_URL")
            if not supabase_db_url:
                console.print("[red]SUPABASE_DATABASE_URL must be set when using --env live, or provide --db-url explicitly[/red]")
                raise typer.Exit(1)
            database_url = supabase_db_url
        else:
            database_url = "postgresql+asyncpg://movements_user:movements_password@movements_postgres:5432/swae_movements"

    console.print(f"[cyan]DB:[/cyan] {database_url.split('@')[-1]}")

    engine = create_async_engine(
        database_url,
        future=True,
        poolclass=NullPool,
        execution_options={"schema_translate_map": {"movements": schema}},
        connect_args={"timeout": 10},  # fail fast on unreachable DB
    )
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    # Importer uses the service module
    from movements_service.movements.repository.database import Base  # type: ignore
    from movements_service.movements.service.csv_importer import import_movements_csv  # type: ignore

    # Ensure schema exists
    async with engine.begin() as conn:
        await conn.execute(text('CREATE SCHEMA IF NOT EXISTS "movements"'))
        await conn.run_sync(Base.metadata.create_all)

    # Run importer
    async with async_session() as session:
        n = await import_movements_csv(session, from_csv)
        await session.commit()
        console.print(f"[green]Imported {n} movements from {from_csv}[/green]")

    await engine.dispose()


@app.callback()
def main(
    from_csv: Optional[str] = typer.Option(None, "--from-csv", help="Path to CSV file"),
    database_url: Optional[str] = typer.Option(None, "--db-url", help="Full DATABASE_URL to use (overrides env)"),
    schema: str = typer.Option("movements", "--schema", help="DB schema name to use"),
    env: Optional[str] = typer.Option(None, "--env", "-e", help="Environment (local, live)"),
):
    """If called without subcommand, run the seeding directly using provided options."""
    if from_csv:
        asyncio.run(_execute(from_csv, database_url, schema, env))


@app.command()
def run(
    from_csv: str = typer.Option(..., "--from-csv", help="Path to CSV file"),
    database_url: Optional[str] = typer.Option(None, "--db-url", help="Full DATABASE_URL to use (overrides env)"),
    schema: str = typer.Option("movements", "--schema", help="DB schema name to use"),
    env: Optional[str] = typer.Option(None, "--env", "-e", help="Environment (local, live)"),
):
    """Seed movements from a CSV file into the configured database."""
    asyncio.run(_execute(from_csv, database_url, schema, env)) 