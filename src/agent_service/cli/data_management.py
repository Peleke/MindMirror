"""
Data management CLI for agent service.

This module provides command-line tools for:
- Building knowledge bases from documents
- Initializing vector stores
- Managing traditions and collections
- Health checks and diagnostics
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from agent_service.qdrant_data_processing import QdrantKnowledgeBaseBuilder
from agent_service.app.clients.qdrant_client import QdrantClient
from config import DATA_DIR

console = Console()
logger = logging.getLogger(__name__)


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def cli(verbose: bool):
    """Agent Service Data Management CLI."""
    if verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)


@cli.command()
@click.option(
    "--source-dirs",
    "-s",
    multiple=True,
    help="Source directories containing tradition documents",
)
@click.option(
    "--tradition",
    "-t",
    help="Specific tradition to build (default: all)",
)
@click.option(
    "--clear-existing",
    is_flag=True,
    help="Clear existing knowledge base before building",
)
@click.option(
    "--data-dir",
    default=DATA_DIR,
    help="Base data directory",
)
def build_knowledge_base(
    source_dirs: tuple,
    tradition: Optional[str],
    clear_existing: bool,
    data_dir: str,
):
    """Build knowledge base from documents."""
    source_dirs_list = list(source_dirs) if source_dirs else [data_dir]
    
    console.print(f"[bold blue]Building knowledge base...[/bold blue]")
    console.print(f"Source directories: {source_dirs_list}")
    if tradition:
        console.print(f"Tradition: {tradition}")
    if clear_existing:
        console.print("[yellow]Clearing existing knowledge base[/yellow]")

    async def _build():
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
                return 1
            progress.update(task, description="✅ Qdrant connected")

        # Build knowledge base
        try:
            result = await builder.build_all_traditions(
                source_dirs=source_dirs_list,
                specific_tradition=tradition,
                clear_existing=clear_existing,
            )
            
            # Display results
            table = Table(title="Knowledge Base Build Results")
            table.add_column("Tradition", style="cyan")
            table.add_column("Files Processed", style="green")
            table.add_column("Chunks Created", style="blue")
            table.add_column("Status", style="yellow")
            
            for tradition_name, stats in result.items():
                status = "✅ Success" if stats.get("success", False) else "❌ Failed"
                table.add_row(
                    tradition_name,
                    str(stats.get("processed_files", 0)),
                    str(stats.get("total_chunks", 0)),
                    status,
                )
            
            console.print(table)
            return 0
            
        except Exception as e:
            console.print(f"[red]❌ Build failed: {e}[/red]")
            return 1

    return asyncio.run(_build())


@cli.command()
@click.option(
    "--tradition",
    "-t",
    help="Specific tradition to check (default: all)",
)
def health_check(tradition: Optional[str]):
    """Check health of knowledge base and services."""
    console.print("[bold blue]Health Check[/bold blue]")
    
    async def _check():
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
                    return 1
            except Exception as e:
                progress.update(task, description=f"❌ Qdrant error: {e}")
                return 1

        # Check collections
        try:
            collections = qdrant_client.client.get_collections()
            
            table = Table(title="Knowledge Base Collections")
            table.add_column("Collection", style="cyan")
            table.add_column("Points", style="green")
            table.add_column("Status", style="yellow")
            
            for collection in collections.collections:
                if tradition and not collection.name.startswith(tradition):
                    continue
                    
                try:
                    info = qdrant_client.client.get_collection(collection.name)
                    points = info.points_count if hasattr(info, "points_count") else "Unknown"
                    status = "✅ Active" if points > 0 else "⚠️ Empty"
                    table.add_row(collection.name, str(points), status)
                except Exception as e:
                    table.add_row(collection.name, "Error", f"❌ {e}")
            
            console.print(table)
            return 0
            
        except Exception as e:
            console.print(f"[red]❌ Collection check failed: {e}[/red]")
            return 1

    return asyncio.run(_check())


@cli.command()
@click.option(
    "--tradition",
    "-t",
    required=True,
    help="Tradition to clear",
)
@click.option(
    "--confirm",
    is_flag=True,
    help="Skip confirmation prompt",
)
def clear_tradition(tradition: str, confirm: bool):
    """Clear a tradition's knowledge base."""
    if not confirm:
        if not click.confirm(f"Are you sure you want to clear tradition '{tradition}'?"):
            console.print("[yellow]Operation cancelled[/yellow]")
            return 0
    
    console.print(f"[bold red]Clearing tradition: {tradition}[/bold red]")
    
    async def _clear():
        qdrant_client = QdrantClient()
        
        try:
            # Get collection name
            collection_name = qdrant_client.get_knowledge_collection_name(tradition)
            
            # Delete collection
            await qdrant_client.delete_collection(collection_name)
            console.print(f"[green]✅ Cleared tradition: {tradition}[/green]")
            return 0
            
        except Exception as e:
            console.print(f"[red]❌ Failed to clear tradition: {e}[/red]")
            return 1

    return asyncio.run(_clear())


@cli.command()
@click.option(
    "--source-dirs",
    "-s",
    multiple=True,
    help="Source directories to scan",
)
@click.option(
    "--data-dir",
    default=DATA_DIR,
    help="Base data directory",
)
def list_traditions(source_dirs: tuple, data_dir: str):
    """List available traditions and their document sources."""
    source_dirs_list = list(source_dirs) if source_dirs else [data_dir]
    
    console.print("[bold blue]Available Traditions[/bold blue]")
    
    async def _list():
        builder = QdrantKnowledgeBaseBuilder()
        
        traditions = builder.discover_source_directories(source_dirs_list)
        
        if not traditions:
            console.print("[yellow]No traditions found[/yellow]")
            return 0
        
        table = Table(title="Traditions")
        table.add_column("Tradition", style="cyan")
        table.add_column("Source Directories", style="green")
        table.add_column("Document Count", style="blue")
        
        for tradition, dirs in traditions.items():
            # Count documents
            total_docs = 0
            for dir_path in dirs:
                total_docs += len(list(dir_path.glob("*.pdf")))
                total_docs += len(list(dir_path.glob("*.txt")))
            
            table.add_row(
                tradition,
                "\n".join(str(d) for d in dirs),
                str(total_docs),
            )
        
        console.print(table)
        return 0

    return asyncio.run(_list())


if __name__ == "__main__":
    sys.exit(cli()) 