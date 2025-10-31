import enum


class MealType(enum.Enum):
    """Enum for meal types."""

    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class NutrientUnit(enum.Enum):
    """Enum for nutrient units."""

    GRAMS = "grams"
    MILLIGRAMS = "milligrams"
    MICROGRAMS = "micrograms"
    IU = "iu"  # International Units
