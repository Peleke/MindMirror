"""initial schema - complete practices service database

Revision ID: 001
Revises:
Create Date: 2025-10-22 13:30:00

This migration creates the complete practices service schema including:
- Template tables (practice_templates, prescription_templates, movement_templates, set_templates)
- Instance tables (practice_instances, prescription_instances, movement_instances, set_instances)
- Program tables (programs, program_tags, program_practice_links)
- Enrollment and scheduling (program_enrollments, scheduled_practices)
- All enums, constraints, indexes, and foreign keys

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

SCHEMA = 'practices'


def upgrade() -> None:
    # Create practices schema
    op.execute(f'CREATE SCHEMA IF NOT EXISTS {SCHEMA}')

    # Note: enrollment_status_enum is created automatically by SQLAlchemy
    # when the program_enrollments table is created (line 174)

    # ============================================================
    # BASE TEMPLATE TABLES
    # ============================================================

    # practice_templates
    op.create_table(
        'practice_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('modified_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('title', sa.String(256), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('duration', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        schema=SCHEMA
    )

    # prescription_templates
    op.create_table(
        'prescription_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('modified_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.String(), nullable=False, server_default=''),
        sa.Column('block', sa.String(64), nullable=False, server_default='other'),
        sa.Column('practice_template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('prescribed_rounds', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['practice_template_id'], [f'{SCHEMA}.practice_templates.id'], ondelete='CASCADE'),
        sa.CheckConstraint("block IN ('warmup', 'workout', 'cooldown', 'other')", name='block_check'),
        schema=SCHEMA
    )

    # movement_templates
    op.create_table(
        'movement_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('modified_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('name', sa.String(256), nullable=False),
        sa.Column('metric_unit', sa.String(64), nullable=False, server_default='iterative'),
        sa.Column('metric_value', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('description', sa.String(), nullable=False, server_default=''),
        sa.Column('prescribed_sets', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('video_url', sa.String(), nullable=True),
        sa.Column('movement_class', sa.String(64), nullable=False, server_default='other'),
        sa.Column('rest_duration', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('exercise_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('movement_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('prescription_template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['prescription_template_id'], [f'{SCHEMA}.prescription_templates.id'], ondelete='CASCADE'),
        sa.CheckConstraint("metric_unit IN ('iterative', 'temporal', 'breath', 'other')", name='metric_unit_check'),
        sa.CheckConstraint("movement_class IN ('conditioning', 'power', 'strength', 'mobility', 'other')", name='movement_class_check'),
        schema=SCHEMA
    )

    # set_templates
    op.create_table(
        'set_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('modified_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('reps', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('load_value', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('load_unit', sa.String(64), nullable=False, server_default='pounds'),
        sa.Column('duration', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rest_duration', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('movement_template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['movement_template_id'], [f'{SCHEMA}.movement_templates.id'], ondelete='CASCADE'),
        sa.CheckConstraint("load_unit IN ('pounds', 'kilograms', 'bodyweight', 'other')", name='load_unit_check'),
        sa.CheckConstraint("reps >= 0", name='reps_check'),
        schema=SCHEMA
    )

    # ============================================================
    # PROGRAM TABLES
    # ============================================================

    # programs
    op.create_table(
        'programs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('level', sa.String(50), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('habits_program_template_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('modified_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        schema=SCHEMA
    )

    # program_tags
    op.create_table(
        'program_tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('program_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('modified_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['program_id'], [f'{SCHEMA}.programs.id']),
        sa.UniqueConstraint('program_id', 'name', name='_program_tag_name_uc'),
        schema=SCHEMA
    )

    # program_practice_links
    op.create_table(
        'program_practice_links',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('program_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('practice_template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sequence_order', sa.Integer(), nullable=False),
        sa.Column('interval_days_after', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('modified_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['program_id'], [f'{SCHEMA}.programs.id']),
        sa.ForeignKeyConstraint(['practice_template_id'], [f'{SCHEMA}.practice_templates.id']),
        sa.UniqueConstraint('program_id', 'sequence_order', name='_program_sequence_uc'),
        schema=SCHEMA
    )

    # ============================================================
    # ENROLLMENT & SCHEDULING
    # ============================================================

    # program_enrollments
    op.create_table(
        'program_enrollments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('program_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('enrolled_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.Enum('active', 'inactive', 'cancelled', 'completed', 'pending', name='enrollment_status_enum', schema=SCHEMA), nullable=False, server_default='active'),
        sa.Column('current_practice_link_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('modified_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['program_id'], [f'{SCHEMA}.programs.id']),
        sa.ForeignKeyConstraint(['current_practice_link_id'], [f'{SCHEMA}.program_practice_links.id']),
        schema=SCHEMA
    )
    op.create_index('ix_program_enrollments_user_id', 'program_enrollments', ['user_id'], schema=SCHEMA)
    op.create_index('ix_program_enrollments_enrolled_by_user_id', 'program_enrollments', ['enrolled_by_user_id'], schema=SCHEMA)

    # ============================================================
    # INSTANCE TABLES
    # ============================================================

    # practice_instances
    op.create_table(
        'practice_instances',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('modified_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False, server_default=sa.text('CURRENT_DATE')),
        sa.Column('title', sa.String(256), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('duration', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('completed_at', sa.Date(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('enrollment_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['template_id'], [f'{SCHEMA}.practice_templates.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['enrollment_id'], [f'{SCHEMA}.program_enrollments.id'], ondelete='CASCADE'),
        schema=SCHEMA
    )

    # prescription_instances
    op.create_table(
        'prescription_instances',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('modified_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.String(), nullable=False, server_default=''),
        sa.Column('block', sa.String(64), nullable=False, server_default='other'),
        sa.Column('practice_instance_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('prescribed_rounds', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('complete', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['practice_instance_id'], [f'{SCHEMA}.practice_instances.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['template_id'], [f'{SCHEMA}.prescription_templates.id'], ondelete='SET NULL'),
        sa.CheckConstraint("block IN ('warmup', 'workout', 'cooldown', 'other')", name='block_check'),
        schema=SCHEMA
    )

    # movement_instances
    op.create_table(
        'movement_instances',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('modified_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('name', sa.String(256), nullable=False),
        sa.Column('metric_unit', sa.String(64), nullable=False, server_default='iterative'),
        sa.Column('metric_value', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('description', sa.String(), nullable=False, server_default=''),
        sa.Column('prescribed_sets', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('video_url', sa.String(), nullable=True),
        sa.Column('movement_class', sa.String(64), nullable=False, server_default='other'),
        sa.Column('rest_duration', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('exercise_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('complete', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('prescription_instance_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['prescription_instance_id'], [f'{SCHEMA}.prescription_instances.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['template_id'], [f'{SCHEMA}.movement_templates.id'], ondelete='SET NULL'),
        sa.CheckConstraint("metric_unit IN ('iterative', 'temporal', 'breath', 'other')", name='metric_unit_check'),
        sa.CheckConstraint("movement_class IN ('conditioning', 'power', 'strength', 'mobility', 'other')", name='movement_class_check'),
        schema=SCHEMA
    )

    # set_instances
    op.create_table(
        'set_instances',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('modified_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('reps', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('load_value', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('load_unit', sa.String(64), nullable=False, server_default='pounds'),
        sa.Column('duration', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rest_duration', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('complete', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('perceived_exertion', sa.Integer(), nullable=False, server_default='2'),
        sa.Column('video_url', sa.String(), nullable=True),
        sa.Column('thumbnail_url', sa.String(), nullable=True),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('movement_instance_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['movement_instance_id'], [f'{SCHEMA}.movement_instances.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['template_id'], [f'{SCHEMA}.set_templates.id'], ondelete='SET NULL'),
        sa.CheckConstraint("perceived_exertion >= 1 AND perceived_exertion <= 4", name='perceived_exertion_check'),
        sa.CheckConstraint("load_unit IN ('pounds', 'kilograms', 'bodyweight', 'other')", name='load_unit_check'),
        sa.CheckConstraint("reps >= 0", name='reps_check'),
        schema=SCHEMA
    )

    # scheduled_practices
    op.create_table(
        'scheduled_practices',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('enrollment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('practice_template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('practice_instance_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('scheduled_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('modified_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['enrollment_id'], [f'{SCHEMA}.program_enrollments.id']),
        sa.ForeignKeyConstraint(['practice_template_id'], [f'{SCHEMA}.practice_templates.id']),
        sa.ForeignKeyConstraint(['practice_instance_id'], [f'{SCHEMA}.practice_instances.id']),
        schema=SCHEMA
    )
    op.create_index('ix_scheduled_practices_enrollment_id', 'scheduled_practices', ['enrollment_id'], schema=SCHEMA)
    op.create_index('ix_scheduled_practices_practice_template_id', 'scheduled_practices', ['practice_template_id'], schema=SCHEMA)


def downgrade() -> None:
    """Drop entire practices schema and all contents."""
    # Drop tables in reverse dependency order
    op.drop_table('scheduled_practices', schema=SCHEMA)
    op.drop_table('set_instances', schema=SCHEMA)
    op.drop_table('movement_instances', schema=SCHEMA)
    op.drop_table('prescription_instances', schema=SCHEMA)
    op.drop_table('practice_instances', schema=SCHEMA)
    op.drop_table('program_enrollments', schema=SCHEMA)
    op.drop_table('program_practice_links', schema=SCHEMA)
    op.drop_table('program_tags', schema=SCHEMA)
    op.drop_table('programs', schema=SCHEMA)
    op.drop_table('set_templates', schema=SCHEMA)
    op.drop_table('movement_templates', schema=SCHEMA)
    op.drop_table('prescription_templates', schema=SCHEMA)
    op.drop_table('practice_templates', schema=SCHEMA)

    # Drop enum
    op.execute('DROP TYPE IF EXISTS practices.enrollment_status_enum')

    # Drop schema
    op.execute(f'DROP SCHEMA IF EXISTS {SCHEMA} CASCADE')
