from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

import strawberry

from practices.domain.models import (
    DomainProgram,
    DomainProgramEnrollment,
    DomainProgramPracticeLink,
    DomainProgramTag,
)

from .enrollment_types import ProgramEnrollmentTypeGQL
from .practice_template_types import PracticeTemplateType


@strawberry.type
class ProgramTagType:
    """GraphQL type for program tags."""

    id_: strawberry.ID
    program_id: strawberry.ID
    name: str
    created_at: datetime
    modified_at: datetime


@strawberry.type
class ProgramPracticeLinkType:
    """GraphQL type for program-practice links."""

    id_: strawberry.ID
    program_id: strawberry.ID
    practice_id: strawberry.ID
    sequence_order: int
    interval_days_after: int
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None

    # Relationship field
    practice_template: Optional[PracticeTemplateType] = None


@strawberry.type
class ProgramType:
    """GraphQL type for programs."""

    id_: strawberry.ID
    name: str
    description: Optional[str] = None
    level: Optional[str] = None  # E.g., "BEGINNER", "INTERMEDIATE", "ADVANCED"
    created_at: datetime
    modified_at: datetime
    habits_program_template_id: Optional[strawberry.ID] = None
    tags: List[ProgramTagType]
    practice_links: List[ProgramPracticeLinkType]
    enrollments: List[ProgramEnrollmentTypeGQL]
    practice_count: int
    total_duration_days: int

    @classmethod
    def from_domain(cls, domain_program: DomainProgram) -> "ProgramType":
        """Convert domain program model to GraphQL type."""
        return cls(
            id_=domain_program.id_,
            name=domain_program.name,
            description=domain_program.description,
            level=domain_program.level,
            created_at=domain_program.created_at,
            modified_at=domain_program.modified_at,
            habits_program_template_id=domain_program.habits_program_template_id,
            tags=[
                ProgramTagType(
                    id_=tag.id_,
                    program_id=tag.program_id,
                    name=tag.name,
                    created_at=tag.created_at,
                    modified_at=tag.modified_at,
                )
                for tag in domain_program.tags
            ],
            practice_links=[
                ProgramPracticeLinkType(
                    id_=link.id_,
                    program_id=link.program_id,
                    practice_id=link.practice_id,
                    sequence_order=link.sequence_order,
                    interval_days_after=link.interval_days_after,
                    created_at=link.created_at,
                    modified_at=link.modified_at,
                    practice_template=link.practice,  # If populated as a template-shaped object
                )
                for link in domain_program.practice_links
            ],
            enrollments=[
                ProgramEnrollmentTypeGQL(
                    id_=e.id_,
                    program_id=e.program_id,
                    user_id=e.user_id,
                    enrolled_by_user_id=e.enrolled_by_user_id,
                    status=e.status.value,
                    created_at=e.created_at,
                    modified_at=e.modified_at,
                )
                for e in domain_program.enrollments
            ],
            practice_count=domain_program.practice_count,
            total_duration_days=domain_program.total_duration_days,
        )


@strawberry.input
class ProgramTagInput:
    """Input type for creating program tags."""

    name: str


@strawberry.input
class ProgramPracticeLinkInput:
    """Input type for linking practices to programs."""

    practice_template_id: Optional[strawberry.ID] = None
    practice_id: Optional[strawberry.ID] = None
    sequence_order: int
    interval_days_after: int = 1


@strawberry.input
class ProgramCreateInput:
    """Input type for creating programs."""

    name: str
    description: Optional[str] = None
    level: Optional[str] = None
    habits_program_template_id: Optional[strawberry.ID] = None
    tags: Optional[List[ProgramTagInput]] = strawberry.field(default_factory=list)
    practice_links: Optional[List[ProgramPracticeLinkInput]] = strawberry.field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert input to dictionary for service layer."""
        result = {
            "name": self.name,
        }

        if self.description is not None:
            result["description"] = self.description

        if self.level is not None:
            result["level"] = self.level

        if self.habits_program_template_id is not None:
            result["habits_program_template_id"] = UUID(self.habits_program_template_id)

        if self.tags:
            result["tags"] = [{"name": tag.name} for tag in self.tags]

        if self.practice_links:
            result["practice_links"] = [
                {
                    "practice_template_id": UUID(link.practice_template_id) if link.practice_template_id is not None else UUID(link.practice_id),
                    "sequence_order": link.sequence_order,
                    "interval_days_after": link.interval_days_after,
                }
                for link in self.practice_links
            ]

        return result


@strawberry.input
class ProgramUpdateInput:
    """Input type for updating programs."""

    name: Optional[str] = None
    description: Optional[str] = None
    level: Optional[str] = None
    habits_program_template_id: Optional[strawberry.ID] = None
    tags: Optional[List[ProgramTagInput]] = None
    practice_links: Optional[List[ProgramPracticeLinkInput]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert input to dictionary for service layer."""
        result = {}

        if self.name is not None:
            result["name"] = self.name

        if self.description is not None:
            result["description"] = self.description

        if self.level is not None:
            result["level"] = self.level

        if self.habits_program_template_id is not None:
            result["habits_program_template_id"] = UUID(self.habits_program_template_id)

        if self.tags is not None:
            result["tags"] = [{"name": tag.name} for tag in self.tags]

        if self.practice_links is not None:
            result["practice_links"] = [
                {
                    "practice_id": UUID(link.practice_id),
                    "sequence_order": link.sequence_order,
                    "interval_days_after": link.interval_days_after,
                }
                for link in self.practice_links
            ]

        return result
