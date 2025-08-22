import enum
from datetime import date, datetime
from typing import Annotated, List, Optional
from uuid import UUID

import strawberry


# Strawberry Enums (mirroring repository/models/enums.py)
@strawberry.enum(name="MealTypeValueGQL")
class MealTypeGQLEnum(enum.Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


# Forward references for GraphQL types
class FoodItemTypeGQL:
    pass


class MealFoodTypeGQL:
    pass


class MealTypeGQLForwardRef:  # Using a different name for forward ref if MealTypeGQL is already defined as enum
    pass


class UserGoalsTypeGQL:
    pass


class WaterConsumptionTypeGQL:
    pass


# Strawberry Types (based on Domain Models)


@strawberry.type
class FoodItemTypeGQL:
    id_: strawberry.ID
    created_at: datetime
    modified_at: datetime
    name: str
    serving_size: float
    serving_unit: str
    calories: float
    protein: float
    carbohydrates: float
    fat: float
    saturated_fat: Optional[float] = None
    monounsaturated_fat: Optional[float] = None
    polyunsaturated_fat: Optional[float] = None
    trans_fat: Optional[float] = None
    cholesterol: Optional[float] = None
    fiber: Optional[float] = None
    sugar: Optional[float] = None
    sodium: Optional[float] = None
    potassium: Optional[float] = None
    calcium: Optional[float] = None
    iron: Optional[float] = None
    vitamin_d: Optional[float] = None
    zinc: Optional[float] = None
    notes: Optional[str] = None
    user_id: Optional[str] = None  # Assuming food items can be user-specific or global


@strawberry.type
class MealFoodTypeGQL:
    id_: strawberry.ID
    created_at: datetime
    modified_at: datetime
    meal_id: strawberry.ID
    food_item_id: strawberry.ID
    quantity: float
    serving_unit: str  # e.g., 'g', 'oz', 'cup', 'piece'
    food_item: FoodItemTypeGQL


@strawberry.type
class MealTypeGQL:  # Main Meal Type
    id_: strawberry.ID
    created_at: datetime
    modified_at: datetime
    user_id: str
    name: str
    type: MealTypeGQLEnum  # Use renamed Python enum
    date: datetime  # Changed from date to datetime to match domain/repo model
    notes: Optional[str] = None
    meal_foods: List[MealFoodTypeGQL]


@strawberry.type
class UserGoalsTypeGQL:
    id_: strawberry.ID
    created_at: datetime
    modified_at: datetime
    user_id: str
    daily_calorie_goal: float
    daily_water_goal: float
    daily_protein_goal: Optional[float] = None
    daily_carbs_goal: Optional[float] = None
    daily_fat_goal: Optional[float] = None


@strawberry.type
class WaterConsumptionTypeGQL:
    id_: strawberry.ID
    created_at: datetime
    modified_at: datetime
    user_id: str
    quantity: float  # in mL
    consumed_at: datetime


# Input types for Mutations


@strawberry.input
class FoodItemCreateInput:
    name: str
    serving_size: float
    serving_unit: str
    calories: float
    protein: float
    carbohydrates: float
    fat: float
    saturated_fat: Optional[float] = None
    monounsaturated_fat: Optional[float] = None
    polyunsaturated_fat: Optional[float] = None
    trans_fat: Optional[float] = None
    cholesterol: Optional[float] = None
    fiber: Optional[float] = None
    sugar: Optional[float] = None
    sodium: Optional[float] = None
    potassium: Optional[float] = None
    calcium: Optional[float] = None
    iron: Optional[float] = None
    vitamin_d: Optional[float] = None
    zinc: Optional[float] = None
    notes: Optional[str] = None
    user_id: Optional[str] = None


@strawberry.input
class FoodItemUpdateInput:
    name: Optional[str] = None
    serving_size: Optional[float] = None
    serving_unit: Optional[str] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbohydrates: Optional[float] = None
    fat: Optional[float] = None
    saturated_fat: Optional[float] = None
    monounsaturated_fat: Optional[float] = None
    polyunsaturated_fat: Optional[float] = None
    trans_fat: Optional[float] = None
    cholesterol: Optional[float] = None
    fiber: Optional[float] = None
    sugar: Optional[float] = None
    sodium: Optional[float] = None
    potassium: Optional[float] = None
    calcium: Optional[float] = None
    iron: Optional[float] = None
    vitamin_d: Optional[float] = None
    zinc: Optional[float] = None
    notes: Optional[str] = None
    # user_id is typically not updatable, or handled via specific logic


@strawberry.input
class MealFoodInput:  # Used for creating/updating meal_foods within a meal
    food_item_id: strawberry.ID
    quantity: float
    serving_unit: str


@strawberry.input
class MealCreateInput:
    user_id: str
    name: str
    type: MealTypeGQLEnum  # Use renamed Python enum
    date: datetime  # Expect ISO datetime string, Strawberry will parse to datetime
    notes: Optional[str] = None
    meal_foods_data: List[MealFoodInput] = strawberry.field(default_factory=list)


@strawberry.input
class MealUpdateInput:
    name: Optional[str] = None
    type: Optional[MealTypeGQLEnum] = None  # Use renamed Python enum
    date: Optional[datetime] = None  # Expect ISO datetime string, Strawberry will parse to datetime
    notes: Optional[str] = None
    # For updating meal_foods, it's often easier to have separate mutations
    # like addFoodToMeal, removeFoodFromMeal, updateMealFoodQuantity.
    # Alternatively, one could pass the full list of meal_foods_data to replace existing.


@strawberry.input
class UserGoalsCreateInput:
    user_id: str
    daily_calorie_goal: float
    daily_water_goal: float
    daily_protein_goal: Optional[float] = None
    daily_carbs_goal: Optional[float] = None
    daily_fat_goal: Optional[float] = None


@strawberry.input
class UserGoalsUpdateInput:
    daily_calorie_goal: Optional[float] = None
    daily_water_goal: Optional[float] = None
    daily_protein_goal: Optional[float] = None
    daily_carbs_goal: Optional[float] = None
    daily_fat_goal: Optional[float] = None
    # user_id is the key and should not be updatable here.


@strawberry.input
class WaterConsumptionCreateInput:
    user_id: str
    quantity: float
    consumed_at: str  # Expect ISO datetime string, will be converted by service


@strawberry.input
class WaterConsumptionUpdateInput:
    quantity: Optional[float] = None
    consumed_at: Optional[str] = None  # Expect ISO datetime string


__all__ = [
    "MealTypeGQLEnum",
    "FoodItemTypeGQL",
    "MealFoodTypeGQL",
    "MealTypeGQL",
    "UserGoalsTypeGQL",
    "WaterConsumptionTypeGQL",
    "FoodItemCreateInput",
    "FoodItemUpdateInput",
    "MealFoodInput",
    "MealCreateInput",
    "MealUpdateInput",
    "UserGoalsCreateInput",
    "UserGoalsUpdateInput",
    "WaterConsumptionCreateInput",
    "WaterConsumptionUpdateInput",
]
