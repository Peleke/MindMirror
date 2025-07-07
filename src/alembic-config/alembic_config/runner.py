"""High-level Alembic command runner."""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from alembic.config import Config
from alembic import command

from .config import get_alembic_config


def run_alembic_command(cmd: str, *args: str, **kwargs) -> int:
    """Run an Alembic command with the configured setup."""
    config = get_alembic_config()
    
    # Get the command function
    cmd_func = getattr(command, cmd, None)
    if cmd_func is None:
        raise ValueError(f"Unknown Alembic command: {cmd}")
    
    # Debug: Check if there's a --sql flag in the args
    if "--sql" in args:
        print(f"DEBUG: Found --sql flag in args: {args}", file=sys.stderr)
    
    # Run the command
    try:
        cmd_func(config, *args, **kwargs)
        return 0
    except Exception as e:
        print(f"Error running Alembic command '{cmd}': {e}", file=sys.stderr)
        return 1


def run_migration(action: str, revision: Optional[str] = None, **kwargs) -> int:
    """Run a migration action (upgrade, downgrade, etc.)."""
    if action == "upgrade":
        return run_alembic_command("upgrade", revision or "head")
    elif action == "downgrade":
        if not revision:
            raise ValueError("Revision required for downgrade")
        return run_alembic_command("downgrade", revision)
    elif action == "revision":
        # For revision, we need to handle autogenerate properly
        return run_alembic_command(
            "revision",
            message="revision" or "Auto-generated migration",
            autogenerate=True,
        )
    elif action == "current":
        return run_alembic_command("current")
    elif action == "history":
        return run_alembic_command("history")
    elif action == "show":
        if not revision:
            raise ValueError("Revision required for show")
        return run_alembic_command("show", revision)
    else:
        raise ValueError(f"Unknown migration action: {action}")


def init_alembic() -> int:
    """Initialize Alembic in the current project."""
    config = get_alembic_config()
    
    # Check if alembic directory already exists
    alembic_dir = Path(config.get_main_option("script_location"))
    if alembic_dir.exists():
        print("Alembic already initialized")
        return 0
    
    # Create alembic directory structure
    alembic_dir.mkdir(parents=True, exist_ok=True)
    versions_dir = alembic_dir / "versions"
    versions_dir.mkdir(exist_ok=True)
    
    # Create __init__.py files
    (alembic_dir / "__init__.py").touch()
    (versions_dir / "__init__.py").touch()
    
    print("Alembic initialized successfully")
    return 0


def check_health() -> int:
    """Check database connection and migration status."""
    try:
        # Try to get current revision
        result = run_alembic_command("current")
        if result == 0:
            print("✅ Database connection and migrations are healthy")
            return 0
        else:
            print("❌ Database connection or migration issues detected")
            return 1
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return 1


def reset_database() -> int:
    """Reset database by downgrading to base and upgrading to head."""
    print("⚠️  This will reset the database. Are you sure? (y/N): ", end="")
    response = input().strip().lower()
    
    if response not in ['y', 'yes']:
        print("Reset cancelled")
        return 0
    
    print("Downgrading to base...")
    result = run_alembic_command("downgrade", "base")
    if result != 0:
        print("Failed to downgrade to base")
        return result
    
    print("Upgrading to head...")
    result = run_alembic_command("upgrade", "head")
    if result != 0:
        print("Failed to upgrade to head")
        return result
    
    print("Database reset completed successfully")
    return 0 