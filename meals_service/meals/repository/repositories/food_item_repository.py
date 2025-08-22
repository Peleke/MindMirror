from typing import Any, List, Optional
from uuid import UUID

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from meals.domain.models import DomainFoodItem
from meals.repository.models import FoodItemModel


class FoodItemRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_food_item(self, food_item_data: dict) -> DomainFoodItem:
        """Create a new food item."""
        new_food_item = FoodItemModel(**food_item_data)
        self.session.add(new_food_item)
        await self.session.flush()  # Get ID for return
        await self.session.refresh(new_food_item)
        return DomainFoodItem.model_validate(new_food_item)

    async def get_food_item_by_id(self, food_item_id: UUID) -> Optional[DomainFoodItem]:
        """Get a food item by ID."""
        stmt = select(FoodItemModel).where(FoodItemModel.id_ == food_item_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()
        return DomainFoodItem.model_validate(record) if record else None

    async def list_food_items(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        search_term: Optional[str] = None,
    ) -> List[DomainFoodItem]:
        """List PUBLIC food items (user_id is NULL) with optional search and pagination."""
        stmt = select(FoodItemModel).where(FoodItemModel.user_id == None).order_by(FoodItemModel.name)

        # Apply search filter
        if search_term:
            stmt = stmt.where(FoodItemModel.name.ilike(f"%{search_term}%"))

        # Apply pagination
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        records = result.scalars().all()
        return [DomainFoodItem.model_validate(record) for record in records]

    async def list_food_items_by_user(
        self,
        user_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        search_term: Optional[str] = None,
    ) -> List[DomainFoodItem]:
        """List food items for a specific user with optional search and pagination."""
        stmt = select(FoodItemModel).where(FoodItemModel.user_id == user_id).order_by(FoodItemModel.name)

        # Apply search filter
        if search_term:
            stmt = stmt.where(FoodItemModel.name.ilike(f"%{search_term}%"))

        # Apply pagination
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        records = result.scalars().all()
        return [DomainFoodItem.model_validate(record) for record in records]

    async def list_food_items_for_user_with_public(
        self,
        user_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        search_term: Optional[str] = None,
    ) -> List[DomainFoodItem]:
        """List both public food items AND user's personal food items with optional search and pagination."""
        stmt = select(FoodItemModel).where(
            or_(
                FoodItemModel.user_id == None,  # Public foods
                FoodItemModel.user_id == user_id  # User's personal foods
            )
        ).order_by(FoodItemModel.name)

        # Apply search filter
        if search_term:
            stmt = stmt.where(FoodItemModel.name.ilike(f"%{search_term}%"))

        # Apply pagination
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        records = result.scalars().all()
        return [DomainFoodItem.model_validate(record) for record in records]

    async def update_food_item(self, food_item_id: UUID, update_data: dict) -> Optional[DomainFoodItem]:
        """Update a food item."""
        stmt = select(FoodItemModel).where(FoodItemModel.id_ == food_item_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            return None

        for key, value in update_data.items():
            if hasattr(record, key):
                setattr(record, key, value)

        await self.session.flush()
        await self.session.refresh(record)
        return DomainFoodItem.model_validate(record)

    async def delete_food_item(self, food_item_id: UUID) -> bool:
        """Delete a food item."""
        stmt = select(FoodItemModel).where(FoodItemModel.id_ == food_item_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if record:
            await self.session.delete(record)
            await self.session.flush()
            return True
        return False

    async def search_food_items(self, query: str, limit: Optional[int] = None) -> List[DomainFoodItem]:
        """Search food items by name with fuzzy matching."""
        stmt = select(FoodItemModel).where(FoodItemModel.name.ilike(f"%{query}%")).order_by(FoodItemModel.name)

        if limit:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        records = result.scalars().all()
        return [DomainFoodItem.model_validate(record) for record in records]

    async def search_food_items_by_name(self, name: str, limit: int = 20) -> List[DomainFoodItem]:
        """Search food items by name with fuzzy matching."""
        stmt = (
            select(FoodItemModel).where(FoodItemModel.name.ilike(f"%{name}%")).order_by(FoodItemModel.name).limit(limit)
        )
        result = await self.session.execute(stmt)
        records = result.scalars().all()
        return [DomainFoodItem.model_validate(record) for record in records]
