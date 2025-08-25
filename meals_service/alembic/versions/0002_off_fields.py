from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0002_off_fields'
down_revision = '0001_init'
branch_labels = None
depends_on = None

SCHEMA = 'meals'


def upgrade() -> None:
    with op.batch_alter_table('food_items', schema=SCHEMA) as batch_op:
        batch_op.add_column(sa.Column('brand', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('thumbnail_url', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('source', sa.String(length=16), nullable=False, server_default='local'))
        batch_op.add_column(sa.Column('external_source', sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column('external_id', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('external_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True))

    # Helpful index for import idempotency/lookups
    op.execute(sa.text('CREATE INDEX IF NOT EXISTS ix_meals_food_items_ext ON meals.food_items(external_source, external_id)'))


def downgrade() -> None:
    with op.batch_alter_table('food_items', schema=SCHEMA) as batch_op:
        batch_op.drop_column('external_metadata')
        batch_op.drop_column('external_id')
        batch_op.drop_column('external_source')
        batch_op.drop_column('source')
        batch_op.drop_column('thumbnail_url')
        batch_op.drop_column('brand')

    op.execute(sa.text('DROP INDEX IF EXISTS meals.ix_meals_food_items_ext')) 