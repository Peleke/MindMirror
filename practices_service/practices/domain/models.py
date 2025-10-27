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


# Forward declarations for Pydantic models with circular dependencies
class DomainSet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_: UUID
    created_at: datetime
    modified_at: datetime
    position: Optional[int] = None
    reps: Optional[int] = None
    duration: Optional[float] = None  # seconds
    rest_duration: Optional[float] = None  # seconds
    load_value: Optional[float] = None  # e.g., weight
    load_unit: Optional[LoadUnit] = None
    perceived_exertion: Optional[int] = None
    complete: bool = False
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    notes: Optional[str] = None
    prescribed_movement_id: UUID


class DomainPrescribedMovement(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_: UUID
    created_at: datetime
    modified_at: datetime
    position: Optional[int] = None
    name: str
    description: Optional[str] = None
    metric_unit: MetricUnit
    metric_value: float
    movement_class: Optional[MovementClass] = None
    prescribed_sets: Optional[int] = None  # How many sets are prescribed
    rest_duration: Optional[float] = None  # seconds
    notes: Optional[str] = None
    video_url: Optional[str] = None  # URL for the movement itself
    prescription_id: UUID
    exercise_id: Optional[UUID] = None  # ADDED for federation
    sets: List[DomainSet] = []


class DomainPrescription(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_: UUID
    created_at: datetime
    modified_at: datetime
    name: Optional[str] = None
    description: Optional[str] = None
    block: Block
    prescribed_rounds: int = 1
    complete: bool = False
    position: int  # Order of this prescription within the practice
    notes: Optional[str] = None
    practice_id: UUID
    movements: List[DomainPrescribedMovement] = []


class DomainPractice(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_: UUID
    created_at: datetime
    modified_at: datetime
    date: date
    title: str
    description: Optional[str] = None
    notes: Optional[str] = None
    duration: Optional[float] = None  # Intended or actual duration in minutes
    complete: bool = False
    user_id: Optional[str] = None  # Assuming user_id might be a string
    prescriptions: List[DomainPrescription] = []
