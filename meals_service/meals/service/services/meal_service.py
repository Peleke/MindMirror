from datetime import date, datetime, time
from typing import Any, Dict, List, Optional
from uuid import UUID

from meals.domain.models import DomainMeal
from meals.repository.models.enums import MealType as RepoMealType
from meals.repository.repositories import MealRepository
from meals.web.graphql.types import MealTypeGQLEnum


class MealService:
    def __init__(self, repository: MealRepository):
        self.repository = repository

    async def create_meal(self, meal_data: Dict[str, Any]) -> DomainMeal:
        """Create a new meal with nested food items."""
        # Date is now expected to be a datetime object from GraphQL layer
        if "date" in meal_data and not isinstance(meal_data["date"], datetime):
            # This case should ideally not happen if GraphQL types are correct
            # but adding a fallback or raising an error might be useful.
            raise ValueError(f"Meal date must be a datetime object. Got: {type(meal_data['date'])}")

        # Convert MealTypeGQLEnum to the repository enum's NAME (e.g., "LUNCH")
        if "type" in meal_data and isinstance(meal_data["type"], MealTypeGQLEnum):
            try:
                repo_enum_member = RepoMealType(meal_data["type"].value)
                meal_data["type"] = repo_enum_member.name
            except ValueError:
                raise ValueError(f"Invalid meal type value received from GQL: {meal_data['type'].value}")

        return await self.repository.create_meal_with_foods(meal_data)

    async def get_meal_by_id(self, meal_id: UUID) -> Optional[DomainMeal]:
        """Get a meal by ID."""
        return await self.repository.get_meal_by_id(meal_id)

    async def list_meals_by_user_and_date_range(
        self,
        user_id: str,
        start_date: date,
        end_date: date,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[DomainMeal]:
        """List meals for a user within a date range."""
        return await self.repository.list_meals_by_user_and_date_range(
            user_id=user_id, start_date=start_date, end_date=end_date, limit=limit, offset=offset
        )

    async def list_meals_by_user(
        self,
        user_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        search_term: Optional[str] = None,
    ) -> List[DomainMeal]:
        """List all meals for a user with pagination and optional search."""
        return await self.repository.list_meals_by_user(user_id, limit, offset, search_term)

    async def update_meal(self, meal_id: UUID, update_data: Dict[str, Any]) -> Optional[DomainMeal]:
        """Update a meal."""
        # Date is now expected to be a datetime object from GraphQL layer
        if "date" in update_data and update_data["date"] is not None and not isinstance(update_data["date"], datetime):
            # This case should ideally not happen.
            raise ValueError(f"Meal date for update must be a datetime object. Got: {type(update_data['date'])}")

        # Convert MealTypeGQLEnum to the repository enum's NAME (e.g., "LUNCH")
        if "type" in update_data and isinstance(update_data["type"], MealTypeGQLEnum):
            try:
                repo_enum_member = RepoMealType(update_data["type"].value)
                update_data["type"] = repo_enum_member.name
            except ValueError:
                raise ValueError(f"Invalid meal type value received from GQL for update: {update_data['type'].value}")

        return await self.repository.update_meal(meal_id, update_data)

    async def delete_meal(self, meal_id: UUID) -> bool:
        """Delete a meal."""
        return await self.repository.delete_meal(meal_id)

    async def add_food_to_meal(
        self, meal_id: UUID, food_item_id: UUID, quantity: float, serving_unit: str
    ) -> Optional[DomainMeal]:
        """Add a food item to an existing meal."""
        return await self.repository.add_food_to_meal(meal_id, food_item_id, quantity, serving_unit)

    async def remove_food_from_meal(self, meal_id: UUID, food_item_id: UUID) -> Optional[DomainMeal]:
        """Remove a food item from a meal."""
        return await self.repository.remove_food_from_meal(meal_id, food_item_id)
