from typing import List, Optional, Type

import strawberry
from strawberry.extensions import SchemaExtension

from .resolvers import Mutation, Query
from .types import (  # Enums and Input types are not directly part of the schema types list usually,; Strawberry infers them from Query/Mutation definitions.
    FoodItemTypeGQL,
    MealFoodTypeGQL,
    MealTypeGQL,
    UserGoalsTypeGQL,
    WaterConsumptionTypeGQL,
)

# Explicitly list your main GQL types here to ensure they are included in the schema
# This helps avoid issues with types not being found, especially with forward references or federation.
MAIN_GQL_TYPES = (
    FoodItemTypeGQL,
    MealFoodTypeGQL,
    MealTypeGQL,  # The main object type, not the enum
    UserGoalsTypeGQL,
    WaterConsumptionTypeGQL,
    # Add other top-level queryable/mutable types if they aren't directly referenced by Query/Mutation fields
)


def get_schema(extensions: Optional[List[Type[SchemaExtension]]] = None) -> strawberry.Schema:
    # Ensure extensions is an empty list if None is passed
    current_extensions = extensions if extensions is not None else []
    return strawberry.Schema(
        query=Query,
        mutation=Mutation,
        types=MAIN_GQL_TYPES,  # Explicitly include types
        extensions=current_extensions,  # Pass the processed extensions list
    )


# Default schema instance (primarily for Django or similar frameworks)
# For FastAPI, the router usually calls get_schema directly.
schema = get_schema()

__all__ = ["schema", "get_schema"]
