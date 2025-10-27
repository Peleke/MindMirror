import asyncio
import os
import uuid
from datetime import datetime

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker  # Corrected from sqlalchemy.ext.asyncio

from users.repository.database import (
    SCHEMA_NAME as DB_SCHEMA,  # Use schema name from database.py
)
from users.repository.models import (
    SchedulableModel,
    ServiceEnum,
    ServiceModel,
    UserModel,
    UserServicesModel,
)

# Models and Enums from the users service
from users.repository.models.base import Base  # The SQLAlchemy Base

# Environment variables for database connection (these will be set by Docker Compose)
DB_USER = os.getenv("DB_USER", "users_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "users_password")
DB_HOST = os.getenv("DB_HOST", "localhost")  # Default for local, Docker overrides
DB_PORT = os.getenv("DB_PORT", "5433")  # Default for local, Docker overrides
DB_NAME = os.getenv("DB_NAME", "users_db")
DB_DRIVER = os.getenv("DB_DRIVER", "asyncpg")

DATABASE_URL = f"postgresql+{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


async def create_tables_and_schema(engine):
    async with engine.begin() as conn:
        # Attempt to drop potentially conflicting old enum from public schema or default path
        print(f"Attempting to drop ENUM type 'serviceenum' from public schema if it exists...")
        await conn.execute(text(f"DROP TYPE IF EXISTS public.serviceenum CASCADE"))
        print(f"Attempting to drop ENUM type 'serviceenum' from users schema if it exists...")
        await conn.execute(text(f"DROP TYPE IF EXISTS users.serviceenum CASCADE"))
        print(f"ENUM type 'public.serviceenum' dropped or did not exist.")
        print(f"Attempting to drop ENUM type 'serviceenum' (schema-unqualified) if it exists...")
        await conn.execute(
            text(f"DROP TYPE IF EXISTS serviceenum CASCADE")
        )  # In case it's in search_path but not public explicitly
        print(f"ENUM type 'serviceenum' (schema-unqualified) dropped or did not exist.")

        print(f"Attempting to drop schema '{DB_SCHEMA}' if it exists...")
        await conn.execute(text(f"DROP SCHEMA IF EXISTS {DB_SCHEMA} CASCADE"))
        print(f"Schema '{DB_SCHEMA}' dropped or did not exist.")

        print(f"Attempting to create schema '{DB_SCHEMA}'...")
        await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {DB_SCHEMA}"))
        print(f"Schema '{DB_SCHEMA}' created or already exists.")

        # Ensure Base.metadata.schema is set; it should be from users.repository.database
        if Base.metadata.schema != DB_SCHEMA:
            print(
                f"Warning: Base.metadata.schema ('{Base.metadata.schema}') does not match DB_SCHEMA ('{DB_SCHEMA}'). Overriding for seeder."
            )
            Base.metadata.schema = DB_SCHEMA

        print(f"Creating all tables in schema '{DB_SCHEMA}'...")
        await conn.run_sync(Base.metadata.create_all)

        # Create the service_type enum if it doesn't exist (idempotent way)
        # This is often handled by migrations but can be here for standalone seeder
        print(f"Creating ENUM type '{DB_SCHEMA}.service_type' if not exists...")
        await conn.execute(
            text(
                f"""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type typ JOIN pg_namespace ns ON ns.oid = typ.typnamespace WHERE typname = 'service_type' AND ns.nspname = '{DB_SCHEMA}') THEN
                    CREATE TYPE {DB_SCHEMA}.service_type AS ENUM (
                        'meals',
                        'practice',
                        'shadow_boxing',
                        'fitness_db',
                        'programs'
                    );
                    RAISE NOTICE 'ENUM type {DB_SCHEMA}.service_type created.';
                ELSE
                    RAISE NOTICE 'ENUM type {DB_SCHEMA}.service_type already exists.';
                END IF;
            END$$;
        """
            )
        )

        # Create the automatic timestamp update function for 'modified_at' columns
        print(f"Creating/Replacing function '{DB_SCHEMA}.update_modified_at_column'...")
        await conn.execute(
            text(
                f"""
            CREATE OR REPLACE FUNCTION {DB_SCHEMA}.update_modified_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.modified_at = clock_timestamp();
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        """
            )
        )
        print(f"Function '{DB_SCHEMA}.update_modified_at_column' created/replaced.")

        # Add triggers for timestamp updates (idempotently, if possible, or ensure tables exist)
        tables_for_triggers = ["users", "services", "user_services", "schedulables"]
        for table_name in tables_for_triggers:
            trigger_name = f"update_{table_name}_modified_at"
            print(f"Creating trigger '{trigger_name}' on table '{DB_SCHEMA}.{table_name}'...")
            await conn.execute(
                text(f"DROP TRIGGER IF EXISTS {trigger_name} ON {DB_SCHEMA}.{table_name};")
            )  # Drop if exists to ensure clean state
            await conn.execute(
                text(
                    f"""
                CREATE TRIGGER {trigger_name}
                BEFORE UPDATE ON {DB_SCHEMA}.{table_name}
                FOR EACH ROW
                EXECUTE FUNCTION {DB_SCHEMA}.update_modified_at_column();
            """
                )
            )
            print(f"Trigger '{trigger_name}' created on table '{DB_SCHEMA}.{table_name}'.")

        print("Tables, schema, enum, function, and triggers created successfully.")


async def seed_data(async_session_factory):
    now = datetime.utcnow()  # Use UTC for consistency

    async with async_session_factory() as session:
        try:
            # 1. Seed Services from ServiceEnum
            seeded_services = {}
            print("Seeding services...")
            for service_enum_member in ServiceEnum:
                service_name = service_enum_member.value
                # Define a placeholder URL for each service
                service_url_map = {
                    ServiceEnum.MEALS: "http://meals:8000/graphql",
                    ServiceEnum.PRACTICE: "http://practices:8000/graphql",
                    ServiceEnum.SHADOW_BOXING: "http://boxing:8000/graphql",
                    ServiceEnum.FITNESS_DB: "http://movements:8000/graphql",  # Corresponds to FITNESS_SERVICE_URL in config
                    ServiceEnum.PROGRAMS: "http://programs:8000/graphql",  # Assuming 'programs' service name and port 8000
                }
                default_url = "http://mesh:8000/graphql"  # This default won't be used if all enums are in map
                service_url = service_url_map.get(service_enum_member, default_url)

                existing_service_stmt = text(f"SELECT id FROM {DB_SCHEMA}.services WHERE name = :name")
                result = await session.execute(existing_service_stmt, {"name": service_name})
                existing_service_row = result.fetchone()

                if not existing_service_row:
                    service = ServiceModel(
                        name=service_enum_member,
                        description=f"Service for {service_name.replace('_', ' ').title()}",
                        url=service_url,  # Add the URL here
                    )
                    session.add(service)
                    await session.flush()
                    seeded_services[service_enum_member] = service
                    print(f"  Added service: {service_name} with URL: {service_url}")
                else:
                    print(f"  Service '{service_name}' already exists, checking/updating URL.")
                    # If it exists, fetch the ORM model to update its URL if necessary
                    existing_service_orm_stmt = select(ServiceModel).where(ServiceModel.name == service_enum_member)
                    existing_service_orm_result = await session.execute(existing_service_orm_stmt)
                    existing_service_orm = existing_service_orm_result.scalars().first()
                    if existing_service_orm and existing_service_orm.url != service_url:
                        print(
                            f"    Updating URL for {service_name} from '{existing_service_orm.url}' to '{service_url}'"
                        )
                        existing_service_orm.url = service_url
                        await session.flush()
                    elif existing_service_orm:
                        print(f"    URL for {service_name} is already up-to-date ('{existing_service_orm.url}').")
                    seeded_services[service_enum_member] = existing_service_orm  # Ensure it's in seeded_services

            await session.flush()  # Ensure all new services are flushed

            # Re-fetch services to ensure we have ORM objects with IDs for relationships
            print("Re-fetching services after potential creation...")
            for service_enum_member in ServiceEnum:
                if service_enum_member not in seeded_services:
                    # service_obj_id_row = await session.execute( # Commenting out unused raw SQL
                    #     text(f"SELECT id FROM {DB_SCHEMA}.services WHERE name = '{service_enum_member.value}'")
                    # )
                    # This is the ORM way, which is good.
                    # The late import of 'select' is no longer needed here as it's global.
                    # from sqlalchemy import select
                    stmt = select(ServiceModel).where(ServiceModel.name == service_enum_member)
                    result = await session.execute(stmt)
                    service_model_instance = result.scalars().first()
                    if service_model_instance:
                        seeded_services[service_enum_member] = service_model_instance
                        print(
                            f"  Re-fetched service for linking: {service_enum_member.value} (ID: {service_model_instance.id_})"
                        )
                    else:
                        print(
                            f"  ERROR: Service {service_enum_member.value} was not found after attempting to seed/find it."
                        )

            # 2. Seed Users
            print("Seeding users...")
            user1_supabase_id = "seed_supabase_user_1"
            user2_supabase_id = "seed_supabase_user_2"  # This user won't be linked to all services for variety
            user3_supabase_id = "seed_supabase_user_3"
            USER3_INTERNAL_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

            user1 = await session.scalar(select(UserModel).where(UserModel.supabase_id == user1_supabase_id))
            if not user1:
                user1 = UserModel(supabase_id=user1_supabase_id, keycloak_id=str(uuid.uuid4()))
                session.add(user1)
                print(f"  Added user: {user1_supabase_id}")
            else:
                print(f"  User '{user1_supabase_id}' already exists.")

            user2 = await session.scalar(select(UserModel).where(UserModel.supabase_id == user2_supabase_id))
            if not user2:
                user2 = UserModel(supabase_id=user2_supabase_id)
                session.add(user2)
                print(f"  Added user: {user2_supabase_id}")
            else:
                print(f"  User '{user2_supabase_id}' already exists.")

            user3 = await session.scalar(select(UserModel).where(UserModel.id_ == USER3_INTERNAL_ID))
            if not user3:
                # Check if a user with that supabase_id already exists to avoid unique constraint violation
                existing_user_by_supabase = await session.scalar(
                    select(UserModel).where(UserModel.supabase_id == user3_supabase_id)
                )
                if existing_user_by_supabase:
                    print(
                        f"  User with supabase_id '{user3_supabase_id}' already exists with a different internal ID. Skipping user3 creation with hardcoded ID."
                    )
                    user3 = existing_user_by_supabase  # Use existing user if supabase_id clashes
                else:
                    user3 = UserModel(
                        id_=USER3_INTERNAL_ID,  # Assign hardcoded internal ID
                        supabase_id=user3_supabase_id,
                        keycloak_id=str(uuid.uuid4()),  # Optional: add a keycloak_id
                    )
                    session.add(user3)
                    print(f"  Added user: {user3_supabase_id} with internal ID {USER3_INTERNAL_ID}")
            else:
                print(
                    f"  User with internal ID '{USER3_INTERNAL_ID}' (supabase_id: '{user3.supabase_id}') already exists."
                )

            await session.flush()  # Get IDs for user1, user2 and ensure user3 is flushed

            # 3. Link Users to Services
            print("Linking users to services...")
            users_to_link_all = []
            if user1 and user1.id_:
                users_to_link_all.append(user1)
            if user3 and user3.id_:
                users_to_link_all.append(user3)

            for user_to_link in users_to_link_all:
                user_identifier_for_log = user_to_link.supabase_id  # or user_to_link.id_ for internal ID logging
                print(f"  Processing links for user: {user_identifier_for_log}")
                for service_enum_member, service_model_instance in seeded_services.items():
                    if service_model_instance and service_model_instance.id_:
                        link_exists = await session.scalar(
                            select(UserServicesModel).where(
                                UserServicesModel.user_id == user_to_link.id_,
                                UserServicesModel.service_id == service_model_instance.id_,
                            )
                        )
                        if not link_exists:
                            new_link = UserServicesModel(
                                user_id=user_to_link.id_, service_id=service_model_instance.id_
                            )
                            session.add(new_link)
                            print(f"    Linked user {user_identifier_for_log} to {service_enum_member.value}")
                        else:
                            print(f"    User {user_identifier_for_log} already linked to {service_enum_member.value}")
                    else:
                        print(
                            f"    Skipping link for user {user_identifier_for_log} to {service_enum_member.value} - service model or ID missing."
                        )

            # Example: Link user2 (seed_supabase_user_2) only to FITNESS_DB for variety, if desired
            if (
                user2
                and user2.id_
                and ServiceEnum.FITNESS_DB in seeded_services
                and seeded_services[ServiceEnum.FITNESS_DB].id_
            ):
                link_user2_fitness_exists = await session.scalar(
                    select(UserServicesModel).where(
                        UserServicesModel.user_id == user2.id_,
                        UserServicesModel.service_id == seeded_services[ServiceEnum.FITNESS_DB].id_,
                    )
                )
                if not link_user2_fitness_exists:
                    link_user2_fitness = UserServicesModel(
                        user_id=user2.id_, service_id=seeded_services[ServiceEnum.FITNESS_DB].id_
                    )
                    session.add(link_user2_fitness)
                    print(f"  Linked {user2.supabase_id} to FITNESS_DB (specific link example)")

            await session.flush()

            # 4. Seed Schedulables
            print("Seeding schedulables...")
            if user1 and user1.id_ and ServiceEnum.MEALS in seeded_services and seeded_services[ServiceEnum.MEALS].id_:
                # Check if a similar schedulable exists to avoid duplicates if seeder runs multiple times
                sched1_name = "Eat a healthy breakfast"
                sched1_exists = await session.scalar(
                    select(SchedulableModel).where(
                        SchedulableModel.user_id == user1.id_,
                        SchedulableModel.service_id == seeded_services[ServiceEnum.MEALS].id_,
                        SchedulableModel.name == sched1_name,
                    )
                )
                if not sched1_exists:
                    sched1 = SchedulableModel(
                        name=sched1_name,
                        description="Remember your morning nutrition.",
                        entity_id=uuid.uuid4(),  # Example entity ID
                        completed=False,
                        user_id=user1.id_,
                        service_id=seeded_services[ServiceEnum.MEALS].id_,
                    )
                    session.add(sched1)
                    print(f"  Added schedulable '{sched1_name}' for {user1_supabase_id}")

            if (
                user1
                and user1.id_
                and ServiceEnum.PRACTICE in seeded_services
                and seeded_services[ServiceEnum.PRACTICE].id_
            ):
                sched2_name = "Practice new skill for 30 mins"
                sched2_exists = await session.scalar(
                    select(SchedulableModel).where(
                        SchedulableModel.user_id == user1.id_,
                        SchedulableModel.service_id == seeded_services[ServiceEnum.PRACTICE].id_,
                        SchedulableModel.name == sched2_name,
                    )
                )
                if not sched2_exists:
                    sched2 = SchedulableModel(
                        name=sched2_name,
                        description="Focus on deliberate practice.",
                        entity_id=uuid.uuid4(),  # Example entity ID
                        completed=True,  # Example of a completed one
                        user_id=user1.id_,
                        service_id=seeded_services[ServiceEnum.PRACTICE].id_,
                    )
                    session.add(sched2)
                    print(f"  Added schedulable '{sched2_name}' for {user1_supabase_id}")

            await session.commit()
            print("Data seeded successfully.")

        except Exception as e:
            await session.rollback()
            print(f"Error during data seeding: {e}")
            import traceback

            traceback.print_exc()
            raise


async def main():
    print(f"Users Seeder: Connecting to database: {DB_HOST}:{DB_PORT}/{DB_NAME} as {DB_USER}")
    engine = create_async_engine(DATABASE_URL, echo=False)  # Set echo=True for SQL logging if needed

    # Create a session factory for the seeder
    # Using sessionmaker directly as in practices seeder
    seeder_async_session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    await create_tables_and_schema(engine)
    await seed_data(seeder_async_session_factory)

    await engine.dispose()
    print("Users Seeder: Database connection closed.")


if __name__ == "__main__":
    print("Starting Users database seeder...")
    # Make sure models (Base.metadata.schema) are correct before running.
    asyncio.run(main())
