from uuid import UUID

import pytest

from meals.repository.repositories.food_item_repository import FoodItemRepository


@pytest.mark.asyncio
class TestFoodItemRepository:

    async def test_create_and_get_food_item(self, seed_db, session):
        """Test creating a new food item and retrieving it."""
        new_food_data = {
            "name": "Banana",
            "serving_size": 118.0,
            "serving_unit": "g",
            "calories": 105.0,
            "protein": 1.3,
            "carbohydrates": 27.0,
            "fat": 0.3,
            "fiber": 3.1,
            "sugar": 14.2,
            "potassium": 358.0,
        }

        food_repo = FoodItemRepository(session)
        created_food = await food_repo.create_food_item(new_food_data)

        assert created_food is not None
        assert created_food.name == "Banana"
        assert created_food.calories == 105.0
        assert created_food.protein == 1.3
        assert created_food.fiber == 3.1

        # Test retrieval
        fetched_food = await food_repo.get_food_item_by_id(created_food.id_)
        assert fetched_food is not None
        assert fetched_food.name == "Banana"
        assert fetched_food.id_ == created_food.id_

    async def test_list_food_items(self, seed_db, session):
        """Test listing food items with pagination and filtering."""
        food_repo = FoodItemRepository(session)

        # List all food items - should only list public items (oatmeal from seed_db)
        all_foods = await food_repo.list_food_items()
        # Assuming 'oatmeal' is the only public item from seed_db.
        # If apple and chicken_breast are user-specific, this should be 1.
        assert len(all_foods) == 1
        assert all_foods[0].name == "Oatmeal"  # Verify it's the oatmeal

        # Test pagination (still on public items)
        # If only 1 public item, limit=2 should still return 1.
        limited_foods = await food_repo.list_food_items(limit=2)
        assert len(limited_foods) == 1

        # Test offset (still on public items)
        # If only 1 public item, offset=1 should return 0.
        offset_foods = await food_repo.list_food_items(limit=2, offset=1)
        assert len(offset_foods) == 0

        # Test search by name (on public items)
        # "Apple" is user-specific in seed_db, so searching public items should yield 0
        apple_foods = await food_repo.list_food_items(search_term="Apple")
        assert len(apple_foods) == 0

        # Test search for a public item
        oatmeal_foods = await food_repo.list_food_items(search_term="Oatmeal")
        assert len(oatmeal_foods) == 1
        assert oatmeal_foods[0].name == "Oatmeal"

    async def test_search_food_items_by_name(self, seed_db, session):
        """Test fuzzy search functionality."""
        food_repo = FoodItemRepository(session)

        # Test exact match
        results = await food_repo.search_food_items_by_name("Apple")
        assert len(results) == 1
        assert results[0].name == "Apple"

        # Test partial match
        results = await food_repo.search_food_items_by_name("Chick")
        assert len(results) == 1
        assert results[0].name == "Chicken Breast"

        # Test case insensitive
        results = await food_repo.search_food_items_by_name("oat")
        assert len(results) == 1
        assert results[0].name == "Oatmeal"

        # Test no match
        results = await food_repo.search_food_items_by_name("NonExistent")
        assert len(results) == 0

    async def test_update_food_item(self, seed_db, session):
        """Test updating food item properties."""
        food_repo = FoodItemRepository(session)
        apple = seed_db["apple"]

        update_data = {
            "name": "Green Apple",
            "calories": 58.0,
            "sugar": 11.0,
        }

        updated_food = await food_repo.update_food_item(apple.id_, update_data)

        assert updated_food is not None
        assert updated_food.name == "Green Apple"
        assert updated_food.calories == 58.0
        assert updated_food.sugar == 11.0
        # Unchanged fields should remain the same
        assert updated_food.protein == 0.3
        assert updated_food.carbohydrates == 14.0

    async def test_update_nonexistent_food_item(self, seed_db, session):
        """Test updating a food item that doesn't exist."""
        food_repo = FoodItemRepository(session)
        fake_uuid = UUID("00000000-0000-0000-0000-000000000000")

        update_data = {"name": "Should Not Update"}
        result = await food_repo.update_food_item(fake_uuid, update_data)

        assert result is None

    async def test_delete_food_item(self, seed_db, session):
        """Test deleting a food item."""
        food_repo = FoodItemRepository(session)
        chicken = seed_db["chicken_breast"]

        # Delete the food item
        result = await food_repo.delete_food_item(chicken.id_)
        assert result is True

        # Verify it's gone
        fetched_food = await food_repo.get_food_item_by_id(chicken.id_)
        assert fetched_food is None

    async def test_delete_nonexistent_food_item(self, seed_db, session):
        """Test deleting a food item that doesn't exist."""
        food_repo = FoodItemRepository(session)
        fake_uuid = UUID("00000000-0000-0000-0000-000000000000")

        result = await food_repo.delete_food_item(fake_uuid)
        assert result is False

    async def test_get_nonexistent_food_item(self, seed_db, session):
        """Test getting a food item that doesn't exist."""
        food_repo = FoodItemRepository(session)
        fake_uuid = UUID("00000000-0000-0000-0000-000000000000")

        result = await food_repo.get_food_item_by_id(fake_uuid)
        assert result is None

    async def test_create_food_item_with_optional_fields(self, seed_db, session):
        """Test creating food item with all optional nutrition fields."""
        food_repo = FoodItemRepository(session)

        comprehensive_food_data = {
            "name": "Comprehensive Food",
            "serving_size": 100.0,
            "serving_unit": "g",
            "calories": 200.0,
            "protein": 20.0,
            "carbohydrates": 30.0,
            "fat": 10.0,
            "saturated_fat": 3.0,
            "monounsaturated_fat": 4.0,
            "polyunsaturated_fat": 2.0,
            "trans_fat": 0.5,
            "cholesterol": 50.0,
            "fiber": 5.0,
            "sugar": 8.0,
            "sodium": 200.0,
            "vitamin_d": 2.5,
            "calcium": 150.0,
            "iron": 2.0,
            "potassium": 300.0,
            "zinc": 1.5,
        }

        created_food = await food_repo.create_food_item(comprehensive_food_data)

        assert created_food is not None
        assert created_food.name == "Comprehensive Food"
        assert created_food.saturated_fat == 3.0
        assert created_food.vitamin_d == 2.5
        assert created_food.calcium == 150.0
        assert created_food.zinc == 1.5

    async def test_list_food_items_with_filters(self, seed_db, session):
        """Test listing food items with custom filters."""
        food_repo = FoodItemRepository(session)

        # Create a public food item with specific calories for filtering
        high_calorie_food_data = {
            "name": "High Calorie Food",
            "serving_size": 100.0,
            "serving_unit": "g",
            "calories": 500.0,
            "protein": 10.0,
            "carbohydrates": 20.0,
            "fat": 15.0,
            "user_id": None,  # Explicitly public
        }

        await food_repo.create_food_item(high_calorie_food_data)

        # list_food_items fetches public items. Seed_db has "oatmeal" (public). This test adds one more.
        all_public_foods = await food_repo.list_food_items()
        assert len(all_public_foods) == 2  # "oatmeal" + "High Calorie Food"
