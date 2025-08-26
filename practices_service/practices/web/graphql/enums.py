import enum

import strawberry


@strawberry.enum
class BlockGQL(enum.Enum):
    WARMUP = "warmup"
    WORKOUT = "workout"
    COOLDOWN = "cooldown"
    OTHER = "other"


@strawberry.enum
class MetricUnitGQL(enum.Enum):
    ITERATIVE = "iterative"
    TEMPORAL = "temporal"
    BREATH = "breath"
    OTHER = "other"


@strawberry.enum
class MovementClassGQL(enum.Enum):
    CONDITIONING = "conditioning"
    POWER = "power"
    STRENGTH = "strength"
    MOBILITY = "mobility"
    OTHER = "other"


@strawberry.enum
class LoadUnitGQL(enum.Enum):
    POUNDS = "pounds"
    KILOGRAMS = "kilograms"
    BODYWEIGHT = "bodyweight"
    OTHER = "other"


__all__ = ["BlockGQL", "MetricUnitGQL", "MovementClassGQL", "LoadUnitGQL"]
