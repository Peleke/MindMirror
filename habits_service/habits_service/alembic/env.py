from __future__ import with_statement

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context

from habits_service.habits_service.app.config import get_settings
from habits_service.habits_service.app.db.models import Base


settings = get_settings()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = settings.database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        version_table_schema=settings.database_schema,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=True,
        version_table_schema=settings.database_schema,
    )

    with context.begin_transaction():
        context.run_migrations()
        # Safety: create missing columns if schema out-of-sync
        schema = settings.database_schema
        connection.execute(text(f"ALTER TABLE {schema}.lesson_templates ADD COLUMN IF NOT EXISTS segments_json JSON NULL"))
        connection.execute(text(f"ALTER TABLE {schema}.lesson_templates ADD COLUMN IF NOT EXISTS default_segment VARCHAR NULL"))


async def run_migrations_online() -> None:
    connectable = AsyncEngine(
        pool.NullPool,
        url=settings.database_url,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())


