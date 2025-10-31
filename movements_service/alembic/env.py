from __future__ import annotations

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, text
from alembic import context

from movements.repository.database import Base
from movements.web.config import Config

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Convert asyncpg URL to psycopg2 URL for synchronous operation
database_url = str(Config.DATABASE_URL).replace("postgresql+asyncpg://", "postgresql://")
config.set_main_option("sqlalchemy.url", database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        version_table_schema="movements",
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # Connection args for pgbouncer compatibility
    connectable = engine_from_config(
        config.get_section(config.config_ini_section) or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args={
            "options": "-c statement_timeout=30000"  # 30 second timeout
        }
    )

    with connectable.connect() as connection:
        # Create schema if it doesn't exist
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS movements"))
        connection.commit()

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            version_table_schema="movements",
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 