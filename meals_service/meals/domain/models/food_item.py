from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DomainFoodItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_: UUID
    created_at: datetime
    modified_at: datetime

    # Basic information
    name: str
    serving_size: float
    serving_unit: str

    # Macronutrients (required)
    calories: float
    protein: float
    carbohydrates: float
    fat: float

    # Fat breakdown (optional)
    saturated_fat: Optional[float] = None
    monounsaturated_fat: Optional[float] = None
    polyunsaturated_fat: Optional[float] = None
    trans_fat: Optional[float] = None

    # Other nutrients (optional)
    cholesterol: Optional[float] = None  # mg
    fiber: Optional[float] = None  # g
    sugar: Optional[float] = None  # g
    sodium: Optional[float] = None  # mg

    # Vitamins and minerals (optional)
    vitamin_d: Optional[float] = None  # μg
    calcium: Optional[float] = None  # mg
    iron: Optional[float] = None  # mg
    potassium: Optional[float] = None  # mg
    zinc: Optional[float] = None  # mg

    # User association and notes
    user_id: Optional[str] = None
    notes: Optional[str] = None
