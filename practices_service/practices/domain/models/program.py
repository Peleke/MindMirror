from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .enrollment import DomainProgramEnrollment
from .practice_template import DomainPracticeTemplate


class DomainScheduledPractice(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_: UUID
    enrollment_id: UUID
    practice_template_id: UUID
    practice_instance_id: Optional[UUID] = None
    scheduled_date: date


class DomainProgramTag(BaseModel):
    """Domain model for a program tag."""

    model_config = ConfigDict(from_attributes=True)
    id_: UUID
    program_id: UUID
    name: str
    created_at: datetime
    modified_at: datetime


class DomainProgramPracticeLink(BaseModel):
    """Domain model for a link between a program and a practice template."""

    model_config = ConfigDict(from_attributes=True)
    id_: UUID
    program_id: UUID
    practice_template_id: UUID  # Changed from practice_id
    sequence_order: int
    interval_days_after: int = 1

    practice_template: Optional[DomainPracticeTemplate] = None


class DomainProgram(BaseModel):
    """Domain model for a program."""

    model_config = ConfigDict(from_attributes=True)
    id_: UUID
    name: str
    description: Optional[str] = None
    level: Optional[str] = None
    created_at: datetime
    modified_at: datetime
    user_id: UUID
    habits_program_template_id: Optional[UUID] = None

    tags: List[DomainProgramTag] = Field(default_factory=list)
    practice_links: List[DomainProgramPracticeLink] = Field(default_factory=list)
    enrollments: List[DomainProgramEnrollment] = Field(default_factory=list)
    scheduled_practices: List[DomainScheduledPractice] = Field(default_factory=list)

    @property
    def practice_count(self) -> int:
        return len(self.practice_links)
