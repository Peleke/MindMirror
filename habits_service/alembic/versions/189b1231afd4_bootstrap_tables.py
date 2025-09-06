"""add cascade deletes for program templates and step lesson templates; restrict user assignments

Revision ID: 2a3f4c9d1cde
Revises: 189b1231afd4
Create Date: 2025-09-06 00:00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2a3f4c9d1cde'
down_revision = '189b1231afd4'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # program_step_templates -> program_templates ON DELETE CASCADE
    op.execute(
        """
        ALTER TABLE habits.program_step_templates
        DROP CONSTRAINT IF EXISTS program_step_templates_program_template_id_fkey;
        ALTER TABLE habits.program_step_templates
        ADD CONSTRAINT program_step_templates_program_template_id_fkey
        FOREIGN KEY (program_template_id)
        REFERENCES habits.program_templates(id)
        ON DELETE CASCADE;
        """
    )

    # step_lesson_templates -> program_step_templates ON DELETE CASCADE
    op.execute(
        """
        ALTER TABLE habits.step_lesson_templates
        DROP CONSTRAINT IF EXISTS step_lesson_templates_program_step_template_id_fkey;
        ALTER TABLE habits.step_lesson_templates
        ADD CONSTRAINT step_lesson_templates_program_step_template_id_fkey
        FOREIGN KEY (program_step_template_id)
        REFERENCES habits.program_step_templates(id)
        ON DELETE CASCADE;
        """
    )

    # user_program_assignments -> program_templates ON DELETE RESTRICT (explicit)
    op.execute(
        """
        ALTER TABLE habits.user_program_assignments
        DROP CONSTRAINT IF EXISTS user_program_assignments_program_template_id_fkey;
        ALTER TABLE habits.user_program_assignments
        ADD CONSTRAINT user_program_assignments_program_template_id_fkey
        FOREIGN KEY (program_template_id)
        REFERENCES habits.program_templates(id)
        ON DELETE RESTRICT;
        """
    )


def downgrade() -> None:
    # Best-effort revert to NO ACTION (default) for all three relations
    op.execute(
        """
        ALTER TABLE habits.program_step_templates
        DROP CONSTRAINT IF EXISTS program_step_templates_program_template_id_fkey;
        ALTER TABLE habits.program_step_templates
        ADD CONSTRAINT program_step_templates_program_template_id_fkey
        FOREIGN KEY (program_template_id)
        REFERENCES habits.program_templates(id);
        """
    )

    op.execute(
        """
        ALTER TABLE habits.step_lesson_templates
        DROP CONSTRAINT IF EXISTS step_lesson_templates_program_step_template_id_fkey;
        ALTER TABLE habits.step_lesson_templates
        ADD CONSTRAINT step_lesson_templates_program_step_template_id_fkey
        FOREIGN KEY (program_step_template_id)
        REFERENCES habits.program_step_templates(id);
        """
    )

    op.execute(
        """
        ALTER TABLE habits.user_program_assignments
        DROP CONSTRAINT IF EXISTS user_program_assignments_program_template_id_fkey;
        ALTER TABLE habits.user_program_assignments
        ADD CONSTRAINT user_program_assignments_program_template_id_fkey
        FOREIGN KEY (program_template_id)
        REFERENCES habits.program_templates(id);
        """
    )


