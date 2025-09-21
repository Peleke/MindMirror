import enum
from datetime import datetime
from typing import Optional
from uuid import UUID

import strawberry


@strawberry.enum
class EnrollmentStatusGQL(enum.Enum):
    """GraphQL enum for the status of a program enrollment."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


@strawberry.input
class AttachLessonsToProgramEnrollmentInput:
    """Input for attaching lessons to a program enrollment."""

    enrollment_id: strawberry.ID
    lesson_template_slug: str
    day_offset: int
    on_workout_day: bool = False
    segment_ids: Optional[List[strawberry.ID]] = None


@strawberry.input
class EnrollInProgramInput:
    """Input for enrolling in a program with optional repeat count."""

    program_id: strawberry.ID
    repeat_count: int = 1


@strawberry.type
class ProgramEnrollmentTypeGQL:
    """GraphQL type representing a user's enrollment in a program."""

    id_: strawberry.ID
    program_id: strawberry.ID
    user_id: strawberry.ID
    enrolled_by_user_id: Optional[strawberry.ID] = None
    status: EnrollmentStatusGQL
    created_at: datetime
    modified_at: datetime
    current_practice_link_id: Optional[strawberry.ID] = None
