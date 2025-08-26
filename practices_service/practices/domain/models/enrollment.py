import enum
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EnrollmentStatus(str, enum.Enum):
    """Pydantic-compatible enum for enrollment status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class DomainProgramEnrollment(BaseModel):
    """Domain model for a program enrollment."""

    model_config = ConfigDict(from_attributes=True)

    id_: UUID
    program_id: UUID
    user_id: UUID
    enrolled_by_user_id: Optional[UUID] = None
    status: EnrollmentStatus
    created_at: datetime
    modified_at: datetime
    current_practice_link_id: Optional[UUID] = None

    # Note: We don't include the full 'program' or 'user' objects here
    # to avoid circular dependencies and keep the model focused.
    # They can be retrieved by their respective IDs if needed.
