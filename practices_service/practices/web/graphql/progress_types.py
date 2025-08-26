import uuid
from datetime import date

import strawberry


@strawberry.type
class ScheduledPracticeTypeGQL:
    """GraphQL type representing a scheduled practice for a user."""

    id_: strawberry.ID
    enrollment_id: strawberry.ID
    practice_id: strawberry.ID
    scheduled_date: date
