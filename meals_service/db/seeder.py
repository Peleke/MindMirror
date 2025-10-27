import asyncio
import os
from datetime import date, datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Meals service specific imports
from meals.repository.models.base import Base  # Assuming Base is in this path
from meals.repository.models.enums import MealType
from meals.repository.models.food_item import FoodItemModel
from meals.repository.models.meal import MealModel
from meals.repository.models.meal_food import MealFoodModel
from meals.repository.models.user_goals import UserGoalsModel
from meals.repository.models.water_consumption import WaterConsumptionModel
from meals.web.config import Config  # For database configuration

DB_USER = Config.DB_USER
DB_PASSWORD = Config.DB_PASSWORD
DB_HOST = Config.DB_HOST
DB_PORT = Config.DB_PORT
DB_NAME = Config.DB_NAME
DB_SCHEMA = "meals"  # Define the schema for meals service

DATABASE_URL = Config.DATABASE_URL

# Define a test user ID, similar to the practices seeder
TEST_USER_ID = "test-user-meals-seeder"


async def create_tables_and_schema(engine):
    async with engine.begin() as conn:
        print(f"Dropping schema {DB_SCHEMA} if exists...")
        await conn.execute(text(f'DROP SCHEMA IF EXISTS "{DB_SCHEMA}" CASCADE'))
        print(f"Creating schema {DB_SCHEMA}...")
        await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{DB_SCHEMA}" '))
        # Ensure Base.metadata.schema is set correctly in your models/base.py
        # If not, you might need to set it here: Base.metadata.schema = DB_SCHEMA
        print(f"Creating all tables in schema {DB_SCHEMA}...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully in meals schema.")


async def seed_data(async_session_factory: sessionmaker):
    now = datetime.now(timezone.utc)
    today = now.date()

    async with async_session_factory() as session:
        # --- Food Items ---
        apple = FoodItemModel(
            id_=uuid4(),
            name="Apple",
            serving_size=100,
            serving_unit="g",
            calories=52,
            protein=0.3,
            carbohydrates=14,
            fat=0.2,
            user_id=TEST_USER_ID,
            notes="A crisp red apple.",
        )
        banana = FoodItemModel(
            id_=uuid4(),
            name="Banana",
            serving_size=118,
            serving_unit="g",
            calories=105,
            protein=1.3,
            carbohydrates=27,
            fat=0.3,
            user_id=None,
            notes="A ripe banana, good source of potassium.",
        )
        chicken_breast = FoodItemModel(
            id_=uuid4(),
            name="Chicken Breast",
            serving_size=100,
            serving_unit="g",
            calories=165,
            protein=31,
            carbohydrates=0,
            fat=3.6,
            user_id=TEST_USER_ID,
            notes="Skinless, boneless chicken breast.",
        )
        rice = FoodItemModel(
            id_=uuid4(),
            name="White Rice (Cooked)",
            serving_size=150,
            serving_unit="g",
            calories=195,
            protein=4.0,
            carbohydrates=43,
            fat=0.3,
            user_id=None,
            notes="Steamed white rice.",
        )
        spinach = FoodItemModel(
            id_=uuid4(),
            name="Spinach",
            serving_size=100,
            serving_unit="g",
            calories=23,
            protein=2.9,
            carbohydrates=3.6,
            fat=0.4,
            user_id=None,
            notes="Fresh spinach leaves.",
        )

        session.add_all([apple, banana, chicken_breast, rice, spinach])
        await session.flush()  # Ensure IDs are available

        # --- User Goals ---
        user_goals1 = UserGoalsModel(
            id_=uuid4(),
            user_id=TEST_USER_ID,
            daily_calorie_goal=2200,
            daily_water_goal=2500,
            daily_protein_goal=150,
            daily_carbs_goal=250,
            daily_fat_goal=70,
        )
        session.add(user_goals1)

        # --- Water Consumption ---
        water1 = WaterConsumptionModel(
            id_=uuid4(), user_id=TEST_USER_ID, quantity=500, consumed_at=now - timedelta(hours=2)
        )
        water2 = WaterConsumptionModel(
            id_=uuid4(), user_id=TEST_USER_ID, quantity=750, consumed_at=now - timedelta(hours=1)
        )
        session.add_all([water1, water2])

        # --- Meals ---
        meal1_breakfast_id = uuid4()
        meal1_breakfast = MealModel(
            id_=meal1_breakfast_id,
            user_id=TEST_USER_ID,
            name="Morning Oatmeal",
            type=MealType.BREAKFAST,
            date=now - timedelta(days=1),
        )
        session.add(meal1_breakfast)
        await session.flush()

        meal_food1_apple = MealFoodModel(
            id_=uuid4(), meal_id=meal1_breakfast_id, food_item_id=apple.id_, quantity=1, serving_unit="medium"
        )
        meal_food1_banana = MealFoodModel(
            id_=uuid4(), meal_id=meal1_breakfast_id, food_item_id=banana.id_, quantity=0.5, serving_unit="large"
        )
        session.add_all([meal_food1_apple, meal_food1_banana])

        meal2_lunch_id = uuid4()
        meal2_lunch = MealModel(
            id_=meal2_lunch_id, user_id=TEST_USER_ID, name="Chicken Salad Lunch", type=MealType.LUNCH, date=today
        )
        session.add(meal2_lunch)
        await session.flush()

        meal_food2_chicken = MealFoodModel(
            id_=uuid4(), meal_id=meal2_lunch_id, food_item_id=chicken_breast.id_, quantity=150, serving_unit="g"
        )
        meal_food2_spinach = MealFoodModel(
            id_=uuid4(), meal_id=meal2_lunch_id, food_item_id=spinach.id_, quantity=50, serving_unit="g"
        )
        session.add_all([meal_food2_chicken, meal_food2_spinach])

        # Another user's data for testing isolation (optional)
        OTHER_USER_ID = "other-test-user-meals"
        user_goals_other = UserGoalsModel(
            id_=uuid4(), user_id=OTHER_USER_ID, daily_calorie_goal=2000, daily_water_goal=2000
        )
        session.add(user_goals_other)

        water_other = WaterConsumptionModel(id_=uuid4(), user_id=OTHER_USER_ID, quantity=1000, consumed_at=now)
        session.add(water_other)

        meal_other_id = uuid4()
        meal_other = MealModel(
            id_=meal_other_id, user_id=OTHER_USER_ID, name="Other User Dinner", type=MealType.DINNER, date=today
        )
        session.add(meal_other)
        await session.flush()
        meal_food_other_rice = MealFoodModel(
            id_=uuid4(), meal_id=meal_other_id, food_item_id=rice.id_, quantity=100, serving_unit="g"
        )
        session.add(meal_food_other_rice)

        try:
            await session.commit()
            print("Meals data seeded successfully.")
        except Exception as e:
            await session.rollback()
            print(f"Error seeding meals data: {e}")
            raise


async def main():
    print(f"Connecting to meals database: {DB_HOST}:{DB_PORT}/{DB_NAME} as {DB_USER}")
    engine = create_async_engine(DATABASE_URL, echo=False)  # Set echo=True for SQL logging if needed

    async_session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    await create_tables_and_schema(engine)
    await seed_data(async_session_factory)

    await engine.dispose()
    print("Meals database connection closed.")


if __name__ == "__main__":
    print("Starting meals database seeder...")
    # Ensure your models (especially Base.metadata.schema in meals/repository/models/base.py)
    # are correctly set up before running this. Example:
    # from sqlalchemy.orm import DeclarativeBase
    # class Base(DeclarativeBase):
    #     __abstract__ = True
    #     metadata = MetaData(schema="meals") # Ensure schema="meals" is set here
    asyncio.run(main())
