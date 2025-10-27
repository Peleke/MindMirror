import asyncio
import os
from datetime import date, datetime, timedelta
from uuid import UUID, uuid4

from shared.auth import CurrentUser, UserRole
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Updated imports to match current model structure
from practices.repository.models.base import Base
from practices.repository.models.movement_instance import MovementInstanceModel
from practices.repository.models.movement_template import MovementTemplateModel
from practices.repository.models.practice_instance import PracticeInstanceModel
from practices.repository.models.practice_template import PracticeTemplateModel
from practices.repository.models.prescription_instance import PrescriptionInstanceModel
from practices.repository.models.prescription_template import PrescriptionTemplateModel
from practices.repository.models.program import ProgramModel, ProgramTagModel
from practices.repository.models.program_enrollment import (
    EnrollmentStatus,
    ProgramEnrollmentModel,
)
from practices.repository.models.program_practice_link import ProgramPracticeLinkModel
from practices.repository.models.scheduled_practice import ScheduledPracticeModel
from practices.repository.models.set_instance import SetInstanceModel
from practices.repository.models.set_template import SetTemplateModel

# Environment variables for database connection
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_DB", "swae")  # Using DB_DB as in your docker-compose
DB_SCHEMA = "practices"

# Define user IDs to be used for practices (matching test fixtures)
COACH_USER_ID = UUID("00000000-0000-0000-0000-000000000001")
CLIENT_USER_ID_ONE = UUID("00000000-0000-0000-0000-000000000002")
CLIENT_USER_ID_TWO = UUID("00000000-0000-0000-0000-000000000003")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


async def create_tables_and_schema(engine):
    async with engine.begin() as conn:
        print(f"Dropping schema {DB_SCHEMA} if exists...")
        await conn.execute(text(f"DROP SCHEMA IF EXISTS {DB_SCHEMA} CASCADE"))
        print(f"Creating schema {DB_SCHEMA}...")
        await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {DB_SCHEMA}"))
        print(f"Creating all tables in schema {DB_SCHEMA}...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully.")


async def seed_data(async_session_factory):
    """Seed the database with initial data matching the test fixtures."""

    async with async_session_factory() as session:
        print("Creating templates...")

        # === Create Template Hierarchy ===
        # 1. Practice Template (owned by coach)
        practice_template = PracticeTemplateModel(
            id_=uuid4(),
            user_id=COACH_USER_ID,
            title="Coach's Strength Template",
            description="A comprehensive strength training template",
            duration=60.0,
        )

        # 2. Prescription Templates
        prescription_template = PrescriptionTemplateModel(
            id_=uuid4(),
            practice_template_id=practice_template.id_,
            name="Main Workout",
            block="workout",
            position=0,
            prescribed_rounds=3,
            description="Primary strength training block",
        )

        warmup_prescription_template = PrescriptionTemplateModel(
            id_=uuid4(),
            practice_template_id=practice_template.id_,
            name="Warm-up",
            block="warmup",
            position=1,
            prescribed_rounds=1,
            description="Dynamic warm-up to prepare for training",
        )

        # 3. Movement Templates
        movement_template = MovementTemplateModel(
            id_=uuid4(),
            prescription_template_id=prescription_template.id_,
            name="Barbell Squat",
            position=0,
            metric_unit="iterative",
            metric_value=8,
            prescribed_sets=3,
            description="Compound lower body exercise",
            movement_class="strength",
            rest_duration=90.0,
            exercise_id=str(uuid4()),  # Mock exercise DB ID
        )

        movement_template2 = MovementTemplateModel(
            id_=uuid4(),
            prescription_template_id=prescription_template.id_,
            name="Bench Press",
            position=1,
            metric_unit="iterative",
            metric_value=10,
            prescribed_sets=3,
            description="Upper body pressing movement",
            movement_class="strength",
            rest_duration=120.0,
        )

        # 4. Set Templates
        set_templates = [
            SetTemplateModel(
                id_=uuid4(),
                movement_template_id=movement_template.id_,
                position=i,
                reps=8,
                load_value=135 + (i * 10),
                load_unit="pounds",
                rest_duration=90,
            )
            for i in range(3)
        ]

        print("Creating instances...")

        # === Create Instance Hierarchy ===
        # 1. Practice Instance (for client)
        practice_instance = PracticeInstanceModel(
            id_=uuid4(),
            user_id=CLIENT_USER_ID_ONE,
            template_id=practice_template.id_,
            date=date.today(),
            title=practice_template.title,
            description=practice_template.description,
            duration=practice_template.duration,
        )

        # 2. Prescription Instance
        prescription_instance = PrescriptionInstanceModel(
            id_=uuid4(),
            practice_instance_id=practice_instance.id_,
            template_id=prescription_template.id_,
            name=prescription_template.name,
            block=prescription_template.block,
            position=prescription_template.position,
            prescribed_rounds=prescription_template.prescribed_rounds,
            description=prescription_template.description,
        )

        # 3. Movement Instances
        movement_instance = MovementInstanceModel(
            id_=uuid4(),
            prescription_instance_id=prescription_instance.id_,
            template_id=movement_template.id_,
            name=movement_template.name,
            position=movement_template.position,
            metric_unit=movement_template.metric_unit,
            metric_value=movement_template.metric_value,
            description=movement_template.description,
            movement_class=movement_template.movement_class,
            prescribed_sets=movement_template.prescribed_sets,
            rest_duration=movement_template.rest_duration,
            exercise_id=movement_template.exercise_id,
        )

        movement_instance2 = MovementInstanceModel(
            id_=uuid4(),
            prescription_instance_id=prescription_instance.id_,
            template_id=movement_template2.id_,
            name=movement_template2.name,
            position=movement_template2.position,
            metric_unit=movement_template2.metric_unit,
            metric_value=movement_template2.metric_value,
            description=movement_template2.description,
            movement_class=movement_template2.movement_class,
            prescribed_sets=movement_template2.prescribed_sets,
            rest_duration=movement_template2.rest_duration,
        )

        # 4. Set Instances
        set_instances = [
            SetInstanceModel(
                id_=uuid4(),
                movement_instance_id=movement_instance.id_,
                template_id=st.id_,
                position=st.position,
                reps=st.reps,
                load_value=st.load_value,
                load_unit=st.load_unit,
                rest_duration=st.rest_duration,
            )
            for st in set_templates
        ]

        print("Creating program...")

        # === Create Program ===
        program = ProgramModel(
            id_=uuid4(),
            user_id=COACH_USER_ID,
            name="6-Week Strength Program",
            description="Progressive strength training program",
            level="intermediate",
        )

        program_tags = [
            ProgramTagModel(program_id=program.id_, name="strength"),
            ProgramTagModel(program_id=program.id_, name="intermediate"),
        ]

        program_practice_link = ProgramPracticeLinkModel(
            program_id=program.id_,
            practice_template_id=practice_template.id_,
            sequence_order=1,
            interval_days_after=2,
        )

        # === Create Enrollments ===
        enrollment_one = ProgramEnrollmentModel(
            id_=uuid4(),
            program_id=program.id_,
            user_id=CLIENT_USER_ID_ONE,
            status=EnrollmentStatus.ACTIVE,
        )

        enrollment_two = ProgramEnrollmentModel(
            id_=uuid4(),
            program_id=program.id_,
            user_id=CLIENT_USER_ID_TWO,
            status=EnrollmentStatus.ACTIVE,
        )

        # Create a scheduled practice for progress tracking
        scheduled_practice = ScheduledPracticeModel(
            id_=uuid4(),
            enrollment_id=enrollment_one.id_,
            practice_template_id=practice_template.id_,
            practice_instance_id=practice_instance.id_,
            scheduled_date=date.today(),
        )

        print("Adding all entities to session...")

        # Collect all DB entities to be created
        db_entities = [
            # Templates
            practice_template,
            prescription_template,
            warmup_prescription_template,
            movement_template,
            movement_template2,
            *set_templates,
            # Instances
            practice_instance,
            prescription_instance,
            movement_instance,
            movement_instance2,
            *set_instances,
            # Program & Enrollments
            program,
            *program_tags,
            program_practice_link,
            enrollment_one,
            enrollment_two,
            scheduled_practice,
        ]

        session.add_all(db_entities)

        try:
            await session.commit()
            print("Data seeded successfully.")
            print(f"Created:")
            print(f"  - 1 practice template with 2 prescription templates")
            print(f"  - 2 movement templates with {len(set_templates)} set templates")
            print(f"  - 1 practice instance with prescription and movement instances")
            print(f"  - 1 program with 2 enrollments")
            print(f"  - Coach user ID: {COACH_USER_ID}")
            print(f"  - Client user IDs: {CLIENT_USER_ID_ONE}, {CLIENT_USER_ID_TWO}")
        except Exception as e:
            await session.rollback()
            print(f"Error seeding data: {e}")
            raise


async def main():
    print(f"Connecting to database: {DB_HOST}:{DB_PORT}/{DB_NAME} as {DB_USER}")
    engine = create_async_engine(DATABASE_URL, echo=False)  # Set echo=True for SQL logging

    # Create a session factory
    async_session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    await create_tables_and_schema(engine)
    await seed_data(async_session_factory)

    await engine.dispose()
    print("Database connection closed.")


if __name__ == "__main__":
    print("Starting database seeder...")
    print("This seeder creates a structure matching the test fixtures:")
    print("- Practice templates with prescriptions, movements, and sets")
    print("- Practice instances for testing")
    print("- Programs with enrollments")
    print("- All using the current model structure")
    asyncio.run(main())
