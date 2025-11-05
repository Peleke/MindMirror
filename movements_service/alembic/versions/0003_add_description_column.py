"""add description column

Revision ID: 0003_add_description_column
Revises: 0002_add_metadata_jsonb
Create Date: 2025-11-03

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0003_add_description_column'
down_revision = '0002_add_metadata_jsonb'
branch_labels = None
depends_on = None

SCHEMA = 'movements'


def upgrade() -> None:
    """Add description column to movements table."""
    op.add_column(
        'movements',
        sa.Column('description', sa.String(), nullable=True),
        schema=SCHEMA
    )


def downgrade() -> None:
    """Remove description column."""
    op.drop_column('movements', 'description', schema=SCHEMA)
