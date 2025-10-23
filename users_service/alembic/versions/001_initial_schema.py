"""initial schema - complete users service database

Revision ID: 001
Revises:
Create Date: 2025-10-22 13:30:00

This migration creates the complete users service schema including:
- users table (core user data with supabase_id and keycloak_id)
- services table (available services: meals, practice, sleep, etc.)
- user_services table (linking table for user subscriptions)
- schedulables table (federated tasks from all services)
- user_roles table (role-domain assignments: coach, client, admin)
- coach_client_relationships table (simplified coach-client links)
- coach_client_associations table (domain-specific coach-client links)
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

SCHEMA = 'users'


def upgrade() -> None:
    # Create users schema
    op.execute(f'CREATE SCHEMA IF NOT EXISTS {SCHEMA}')

    # Create enums
    op.execute("""
        CREATE TYPE users.service_type AS ENUM (
            'meals', 'practice', 'sleep', 'shadow_boxing', 'fitness_db', 'programs'
        )
    """)

    op.execute("""
        CREATE TYPE users.role_enum AS ENUM (
            'coach', 'client', 'admin'
        )
    """)

    op.execute("""
        CREATE TYPE users.domain_enum AS ENUM (
            'practices', 'meals', 'sleep', 'system'
        )
    """)

    op.execute("""
        CREATE TYPE users.association_status_enum AS ENUM (
            'pending', 'accepted', 'rejected', 'terminated'
        )
    """)

    # ============================================================
    # BASE TABLES
    # ============================================================

    # users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('supabase_id', sa.String(256), nullable=False, unique=True),
        sa.Column('keycloak_id', sa.String(256), nullable=True, unique=True),
        sa.Column('email', sa.String(256), nullable=True),
        sa.Column('first_name', sa.String(256), nullable=True),
        sa.Column('last_name', sa.String(256), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('modified_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        schema=SCHEMA
    )
    op.create_index('ix_users_supabase_id', 'users', ['supabase_id'], unique=False, schema=SCHEMA)
    op.create_index('ix_users_keycloak_id', 'users', ['keycloak_id'], unique=False, schema=SCHEMA)
    op.create_index('ix_users_email', 'users', ['email'], unique=False, schema=SCHEMA)

    # services table
    op.create_table(
        'services',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.Enum('meals', 'practice', 'sleep', 'shadow_boxing', 'fitness_db', 'programs', name='service_type', schema=SCHEMA), nullable=False, unique=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('modified_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.UniqueConstraint('name', name='uq_services_name'),
        schema=SCHEMA
    )
    op.create_index('ix_services_name', 'services', ['name'], unique=False, schema=SCHEMA)

    # ============================================================
    # RELATIONSHIP TABLES
    # ============================================================

    # user_services (linking table)
    op.create_table(
        'user_services',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('service_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('modified_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], [f'{SCHEMA}.users.id']),
        sa.ForeignKeyConstraint(['service_id'], [f'{SCHEMA}.services.id']),
        sa.PrimaryKeyConstraint('user_id', 'service_id'),
        schema=SCHEMA
    )
    op.create_index('ix_user_services_user_id', 'user_services', ['user_id'], unique=False, schema=SCHEMA)
    op.create_index('ix_user_services_service_id', 'user_services', ['service_id'], unique=False, schema=SCHEMA)

    # schedulables table
    op.create_table(
        'schedulables',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(256), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('service_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('modified_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], [f'{SCHEMA}.users.id']),
        sa.ForeignKeyConstraint(['service_id'], [f'{SCHEMA}.services.id']),
        schema=SCHEMA
    )
    op.create_index('ix_schedulables_entity_id', 'schedulables', ['entity_id'], unique=False, schema=SCHEMA)
    op.create_index('ix_schedulables_user_id', 'schedulables', ['user_id'], unique=False, schema=SCHEMA)
    op.create_index('ix_schedulables_service_id', 'schedulables', ['service_id'], unique=False, schema=SCHEMA)

    # user_roles table
    op.create_table(
        'user_roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.Enum('coach', 'client', 'admin', name='role_enum', schema=SCHEMA), nullable=False),
        sa.Column('domain', sa.Enum('practices', 'meals', 'sleep', 'system', name='domain_enum', schema=SCHEMA), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('modified_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], [f'{SCHEMA}.users.id']),
        sa.UniqueConstraint('user_id', 'role', 'domain', name='uq_user_role_domain'),
        schema=SCHEMA
    )

    # coach_client_relationships table (new simplified structure)
    op.create_table(
        'coach_client_relationships',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('coach_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('client_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.Enum('pending', 'accepted', 'rejected', 'terminated', name='association_status_enum', schema=SCHEMA), nullable=False, server_default='pending'),
        sa.Column('requested_by', sa.String(10), nullable=False),  # 'coach' or 'client'
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('modified_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.ForeignKeyConstraint(['coach_user_id'], [f'{SCHEMA}.users.id']),
        sa.ForeignKeyConstraint(['client_user_id'], [f'{SCHEMA}.users.id']),
        sa.UniqueConstraint('coach_user_id', 'client_user_id', name='uq_coach_client'),
        schema=SCHEMA
    )

    # coach_client_associations table (domain-specific)
    op.create_table(
        'coach_client_associations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('coach_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('requester_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('domain', sa.Enum('practices', 'meals', 'sleep', 'system', name='domain_enum', schema=SCHEMA), nullable=False),
        sa.Column('status', sa.Enum('pending', 'accepted', 'rejected', 'terminated', name='association_status_enum', schema=SCHEMA), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.Column('modified_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
        sa.ForeignKeyConstraint(['coach_id'], [f'{SCHEMA}.users.id']),
        sa.ForeignKeyConstraint(['client_id'], [f'{SCHEMA}.users.id']),
        sa.ForeignKeyConstraint(['requester_id'], [f'{SCHEMA}.users.id']),
        sa.UniqueConstraint('coach_id', 'client_id', 'domain', name='uq_coach_client_domain'),
        schema=SCHEMA
    )


def downgrade() -> None:
    """Drop entire users schema and all contents."""
    # Drop tables in reverse dependency order
    op.drop_table('coach_client_associations', schema=SCHEMA)
    op.drop_table('coach_client_relationships', schema=SCHEMA)
    op.drop_table('user_roles', schema=SCHEMA)
    op.drop_table('schedulables', schema=SCHEMA)
    op.drop_table('user_services', schema=SCHEMA)
    op.drop_table('services', schema=SCHEMA)
    op.drop_table('users', schema=SCHEMA)

    # Drop enums
    op.execute('DROP TYPE IF EXISTS users.association_status_enum')
    op.execute('DROP TYPE IF EXISTS users.domain_enum')
    op.execute('DROP TYPE IF EXISTS users.role_enum')
    op.execute('DROP TYPE IF EXISTS users.service_type')

    # Drop schema
    op.execute(f'DROP SCHEMA IF EXISTS {SCHEMA} CASCADE')
