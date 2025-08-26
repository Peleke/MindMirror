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
