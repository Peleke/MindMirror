from datetime import date
from typing import Optional

from pydantic import BaseModel


class UserGoals(BaseModel):
    """
    Pydantic model for a user's nutritional goals, based on the
    UserGoalsModel from the 'meals' service.
    """

    daily_calorie_goal: Optional[float] = None
    daily_protein_goal: Optional[float] = None
    daily_carbs_goal: Optional[float] = None
    daily_fat_goal: Optional[float] = None
    # We can add other goals like water, etc. as needed.


class PracticeInstance(BaseModel):
    """
    Pydantic model representing a completed workout, based on the
    PracticeInstanceModel from the 'practices' service.
    """

    title: str
    completed_at: Optional[date] = None
    # We can add more details like duration, notes, etc. later.


class MealLog(BaseModel):
    """
    Pydantic model representing a single meal log entry.
    """

    name: str
    calories: float
    protein: float
    carbs: float
    fat: float
    date: date
