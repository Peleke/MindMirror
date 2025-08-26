from datetime import datetime
from typing import List, Optional

import strawberry

from .enums import (
    BlockGQL,
    LoadUnitGQL,
    MetricUnitGQL,
    MovementClassGQL,
)
from .federation import ExerciseType, MovementRef


@strawberry.type
class SetTemplateType:
    id_: strawberry.ID
    position: Optional[int] = None
    reps: Optional[int] = None
    duration: Optional[float] = None
    rest_duration: Optional[float] = None
    load_value: Optional[float] = None
    load_unit: Optional[LoadUnitGQL] = None
    movement_template_id: strawberry.ID


@strawberry.type
class MovementTemplateType:
    id_: strawberry.ID
    position: Optional[int] = None
    name: str
    description: Optional[str] = None
    metric_unit: MetricUnitGQL
    metric_value: float
    movement_class: Optional[MovementClassGQL] = None
    prescribed_sets: Optional[int] = None
    rest_duration: Optional[float] = None
    video_url: Optional[str] = None
    prescription_template_id: strawberry.ID
    exercise_id: Optional[strawberry.ID] = None
    movement_id: Optional[strawberry.ID] = None
    sets: List[SetTemplateType]

    @strawberry.field
    def exercise(self) -> Optional[ExerciseType]:
        if self.exercise_id:
            return ExerciseType(id=self.exercise_id)
        return None

    @strawberry.field
    def movement(self) -> Optional[MovementRef]:
        if self.movement_id:
            return MovementRef(id_=self.movement_id)
        return None


@strawberry.type
class PrescriptionTemplateType:
    id_: strawberry.ID
    name: Optional[str] = None
    description: Optional[str] = None
    block: BlockGQL
    prescribed_rounds: int = 1
    position: int
    practice_template_id: strawberry.ID
    movements: List[MovementTemplateType]


@strawberry.type
class PracticeTemplateType:
    id_: strawberry.ID
    created_at: datetime
    modified_at: datetime
    title: str
    description: Optional[str] = None
    duration: Optional[float] = None
    user_id: Optional[strawberry.ID] = None
    prescriptions: List[PrescriptionTemplateType]


__all__ = [
    "SetTemplateType",
    "MovementTemplateType",
    "PrescriptionTemplateType",
    "PracticeTemplateType",
]
