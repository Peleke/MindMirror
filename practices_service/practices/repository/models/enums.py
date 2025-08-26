from enum import Enum


class Block(str, Enum):
    WARMUP = "warmup"
    WORKOUT = "workout"
    COOLDOWN = "cooldown"
    OTHER = "other"


class MetricUnit(str, Enum):
    ITERATIVE = "iterative"
    TEMPORAL = "temporal"
    BREATH = "breath"
    OTHER = "other"


class MovementClass(str, Enum):
    CONDITIONING = "conditioning"
    POWER = "power"
    STRENGTH = "strength"
    MOBILITY = "mobility"
    OTHER = "other"


class LoadUnit(str, Enum):
    POUNDS = "pounds"
    KILOGRAMS = "kilograms"
    BODYWEIGHT = "bodyweight"
    OTHER = "other"  # Added OTHER to be safe, FE might not use it for load but good for flexibility
