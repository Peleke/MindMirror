"""Supabase database management commands."""

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Import from our new alembic-config package
from alembic_config import (
    run_alembic_command,
    run_migration,
    init_alembic,
    check_health,
    reset_database,
    get_database_url,
    is_supabase_environment,
    set_environment,
    get_current_environment,
    get_schema_name
)

console = Console()
app = typer.Typer(name="supabase", help="Supabase database management")


def _set_environment(env: str, schema: str = None) -> None:
    """Set the environment and schema for Alembic operations."""
    if env:
        set_environment(env)
        console.print(f"[blue]Using environment: {env}[/blue]")
    else:
        current_env = get_current_environment()
        console.print(f"[blue]Using environment: {current_env}[/blue]")
    
    if schema:
        # Set schema via environment variable
        import os
        os.environ["DB_SCHEMA"] = schema
        console.print(f"[blue]Using schema: {schema}[/blue]")
    else:
        current_schema = get_schema_name()
        console.print(f"[blue]Using schema: {current_schema}[/blue]")


@app.command()
def init(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    env: str = typer.Option(None, "--env", "-e", help="Environment (supabase, local)"),
    schema: str = typer.Option(None, "--schema", "-s", help="Database schema name"),
):
    """Initialize Alembic for database migrations."""
    _set_environment(env, schema)
    console.print("[bold blue]Initializing Alembic...[/bold blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Initializing Alembic...", total=None)
        
        result = init_alembic()
        
        if result == 0:
            progress.update(task, description="✅ Alembic initialized successfully")
            console.print("[green]✅ Alembic initialized successfully![/green]")
            console.print("[green]You can now use 'mindmirror supabase revision' to create new migrations[/green]")
        else:
            progress.update(task, description="❌ Failed to initialize Alembic")
            console.print("[red]❌ Failed to initialize Alembic[/red]")
            raise typer.Exit(1)


@app.command()
def revision(
    message: str = typer.Argument(..., help="Migration message"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    env: str = typer.Option(None, "--env", "-e", help="Environment (supabase, local)"),
    schema: str = typer.Option(None, "--schema", "-s", help="Database schema name"),
):
    """Create a new migration revision."""
    _set_environment(env, schema)
    console.print(f"[bold blue]Creating migration: {message}[/bold blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Creating migration revision...", total=None)
        
        result = run_migration("revision", message)
        
        if result == 0:
            progress.update(task, description="✅ Migration revision created")
            console.print("[green]✅ Migration revision created successfully![/green]")
            console.print("[green]Use 'mindmirror supabase upgrade' to apply the migration[/green]")
        else:
            progress.update(task, description="❌ Failed to create migration")
            console.print("[red]❌ Failed to create migration revision[/red]")
            raise typer.Exit(1)


@app.command()
def upgrade(
    target: str = typer.Option("head", "--target", "-t", help="Target revision"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    env: str = typer.Option(None, "--env", "-e", help="Environment (supabase, local)"),
    schema: str = typer.Option(None, "--schema", "-s", help="Database schema name"),
):
    """Upgrade database to target revision."""
    _set_environment(env, schema)
    console.print(f"[bold blue]Upgrading database to {target}...[/bold blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Upgrading database...", total=None)
        
        result = run_migration("upgrade", target)
        
        if result == 0:
            progress.update(task, description="✅ Database upgraded successfully")
            console.print(f"[green]✅ Database upgraded to {target} successfully![/green]")
        else:
            progress.update(task, description="❌ Failed to upgrade database")
            console.print("[red]❌ Failed to upgrade database[/red]")
            raise typer.Exit(1)


@app.command()
def downgrade(
    target: str = typer.Argument(..., help="Target revision to downgrade to"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    env: str = typer.Option(None, "--env", "-e", help="Environment (supabase, local)"),
    schema: str = typer.Option(None, "--schema", "-s", help="Database schema name"),
):
    """Downgrade database to target revision."""
    _set_environment(env, schema)
    console.print(f"[bold blue]Downgrading database to {target}...[/bold blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Downgrading database...", total=None)
        
        result = run_migration("downgrade", target)
        
        if result == 0:
            progress.update(task, description="✅ Database downgraded successfully")
            console.print(f"[green]✅ Database downgraded to {target} successfully![/green]")
        else:
            progress.update(task, description="❌ Failed to downgrade database")
            console.print("[red]❌ Failed to downgrade database[/red]")
            raise typer.Exit(1)


@app.command()
def status(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    env: str = typer.Option(None, "--env", "-e", help="Environment (supabase, local)"),
    schema: str = typer.Option(None, "--schema", "-s", help="Database schema name"),
):
    """Show current migration status."""
    _set_environment(env, schema)
    console.print("[bold blue]Checking migration status...[/bold blue]")
    
    # Get current revision
    result = run_alembic_command("current")
    
    if result == 0:
        console.print("[green]✅ Migration status retrieved successfully[/green]")
    else:
        console.print("[red]❌ Failed to get migration status[/red]")
        raise typer.Exit(1)


@app.command()
def history(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    env: str = typer.Option(None, "--env", "-e", help="Environment (supabase, local)"),
    schema: str = typer.Option(None, "--schema", "-s", help="Database schema name"),
):
    """Show migration history."""
    _set_environment(env, schema)
    console.print("[bold blue]Retrieving migration history...[/bold blue]")
    
    result = run_alembic_command("history")
    
    if result == 0:
        console.print("[green]✅ Migration history retrieved successfully[/green]")
    else:
        console.print("[red]❌ Failed to get migration history[/red]")
        raise typer.Exit(1)


@app.command()
def health(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    env: str = typer.Option(None, "--env", "-e", help="Environment (supabase, local)"),
    schema: str = typer.Option(None, "--schema", "-s", help="Database schema name"),
):
    """Check database and migration health."""
    _set_environment(env, schema)
    console.print("[bold blue]Checking database health...[/bold blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Checking database connection...", total=None)
        
        # Show database info
        db_url = get_database_url()
        is_supabase = is_supabase_environment()
        current_env = get_current_environment()
        
        progress.update(task, description="✅ Database connection info retrieved")
        
        # Create info table
        table = Table(title="Database Health Check")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Environment", current_env.title())
        table.add_row("Database URL", db_url.split("@")[-1] if "@" in db_url else db_url)
        table.add_row("Connection", "✅ Connected" if is_supabase else "✅ Local")
        
        console.print(table)
        
        # Check migration status
        task = progress.add_task("Checking migration status...", total=None)
        result = check_health()
        
        if result == 0:
            progress.update(task, description="✅ Migrations healthy")
            console.print("[green]✅ Database and migrations are healthy![/green]")
        else:
            progress.update(task, description="❌ Migration issues detected")
            console.print("[red]❌ Database or migration issues detected[/red]")
            raise typer.Exit(1)


@app.command()
def reset(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    env: str = typer.Option(None, "--env", "-e", help="Environment (supabase, local)"),
    schema: str = typer.Option(None, "--schema", "-s", help="Database schema name"),
):
    """Reset database by downgrading to base and upgrading to head."""
    _set_environment(env, schema)
    console.print("[bold red]⚠️  This will reset the database![/bold red]")
    
    result = reset_database()
    
    if result == 0:
        console.print("[green]✅ Database reset completed successfully![/green]")
    else:
        console.print("[red]❌ Failed to reset database[/red]")
        raise typer.Exit(1)


 