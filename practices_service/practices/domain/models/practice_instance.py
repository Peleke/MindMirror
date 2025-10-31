from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from practices.repository.models.enums import (
    Block,
    LoadUnit,
    MetricUnit,
    MovementClass,
)


class DomainSetInstance(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_: UUID
    position: Optional[int] = None
    reps: Optional[int] = None
    duration: Optional[float] = None
    rest_duration: Optional[float] = None
    load_value: Optional[float] = None
    load_unit: Optional[LoadUnit] = None
    perceived_exertion: Optional[int] = None
    complete: bool = False
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None
    movement_instance_id: UUID
    template_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None


class DomainMovementInstance(BaseModel):
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
    notes: Optional[str] = None
    video_url: Optional[str] = None
    complete: bool = False
    completed_at: Optional[datetime] = None
    prescription_instance_id: UUID
    exercise_id: Optional[UUID] = None
    template_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    sets: List[DomainSetInstance] = []


class DomainPrescriptionInstance(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_: UUID
    name: Optional[str] = None
    description: Optional[str] = None
    block: Block
    prescribed_rounds: int = 1
    complete: bool = False
    position: int
    notes: Optional[str] = None
    practice_instance_id: UUID
    template_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    movements: List[DomainMovementInstance] = []


class DomainPracticeInstance(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_: UUID
    created_at: datetime
    modified_at: datetime
    date: date
    title: str
    description: Optional[str] = None
    notes: Optional[str] = None
    duration: Optional[float] = None
    completed_at: Optional[date] = None
    user_id: Optional[UUID] = None
    template_id: Optional[UUID] = None
    enrollment_id: Optional[UUID] = None
    prescriptions: List[DomainPrescriptionInstance] = []
