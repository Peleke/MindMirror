"""initial schema - complete habits service database

Revision ID: 001
Revises:
Create Date: 2025-10-22 13:30:00

This migration consolidates the complete habits service schema including:
- All 16 tables (templates, events, ACL, provenance)
- CASCADE delete behaviors for program hierarchies
- Soft delete functionality for program templates
- All indexes, constraints, and triggers

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create habits schema if it doesn't exist
    op.execute('CREATE SCHEMA IF NOT EXISTS habits')

    # ============================================================
    # BASE TABLES (No foreign keys)
    # ============================================================

    # habit_templates
    op.create_table(
        'habit_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('short_description', sa.Text(), nullable=True),
        sa.Column('hero_image_url', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('level', sa.Integer(), nullable=True),
        sa.Column('default_duration_days', sa.Integer(), nullable=False, server_default='7'),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
        schema='habits'
    )
    op.create_index(op.f('ix_habits_habit_templates_slug'), 'habit_templates', ['slug'], unique=False, schema='habits')

    # lesson_templates
    op.create_table(
        'lesson_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('markdown_content', sa.Text(), nullable=False),
        sa.Column('subtitle', sa.Text(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('est_read_minutes', sa.Integer(), nullable=True),
        sa.Column('hero_image_url', sa.String(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('content_hash', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('metadata_json', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('segments_json', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('default_segment', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
        schema='habits'
    )
    op.create_index(op.f('ix_habits_lesson_templates_slug'), 'lesson_templates', ['slug'], unique=False, schema='habits')

    # program_templates (includes soft delete column from migration 3)
    op.create_table(
        'program_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('subtitle', sa.Text(), nullable=True),
        sa.Column('hero_image_url', sa.String(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('content_hash', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),  # Soft delete support
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
        schema='habits'
    )
    op.create_index(op.f('ix_habits_program_templates_slug'), 'program_templates', ['slug'], unique=False, schema='habits')

    # Partial unique index on title for active (not deleted) rows
    op.execute(
        """
        CREATE UNIQUE INDEX program_templates_title_active_idx
        ON habits.program_templates (title)
        WHERE is_deleted = false;
        """
    )

    # ============================================================
    # RELATIONSHIP TABLES (With foreign keys - CASCADE behavior)
    # ============================================================

    # program_step_templates (CASCADE delete from migration 2)
    op.create_table(
        'program_step_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('program_template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sequence_index', sa.Integer(), nullable=False),
        sa.Column('habit_template_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('duration_days', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['habit_template_id'], ['habits.habit_templates.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['program_template_id'], ['habits.program_templates.id'], ondelete='CASCADE'),  # CASCADE
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('program_template_id', 'sequence_index', name='uq_program_step_sequence'),
        schema='habits'
    )
    op.create_index(op.f('ix_habits_program_step_templates_habit_template_id'), 'program_step_templates', ['habit_template_id'], unique=False, schema='habits')
    op.create_index(op.f('ix_habits_program_step_templates_program_template_id'), 'program_step_templates', ['program_template_id'], unique=False, schema='habits')

    # step_lesson_templates (CASCADE delete from migration 2)
    op.create_table(
        'step_lesson_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('program_step_template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('day_index', sa.Integer(), nullable=False),
        sa.Column('lesson_template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['lesson_template_id'], ['habits.lesson_templates.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['program_step_template_id'], ['habits.program_step_templates.id'], ondelete='CASCADE'),  # CASCADE
        sa.PrimaryKeyConstraint('id'),
        schema='habits'
    )
    op.create_index('ix_step_day', 'step_lesson_templates', ['program_step_template_id', 'day_index'], unique=False, schema='habits')
    op.create_index(op.f('ix_habits_step_lesson_templates_lesson_template_id'), 'step_lesson_templates', ['lesson_template_id'], unique=False, schema='habits')
    op.create_index(op.f('ix_habits_step_lesson_templates_program_step_template_id'), 'step_lesson_templates', ['program_step_template_id'], unique=False, schema='habits')

    # lesson_segments
    op.create_table(
        'lesson_segments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('lesson_template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('day_index_within_step', sa.Integer(), nullable=True),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('subtitle', sa.Text(), nullable=True),
        sa.Column('markdown_content', sa.Text(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('metadata_json', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['lesson_template_id'], ['habits.lesson_templates.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        schema='habits'
    )
    op.create_index('ix_lesson_segments_lesson', 'lesson_segments', ['lesson_template_id'], unique=False, schema='habits')
    op.create_index(op.f('ix_habits_lesson_segments_lesson_template_id'), 'lesson_segments', ['lesson_template_id'], unique=False, schema='habits')

    # step_daily_plan
    op.create_table(
        'step_daily_plan',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('program_step_template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('day_index', sa.Integer(), nullable=False),
        sa.Column('habit_variant_text', sa.Text(), nullable=True),
        sa.Column('journal_prompt_text', sa.Text(), nullable=True),
        sa.Column('lesson_segment_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('metadata_json', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['lesson_segment_id'], ['habits.lesson_segments.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['program_step_template_id'], ['habits.program_step_templates.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('program_step_template_id', 'day_index', name='uq_step_daily_plan_day'),
        schema='habits'
    )
    op.create_index('ix_step_daily_plan_step_day', 'step_daily_plan', ['program_step_template_id', 'day_index'], unique=False, schema='habits')
    op.create_index(op.f('ix_habits_step_daily_plan_lesson_segment_id'), 'step_daily_plan', ['lesson_segment_id'], unique=False, schema='habits')
    op.create_index(op.f('ix_habits_step_daily_plan_program_step_template_id'), 'step_daily_plan', ['program_step_template_id'], unique=False, schema='habits')

    # ============================================================
    # USER DATA TABLES
    # ============================================================

    # user_program_assignments (RESTRICT from migration 2)
    op.create_table(
        'user_program_assignments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('program_template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['program_template_id'], ['habits.program_templates.id'], ondelete='RESTRICT'),  # RESTRICT
        sa.PrimaryKeyConstraint('id'),
        schema='habits'
    )
    op.create_index(op.f('ix_habits_user_program_assignments_program_template_id'), 'user_program_assignments', ['program_template_id'], unique=False, schema='habits')
    op.create_index(op.f('ix_habits_user_program_assignments_user_id'), 'user_program_assignments', ['user_id'], unique=False, schema='habits')

    # habit_events
    op.create_table(
        'habit_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('habit_template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('program_assignment_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('response', sa.String(), nullable=False),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['habit_template_id'], ['habits.habit_templates.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['program_assignment_id'], ['habits.user_program_assignments.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'habit_template_id', 'date', 'program_assignment_id', name='uq_habit_event_uniqueness'),
        schema='habits'
    )
    op.create_index(op.f('ix_habits_habit_events_habit_template_id'), 'habit_events', ['habit_template_id'], unique=False, schema='habits')
    op.create_index(op.f('ix_habits_habit_events_program_assignment_id'), 'habit_events', ['program_assignment_id'], unique=False, schema='habits')
    op.create_index(op.f('ix_habits_habit_events_user_id'), 'habit_events', ['user_id'], unique=False, schema='habits')

    # lesson_events
    op.create_table(
        'lesson_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('lesson_template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('program_assignment_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['lesson_template_id'], ['habits.lesson_templates.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['program_assignment_id'], ['habits.user_program_assignments.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        schema='habits'
    )
    op.create_index(op.f('ix_habits_lesson_events_lesson_template_id'), 'lesson_events', ['lesson_template_id'], unique=False, schema='habits')
    op.create_index(op.f('ix_habits_lesson_events_program_assignment_id'), 'lesson_events', ['program_assignment_id'], unique=False, schema='habits')
    op.create_index(op.f('ix_habits_lesson_events_user_id'), 'lesson_events', ['user_id'], unique=False, schema='habits')

    # journal_task_events
    op.create_table(
        'journal_task_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='habits'
    )
    op.create_index(op.f('ix_habits_journal_task_events_user_id'), 'journal_task_events', ['user_id'], unique=False, schema='habits')

    # lesson_tasks
    op.create_table(
        'lesson_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('lesson_template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('segment_ids_json', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('program_enrollment_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['lesson_template_id'], ['habits.lesson_templates.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'lesson_template_id', 'date', name='uq_lesson_task_uniqueness'),
        schema='habits'
    )
    op.create_index('ix_lesson_tasks_user_date', 'lesson_tasks', ['user_id', 'date'], unique=False, schema='habits')
    op.create_index(op.f('ix_habits_lesson_tasks_lesson_template_id'), 'lesson_tasks', ['lesson_template_id'], unique=False, schema='habits')
    op.create_index(op.f('ix_habits_lesson_tasks_user_id'), 'lesson_tasks', ['user_id'], unique=False, schema='habits')

    # ============================================================
    # ACL & PROVENANCE TABLES
    # ============================================================

    # template_access
    op.create_table(
        'template_access',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('kind', sa.String(), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('permission', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("permission in ('owner','edit','view')", name='ck_template_access_permission'),
        sa.CheckConstraint("kind in ('habit','lesson','program')", name='ck_template_access_kind'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('kind', 'template_id', 'user_id', 'permission', name='uq_template_access'),
        schema='habits'
    )
    op.create_index('ix_template_access_template', 'template_access', ['kind', 'template_id'], unique=False, schema='habits')
    op.create_index('ix_template_access_user_kind', 'template_access', ['user_id', 'kind'], unique=False, schema='habits')
    op.create_index(op.f('ix_habits_template_access_template_id'), 'template_access', ['template_id'], unique=False, schema='habits')
    op.create_index(op.f('ix_habits_template_access_user_id'), 'template_access', ['user_id'], unique=False, schema='habits')

    # template_provenance
    op.create_table(
        'template_provenance',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('kind', sa.String(), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('origin', sa.String(), nullable=False),
        sa.Column('origin_user_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("origin in ('system','user','import')", name='ck_template_provenance_origin'),
        sa.CheckConstraint("kind in ('habit','lesson','program')", name='ck_template_provenance_kind'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('kind', 'template_id', name='uq_template_provenance_template'),
        schema='habits'
    )
    op.create_index(op.f('ix_habits_template_provenance_origin_user_id'), 'template_provenance', ['origin_user_id'], unique=False, schema='habits')
    op.create_index(op.f('ix_habits_template_provenance_template_id'), 'template_provenance', ['template_id'], unique=False, schema='habits')

    # ============================================================
    # TRIGGERS & FUNCTIONS (from migration 3)
    # ============================================================

    # Guard: prevent assigning users to deleted programs
    op.execute(
        """
        CREATE OR REPLACE FUNCTION habits.prevent_assign_to_deleted()
        RETURNS trigger AS $$
        BEGIN
          IF EXISTS (
            SELECT 1 FROM habits.program_templates pt
            WHERE pt.id = NEW.program_template_id AND pt.is_deleted = true
          ) THEN
            RAISE EXCEPTION 'Cannot assign user to a deleted program (%).', NEW.program_template_id
            USING ERRCODE = 'check_violation';
          END IF;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE TRIGGER trg_prevent_assign_deleted_program
        BEFORE INSERT OR UPDATE ON habits.user_program_assignments
        FOR EACH ROW EXECUTE FUNCTION habits.prevent_assign_to_deleted();
        """
    )

    # Helper: archive function to soft-delete a program
    op.execute(
        """
        CREATE OR REPLACE FUNCTION habits.archive_program_template(p_id uuid)
        RETURNS void LANGUAGE plpgsql AS $$
        BEGIN
          UPDATE habits.program_templates SET is_deleted = true WHERE id = p_id;
        END $$;
        """
    )


def downgrade() -> None:
    """Drop entire habits schema and all contents."""
    # Drop triggers and functions
    op.execute('DROP TRIGGER IF EXISTS trg_prevent_assign_deleted_program ON habits.user_program_assignments')
    op.execute('DROP FUNCTION IF EXISTS habits.prevent_assign_to_deleted()')
    op.execute('DROP FUNCTION IF EXISTS habits.archive_program_template(uuid)')

    # Drop tables in reverse order (respecting FK dependencies)
    op.drop_table('template_provenance', schema='habits')
    op.drop_table('template_access', schema='habits')
    op.drop_table('lesson_tasks', schema='habits')
    op.drop_table('journal_task_events', schema='habits')
    op.drop_table('lesson_events', schema='habits')
    op.drop_table('habit_events', schema='habits')
    op.drop_table('user_program_assignments', schema='habits')
    op.drop_table('step_daily_plan', schema='habits')
    op.drop_table('lesson_segments', schema='habits')
    op.drop_table('step_lesson_templates', schema='habits')
    op.drop_table('program_step_templates', schema='habits')
    op.drop_table('program_templates', schema='habits')
    op.drop_table('lesson_templates', schema='habits')
    op.drop_table('habit_templates', schema='habits')

    # Drop schema
    op.execute('DROP SCHEMA IF EXISTS habits CASCADE')
