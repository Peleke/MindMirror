import uuid
from typing import NewType

import strawberry

# Define a new type for UUID for clarity in the codebase
UUID = strawberry.scalar(
    NewType("UUID", uuid.UUID),
    serialize=lambda v: str(v),
    parse_value=lambda v: uuid.UUID(v),
    description="The `UUID` scalar type represents a universally unique identifier.",
)

# Define a placeholder for the Domain scalar if you need custom logic,
# otherwise, using the registered enum directly is often sufficient.
# If you need a scalar for validation purposes:
from users.repository.models import DomainModel

DomainScalar = strawberry.scalar(
    NewType("DomainScalar", str),
    serialize=lambda v: str(v.value) if isinstance(v, DomainModel) else str(v),
    parse_value=lambda v: DomainModel(v.lower()),
    description="A domain within the system, like 'practices' or 'meals'.",
)

__all__ = ["UUID", "DomainScalar"]
