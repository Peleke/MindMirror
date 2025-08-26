from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from practices.repository.models.enums import (
    Block,
    LoadUnit,
    MetricUnit,
    MovementClass,
)


class DomainSetTemplate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_: UUID
    position: Optional[int] = None
    reps: Optional[int] = None
    duration: Optional[float] = None
    rest_duration: Optional[float] = None
    load_value: Optional[float] = None
    load_unit: Optional[LoadUnit] = None
    movement_template_id: UUID


class DomainMovementTemplate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_: UUID
    position: Optional[int] = None
    name: str
    description: Optional[str] = None
    metric_unit: MetricUnit
    metric_value: float
    movement_class: Optional[MovementClass] = None
    prescribed_sets: Optional[int] = None
    rest_duration: Optional[float] = None
    video_url: Optional[str] = None
    prescription_template_id: UUID
    exercise_id: Optional[UUID] = None
    sets: List[DomainSetTemplate] = []


class DomainPrescriptionTemplate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_: UUID
    name: Optional[str] = None
    description: Optional[str] = None
    block: Block
    prescribed_rounds: int = 1
    position: int
    practice_template_id: UUID
    movements: List[DomainMovementTemplate] = []


class DomainPracticeTemplate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_: UUID
    created_at: datetime
    modified_at: datetime
    title: str
    description: Optional[str] = None
    duration: Optional[float] = None
    user_id: Optional[UUID] = None
    prescriptions: List[DomainPrescriptionTemplate] = []
