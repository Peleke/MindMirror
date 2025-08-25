from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None

SCHEMA = 'movements'


def upgrade() -> None:
    op.execute(sa.text(f'CREATE SCHEMA IF NOT EXISTS "{SCHEMA}"'))

    op.create_table(
        'movements',
        sa.Column('id', postgresql.UUID(), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()')),
        sa.Column('modified_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()')),
        sa.Column('slug', sa.String(), nullable=False, unique=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('difficulty', sa.String()),
        sa.Column('body_region', sa.String()),
        sa.Column('target_muscle_group', sa.String()),
        sa.Column('prime_mover_muscle', sa.String()),
        sa.Column('posture', sa.String()),
        sa.Column('arm_mode', sa.String()),
        sa.Column('arm_pattern', sa.String()),
        sa.Column('grip', sa.String()),
        sa.Column('load_position', sa.String()),
        sa.Column('leg_pattern', sa.String()),
        sa.Column('foot_elevation', sa.String()),
        sa.Column('combo_type', sa.String()),
        sa.Column('mechanics', sa.String()),
        sa.Column('laterality', sa.String()),
        sa.Column('primary_classification', sa.String()),
        sa.Column('force_type', sa.String()),
        sa.Column('archetype', sa.String()),
        sa.Column('short_video_url', sa.String()),
        sa.Column('long_video_url', sa.String()),
        sa.Column('gif_url', sa.String()),
        sa.Column('source', sa.String()),
        sa.Column('external_id', sa.String()),
        sa.Column('is_public', sa.Boolean(), server_default=sa.text('true')),
        sa.Column('user_id', sa.String()),
        schema=SCHEMA,
    )
    op.create_index('ix_movements_name', f'{SCHEMA}.movements', ['name'])
    op.create_index('ix_movements_body_region', f'{SCHEMA}.movements', ['body_region'])
    op.create_index('ix_movements_user_id', f'{SCHEMA}.movements', ['user_id'])
    op.create_index('ix_movements_external_id', f'{SCHEMA}.movements', ['external_id'])

    op.create_table(
        'movement_aliases',
        sa.Column('id', postgresql.UUID(), primary_key=True),
        sa.Column('movement_id', postgresql.UUID(), nullable=False),
        sa.Column('alias', sa.String(), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()')),
        schema=SCHEMA,
    )
    op.create_index('ix_alias_movement_id', f'{SCHEMA}.movement_aliases', ['movement_id'])

    op.create_table(
        'movement_muscle_links',
        sa.Column('movement_id', postgresql.UUID(), primary_key=True),
        sa.Column('muscle_name', sa.String(), primary_key=True),
        sa.Column('role', sa.String(), primary_key=True),
        schema=SCHEMA,
    )
    op.create_index('ix_muscle_movement_id', f'{SCHEMA}.movement_muscle_links', ['movement_id'])

    op.create_table(
        'movement_equipment_links',
        sa.Column('movement_id', postgresql.UUID(), primary_key=True),
        sa.Column('equipment_name', sa.String(), primary_key=True),
        sa.Column('role', sa.String(), primary_key=True),
        sa.Column('item_count', sa.Integer()),
        schema=SCHEMA,
    )
    op.create_index('ix_equipment_movement_id', f'{SCHEMA}.movement_equipment_links', ['movement_id'])

    op.create_table(
        'movement_pattern_links',
        sa.Column('movement_id', postgresql.UUID(), primary_key=True),
        sa.Column('pattern_name', sa.String(), primary_key=True),
        sa.Column('position', sa.Integer(), nullable=False, server_default='1'),
        schema=SCHEMA,
    )
    op.create_index('ix_pattern_movement_id', f'{SCHEMA}.movement_pattern_links', ['movement_id'])

    op.create_table(
        'movement_plane_links',
        sa.Column('movement_id', postgresql.UUID(), primary_key=True),
        sa.Column('plane_name', sa.String(), primary_key=True),
        sa.Column('position', sa.Integer(), nullable=False, server_default='1'),
        schema=SCHEMA,
    )
    op.create_index('ix_plane_movement_id', f'{SCHEMA}.movement_plane_links', ['movement_id'])

    op.create_table(
        'movement_tag_links',
        sa.Column('movement_id', postgresql.UUID(), primary_key=True),
        sa.Column('tag_name', sa.String(), primary_key=True),
        schema=SCHEMA,
    )
    op.create_index('ix_tag_movement_id', f'{SCHEMA}.movement_tag_links', ['movement_id'])

    op.create_table(
        'movement_instructions',
        sa.Column('movement_id', postgresql.UUID(), primary_key=True),
        sa.Column('position', sa.Integer(), primary_key=True),
        sa.Column('text', sa.String(), nullable=False),
        schema=SCHEMA,
    )
    op.create_index('ix_instr_movement_id', f'{SCHEMA}.movement_instructions', ['movement_id'])


def downgrade() -> None:
    op.drop_table('movement_instructions', schema=SCHEMA)
    op.drop_table('movement_tag_links', schema=SCHEMA)
    op.drop_table('movement_plane_links', schema=SCHEMA)
    op.drop_table('movement_pattern_links', schema=SCHEMA)
    op.drop_table('movement_equipment_links', schema=SCHEMA)
    op.drop_table('movement_muscle_links', schema=SCHEMA)
    op.drop_table('movement_aliases', schema=SCHEMA)
    op.drop_index('ix_movements_external_id', table_name='movements', schema=SCHEMA)
    op.drop_index('ix_movements_user_id', table_name='movements', schema=SCHEMA)
    op.drop_index('ix_movements_body_region', table_name='movements', schema=SCHEMA)
    op.drop_index('ix_movements_name', table_name='movements', schema=SCHEMA)
    op.drop_table('movements', schema=SCHEMA) 