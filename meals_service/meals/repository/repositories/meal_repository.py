from datetime import date, datetime, time
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from meals.domain.models import DomainMeal
from meals.repository.models import (
    FoodItemModel,
    MealFoodModel,
    MealModel,
)
from meals.repository.models.enums import MealType


class MealRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _model_to_dict(self, model: MealModel) -> Dict[str, Any]:
        """Convert a SQLAlchemy model to a dictionary for Pydantic validation."""
        # Convert enum name string from DB to actual Enum member for Pydantic validation
        db_type_value = model.type
        repo_meal_type_member = None
        if isinstance(db_type_value, str):  # It will be a string like 'DINNER' from the DB
            try:
                repo_meal_type_member = MealType[db_type_value]  # Access enum member by name
            except KeyError:
                # This should not happen if DB enum values match Python enum names
                raise ValueError(f"Invalid meal type '{db_type_value}' found in database for meal ID {model.id_}")
        elif isinstance(db_type_value, MealType):  # If it's already an enum (less likely from direct DB read)
            repo_meal_type_member = db_type_value
        else:
            raise ValueError(
                f"Unexpected meal type format '{type(db_type_value)}' from database for meal ID {model.id_}"
            )

        result = {
            "id_": model.id_,
            "created_at": model.created_at,
            "modified_at": model.modified_at,
            "name": model.name,
            "type": repo_meal_type_member,  # Use the converted enum member
            "date": model.date,
            "notes": model.notes,
            "user_id": model.user_id,
            "meal_foods": [],
        }

        # Add meal_foods if loaded
        if model.meal_foods:
            result["meal_foods"] = []
            for meal_food in model.meal_foods:
                meal_food_dict = {
                    "id_": meal_food.id_,
                    "created_at": meal_food.created_at,
                    "modified_at": meal_food.modified_at,
                    "meal_id": meal_food.meal_id,
                    "food_item_id": meal_food.food_item_id,
                    "quantity": meal_food.quantity,
                    "serving_unit": meal_food.serving_unit,
                    "food_item": None,
                }

                # Add food item if loaded
                if meal_food.food_item:
                    food_item = meal_food.food_item
                    meal_food_dict["food_item"] = {
                        "id_": food_item.id_,
                        "created_at": food_item.created_at,
                        "modified_at": food_item.modified_at,
                        "name": food_item.name,
                        "serving_size": food_item.serving_size,
                        "serving_unit": food_item.serving_unit,
                        "calories": food_item.calories,
                        "protein": food_item.protein,
                        "carbohydrates": food_item.carbohydrates,
                        "fat": food_item.fat,
                        "saturated_fat": food_item.saturated_fat,
                        "monounsaturated_fat": food_item.monounsaturated_fat,
                        "polyunsaturated_fat": food_item.polyunsaturated_fat,
                        "trans_fat": food_item.trans_fat,
                        "cholesterol": food_item.cholesterol,
                        "fiber": food_item.fiber,
                        "sugar": food_item.sugar,
                        "sodium": food_item.sodium,
                        "vitamin_d": food_item.vitamin_d,
                        "calcium": food_item.calcium,
                        "iron": food_item.iron,
                        "potassium": food_item.potassium,
                        "zinc": food_item.zinc,
                    }

                result["meal_foods"].append(meal_food_dict)

        return result

    async def create_meal_with_foods(self, meal_data: dict) -> DomainMeal:
        """Create a new meal with nested food items."""
        meal_foods_data = meal_data.pop("meal_foods_data", [])

        # Create MealModel instance first
        new_meal = MealModel(**meal_data)
        self.session.add(new_meal)
        await self.session.flush()  # Get ID for relationships
        await self.session.refresh(new_meal)

        # Create meal_foods relationships
        created_meal_foods = []
        for meal_food_data in meal_foods_data:
            # Ensure meal_id is set
            meal_food_data["meal_id"] = new_meal.id_
            new_meal_food = MealFoodModel(**meal_food_data)
            self.session.add(new_meal_food)
            await self.session.flush()
            await self.session.refresh(new_meal_food)
            created_meal_foods.append(new_meal_food)

        new_meal.meal_foods = created_meal_foods

        # Re-fetch with all relationships loaded
        stmt = (
            select(MealModel)
            .where(MealModel.id_ == new_meal.id_)
            .options(selectinload(MealModel.meal_foods).selectinload(MealFoodModel.food_item))
        )
        result = await self.session.execute(stmt)
        refetched_meal = result.scalar_one_or_none()
        if not refetched_meal:
            raise Exception("Failed to re-fetch meal after creation")

        # Convert to dict before passing to model_validate
        meal_dict = self._model_to_dict(refetched_meal)
        return DomainMeal.model_validate(meal_dict)

    async def get_meal_by_id(self, meal_id: UUID) -> Optional[DomainMeal]:
        """Get a meal by ID with all relationships loaded."""
        stmt = (
            select(MealModel)
            .where(MealModel.id_ == meal_id)
            .options(selectinload(MealModel.meal_foods).selectinload(MealFoodModel.food_item))
        )
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            return None

        # Convert to dict before passing to model_validate
        meal_dict = self._model_to_dict(record)
        return DomainMeal.model_validate(meal_dict)

    async def list_meals_by_user_and_date_range(
        self,
        user_id: str,
        start_date: date,
        end_date: date,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[DomainMeal]:
        """List meals for a user within a date range."""
        # Convert date objects to datetime objects for proper boundary handling
        start_datetime = datetime.combine(start_date, time.min)  # Start of start_date (00:00:00)
        end_datetime = datetime.combine(end_date, time.max)  # End of end_date (23:59:59.999999)

        stmt = (
            select(MealModel)
            .where(MealModel.user_id == user_id)
            .where(MealModel.date >= start_datetime)
            .where(MealModel.date <= end_datetime)
            .options(selectinload(MealModel.meal_foods).selectinload(MealFoodModel.food_item))
            .order_by(MealModel.date.desc(), MealModel.created_at.desc())
        )

        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        records = result.scalars().all()

        # Convert each record to dict before passing to model_validate
        return [DomainMeal.model_validate(self._model_to_dict(record)) for record in records]

    async def list_meals_by_user(
        self,
        user_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        search_term: Optional[str] = None,
    ) -> List[DomainMeal]:
        """List all meals for a user with pagination and optional search."""
        stmt = (
            select(MealModel)
            .where(MealModel.user_id == user_id)
            .options(selectinload(MealModel.meal_foods).selectinload(MealFoodModel.food_item))
            .order_by(MealModel.date.desc(), MealModel.created_at.desc())
        )

        # Apply search filter
        if search_term:
            stmt = stmt.where(MealModel.name.ilike(f"%{search_term}%"))

        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        records = result.scalars().all()

        # Convert each record to dict before passing to model_validate
        return [DomainMeal.model_validate(self._model_to_dict(record)) for record in records]

    async def update_meal(self, meal_id: UUID, update_data: dict) -> Optional[DomainMeal]:
        """Update a meal. Basic update focuses on MealModel fields only."""
        stmt = select(MealModel).where(MealModel.id_ == meal_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            return None

        for key, value in update_data.items():
            if hasattr(record, key):
                setattr(record, key, value)

        await self.session.flush()

        # Re-fetch with all relationships loaded for consistent return type
        return await self.get_meal_by_id(meal_id)

    async def delete_meal(self, meal_id: UUID) -> bool:
        """Delete a meal (cascading deletes will handle meal_foods)."""
        stmt = select(MealModel).where(MealModel.id_ == meal_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if record:
            await self.session.delete(record)
            await self.session.flush()
            return True
        return False

    async def add_food_to_meal(
        self, meal_id: UUID, food_item_id: UUID, quantity: float, serving_unit: str
    ) -> Optional[DomainMeal]:
        """Add a food item to an existing meal."""
        # Create new meal_food relationship
        meal_food_data = {
            "meal_id": meal_id,
            "food_item_id": food_item_id,
            "quantity": quantity,
            "serving_unit": serving_unit,
        }

        new_meal_food = MealFoodModel(**meal_food_data)
        self.session.add(new_meal_food)
        await self.session.flush()

        # Clear session cache to ensure fresh data on re-fetch
        self.session.expunge_all()

        # Return updated meal
        return await self.get_meal_by_id(meal_id)

    async def remove_food_from_meal(self, meal_id: UUID, food_item_id: UUID) -> Optional[DomainMeal]:
        """Remove a food item from a meal."""
        stmt = select(MealFoodModel).where(MealFoodModel.meal_id == meal_id, MealFoodModel.food_item_id == food_item_id)
        result = await self.session.execute(stmt)
        meal_food = result.scalar_one_or_none()

        if meal_food:
            await self.session.delete(meal_food)
            await self.session.flush()

        # Clear session cache to ensure fresh data on re-fetch
        self.session.expunge_all()

        # Return updated meal
        return await self.get_meal_by_id(meal_id)
