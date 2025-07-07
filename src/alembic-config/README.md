# Alembic Config Package

This package provides Alembic configuration and utilities for MindMirror database migrations.

## Purpose

- Centralizes Alembic configuration for all MindMirror services
- Provides a clean interface for database migration operations
- Handles both local development and production Supabase environments
- Integrates with the central models aggregator

## Installation

```bash
# Install in development mode
poetry install

# Or install in another project
poetry add ../src/alembic-config
```

## Usage

```python
from alembic_config import get_alembic_config, run_migration

# Get configured Alembic config
config = get_alembic_config()

# Run migrations
run_migration(config, "upgrade", "head")
```

## Configuration

The package automatically detects the environment and configures:
- Database URL (local or Supabase)
- SQLAlchemy driver (psycopg2 for local, asyncpg for Supabase)
- Model metadata from the central aggregator
- Migration scripts location

## Environment Variables

- `DATABASE_URL`: Database connection string
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase service role key
- `DB_DRIVER`: Override database driver (psycopg2/asyncpg) 