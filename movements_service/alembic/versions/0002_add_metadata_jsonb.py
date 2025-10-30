"""add metadata jsonb column

Revision ID: 0002_add_metadata_jsonb
Revises: 0001_init
Create Date: 2025-10-29

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0002_add_metadata_jsonb'
down_revision = '0001_init'
branch_labels = None
depends_on = None

SCHEMA = 'movements'


def upgrade() -> None:
    """Add metadata JSONB column to movements table for flexible data storage."""
    op.add_column(
        'movements',
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        schema=SCHEMA
    )


def downgrade() -> None:
    """Remove metadata column."""
    op.drop_column('movements', 'metadata', schema=SCHEMA)
