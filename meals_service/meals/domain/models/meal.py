from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from meals.repository.models.enums import MealType

from .meal_food import DomainMealFood


class DomainMeal(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_: UUID
    created_at: datetime
    modified_at: datetime

    # Meal information
    name: str
    type: MealType
    date: datetime
    notes: Optional[str] = None
    user_id: str  # Internal user ID (not Supabase ID)

    # Nested meal foods
    meal_foods: List[DomainMealFood] = Field(default_factory=list)
