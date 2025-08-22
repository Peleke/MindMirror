from typing import Any, Dict, List, Optional
from uuid import UUID

from meals.domain.models import DomainFoodItem
from meals.repository.repositories import FoodItemRepository


class FoodItemService:
    def __init__(self, repository: FoodItemRepository):
        self.repository = repository

    async def create_food_item(self, food_item_data: Dict[str, Any]) -> DomainFoodItem:
        """Create a new food item."""
        return await self.repository.create_food_item(food_item_data)

    async def get_food_item_by_id(self, food_item_id: UUID) -> Optional[DomainFoodItem]:
        """Get a food item by ID."""
        return await self.repository.get_food_item_by_id(food_item_id)

    async def search_food_items(self, query: str, limit: Optional[int] = None) -> List[DomainFoodItem]:
        """Search food items by name with fuzzy matching."""
        return await self.repository.search_food_items(query, limit)

    async def list_food_items(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        search_term: Optional[str] = None,
    ) -> List[DomainFoodItem]:
        """List all PUBLIC food items with pagination and optional search."""
        return await self.repository.list_food_items(limit=limit, offset=offset, search_term=search_term)

    async def list_food_items_by_user(
        self,
        user_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        search_term: Optional[str] = None,
    ) -> List[DomainFoodItem]:
        """List food items for a specific user with pagination and optional search."""
        return await self.repository.list_food_items_by_user(
            user_id=user_id, limit=limit, offset=offset, search_term=search_term
        )

    async def list_food_items_for_user_with_public(
        self,
        user_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        search_term: Optional[str] = None,
    ) -> List[DomainFoodItem]:
        """List both public food items AND user's personal food items with pagination and optional search."""
        return await self.repository.list_food_items_for_user_with_public(
            user_id=user_id, limit=limit, offset=offset, search_term=search_term
        )

    async def update_food_item(self, food_item_id: UUID, update_data: Dict[str, Any]) -> Optional[DomainFoodItem]:
        """Update a food item."""
        return await self.repository.update_food_item(food_item_id, update_data)

    async def delete_food_item(self, food_item_id: UUID) -> bool:
        """Delete a food item."""
        return await self.repository.delete_food_item(food_item_id)
