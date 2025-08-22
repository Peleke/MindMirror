from datetime import date, datetime, time, timedelta, timezone
from uuid import uuid4

import pytest

from meals.domain.models import DomainMeal
from meals.repository.models.enums import MealType as RepoMealType
from meals.repository.repositories import MealRepository
from meals.service.services import MealService
from meals.web.graphql.types import MealTypeGQLEnum


@pytest.mark.asyncio
class TestMealService:
    async def test_create_meal_with_datetime_input(self, session, seed_db):
        """Test creating a meal with datetime input."""
        meal_repo = MealRepository(session)
        service = MealService(meal_repo)

        now_dt = datetime.now(timezone.utc)
        meal_data = {
            "name": "Service Datetime Meal",
            "type": MealTypeGQLEnum.LUNCH,
            "date": now_dt,
            "user_id": "test-user-service-dt",
            "meal_foods_data": [
                {
                    "food_item_id": seed_db["apple"].id_,
                    "quantity": 150.0,
                    "serving_unit": "g",
                }
            ],
        }

        created_meal = await service.create_meal(meal_data)
        await session.commit()

        assert isinstance(created_meal, DomainMeal)
        assert created_meal.name == meal_data["name"]
        assert created_meal.date == now_dt
        assert len(created_meal.meal_foods) == 1
        db_meal = await meal_repo.get_meal_by_id(created_meal.id_)
        assert db_meal.type == RepoMealType.LUNCH

    async def test_create_meal_invalid_datetime_input_type(self, session, seed_db):
        """Test creating a meal with invalid date type (e.g., string that isn't ISO datetime)."""
        meal_repo = MealRepository(session)
        service = MealService(meal_repo)

        meal_data = {
            "name": "Invalid Date Type Meal",
            "type": MealTypeGQLEnum.BREAKFAST,
            "date": "this-is-not-a-datetime",
            "user_id": "test-user-service-invalid",
            "meal_foods_data": [],
        }
        with pytest.raises(ValueError, match="Meal date must be a datetime object"):
            await service.create_meal(meal_data)

    @pytest.mark.skip()
    async def test_create_meal_invalid_enum_value_in_service(self, session, seed_db):
        """Test creating a meal with an invalid GQL enum value passed to service."""
        meal_repo = MealRepository(session)
        service = MealService(meal_repo)
        now_dt = datetime.now(timezone.utc)
        meal_data_invalid_enum = {
            "name": "Invalid Enum Meal",
            "type": "INVALID_MEAL_TYPE",
            "date": now_dt,
            "user_id": "test-user-service-invalid-enum",
        }
        with pytest.raises(ValueError, match="Invalid meal type value received from GQL"):
            await service.create_meal({**meal_data_invalid_enum, "type": MealTypeGQLEnum.LUNCH})

    async def test_get_meal_by_id(self, session, seed_db):
        """Test getting a meal by ID."""
        meal_repo = MealRepository(session)
        service = MealService(meal_repo)
        test_meal = seed_db["test_meal"]

        fetched_meal = await service.get_meal_by_id(test_meal.id_)
        assert fetched_meal is not None
        assert fetched_meal.id_ == test_meal.id_
        assert fetched_meal.name == test_meal.name

    async def test_get_meal_by_id_not_found(self, session, seed_db):
        """Test getting a non-existent meal."""
        meal_repo = MealRepository(session)
        service = MealService(meal_repo)

        fake_id = uuid4()
        fetched_meal = await service.get_meal_by_id(fake_id)
        assert fetched_meal is None

    async def test_list_meals_by_user_and_date_range(self, session, seed_db):
        """Test listing meals by user and date range."""
        meal_repo = MealRepository(session)
        service = MealService(meal_repo)

        today = datetime.now(timezone.utc).date()
        yesterday_dt = datetime.now(timezone.utc) - timedelta(days=1)
        yesterday_date_obj = yesterday_dt.date()

        yesterday_meal_data = {
            "name": "Yesterday Service Meal",
            "type": MealTypeGQLEnum.DINNER,
            "date": yesterday_dt,
            "user_id": "test-user-range",
            "meal_foods_data": [],
        }
        await service.create_meal(yesterday_meal_data)
        await session.commit()

        meals = await service.list_meals_by_user_and_date_range(
            user_id="test-user-range",
            start_date=yesterday_date_obj,
            end_date=today,
        )

        assert len(meals) >= 1
        assert any(meal.name == "Yesterday Service Meal" for meal in meals)

    async def test_list_meals_by_user(self, session, seed_db):
        """Test listing all meals for a user with pagination."""
        meal_repo = MealRepository(session)
        service = MealService(meal_repo)

        test_meal = seed_db["test_meal"]
        meals = await service.list_meals_by_user(user_id=test_meal.user_id, limit=10)

        assert len(meals) >= 1
        assert any(meal.id_ == test_meal.id_ for meal in meals)

    async def test_update_meal_with_datetime_input(self, session, seed_db):
        """Test updating a meal with datetime input."""
        meal_repo = MealRepository(session)
        service = MealService(meal_repo)

        initial_dt = datetime.now(timezone.utc) - timedelta(days=10)
        meal_to_update_data = {
            "name": "Meal Before Update DT",
            "type": MealTypeGQLEnum.BREAKFAST,
            "date": initial_dt,
            "user_id": "test-user-update-dt",
        }
        created_meal_domain = await service.create_meal(meal_to_update_data)
        await session.commit()
        assert created_meal_domain is not None

        updated_dt = datetime.now(timezone.utc) - timedelta(days=2)
        update_data = {
            "name": "Updated Service Meal DT",
            "date": updated_dt,
            "type": MealTypeGQLEnum.LUNCH,
        }

        updated_meal = await service.update_meal(created_meal_domain.id_, update_data)
        await session.commit()

        assert updated_meal is not None
        assert updated_meal.name == "Updated Service Meal DT"
        assert updated_meal.date == updated_dt
        db_meal = await meal_repo.get_meal_by_id(created_meal_domain.id_)
        assert db_meal.type == RepoMealType.LUNCH

    async def test_update_meal_invalid_datetime_input_type(self, session, seed_db):
        """Test updating a meal with invalid date type."""
        meal_repo = MealRepository(session)
        service = MealService(meal_repo)

        initial_dt_for_invalid_update = datetime.now(timezone.utc) - timedelta(days=15)
        meal_to_update_for_invalid_data = {
            "name": "Meal Before Invalid Update DT",
            "type": MealTypeGQLEnum.SNACK,
            "date": initial_dt_for_invalid_update,
            "user_id": "test-user-invalid-update-dt",
        }
        created_meal_for_invalid = await service.create_meal(meal_to_update_for_invalid_data)
        await session.commit()
        assert created_meal_for_invalid is not None

        update_data = {
            "date": "not-a-valid-datetime-string-for-service",
        }
        with pytest.raises(ValueError, match="Meal date for update must be a datetime object"):
            await service.update_meal(created_meal_for_invalid.id_, update_data)

    async def test_delete_meal(self, session, seed_db):
        """Test deleting a meal."""
        meal_repo = MealRepository(session)
        service = MealService(meal_repo)

        meal_data_to_delete = {
            "name": "Meal to Delete DT",
            "type": MealTypeGQLEnum.SNACK,
            "date": datetime.now(timezone.utc),
            "user_id": "test-delete-user-dt",
            "meal_foods_data": [],
        }
        created_meal = await service.create_meal(meal_data_to_delete)
        await session.commit()

        deleted = await service.delete_meal(created_meal.id_)
        await session.commit()

        assert deleted is True

        fetched_meal = await service.get_meal_by_id(created_meal.id_)
        assert fetched_meal is None

    async def test_add_food_to_meal(self, session, seed_db):
        """Test adding a food item to a meal."""
        meal_repo = MealRepository(session)
        service = MealService(meal_repo)
        test_meal = seed_db["test_meal"]
        chicken_breast = seed_db["chicken_breast"]

        updated_meal = await service.add_food_to_meal(
            meal_id=test_meal.id_,
            food_item_id=chicken_breast.id_,
            quantity=150.0,
            serving_unit="g",
        )
        await session.commit()

        assert updated_meal is not None
        refetched_meal = await service.get_meal_by_id(test_meal.id_)
        food_names = [mf.food_item.name for mf in refetched_meal.meal_foods]
        assert "Chicken Breast" in food_names

    async def test_remove_food_from_meal(self, session, seed_db):
        """Test removing a food item from a meal."""
        meal_repo = MealRepository(session)
        service = MealService(meal_repo)
        test_meal = seed_db["test_meal"]

        existing_food = test_meal.meal_foods[0].food_item

        updated_meal = await service.remove_food_from_meal(
            meal_id=test_meal.id_,
            food_item_id=existing_food.id_,
        )
        await session.commit()

        assert updated_meal is not None
        refetched_meal = await service.get_meal_by_id(test_meal.id_)
        food_names = [mf.food_item.name for mf in refetched_meal.meal_foods]
        assert existing_food.name not in food_names
