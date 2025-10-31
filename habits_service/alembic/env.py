from __future__ import with_statement

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool, text
from alembic import context

from habits.app.config import get_settings
from habits.app.db.models import Base
from habits.app.db import tables  # noqa: F401 ensure models are imported


settings = get_settings()
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = str(settings.database_url).replace("postgresql+asyncpg://", "postgresql://")
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


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Convert asyncpg URL to psycopg2 URL for synchronous operation
    database_url = str(settings.database_url).replace("postgresql+asyncpg://", "postgresql://")

    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = database_url

    # Connection args for pgbouncer compatibility
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args={
            "options": "-c statement_timeout=30000"  # 30 second timeout
        }
    )

    with connectable.connect() as connection:
        # Create schema if it doesn't exist
        connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {settings.database_schema}"))
        connection.commit()

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            version_table_schema=settings.database_schema,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
