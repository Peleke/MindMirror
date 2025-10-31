from uuid import uuid4

import pytest

from meals.domain.models import DomainFoodItem
from meals.repository.repositories import FoodItemRepository
from meals.service.services import FoodItemService


@pytest.mark.asyncio
class TestFoodItemService:
    async def test_create_food_item(self, session, seed_db):
        """Test creating a food item through the service."""
        food_repo = FoodItemRepository(session)
        service = FoodItemService(food_repo)

        food_data = {
            "name": "Service Test Food",
            "serving_size": 100.0,
            "serving_unit": "g",
            "calories": 200.0,
            "protein": 15.0,
            "carbohydrates": 30.0,
            "fat": 5.0,
        }

        created_food = await service.create_food_item(food_data)
        await session.commit()

        assert isinstance(created_food, DomainFoodItem)
        assert created_food.name == food_data["name"]
        assert created_food.calories == food_data["calories"]

        # Verify in database
        fetched_food = await service.get_food_item_by_id(created_food.id_)
        assert fetched_food is not None
        assert fetched_food.name == food_data["name"]

    async def test_get_food_item_by_id(self, session, seed_db):
        """Test getting a food item by ID."""
        food_repo = FoodItemRepository(session)
        service = FoodItemService(food_repo)
        apple = seed_db["apple"]

        fetched_food = await service.get_food_item_by_id(apple.id_)
        assert fetched_food is not None
        assert fetched_food.id_ == apple.id_
        assert fetched_food.name == apple.name

    async def test_get_food_item_by_id_not_found(self, session, seed_db):
        """Test getting a non-existent food item."""
        food_repo = FoodItemRepository(session)
        service = FoodItemService(food_repo)

        fake_id = uuid4()
        fetched_food = await service.get_food_item_by_id(fake_id)
        assert fetched_food is None

    async def test_search_food_items(self, session, seed_db):
        """Test searching food items by name."""
        food_repo = FoodItemRepository(session)
        service = FoodItemService(food_repo)

        # Search for foods with "chicken" in the name
        results = await service.search_food_items("chicken")
        assert len(results) >= 1
        assert any("chicken" in food.name.lower() for food in results)

        # Search for non-existent food
        results = await service.search_food_items("nonexistent")
        assert len(results) == 0

    async def test_search_food_items_with_limit(self, session, seed_db):
        """Test searching food items with limit."""
        food_repo = FoodItemRepository(session)
        service = FoodItemService(food_repo)

        # Create multiple foods to test limit
        for i in range(5):
            food_data = {
                "name": f"Test Food {i}",
                "serving_size": 100.0,
                "serving_unit": "g",
                "calories": 100.0,
                "protein": 10.0,
                "carbohydrates": 15.0,
                "fat": 2.0,
            }
            await service.create_food_item(food_data)
        await session.commit()

        # Search with limit
        results = await service.search_food_items("test", limit=3)
        assert len(results) <= 3

    async def test_list_food_items(self, session, seed_db):
        """Test listing food items with pagination."""
        food_repo = FoodItemRepository(session)
        service = FoodItemService(food_repo)

        # list_food_items should only return public items (user_id is NULL)
        # From seed_db, "oatmeal" is public. "apple" and "chicken_breast" are user-specific.
        public_foods = await service.list_food_items(limit=10)

        # Check that only public items are listed
        assert len(public_foods) == 1
        assert public_foods[0].name == "Oatmeal"
        assert not any(food.name == "Apple" for food in public_foods)
        assert not any(food.name == "Chicken Breast" for food in public_foods)

        # Add another public item via service to test listing multiple public items
        public_food_data = {
            "name": "Public Service Test Food",
            "serving_size": 50.0,
            "serving_unit": "g",
            "calories": 150.0,
            "protein": 10.0,
            "carbohydrates": 20.0,
            "fat": 3.0,
            "user_id": None,  # Explicitly public
        }
        await service.create_food_item(public_food_data)
        await session.commit()

        all_public_foods_after_add = await service.list_food_items(limit=10)
        assert len(all_public_foods_after_add) == 2  # "oatmeal" + "Public Service Test Food"
        assert any(food.name == "Oatmeal" for food in all_public_foods_after_add)
        assert any(food.name == "Public Service Test Food" for food in all_public_foods_after_add)

    async def test_update_food_item(self, session, seed_db):
        """Test updating a food item."""
        food_repo = FoodItemRepository(session)
        service = FoodItemService(food_repo)
        apple = seed_db["apple"]

        update_data = {
            "name": "Updated Apple",
            "calories": 95.0,
        }

        updated_food = await service.update_food_item(apple.id_, update_data)
        await session.commit()

        assert updated_food is not None
        assert updated_food.name == "Updated Apple"
        assert updated_food.calories == 95.0
        assert updated_food.protein == apple.protein  # Unchanged

        # Verify in database
        fetched_food = await service.get_food_item_by_id(apple.id_)
        assert fetched_food.name == "Updated Apple"

    async def test_update_food_item_not_found(self, session, seed_db):
        """Test updating a non-existent food item."""
        food_repo = FoodItemRepository(session)
        service = FoodItemService(food_repo)

        fake_id = uuid4()
        update_data = {"name": "Non-existent"}

        updated_food = await service.update_food_item(fake_id, update_data)
        assert updated_food is None

    async def test_delete_food_item(self, session, seed_db):
        """Test deleting a food item."""
        food_repo = FoodItemRepository(session)
        service = FoodItemService(food_repo)

        # Create a new food item that won't be referenced by meals
        food_data = {
            "name": "Food to Delete",
            "serving_size": 100.0,
            "serving_unit": "g",
            "calories": 100.0,
            "protein": 10.0,
            "carbohydrates": 15.0,
            "fat": 2.0,
        }
        created_food = await service.create_food_item(food_data)
        await session.commit()

        deleted = await service.delete_food_item(created_food.id_)
        await session.commit()

        assert deleted is True

        # Verify deletion
        fetched_food = await service.get_food_item_by_id(created_food.id_)
        assert fetched_food is None

    async def test_delete_food_item_not_found(self, session, seed_db):
        """Test deleting a non-existent food item."""
        food_repo = FoodItemRepository(session)
        service = FoodItemService(food_repo)

        fake_id = uuid4()
        deleted = await service.delete_food_item(fake_id)
        assert deleted is False
