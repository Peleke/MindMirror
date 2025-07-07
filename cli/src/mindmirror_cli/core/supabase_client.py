"""Supabase database client for MindMirror CLI."""

import asyncio
import logging
import os
from pathlib import Path
from typing import Dict, Optional

import asyncpg
from dotenv import load_dotenv
from rich.console import Console
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables from .env file
# Look for .env in CLI directory first, then project root
cli_dir = Path(__file__).parent.parent.parent  # This is cli/src/
cli_root = cli_dir.parent  # This is cli/
project_root = cli_root.parent  # This is the project root

# Try to load .env from CLI directory first
env_file = cli_root / ".env"
if not env_file.exists():
    # Fall back to project root
    env_file = project_root / ".env"

console = Console()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Debug: Show what paths we're checking
console.print(f"[blue]Looking for .env file...[/blue]")
console.print(f"[blue]CLI root: {cli_root}[/blue]")
console.print(f"[blue]Project root: {project_root}[/blue]")
console.print(f"[blue]Checking CLI .env: {env_file} (exists: {env_file.exists()})[/blue]")

if env_file.exists():
    load_dotenv(env_file)
    console.print(f"[green]✅ Loaded environment from: {env_file}[/green]")
    
    # Debug: Show what we loaded
    console.print(f"[blue]DB_HOST: {os.getenv('DB_HOST', 'NOT SET')}[/blue]")
    console.print(f"[blue]DB_PORT: {os.getenv('DB_PORT', 'NOT SET')}[/blue]")
    console.print(f"[blue]DB_NAME: {os.getenv('DB_NAME', 'NOT SET')}[/blue]")
    console.print(f"[blue]DB_USER: {os.getenv('DB_USER', 'NOT SET')}[/blue]")
    console.print(f"[blue]DB_PASS: {'SET' if os.getenv('DB_PASS') else 'NOT SET'}[/blue]")
else:
    console.print(f"[yellow]⚠️ No .env file found, using system environment variables[/yellow]")

class SupabaseClient:
    """Client for managing Supabase/PostgreSQL database connections."""

    def __init__(self):
        """Initialize the Supabase client."""
        self.db_url = self._get_database_url()
        self.engine = None

    def _get_database_url(self) -> str:
        """Get database URL from environment variables."""
        return (
            f"postgresql+asyncpg://"
            f"{os.getenv('DB_USER', 'postgres')}:"
            f"{os.getenv('DB_PASS', 'password')}@"
            f"{os.getenv('DB_HOST', 'localhost')}:"
            f"{os.getenv('DB_PORT', '5432')}/"
            f"{os.getenv('DB_NAME', 'mindmirror')}"
        )

    def _get_connection_params(self) -> Dict[str, str]:
        """Get connection parameters for asyncpg."""
        params = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "database": os.getenv("DB_NAME", "mindmirror"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASS", "password"),
        }
        
        # Debug logging (without password)
        debug_params = params.copy()
        debug_params["password"] = "***" if debug_params["password"] != "password" else "default"
        logger.debug(f"Database connection parameters: {debug_params}")
        
        return params

    async def health_check(self) -> bool:
        """Check database connection health."""
        try:
            # Use asyncpg for direct connection check
            conn_params = self._get_connection_params()
            conn = await asyncpg.connect(**conn_params)
            try:
                result = await conn.fetchval("SELECT 1")
                return result == 1
            finally:
                await conn.close()
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    async def get_connection_info(self) -> Dict[str, str]:
        """Get database connection information."""
        try:
            conn_params = self._get_connection_params()
            conn = await asyncpg.connect(**conn_params)
            try:
                # Get database info
                result = await conn.fetchrow("SELECT current_database(), current_user, version()")
                
                return {
                    "database": result[0],
                    "user": result[1],
                    "version": result[2].split()[0],
                    "host": conn_params["host"],
                    "port": conn_params["port"],
                }
            finally:
                await conn.close()
        except Exception as e:
            logger.error(f"Failed to get connection info: {e}")
            return {}

    async def check_alembic_version_table(self) -> bool:
        """Check if alembic_version table exists."""
        try:
            conn_params = self._get_connection_params()
            conn = await asyncpg.connect(**conn_params)
            try:
                result = await conn.fetchval(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'alembic_version'
                    )
                    """
                )
                return result
            finally:
                await conn.close()
        except Exception as e:
            logger.error(f"Failed to check alembic_version table: {e}")
            return False

    async def get_current_revision(self) -> Optional[str]:
        """Get current Alembic revision."""
        try:
            conn_params = self._get_connection_params()
            conn = await asyncpg.connect(**conn_params)
            try:
                result = await conn.fetchval("SELECT version_num FROM alembic_version")
                return result
            finally:
                await conn.close()
        except Exception as e:
            logger.error(f"Failed to get current revision: {e}")
            return None

    def get_engine(self):
        """Get SQLAlchemy engine."""
        if not self.engine:
            self.engine = create_engine(self.db_url, echo=False)
        return self.engine

    async def test_connection(self) -> Dict[str, any]:
        """Test database connection and return detailed status."""
        result = {
            "connected": False,
            "error": None,
            "info": {},
        }

        try:
            # Test basic connection
            if await self.health_check():
                result["connected"] = True
                result["info"] = await self.get_connection_info()
                
                # Check Alembic status
                has_alembic_table = await self.check_alembic_version_table()
                result["alembic_initialized"] = has_alembic_table
                
                if has_alembic_table:
                    current_revision = await self.get_current_revision()
                    result["current_revision"] = current_revision
            else:
                result["error"] = "Failed to connect to database"
                
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Connection test failed: {e}")

        return result


# Convenience function for async operations
async def test_supabase_connection() -> Dict[str, any]:
    """Test Supabase connection and return status."""
    client = SupabaseClient()
    return await client.test_connection() 