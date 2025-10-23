"""initial schema - complete meals service database

Revision ID: 001
Revises:
Create Date: 2025-10-22 13:30:00

This migration consolidates the complete meals service schema including:
- All tables (food_items, user_goals, meals, meal_foods, water_consumption)
- Open Food Facts integration fields
- meal_type enum
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

SCHEMA = 'meals'


def upgrade() -> None:
    # Ensure schema
    op.execute(sa.text(f'CREATE SCHEMA IF NOT EXISTS "{SCHEMA}"'))

    # Note: meal_type enum is created automatically by SQLAlchemy
    # when the meals table is created (line 106)

    # food_items (includes Open Food Facts fields from migration 0002)
    op.create_table(
        'food_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('modified_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('name', sa.String(256), nullable=False),
        sa.Column('serving_size', sa.Float, nullable=False),
        sa.Column('serving_unit', sa.String(64), nullable=False),
        sa.Column('calories', sa.Float, nullable=False, server_default=sa.text('0')),
        sa.Column('protein', sa.Float, nullable=False, server_default=sa.text('0')),
        sa.Column('carbohydrates', sa.Float, nullable=False, server_default=sa.text('0')),
        sa.Column('fat', sa.Float, nullable=False, server_default=sa.text('0')),
        sa.Column('saturated_fat', sa.Float),
        sa.Column('monounsaturated_fat', sa.Float),
        sa.Column('polyunsaturated_fat', sa.Float),
        sa.Column('trans_fat', sa.Float),
        sa.Column('cholesterol', sa.Float),
        sa.Column('fiber', sa.Float),
        sa.Column('sugar', sa.Float),
        sa.Column('sodium', sa.Float),
        sa.Column('vitamin_d', sa.Float),
        sa.Column('calcium', sa.Float),
        sa.Column('iron', sa.Float),
        sa.Column('potassium', sa.Float),
        sa.Column('zinc', sa.Float),
        sa.Column('user_id', sa.Text),
        sa.Column('notes', sa.Text),
        # Open Food Facts fields (from migration 0002)
        sa.Column('brand', sa.String(length=128), nullable=True),
        sa.Column('thumbnail_url', sa.Text(), nullable=True),
        sa.Column('source', sa.String(length=16), nullable=False, server_default='local'),
        sa.Column('external_source', sa.String(length=32), nullable=True),
        sa.Column('external_id', sa.String(length=64), nullable=True),
        sa.Column('external_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        schema=SCHEMA,
    )

    # user_goals
    op.create_table(
        'user_goals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('modified_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('user_id', sa.Text, nullable=False, unique=True),
        sa.Column('daily_calorie_goal', sa.Float, nullable=False, server_default=sa.text('2000')),
        sa.Column('daily_water_goal', sa.Float, nullable=False, server_default=sa.text('2000')),
        sa.Column('daily_protein_goal', sa.Float),
        sa.Column('daily_carbs_goal', sa.Float),
        sa.Column('daily_fat_goal', sa.Float),
        schema=SCHEMA,
    )

    # meals
    op.create_table(
        'meals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('modified_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('name', sa.String(256), nullable=False),
        sa.Column('type', sa.Enum('breakfast', 'lunch', 'dinner', 'snack', name='meal_type', schema=SCHEMA), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('notes', sa.Text),
        sa.Column('user_id', sa.Text, nullable=False),
        schema=SCHEMA,
    )

    # meal_foods
    op.create_table(
        'meal_foods',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('modified_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('meal_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('food_item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Float, nullable=False),
        sa.Column('serving_unit', sa.String(64), nullable=False),
        sa.ForeignKeyConstraint(['meal_id'], [f'{SCHEMA}.meals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['food_item_id'], [f'{SCHEMA}.food_items.id']),
        schema=SCHEMA,
    )

    # water_consumption
    op.create_table(
        'water_consumption',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('modified_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('user_id', sa.Text, nullable=False),
        sa.Column('quantity', sa.Float, nullable=False),
        sa.Column('consumed_at', sa.DateTime(timezone=True), nullable=False),
        schema=SCHEMA,
    )

    # Indexes
    op.execute(sa.text('CREATE INDEX IF NOT EXISTS ix_meals_food_items_user_id_name ON meals.food_items(user_id, name)'))
    op.execute(sa.text('CREATE INDEX IF NOT EXISTS ix_meals_food_items_ext ON meals.food_items(external_source, external_id)'))  # From migration 0002
    op.execute(sa.text('CREATE INDEX IF NOT EXISTS ix_meals_meals_user_date ON meals.meals(user_id, date DESC)'))
    op.execute(sa.text('CREATE INDEX IF NOT EXISTS ix_meals_meal_foods_meal_id ON meals.meal_foods(meal_id)'))
    op.execute(sa.text('CREATE INDEX IF NOT EXISTS ix_meals_meal_foods_food_item_id ON meals.meal_foods(food_item_id)'))
    op.execute(sa.text('CREATE INDEX IF NOT EXISTS ix_meals_water_user_time ON meals.water_consumption(user_id, consumed_at DESC)'))


def downgrade() -> None:
    """Drop entire meals schema and all contents."""
    # Drop in reverse order
    op.drop_table('water_consumption', schema=SCHEMA)
    op.drop_table('meal_foods', schema=SCHEMA)
    op.drop_table('meals', schema=SCHEMA)
    op.drop_table('user_goals', schema=SCHEMA)
    op.drop_table('food_items', schema=SCHEMA)
    op.execute(sa.text("DROP TYPE IF EXISTS meals.meal_type"))
    op.execute(sa.text(f'DROP SCHEMA IF EXISTS "{SCHEMA}" CASCADE'))
