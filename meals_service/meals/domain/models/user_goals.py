from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DomainUserGoals(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_: UUID
    created_at: datetime
    modified_at: datetime

    user_id: str  # Internal user ID (not Supabase ID)

    # Daily goals
    daily_calorie_goal: float
    daily_water_goal: float  # mL

    # Optional macro goals
    daily_protein_goal: Optional[float] = None  # g
    daily_carbs_goal: Optional[float] = None  # g
    daily_fat_goal: Optional[float] = None  # g
