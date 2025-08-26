from datetime import date, datetime
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
class SetInstanceType:
    id_: strawberry.ID
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    position: Optional[int] = None
    reps: Optional[int] = None
    duration: Optional[float] = None
    rest_duration: Optional[float] = None
    load_value: Optional[float] = None
    load_unit: Optional[LoadUnitGQL] = None
    perceived_exertion: Optional[int] = None
    complete: bool = False
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None
    movement_instance_id: strawberry.ID
    template_id: Optional[strawberry.ID] = None


@strawberry.type
class MovementInstanceType:
    id_: strawberry.ID
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    position: Optional[int] = None
    name: str
    description: Optional[str] = None
    metric_unit: MetricUnitGQL
    metric_value: float
    movement_class: Optional[MovementClassGQL] = None
    prescribed_sets: Optional[int] = None
    rest_duration: Optional[float] = None
    notes: Optional[str] = None
    video_url: Optional[str] = None
    complete: bool = False
    completed_at: Optional[datetime] = None
    prescription_instance_id: strawberry.ID
    exercise_id: Optional[strawberry.ID] = None
    movement_id: Optional[strawberry.ID] = None
    template_id: Optional[strawberry.ID] = strawberry.field(name="templateId")
    sets: List[SetInstanceType]

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
class PrescriptionInstanceType:
    id_: strawberry.ID
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    name: Optional[str] = None
    description: Optional[str] = None
    block: BlockGQL
    prescribed_rounds: int = 1
    complete: bool = False
    position: int
    notes: Optional[str] = None
    practice_instance_id: strawberry.ID
    template_id: Optional[strawberry.ID] = None
    movements: List[MovementInstanceType]


@strawberry.type
class PracticeInstanceType:
    id_: strawberry.ID = strawberry.field(name="id_")
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    title: str
    date: date
    user_id: strawberry.ID
    template_id: Optional[strawberry.ID] = None
    description: Optional[str] = None
    duration: Optional[float] = None
    notes: Optional[str] = None
    completed_at: Optional[date] = None
    prescriptions: List[PrescriptionInstanceType] = strawberry.field(default_factory=list)


__all__ = [
    "SetInstanceType",
    "MovementInstanceType",
    "PrescriptionInstanceType",
    "PracticeInstanceType",
]
