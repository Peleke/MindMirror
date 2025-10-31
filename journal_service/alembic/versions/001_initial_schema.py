"""initial schema - journal service database

Revision ID: 001
Revises:
Create Date: 2025-10-23 17:00:00

This migration creates the complete journal service schema including:
- journal_entries table (with habit_template_id link added later)
- journal_entry_type_enum (GRATITUDE, REFLECTION, FREEFORM)
- All indexes

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

SCHEMA = 'journal'


def upgrade() -> None:
    # Ensure schema
    op.execute(sa.text(f'CREATE SCHEMA IF NOT EXISTS "{SCHEMA}"'))

    # Note: journal_entry_type_enum is created automatically by SQLAlchemy
    # when the journal_entries table is created (no manual CREATE TYPE needed)

    # journal_entries table
    op.create_table(
        'journal_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('modified_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('entry_type', sa.String(length=50), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('habit_template_id', postgresql.UUID(as_uuid=True), nullable=True),
        schema=SCHEMA,
    )

    # Indexes
    op.create_index('ix_journal_entries_user_id', 'journal_entries', ['user_id'], schema=SCHEMA)
    op.create_index('ix_journal_entries_habit_template_id', 'journal_entries', ['habit_template_id'], schema=SCHEMA)


def downgrade() -> None:
    """Drop entire journal schema and all contents."""
    op.drop_table('journal_entries', schema=SCHEMA)
    op.execute(sa.text(f'DROP SCHEMA IF EXISTS "{SCHEMA}" CASCADE'))
