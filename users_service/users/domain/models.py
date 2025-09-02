import enum
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from users.repository.models import ServiceEnum


# Pydantic-compatible enums for use in domain models
class DomainRole(str, enum.Enum):
    COACH = "coach"
    CLIENT = "client"
    ADMIN = "admin"


class DomainDomain(str, enum.Enum):
    PRACTICES = "practices"
    MEALS = "meals"
    SLEEP = "sleep"
    SYSTEM = "system"


class DomainAssociationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    TERMINATED = "terminated"


class DomainService(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_: UUID
    created_at: datetime
    modified_at: datetime
    name: str
    description: Optional[str] = None
    url: Optional[str] = None


class DomainUserRole(BaseModel):
    """Domain model for a user's role, for use within the application logic."""

    model_config = ConfigDict(from_attributes=True)

    id_: UUID
    user_id: UUID
    role: DomainRole
    domain: DomainDomain
    created_at: datetime


# A summary user model to break circular dependencies in nested structures.
class DomainUserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_: UUID
    created_at: datetime
    modified_at: datetime
    supabase_id: str
    keycloak_id: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class DomainCoachClientRelationship(BaseModel):
    """Domain model for simplified coach-client relationship (new structure)."""

    model_config = ConfigDict(from_attributes=True)

    id_: UUID
    coach_user_id: UUID
    client_user_id: UUID
    status: DomainAssociationStatus
    requested_by: str  # 'coach' or 'client'
    created_at: datetime
    modified_at: datetime

    # Use a non-recursive summary model here to break the validation cycle
    coach: Optional[DomainUserSummary] = None
    client: Optional[DomainUserSummary] = None


class DomainCoachingRequest(BaseModel):
    """Domain model for a coaching request (for GraphQL responses)."""

    model_config = ConfigDict(from_attributes=True)

    id_: UUID
    coach_user_id: UUID
    client_user_id: UUID
    status: DomainAssociationStatus
    requested_by: str
    created_at: datetime
    modified_at: datetime
    coach: Optional[DomainUserSummary] = None
    client: Optional[DomainUserSummary] = None


class DomainCoachClientAssociation(BaseModel):
    """Domain model for a coach-client association."""

    model_config = ConfigDict(from_attributes=True)

    id_: UUID
    coach_id: UUID
    client_id: UUID
    requester_id: UUID
    domain: DomainDomain
    status: DomainAssociationStatus
    created_at: datetime
    modified_at: datetime

    # Use a non-recursive summary model here to break the validation cycle
    coach: Optional[DomainUserSummary] = None
    client: Optional[DomainUserSummary] = None
    requester: Optional[DomainUserSummary] = None


class DomainUserServiceLink(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    service_id: UUID
    created_at: datetime
    modified_at: datetime
    active: bool
    # user: Optional["DomainUser"] = None  # This relation is uni-directional for now
    service: Optional[DomainService] = None


class DomainSchedulable(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_: UUID
    created_at: datetime
    modified_at: datetime
    name: str
    description: Optional[str] = None
    entity_id: UUID  # For federated foreign key
    completed: bool = False
    service_id: UUID
    user_id: UUID
    date: Optional[date] = None
    service: Optional[DomainService] = None
    # user: Optional["DomainUser"] = None # This relation is uni-directional for now


class DomainUser(DomainUserSummary):
    """Full domain model for a user, including all relationships."""

    model_config = ConfigDict(from_attributes=True)

    service_links: List[DomainUserServiceLink] = []
    schedulables: List[DomainSchedulable] = []
    roles: List[DomainUserRole] = []
    
    # New simplified coach-client relationships
    client_relationships: List[DomainCoachClientRelationship] = []
    coach_relationships: List[DomainCoachClientRelationship] = []
    
    # Existing coach-client associations
    coaching_clients: List[DomainCoachClientAssociation] = []
    coaches: List[DomainCoachClientAssociation] = []


# Manually rebuild the models to resolve the forward references.
DomainUser.model_rebuild()
