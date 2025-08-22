from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .food_item import DomainFoodItem


class DomainMealFood(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_: UUID
    created_at: datetime
    modified_at: datetime

    # Foreign keys
    meal_id: UUID
    food_item_id: UUID

    # Quantity information
    quantity: float
    serving_unit: str

    # Nested food item data
    food_item: Optional[DomainFoodItem] = None
