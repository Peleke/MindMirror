import enum
from datetime import date, datetime
from typing import Annotated, List, Optional
from uuid import UUID

import strawberry

from .enums import ServiceTypeGQL


# --- Forward references for Strawberry types with circular dependencies ---
class UserTypeGQL:
    pass


class ServiceTypeGQL_Type:
    pass


class SchedulableTypeGQL:
    pass


class UserServiceLinkTypeGQL:
    pass


class UserRoleTypeGQL:
    pass


class CoachClientAssociationGQL:
    pass


class CoachingRequestGQL:
    pass


class UserSummaryGQL:
    pass


# --- GraphQL Enums ---


@strawberry.enum
class AssociationStatusGQL(enum.Enum):
    """GraphQL enum for the status of a coach-client association."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    TERMINATED = "terminated"


@strawberry.enum
class RoleGQL(enum.Enum):
    """GraphQL enum for user roles."""

    COACH = "coach"
    CLIENT = "client"
    ADMIN = "admin"


@strawberry.enum
class DomainGQL(enum.Enum):
    """GraphQL enum for domains where roles are applicable."""

    PRACTICES = "practices"
    MEALS = "meals"
    SLEEP = "sleep"
    SYSTEM = "system"


# --- GraphQL Types ---


@strawberry.federation.type(keys=["id_"])
class ServiceTypeGQL_Type:
    id_: strawberry.ID
    created_at: datetime
    modified_at: datetime
    name: ServiceTypeGQL
    description: Optional[str] = None
    url: Optional[str] = None

    @classmethod
    async def resolve_reference(
        cls,
        id_: strawberry.ID,
        created_at: Optional[datetime] = None,
        modified_at: Optional[datetime] = None,
        name: Optional[ServiceTypeGQL] = None,
        description: Optional[str] = None,
        url: Optional[str] = None,
    ):
        # Stub implementation
        return cls(
            id_=id_,
            created_at=created_at or datetime.now(),
            modified_at=modified_at or datetime.now(),
            name=name or ServiceTypeGQL.PRACTICE,  # Assuming PRACTICE as a default
            description=description,
            url=url,
        )


@strawberry.federation.type(keys=["userId", "serviceId"], name="UserServiceLink")
class UserServiceLinkTypeGQL:
    user_id: strawberry.ID
    service_id: strawberry.ID
    created_at: datetime
    modified_at: datetime
    active: bool

    user: Optional[Annotated["UserTypeGQL", strawberry.lazy("users.web.graphql.types")]] = None
    service: Optional[ServiceTypeGQL_Type] = None

    @classmethod
    async def resolve_reference(
        cls,
        user_id: strawberry.ID,
        service_id: strawberry.ID,
        created_at: Optional[datetime] = None,
        modified_at: Optional[datetime] = None,
        active: Optional[bool] = None,
    ):
        # Stub: returns a basic representation based on keys.
        # Actual fetching/validation would happen in a real resolver.
        return cls(
            user_id=user_id,
            service_id=service_id,
            created_at=created_at or datetime.now(),
            modified_at=modified_at or datetime.now(),
            active=active if active is not None else True,
        )


@strawberry.federation.type(keys=["id_"])
class SchedulableTypeGQL:
    id_: strawberry.ID
    created_at: datetime
    modified_at: datetime
    name: str
    description: Optional[str] = None
    entity_id: strawberry.ID  # Federated FK - represents an entity in another service
    completed: bool
    service_id_str: strawberry.ID = strawberry.field(name="service_id")
    user_id_str: strawberry.ID = strawberry.field(name="user_id")
    date: date

    service: Optional[ServiceTypeGQL_Type] = None
    user: Optional[Annotated["UserTypeGQL", strawberry.lazy("users.web.graphql.types")]] = None

    @classmethod
    async def resolve_reference(
        cls,
        id_: strawberry.ID,
        user_id_str: strawberry.ID,
        service_id_str: strawberry.ID,
        entity_id: strawberry.ID,
        date: date,
        name: str = "Resolved Schedulable",
        completed: bool = False,
        created_at: Optional[datetime] = None,
        modified_at: Optional[datetime] = None,
        description: Optional[str] = None,
    ):
        # Stub for federation. In a real scenario, this would fetch the schedulable by its ID.
        return cls(
            id_=id_,
            name=name,
            entity_id=entity_id,
            completed=completed,
            service_id_str=service_id_str,
            user_id_str=user_id_str,
            created_at=created_at or datetime.now(),
            modified_at=modified_at or datetime.now(),
            description=description,
            date=date,
        )


@strawberry.federation.type(keys=["id_"])
class UserRoleTypeGQL:
    """GraphQL type for a user's role assignment."""

    id_: strawberry.ID
    role: RoleGQL
    domain: DomainGQL
    created_at: datetime
    # This type represents a value object, so a resolve_reference is likely not needed
    # unless it can be fetched independently by a key.


@strawberry.federation.type(keys=["id_"])
class UserTypeGQL:
    id_: strawberry.ID
    created_at: datetime
    modified_at: datetime
    supabase_id: str
    keycloak_id: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    service_links: List[Annotated["UserServiceLinkTypeGQL", strawberry.lazy("users.web.graphql.types")]] = (
        strawberry.field(default_factory=list)
    )
    schedulables: List[Annotated["SchedulableTypeGQL", strawberry.lazy("users.web.graphql.types")]] = strawberry.field(
        default_factory=list
    )
    roles: List[UserRoleTypeGQL] = strawberry.field(default_factory=list)
    coaching_clients: List[Annotated["CoachClientAssociationGQL", strawberry.lazy("users.web.graphql.types")]] = (
        strawberry.field(default_factory=list)
    )
    coaches: List[Annotated["CoachClientAssociationGQL", strawberry.lazy("users.web.graphql.types")]] = (
        strawberry.field(default_factory=list)
    )

    @classmethod
    async def resolve_reference(
        cls,
        id_: strawberry.ID,
        supabase_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        modified_at: Optional[datetime] = None,
        keycloak_id: Optional[str] = None,
    ):
        # Stub for federation.
        return cls(
            id_=id_,
            supabase_id=supabase_id or "resolved_supabase_id",
            created_at=created_at or datetime.now(),
            modified_at=modified_at or datetime.now(),
            keycloak_id=keycloak_id,
        )


@strawberry.federation.type(keys=["id_"])
class UserSummaryGQL:
    """GraphQL type for user summary (to avoid circular dependencies)."""

    id_: strawberry.ID
    created_at: datetime
    modified_at: datetime
    supabase_id: str
    keycloak_id: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    @classmethod
    async def resolve_reference(
        cls,
        id_: strawberry.ID,
        supabase_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        modified_at: Optional[datetime] = None,
        keycloak_id: Optional[str] = None,
    ):
        return cls(
            id_=id_,
            supabase_id=supabase_id or "resolved_supabase_id",
            created_at=created_at or datetime.now(),
            modified_at=modified_at or datetime.now(),
            keycloak_id=keycloak_id,
        )


@strawberry.federation.type(keys=["id_"])
class CoachingRequestGQL:
    """GraphQL type for a coaching request."""

    id_: strawberry.ID
    coach_user_id: strawberry.ID
    client_user_id: strawberry.ID
    status: AssociationStatusGQL
    requested_by: str
    created_at: datetime
    modified_at: datetime

    coach: Optional[UserSummaryGQL] = None
    client: Optional[UserSummaryGQL] = None

    @classmethod
    async def resolve_reference(
        cls,
        id_: strawberry.ID,
        coach_user_id: strawberry.ID,
        client_user_id: strawberry.ID,
        status: AssociationStatusGQL,
        requested_by: str,
        created_at: Optional[datetime] = None,
        modified_at: Optional[datetime] = None,
    ):
        return cls(
            id_=id_,
            coach_user_id=coach_user_id,
            client_user_id=client_user_id,
            status=status,
            requested_by=requested_by,
            created_at=created_at or datetime.now(),
            modified_at=modified_at or datetime.now(),
        )


@strawberry.federation.type(keys=["id_"])
class CoachClientAssociationGQL:
    """GraphQL type for a coach-client association."""

    id_: strawberry.ID
    domain: DomainGQL
    status: AssociationStatusGQL
    created_at: datetime
    modified_at: datetime

    coach: Annotated["UserTypeGQL", strawberry.lazy("users.web.graphql.types")]
    client: Annotated["UserTypeGQL", strawberry.lazy("users.web.graphql.types")]
    requester: Annotated["UserTypeGQL", strawberry.lazy("users.web.graphql.types")]


__all__ = [
    "ServiceTypeGQL",
    "ServiceTypeGQL_Type",
    "UserServiceLinkTypeGQL",
    "SchedulableTypeGQL",
    "UserTypeGQL",
    "UserSummaryGQL",
    "RoleGQL",
    "DomainGQL",
    "UserRoleTypeGQL",
    "AssociationStatusGQL",
    "CoachClientAssociationGQL",
    "CoachingRequestGQL",
]
