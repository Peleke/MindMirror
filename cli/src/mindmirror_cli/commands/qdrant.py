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

console = Console()
logger = logging.getLogger(__name__)

app = typer.Typer(name="qdrant", help="Qdrant knowledge base operations")


@app.command()
def build(
    tradition: Optional[str] = typer.Option(None, "--tradition", "-t", help="Specific tradition to build"),
    source_dirs: List[str] = typer.Option(["local_gcs_bucket", "pdfs"], "--source-dirs", "-s", help="Source directories"),
    clear_existing: bool = typer.Option(False, "--clear-existing", help="Clear existing knowledge base"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    """Build knowledge base from documents."""
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
def health():
    """Check Qdrant service health."""
    async def _health():
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
    source_dirs: List[str] = typer.Option(["local_gcs_bucket", "pdfs"], "--source-dirs", "-s", help="Source directories to scan")
):
    """List available traditions and their document sources."""
    async def _list():
        console.print("[bold blue]Available Traditions[/bold blue]")

        # Use the tradition loader to discover traditions
        tradition_loader = create_tradition_loader()
        traditions = tradition_loader.list_traditions()

        if not traditions:
            console.print("[yellow]No traditions found[/yellow]")
            return

        table = Table(title="Traditions")
        table.add_column("Tradition", style="cyan")
        table.add_column("Source", style="green")
        table.add_column("Document Count", style="blue")

        for tradition in traditions:
            # Get document count for this tradition
            documents = tradition_loader.get_tradition_documents(tradition)
            doc_count = len(documents)
            
            # Determine source (GCS or local)
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
def list_collections():
    """List Qdrant collections."""
    async def _list():
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
