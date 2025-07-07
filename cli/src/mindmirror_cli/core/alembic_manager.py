"""Alembic migration manager for MindMirror CLI."""

import asyncio
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .supabase_client import SupabaseClient

console = Console()
logger = logging.getLogger(__name__)


class AlembicManager:
    """Manager for Alembic migration operations."""

    def __init__(self):
        """Initialize the Alembic manager."""
        self.supabase_client = SupabaseClient()
        self.alembic_ini_path = Path("alembic.ini")
        self.alembic_versions_path = Path("alembic/versions")

    def _run_alembic_command(self, command: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
        """Run an Alembic command and return the result."""
        try:
            # Ensure we're in the project root
            project_root = Path(__file__).parent.parent.parent.parent.parent
            os.chdir(project_root)
            
            # Build the full command
            full_command = ["alembic"] + command
            
            if capture_output:
                result = subprocess.run(
                    full_command,
                    capture_output=True,
                    text=True,
                    cwd=project_root,
                    env=os.environ.copy(),
                )
                return result.returncode, result.stdout, result.stderr
            else:
                result = subprocess.run(
                    full_command,
                    cwd=project_root,
                    env=os.environ.copy(),
                )
                return result.returncode, "", ""
                
        except Exception as e:
            logger.error(f"Failed to run Alembic command: {e}")
            return 1, "", str(e)

    async def check_alembic_initialized(self) -> bool:
        """Check if Alembic is initialized in the database."""
        return await self.supabase_client.check_alembic_version_table()

    async def get_current_revision(self) -> Optional[str]:
        """Get the current Alembic revision."""
        return await self.supabase_client.get_current_revision()

    async def get_migration_history(self) -> List[Dict[str, str]]:
        """Get migration history."""
        try:
            returncode, stdout, stderr = self._run_alembic_command(["history", "--verbose"])
            if returncode != 0:
                logger.error(f"Failed to get migration history: {stderr}")
                return []
            
            # Parse the history output
            migrations = []
            lines = stdout.strip().split('\n')
            current_revision = await self.get_current_revision()
            
            for line in lines:
                if line.strip() and not line.startswith('Rev:'):
                    # Parse revision line
                    parts = line.split()
                    if len(parts) >= 2:
                        revision = parts[0]
                        description = ' '.join(parts[1:])
                        migrations.append({
                            "revision": revision,
                            "description": description,
                            "current": revision == current_revision
                        })
            
            return migrations
        except Exception as e:
            logger.error(f"Failed to get migration history: {e}")
            return []

    async def get_pending_migrations(self) -> List[str]:
        """Get list of pending migrations."""
        try:
            returncode, stdout, stderr = self._run_alembic_command(["current"])
            if returncode != 0:
                logger.error(f"Failed to get current migration: {stderr}")
                return []
            
            # Get current revision
            current_revision = await self.get_current_revision()
            if not current_revision:
                return []
            
            # Get all revisions
            returncode, stdout, stderr = self._run_alembic_command(["history", "--verbose"])
            if returncode != 0:
                logger.error(f"Failed to get migration history: {stderr}")
                return []
            
            # Parse and find pending migrations
            pending = []
            lines = stdout.strip().split('\n')
            found_current = False
            
            for line in lines:
                if line.strip() and not line.startswith('Rev:'):
                    parts = line.split()
                    if len(parts) >= 1:
                        revision = parts[0]
                        if found_current:
                            pending.append(revision)
                        elif revision == current_revision:
                            found_current = True
            
            return pending
        except Exception as e:
            logger.error(f"Failed to get pending migrations: {e}")
            return []

    async def create_initial_migration(self) -> bool:
        """Create the initial migration."""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Creating initial migration...", total=None)
                
                # Create initial migration
                returncode, stdout, stderr = self._run_alembic_command([
                    "revision", "--autogenerate", "-m", "initial"
                ])
                
                if returncode != 0:
                    progress.update(task, description="❌ Failed to create initial migration")
                    console.print(f"[red]Failed to create initial migration: {stderr}[/red]")
                    return False
                
                progress.update(task, description="✅ Initial migration created")
                
                # Apply the migration
                task = progress.add_task("Applying initial migration...", total=None)
                returncode, stdout, stderr = self._run_alembic_command(["upgrade", "head"])
                
                if returncode != 0:
                    progress.update(task, description="❌ Failed to apply initial migration")
                    console.print(f"[red]Failed to apply initial migration: {stderr}[/red]")
                    return False
                
                progress.update(task, description="✅ Initial migration applied")
                return True
                
        except Exception as e:
            console.print(f"[red]Failed to create initial migration: {e}[/red]")
            return False

    async def create_revision(self, message: str) -> bool:
        """Create a new migration revision."""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Creating migration revision...", total=None)
                
                returncode, stdout, stderr = self._run_alembic_command([
                    "revision", "--autogenerate", "-m", message
                ])
                
                if returncode != 0:
                    progress.update(task, description="❌ Failed to create revision")
                    console.print(f"[red]Failed to create revision: {stderr}[/red]")
                    return False
                
                progress.update(task, description="✅ Revision created")
                
                # Show the generated file
                lines = stdout.strip().split('\n')
                for line in lines:
                    if line.startswith('Generating'):
                        console.print(f"[green]📄 {line}[/green]")
                
                return True
                
        except Exception as e:
            console.print(f"[red]Failed to create revision: {e}[/red]")
            return False

    async def upgrade_database(self, target: str = "head") -> bool:
        """Upgrade database to target revision."""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(f"Upgrading to {target}...", total=None)
                
                returncode, stdout, stderr = self._run_alembic_command(["upgrade", target])
                
                if returncode != 0:
                    progress.update(task, description=f"❌ Failed to upgrade to {target}")
                    console.print(f"[red]Failed to upgrade: {stderr}[/red]")
                    return False
                
                progress.update(task, description=f"✅ Upgraded to {target}")
                return True
                
        except Exception as e:
            console.print(f"[red]Failed to upgrade database: {e}[/red]")
            return False

    async def downgrade_database(self, target: str) -> bool:
        """Downgrade database to target revision."""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(f"Downgrading to {target}...", total=None)
                
                returncode, stdout, stderr = self._run_alembic_command(["downgrade", target])
                
                if returncode != 0:
                    progress.update(task, description=f"❌ Failed to downgrade to {target}")
                    console.print(f"[red]Failed to downgrade: {stderr}[/red]")
                    return False
                
                progress.update(task, description=f"✅ Downgraded to {target}")
                return True
                
        except Exception as e:
            console.print(f"[red]Failed to downgrade database: {e}[/red]")
            return False

    async def get_migration_status(self) -> Dict[str, any]:
        """Get comprehensive migration status."""
        try:
            # Check database connection
            connection_status = await self.supabase_client.test_connection()
            
            if not connection_status["connected"]:
                return {
                    "connected": False,
                    "error": connection_status["error"],
                    "alembic_initialized": False,
                }
            
            # Get Alembic status
            alembic_initialized = await self.check_alembic_initialized()
            current_revision = await self.get_current_revision()
            pending_migrations = await self.get_pending_migrations()
            migration_history = await self.get_migration_history()
            
            return {
                "connected": True,
                "alembic_initialized": alembic_initialized,
                "current_revision": current_revision,
                "pending_migrations": pending_migrations,
                "migration_history": migration_history,
                "connection_info": connection_status["info"],
            }
            
        except Exception as e:
            logger.error(f"Failed to get migration status: {e}")
            return {
                "connected": False,
                "error": str(e),
                "alembic_initialized": False,
            } 
