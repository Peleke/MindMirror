"""Alembic environment configuration."""

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Add src to Python path for model imports
current_dir = Path(__file__).parent.parent
src_path = current_dir.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from alembic_config.utils import get_database_url, get_driver, get_schema_name
from alembic_config.config import get_metadata

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = get_metadata()

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_database_url()
    driver = get_driver()
    
    if driver == "asyncpg":
        url = url.replace("postgresql://", "postgresql+asyncpg://")
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=get_schema_name(),
        include_schemas=True,
        # Don't pass schema to engine creation
        schema=get_schema_name(),
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Get database URL and configure engine
    url = get_database_url()
    driver = get_driver()
    
    # For asyncpg, we need to use psycopg2 for Alembic operations
    # Alembic doesn't handle async drivers well in this context
    if driver == "asyncpg":
        # Convert asyncpg URL to psycopg2 URL for Alembic
        url = url.replace("postgresql+asyncpg://", "postgresql://")
        url = url.replace("postgresql://", "postgresql+psycopg2://")
    
    # Update config with the URL
    config.set_main_option("sqlalchemy.url", url)
    
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    print(target_metadata)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema=get_schema_name(),
            include_schemas=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 