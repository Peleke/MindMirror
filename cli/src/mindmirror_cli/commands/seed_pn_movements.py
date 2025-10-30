"""Seed Precision Nutrition movements from Jen and Craig CSVs."""
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
app = typer.Typer(name="seed-pn-movements", help="Seed PN movements from Jen/Craig CSVs")


async def _execute(
    jen_csv: str,
    craig_csv: str,
    database_url: Optional[str],
    schema: str,
    env: Optional[str],
    update_existing: bool
):
    """Execute the PN movements seeding."""
    if env:
        set_environment(env)
        console.print(f"[blue]Using environment: {get_current_environment()}[/blue]")

    # Determine database URL
    if not database_url:
        if is_live_environment():
            # For staging/production, use SUPABASE_DATABASE_URL or movements-specific URL
            supabase_db_url = os.getenv("SUPABASE_DATABASE_URL") or os.getenv("MOVEMENTS_DATABASE_URL")
            if not supabase_db_url:
                console.print(
                    "[red]SUPABASE_DATABASE_URL or MOVEMENTS_DATABASE_URL must be set "
                    "when using live environments, or provide --db-url explicitly[/red]"
                )
                raise typer.Exit(1)
            database_url = supabase_db_url
        else:
            # Local Docker default
            database_url = "postgresql+asyncpg://movements_user:movements_password@movements_postgres:5432/swae_movements"

    console.print(f"[cyan]DB:[/cyan] {database_url.split('@')[-1]}")
    console.print(f"[cyan]Jen CSV:[/cyan] {jen_csv}")
    console.print(f"[cyan]Craig CSV:[/cyan] {craig_csv}")
    console.print(f"[cyan]Update existing:[/cyan] {update_existing}")

    # Create engine
    engine = create_async_engine(
        database_url,
        future=True,
        poolclass=NullPool,
        execution_options={"schema_translate_map": {"movements": schema}},
        connect_args={"timeout": 10},
    )
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    # Import the PN importer
    from movements.repository.database import Base  # type: ignore
    from movements.service.pn_csv_importer import import_pn_movements_csv  # type: ignore

    # Ensure schema and tables exist
    async with engine.begin() as conn:
        await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
        await conn.run_sync(Base.metadata.create_all)

    # Run importer
    async with async_session() as session:
        console.print("[yellow]Importing PN movements...[/yellow]")
        results = await import_pn_movements_csv(
            session,
            jen_csv,
            craig_csv,
            update_existing=update_existing
        )

        console.print(f"\n[green]✓ Import complete![/green]")
        console.print(f"  Created: {results['created']}")
        console.print(f"  Updated: {results['updated']}")
        console.print(f"  Skipped: {results['skipped']}")
        console.print(f"  Total:   {results['total']}")

    await engine.dispose()


@app.command()
def run(
    jen_csv: str = typer.Option(
        ...,
        "--jen-csv",
        help="Path to jen_export.csv (female coach videos)"
    ),
    craig_csv: str = typer.Option(
        ...,
        "--craig-csv",
        help="Path to craig_export.csv (male coach videos)"
    ),
    database_url: Optional[str] = typer.Option(
        None,
        "--db-url",
        help="Full DATABASE_URL to use (overrides env)"
    ),
    schema: str = typer.Option(
        "movements",
        "--schema",
        help="DB schema name to use"
    ),
    env: Optional[str] = typer.Option(
        None,
        "--env", "-e",
        help="Environment (local, staging, production)"
    ),
    update_existing: bool = typer.Option(
        True,
        "--update-existing/--skip-existing",
        help="Update existing movements or skip them"
    ),
):
    """
    Seed Precision Nutrition movements from Jen and Craig CSVs.

    Both CSVs contain the same exercises but with different coach videos:
    - Jen (female coach) videos -> long_video_url
    - Craig (male coach) videos -> short_video_url

    Examples:
        # Local Docker environment
        mindmirror seed-pn-movements \\
            --jen-csv data/fitness/pn/data/jen_export.csv \\
            --craig-csv data/fitness/pn/data/craig_export.csv

        # Staging environment
        mindmirror seed-pn-movements \\
            --jen-csv data/fitness/pn/data/jen_export.csv \\
            --craig-csv data/fitness/pn/data/craig_export.csv \\
            --env staging
    """
    asyncio.run(_execute(jen_csv, craig_csv, database_url, schema, env, update_existing))


if __name__ == "__main__":
    app()
