from datetime import date, datetime, timedelta
from uuid import UUID

import pytest

from meals.repository.models.enums import MealType
from meals.repository.repositories.meal_repository import MealRepository


@pytest.mark.asyncio
class TestMealRepository:

    async def test_create_meal_with_foods(self, seed_db, session):
        """Test creating a meal with nested food items."""
        meal_data = {
            "name": "Lunch",
            "type": MealType.LUNCH,
            "date": datetime.now(),
            "notes": "Healthy lunch",
            "user_id": "test-user-456",
            "meal_foods_data": [
                {
                    "food_item_id": seed_db["chicken_breast"].id_,
                    "quantity": 150.0,
                    "serving_unit": "g",
                },
                {
                    "food_item_id": seed_db["apple"].id_,
                    "quantity": 200.0,
                    "serving_unit": "g",
                },
            ],
        }

        meal_repo = MealRepository(session)
        created_meal = await meal_repo.create_meal_with_foods(meal_data)

        assert created_meal is not None
        assert created_meal.name == "Lunch"
        assert created_meal.type == MealType.LUNCH
        assert created_meal.user_id == "test-user-456"
        assert len(created_meal.meal_foods) == 2

        # Verify nested food items are loaded
        meal_foods = created_meal.meal_foods
        assert meal_foods[0].food_item is not None
        assert meal_foods[1].food_item is not None

        # Check specific food items
        food_names = [mf.food_item.name for mf in meal_foods]
        assert "Chicken Breast" in food_names
        assert "Apple" in food_names

    async def test_get_meal_by_id(self, seed_db, session):
        """Test retrieving a meal by ID with all relationships."""
        meal_repo = MealRepository(session)
        test_meal = seed_db["test_meal"]

        fetched_meal = await meal_repo.get_meal_by_id(test_meal.id_)

        assert fetched_meal is not None
        assert fetched_meal.id_ == test_meal.id_
        assert fetched_meal.name == "Breakfast"
        assert fetched_meal.type == MealType.BREAKFAST
        assert len(fetched_meal.meal_foods) == 2

        # Verify food items are loaded
        for meal_food in fetched_meal.meal_foods:
            assert meal_food.food_item is not None

    async def test_get_nonexistent_meal(self, seed_db, session):
        """Test getting a meal that doesn't exist."""
        meal_repo = MealRepository(session)
        fake_uuid = UUID("00000000-0000-0000-0000-000000000000")

        result = await meal_repo.get_meal_by_id(fake_uuid)
        assert result is None

    async def test_list_meals_by_user_and_date_range(self, seed_db, session):
        """Test listing meals for a user within a date range."""
        meal_repo = MealRepository(session)

        # Create additional meals for testing
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        # Create meal for yesterday
        yesterday_meal_data = {
            "name": "Yesterday Dinner",
            "type": MealType.DINNER,
            "date": datetime.combine(yesterday, datetime.min.time()),
            "user_id": "test-user-123",
            "meal_foods_data": [
                {
                    "food_item_id": seed_db["chicken_breast"].id_,
                    "quantity": 100.0,
                    "serving_unit": "g",
                }
            ],
        }
        await meal_repo.create_meal_with_foods(yesterday_meal_data)
        await session.commit()  # Persist the meal creation

        # Create meal for tomorrow
        tomorrow_meal_data = {
            "name": "Tomorrow Breakfast",
            "type": MealType.BREAKFAST,
            "date": datetime.combine(tomorrow, datetime.min.time()),
            "user_id": "test-user-123",
            "meal_foods_data": [
                {
                    "food_item_id": seed_db["oatmeal"].id_,
                    "quantity": 50.0,
                    "serving_unit": "g",
                }
            ],
        }
        await meal_repo.create_meal_with_foods(tomorrow_meal_data)
        await session.commit()  # Persist the meal creation

        # Test date range query
        meals_in_range = await meal_repo.list_meals_by_user_and_date_range(
            user_id="test-user-123",
            start_date=yesterday,
            end_date=today,
        )

        # Should include yesterday's meal and today's seeded meal
        assert len(meals_in_range) >= 2
        meal_names = [meal.name for meal in meals_in_range]
        assert "Yesterday Dinner" in meal_names

    async def test_list_meals_by_user(self, seed_db, session):
        """Test listing all meals for a user with pagination."""
        meal_repo = MealRepository(session)

        # List all meals for the test user
        all_meals = await meal_repo.list_meals_by_user("test-user-123")
        assert len(all_meals) >= 1  # At least the seeded meal

        # Test pagination
        limited_meals = await meal_repo.list_meals_by_user("test-user-123", limit=1)
        assert len(limited_meals) == 1

        # Test offset
        if len(all_meals) > 1:
            offset_meals = await meal_repo.list_meals_by_user("test-user-123", limit=1, offset=1)
            assert len(offset_meals) >= 0

    async def test_update_meal(self, seed_db, session):
        """Test updating meal properties."""
        meal_repo = MealRepository(session)
        test_meal = seed_db["test_meal"]

        update_data = {
            "name": "Updated Breakfast",
            "notes": "Updated notes",
            "type": MealType.SNACK,
        }

        updated_meal = await meal_repo.update_meal(test_meal.id_, update_data)

        assert updated_meal is not None
        assert updated_meal.name == "Updated Breakfast"
        assert updated_meal.notes == "Updated notes"
        assert updated_meal.type == MealType.SNACK
        # User ID should remain unchanged
        assert updated_meal.user_id == "test-user-123"

    async def test_update_nonexistent_meal(self, seed_db, session):
        """Test updating a meal that doesn't exist."""
        meal_repo = MealRepository(session)
        fake_uuid = UUID("00000000-0000-0000-0000-000000000000")

        update_data = {"name": "Should Not Update"}
        result = await meal_repo.update_meal(fake_uuid, update_data)

        assert result is None

    async def test_delete_meal(self, seed_db, session):
        """Test deleting a meal."""
        meal_repo = MealRepository(session)

        # Create a meal to delete
        meal_data = {
            "name": "To Delete",
            "type": MealType.SNACK,
            "date": datetime.now(),
            "user_id": "test-user-delete",
            "meal_foods_data": [],
        }

        created_meal = await meal_repo.create_meal_with_foods(meal_data)
        meal_id = created_meal.id_

        # Delete the meal
        result = await meal_repo.delete_meal(meal_id)
        assert result is True

        # Verify it's gone
        fetched_meal = await meal_repo.get_meal_by_id(meal_id)
        assert fetched_meal is None

    async def test_delete_nonexistent_meal(self, seed_db, session):
        """Test deleting a meal that doesn't exist."""
        meal_repo = MealRepository(session)
        fake_uuid = UUID("00000000-0000-0000-0000-000000000000")

        result = await meal_repo.delete_meal(fake_uuid)
        assert result is False

    async def test_add_food_to_meal(self, seed_db, session):
        """Test adding a food item to an existing meal."""
        meal_repo = MealRepository(session)
        test_meal = seed_db["test_meal"]
        chicken_breast = seed_db["chicken_breast"]

        # Check initial state
        initial_meal = await meal_repo.get_meal_by_id(test_meal.id_)
        print(f"Initial meal_foods count: {len(initial_meal.meal_foods)}")

        # Add chicken breast to the meal
        updated_meal = await meal_repo.add_food_to_meal(
            meal_id=test_meal.id_,
            food_item_id=chicken_breast.id_,
            quantity=120.0,
            serving_unit="g",
        )
        print(f"After add_food_to_meal count: {len(updated_meal.meal_foods)}")

        await session.commit()  # Persist the food addition

        # Re-fetch the meal to verify the persisted state
        persisted_meal = await meal_repo.get_meal_by_id(test_meal.id_)
        print(f"After commit count: {len(persisted_meal.meal_foods)}")

        # Check raw database state
        from sqlalchemy import select, text

        from meals.repository.models import MealFoodModel

        stmt = select(MealFoodModel).where(MealFoodModel.meal_id == test_meal.id_)
        result = await session.execute(stmt)
        meal_foods_raw = result.scalars().all()
        print(f"Raw database meal_foods count: {len(meal_foods_raw)}")

        assert persisted_meal is not None
        assert len(persisted_meal.meal_foods) == 3  # Originally 2, now 3

        # Find the newly added food
        chicken_meal_food = None
        for meal_food in persisted_meal.meal_foods:
            if meal_food.food_item.name == "Chicken Breast":
                chicken_meal_food = meal_food
                break

        assert chicken_meal_food is not None
        assert chicken_meal_food.quantity == 120.0
        assert chicken_meal_food.serving_unit == "g"

    async def test_remove_food_from_meal(self, seed_db, session):
        """Test removing a food item from a meal."""
        meal_repo = MealRepository(session)
        test_meal = seed_db["test_meal"]
        apple = seed_db["apple"]

        # Remove apple from the meal
        updated_meal = await meal_repo.remove_food_from_meal(
            meal_id=test_meal.id_,
            food_item_id=apple.id_,
        )
        await session.commit()  # Persist the food removal

        # Re-fetch the meal to verify the persisted state
        persisted_meal = await meal_repo.get_meal_by_id(test_meal.id_)

        assert persisted_meal is not None
        assert len(persisted_meal.meal_foods) == 1  # Originally 2, now 1

        # Verify apple is no longer in the meal
        food_names = [mf.food_item.name for mf in persisted_meal.meal_foods]
        assert "Apple" not in food_names
        assert "Oatmeal" in food_names  # Should still have oatmeal

    async def test_remove_nonexistent_food_from_meal(self, seed_db, session):
        """Test removing a food item that's not in the meal."""
        meal_repo = MealRepository(session)
        test_meal = seed_db["test_meal"]
        chicken_breast = seed_db["chicken_breast"]  # Not in the test meal

        # Try to remove chicken breast (which isn't in the meal)
        updated_meal = await meal_repo.remove_food_from_meal(
            meal_id=test_meal.id_,
            food_item_id=chicken_breast.id_,
        )

        assert updated_meal is not None
        assert len(updated_meal.meal_foods) == 2  # Should remain unchanged

    async def test_create_meal_without_foods(self, seed_db, session):
        """Test creating a meal with no food items."""
        meal_repo = MealRepository(session)

        meal_data = {
            "name": "Empty Meal",
            "type": MealType.SNACK,
            "date": datetime.now(),
            "user_id": "test-user-empty",
            "meal_foods_data": [],
        }

        created_meal = await meal_repo.create_meal_with_foods(meal_data)

        assert created_meal is not None
        assert created_meal.name == "Empty Meal"
        assert len(created_meal.meal_foods) == 0

    async def test_complex_meal_model_to_dict_conversion(self, seed_db, session):
        """Test the complex _model_to_dict method with nested relationships."""
        meal_repo = MealRepository(session)

        # Create a meal with multiple foods to test conversion
        meal_data = {
            "name": "Complex Meal",
            "type": MealType.LUNCH,
            "date": datetime.now(),
            "notes": "Testing conversion",
            "user_id": "test-user-complex",
            "meal_foods_data": [
                {
                    "food_item_id": seed_db["apple"].id_,
                    "quantity": 100.0,
                    "serving_unit": "g",
                },
                {
                    "food_item_id": seed_db["chicken_breast"].id_,
                    "quantity": 150.0,
                    "serving_unit": "g",
                },
                {
                    "food_item_id": seed_db["oatmeal"].id_,
                    "quantity": 50.0,
                    "serving_unit": "g",
                },
            ],
        }

        created_meal = await meal_repo.create_meal_with_foods(meal_data)

        assert created_meal is not None
        assert len(created_meal.meal_foods) == 3

        # Verify all food items have complete nutrition data
        for meal_food in created_meal.meal_foods:
            food_item = meal_food.food_item
            assert food_item is not None
            assert food_item.name is not None
            assert food_item.calories is not None
            assert food_item.protein is not None
            # Optional fields may be None but should be handled properly
            assert hasattr(food_item, "saturated_fat")
            assert hasattr(food_item, "vitamin_d")
