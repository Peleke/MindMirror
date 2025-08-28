import enum
from datetime import date, datetime
from typing import TYPE_CHECKING, Annotated, List, Optional
from uuid import UUID

import strawberry

from .enums import BlockGQL, LoadUnitGQL, MetricUnitGQL, MovementClassGQL
from .practice_template_types import PracticeTemplateType

# Strawberry Enums (mirroring repository/models/enums.py)


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


# Placeholder Ref types for entities from Movements service
# These MUST be defined BEFORE ExerciseType which uses them.
@strawberry.federation.type(keys=["id"], name="Archetype")
class ArchetypeRef:
    id: strawberry.ID  # Serves as the key


@strawberry.federation.type(keys=["id"], name="Equipment")
class EquipmentRef:
    id: strawberry.ID


@strawberry.federation.type(keys=["id"], name="Progression")
class ProgressionRef:
    id: strawberry.ID


@strawberry.federation.type(keys=["id"], name="Regression")
class RegressionRef:
    id: strawberry.ID


# Forward references - do NOT use @strawberry.type here
class PrescriptionType:
    pass


class PrescribedMovementType:
    pass


class SetType:
    pass


class ProgramTagType:
    pass


class ProgramPracticeLinkType:
    pass


class ProgramType:
    pass


class PracticeType:
    pass


# Strawberry Types (based on Domain Models - to be filled in)


@strawberry.type
class SetType:  # Full definition of SetType
    id_: strawberry.ID
    created_at: datetime
    modified_at: datetime
    reps: Optional[int] = None
    load_value: Optional[float] = None
    load_unit: Optional[LoadUnitGQL] = None
    duration: Optional[int] = None
    rest_duration: Optional[int] = None
    complete: bool = False
    prescribed_movement_id: str
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    position: Optional[int] = None
    perceived_exertion: Optional[int] = None
    notes: Optional[str] = None


@strawberry.federation.type(keys=["id"])
class ExerciseType:
    id: strawberry.ID

    @classmethod
    async def resolve_reference(cls, id: strawberry.ID):
        print(f"Practices service: resolve_reference called for ExerciseType id: {id}")
        return cls(id=id)


# PrescribedMovementType, PrescriptionType, PracticeType definitions follow, using ExerciseType and other defined types
@strawberry.type
class PrescribedMovementType:
    id_: strawberry.ID
    created_at: datetime
    modified_at: datetime
    name: str
    metric_unit: MetricUnitGQL
    metric_value: float
    description: str
    prescribed_sets: int
    video_url: Optional[str] = None
    movement_class: MovementClassGQL
    prescription_id: strawberry.ID
    sets: List[SetType]
    rest_duration: int
    position: int
    exercise_id: Optional[strawberry.ID] = None

    @strawberry.field
    def exercise(self) -> Optional[ExerciseType]:
        if self.exercise_id:
            return ExerciseType(id=self.exercise_id)
        return None


@strawberry.type
class PrescriptionType:
    id_: strawberry.ID
    created_at: datetime
    modified_at: datetime
    name: str
    description: Optional[str] = None
    block: BlockGQL
    practice_id: strawberry.ID
    prescribed_rounds: int
    movements: List[PrescribedMovementType]
    complete: bool
    position: int




__all__ = [
    "ProgramTagType",
    "ProgramPracticeLinkType",
    "ProgramType",
]
