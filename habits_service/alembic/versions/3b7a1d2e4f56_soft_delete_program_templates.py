"""soft delete for program_templates and guard assignments to deleted programs

Revision ID: 3b7a1d2e4f56
Revises: 2a3f4c9d1cde
Create Date: 2025-09-06 00:15:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3b7a1d2e4f56'
down_revision = '2a3f4c9d1cde'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1) Add soft-delete column
    op.execute(
        """
        ALTER TABLE habits.program_templates
        ADD COLUMN IF NOT EXISTS is_deleted boolean NOT NULL DEFAULT false;
        """
    )

    # 2) Partial unique index on title for active (not deleted) rows
    op.execute(
        """
        DO $$
        BEGIN
          IF NOT EXISTS (
            SELECT 1 FROM pg_indexes WHERE schemaname = 'habits' AND indexname = 'program_templates_title_active_idx'
          ) THEN
            CREATE UNIQUE INDEX program_templates_title_active_idx
            ON habits.program_templates (title)
            WHERE is_deleted = false;
          END IF;
        END$$;
        """
    )

    # 3) Guard: prevent assigning users to deleted programs
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
        DO $$
        BEGIN
          IF NOT EXISTS (
            SELECT 1 FROM pg_trigger
            WHERE tgname = 'trg_prevent_assign_deleted_program'
          ) THEN
            CREATE TRIGGER trg_prevent_assign_deleted_program
            BEFORE INSERT OR UPDATE ON habits.user_program_assignments
            FOR EACH ROW EXECUTE FUNCTION habits.prevent_assign_to_deleted();
          END IF;
        END$$;
        """
    )

    # 4) Optional helper: archive function to soft-delete a program
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
    # Drop helper function
    op.execute(
        """
        DROP FUNCTION IF EXISTS habits.archive_program_template(uuid);
        """
    )

    # Drop trigger and trigger function
    op.execute(
        """
        DROP TRIGGER IF EXISTS trg_prevent_assign_deleted_program ON habits.user_program_assignments;
        DROP FUNCTION IF EXISTS habits.prevent_assign_to_deleted();
        """
    )

    # Drop partial unique index
    op.execute(
        """
        DROP INDEX IF EXISTS habits.program_templates_title_active_idx;
        """
    )

    # Drop column (note: will fail if views depend on it; adjust if needed)
    op.execute(
        """
        ALTER TABLE habits.program_templates
        DROP COLUMN IF EXISTS is_deleted;
        """
    ) 