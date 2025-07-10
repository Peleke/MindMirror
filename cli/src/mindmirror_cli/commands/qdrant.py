"""Qdrant subcommand for MindMirror CLI."""

import asyncio
import logging
from typing import List, Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from mindmirror_cli.core.builder import QdrantKnowledgeBaseBuilder
from mindmirror_cli.core.client import QdrantClient
from mindmirror_cli.core.tradition_loader import create_tradition_loader
from mindmirror_cli.core.utils import set_environment, get_current_environment, is_live_environment

console = Console()
logger = logging.getLogger(__name__)

app = typer.Typer(name="qdrant", help="Qdrant knowledge base operations")


def _set_environment(env: str) -> None:
    """Set the environment for Qdrant operations."""
    if env:
        set_environment(env)
        console.print(f"[blue]Using environment: {env}[/blue]")
    else:
        current_env = get_current_environment()
        console.print(f"[blue]Using environment: {current_env}[/blue]")


@app.command()
def build(
    tradition: Optional[str] = typer.Option(None, "--tradition", "-t", help="Specific tradition to build"),
    source_dirs: List[str] = typer.Option(["local_gcs_bucket", "pdfs"], "--source-dirs", "-s", help="Source directories"),
    clear_existing: bool = typer.Option(False, "--clear-existing", help="Clear existing knowledge base"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    env: str = typer.Option(None, "--env", "-e", help="Environment (local, live)"),
):
    """Build knowledge base from documents."""
    _set_environment(env)
    
    if verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    async def _build():
        console.print(f"[bold blue]Building knowledge base...[/bold blue]")
        console.print(f"Source directories: {source_dirs}")
        if tradition:
            console.print(f"Tradition: {tradition}")
        if clear_existing:
            console.print("[yellow]Clearing existing knowledge base[/yellow]")

        builder = QdrantKnowledgeBaseBuilder()

        # Health check
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Checking Qdrant connection...", total=None)
            if not await builder.health_check():
                console.print("[red]❌ Qdrant connection failed[/red]")
                raise typer.Exit(1)
            progress.update(task, description="✅ Qdrant connected")

        # Build knowledge base
        try:
            result = await builder.build_all_traditions(
                source_dirs=source_dirs,
                specific_tradition=tradition,
                clear_existing=clear_existing,
            )

            # Display results
            table = Table(title="Knowledge Base Build Results")
            table.add_column("Tradition", style="cyan")
            table.add_column("Files Processed", style="green")
            table.add_column("Chunks Created", style="blue")
            table.add_column("Status", style="yellow")

            for tradition_name, stats in result.get("traditions", {}).items():
                status = "✅ Success" if stats.get("status") == "success" else "❌ Failed"
                table.add_row(
                    tradition_name,
                    str(stats.get("processed_files", 0)),
                    str(stats.get("processed_chunks", 0)),
                    status,
                )

            console.print(table)
            
            if result.get("status") == "success":
                console.print(f"[green]✅ Build completed successfully![/green]")
                console.print(f"📊 Total chunks: {result.get('total_chunks', 0)}")
                console.print(f"⏱️  Duration: {result.get('duration_seconds', 0):.2f}s")
            else:
                console.print(f"[red]❌ Build failed: {result.get('message', 'Unknown error')}[/red]")
                raise typer.Exit(1)

        except Exception as e:
            console.print(f"[red]❌ Build failed: {e}[/red]")
            raise typer.Exit(1)

    asyncio.run(_build())


@app.command()
def seed(
    tradition: Optional[str] = typer.Option(None, "--tradition", "-t", help="Specific tradition to seed"),
    source_dirs: List[str] = typer.Option(["local_gcs_bucket", "pdfs"], "--source-dirs", "-s", help="Source directories"),
    clear_existing: bool = typer.Option(False, "--clear-existing", help="Clear existing knowledge base"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    env: str = typer.Option("live", "--env", "-e", help="Environment (local, live)"),
):
    """Seed live knowledge base from documents."""
    _set_environment(env)
    
    if verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    async def _seed():
        console.print(f"[bold blue]Seeding live knowledge base...[/bold blue]")
        console.print(f"Source directories: {source_dirs}")
        if tradition:
            console.print(f"Tradition: {tradition}")
        if clear_existing:
            console.print("[yellow]Clearing existing knowledge base[/yellow]")

        builder = QdrantKnowledgeBaseBuilder()

        # Health check
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Checking Qdrant connection...", total=None)
            if not await builder.health_check():
                console.print("[red]❌ Qdrant connection failed[/red]")
                raise typer.Exit(1)
            progress.update(task, description="✅ Qdrant connected")

        # Seed knowledge base
        try:
            result = await builder.build_all_traditions(
                source_dirs=source_dirs,
                specific_tradition=tradition,
                clear_existing=clear_existing,
            )

            # Display results
            table = Table(title="Knowledge Base Seed Results")
            table.add_column("Tradition", style="cyan")
            table.add_column("Files Processed", style="green")
            table.add_column("Chunks Created", style="blue")
            table.add_column("Status", style="yellow")

            for tradition_name, stats in result.get("traditions", {}).items():
                status = "✅ Success" if stats.get("status") == "success" else "❌ Failed"
                table.add_row(
                    tradition_name,
                    str(stats.get("processed_files", 0)),
                    str(stats.get("processed_chunks", 0)),
                    status,
                )

            console.print(table)
            
            if result.get("status") == "success":
                console.print(f"[green]✅ Seed completed successfully![/green]")
                console.print(f"📊 Total chunks: {result.get('total_chunks', 0)}")
                console.print(f"⏱️  Duration: {result.get('duration_seconds', 0):.2f}s")
            else:
                console.print(f"[red]❌ Seed failed: {result.get('message', 'Unknown error')}[/red]")
                raise typer.Exit(1)

        except Exception as e:
            console.print(f"[red]❌ Seed failed: {e}[/red]")
            raise typer.Exit(1)

    asyncio.run(_seed())


@app.command()
def health(
    env: str = typer.Option(None, "--env", "-e", help="Environment (local, live)"),
):
    """Check Qdrant service health."""
    async def _health():
        _set_environment(env)
        console.print("[bold blue]Health Check[/bold blue]")

        qdrant_client = QdrantClient()

        # Check Qdrant connection
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Checking Qdrant...", total=None)
            try:
                health = await qdrant_client.health_check()
                if health:
                    progress.update(task, description="✅ Qdrant healthy")
                else:
                    progress.update(task, description="❌ Qdrant unhealthy")
                    raise typer.Exit(1)
            except Exception as e:
                progress.update(task, description=f"❌ Qdrant error: {e}")
                raise typer.Exit(1)

        # Check collections
        try:
            collections = await qdrant_client.list_collections()

            if not collections:
                console.print("📭 No collections found in Qdrant")
                return

            table = Table(title="Knowledge Base Collections")
            table.add_column("Collection", style="cyan")
            table.add_column("Points", style="green")
            table.add_column("Status", style="yellow")

            for collection in collections:
                try:
                    info = await qdrant_client.get_collection_info(collection)
                    points = info.get("points_count", "Unknown") if info else "Unknown"
                    status = "✅ Active" if points and points > 0 else "⚠️ Empty"
                    table.add_row(collection, str(points), status)
                except Exception as e:
                    table.add_row(collection, "Error", f"❌ {e}")

            console.print(table)
            console.print(f"[green]✅ Qdrant is healthy with {len(collections)} collections[/green]")

        except Exception as e:
            console.print(f"[red]❌ Collection check failed: {e}[/red]")
            raise typer.Exit(1)

    asyncio.run(_health())


@app.command()
def list_traditions(
    source_dirs: List[str] = typer.Option(["local_gcs_bucket", "pdfs"], "--source-dirs", "-s", help="Source directories to scan"),
    env: str = typer.Option(None, "--env", "-e", help="Environment (local, live)"),
    project: str = typer.Option(None, "--project", "-p", help="GCP project for GCS client (optional)"),
):
    """List available traditions and their document sources. Supports --env for local/live selection and --project for GCS."""
    def _set_environment(env: str) -> None:
        if env:
            set_environment(env)
            console.print(f"[blue]Using environment: {env}[/blue]")
        else:
            current_env = get_current_environment()
            console.print(f"[blue]Using environment: {current_env}[/blue]")

    async def _list():
        _set_environment(env)
        console.print("[bold blue]Available Traditions[/bold blue]")

        # Use the tradition loader to discover traditions, passing project if provided
        from mindmirror_cli.core.tradition_loader import create_tradition_loader
        loader_kwargs = {}
        if project:
            loader_kwargs['project'] = project
        tradition_loader = create_tradition_loader(**loader_kwargs)
        traditions = tradition_loader.list_traditions()

        if not traditions:
            console.print("[yellow]No traditions found[/yellow]")
            return

        table = Table(title="Traditions")
        table.add_column("Tradition", style="cyan")
        table.add_column("Source", style="green")
        table.add_column("Document Count", style="blue")

        for tradition in traditions:
            documents = tradition_loader.get_tradition_documents(tradition)
            doc_count = len(documents)
            source = "GCS Emulator" if tradition_loader.health_check() else "Local Files"
            table.add_row(
                tradition,
                source,
                str(doc_count),
            )

        console.print(table)
        console.print(f"[green]✅ Found {len(traditions)} traditions[/green]")

    asyncio.run(_list())


@app.command()
def list_collections(
    env: str = typer.Option(None, "--env", "-e", help="Environment (local, live)"),
):
    """List Qdrant collections."""
    async def _list():
        _set_environment(env)
        console.print("[bold blue]Qdrant Collections[/bold blue]")

        qdrant_client = QdrantClient()

        try:
            collections = await qdrant_client.list_collections()

            if not collections:
                console.print("📭 No collections found in Qdrant")
                return

            table = Table(title="Collections")
            table.add_column("Collection", style="cyan")
            table.add_column("Points", style="green")
            table.add_column("Vectors", style="blue")

            for collection in collections:
                try:
                    info = await qdrant_client.get_collection_info(collection)
                    points = info.get("points_count", "Unknown") if info else "Unknown"
                    vectors = info.get("vectors_count", "Unknown") if info else "Unknown"
                    table.add_row(collection, str(points), str(vectors))
                except Exception as e:
                    table.add_row(collection, "Error", f"❌ {e}")

            console.print(table)
            console.print(f"[green]✅ Found {len(collections)} collections[/green]")

        except Exception as e:
            console.print(f"[red]❌ Failed to list collections: {e}[/red]")
            raise typer.Exit(1)

    asyncio.run(_list())


@app.command()
def create_index(
    field: str = typer.Argument(..., help="Field name to create index on"),
    collection: Optional[str] = typer.Option(None, "--collection", "-c", help="Collection name (defaults to all collections)"),
    field_type: str = typer.Option("keyword", "--type", "-t", help="Field type (keyword, integer, float, geo, text)"),
    env: str = typer.Option(None, "--env", "-e", help="Environment (local, live)"),
):
    """Create a field index for filtering in Qdrant collections."""
    async def _create_index():
        _set_environment(env)
        console.print(f"[bold blue]Creating Index[/bold blue]")
        console.print(f"Field: {field}")
        console.print(f"Type: {field_type}")
        if collection:
            console.print(f"Collection: {collection}")

        qdrant_client = QdrantClient()

        # Health check
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Checking Qdrant connection...", total=None)
            if not await qdrant_client.health_check():
                console.print("[red]❌ Qdrant connection failed[/red]")
                raise typer.Exit(1)
            progress.update(task, description="✅ Qdrant connected")

        try:
            if collection:
                # Create index on specific collection
                success = await qdrant_client.create_field_index(collection, field, field_type)
                if success:
                    console.print(f"[green]✅ Created {field_type} index on field '{field}' in collection '{collection}'[/green]")
                else:
                    console.print(f"[red]❌ Failed to create index on field '{field}' in collection '{collection}'[/red]")
                    raise typer.Exit(1)
            else:
                # Create index on all collections
                collections = await qdrant_client.list_collections()
                if not collections:
                    console.print("[yellow]No collections found[/yellow]")
                    return

                table = Table(title="Index Creation Results")
                table.add_column("Collection", style="cyan")
                table.add_column("Field", style="green")
                table.add_column("Type", style="blue")
                table.add_column("Status", style="yellow")

                success_count = 0
                for coll in collections:
                    try:
                        success = await qdrant_client.create_field_index(coll, field, field_type)
                    except Exception as e:
                        console.print(f"[red]❌ Failed for {coll}: {e}[/red]")
                        success = False
                    
                    status = "✅ Success" if success else "❌ Failed"
                    if success:
                        success_count += 1
                    table.add_row(coll, field, field_type, status)

                console.print(table)
                console.print(f"[green]✅ Created index on {success_count}/{len(collections)} collections[/green]")

        except Exception as e:
            console.print(f"[red]❌ Failed to create index: {e}[/red]")
            raise typer.Exit(1)

    asyncio.run(_create_index()) 
