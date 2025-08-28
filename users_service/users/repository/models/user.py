import enum
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class RoleModel(str, enum.Enum):
    """Enumeration for user roles."""

    coach = "coach"
    client = "client"
    admin = "admin"


class DomainModel(str, enum.Enum):
    """
    Enumeration for domains where roles are applicable.
    This allows a user to be a COACH in FITNESS and a CLIENT in NUTRITION.
    """

    practices = "practices"
    meals = "meals"
    sleep = "sleep"
    system = "system"  # For global administrators


class AssociationStatusModel(str, enum.Enum):
    """Enumeration for the status of a coach-client association."""

    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    terminated = "terminated"


class UserRoleModel(Base):
    """Model linking users to roles within a specific domain."""

    __tablename__ = "user_roles"
    __table_args__ = (
        UniqueConstraint("user_id", "role", "domain", name="uq_user_role_domain"),
        {"schema": "users"},
    )

    id_: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4, name="id")
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.users.id"), nullable=False)
    role: Mapped[RoleModel] = mapped_column(Enum(RoleModel, name="role_enum", schema="users"), nullable=False)
    domain: Mapped[DomainModel] = mapped_column(Enum(DomainModel, name="domain_enum", schema="users"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="roles")

    def __repr__(self) -> str:
        return f"<UserRoleModel(user_id={self.user_id}, role='{self.role.value}', domain='{self.domain.value}')>"

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id_": str(self.id_),
            "user_id": str(self.user_id),
            "role": self.role.value,
            "domain": self.domain.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
        }


class CoachClientAssociationModel(Base):
    """Model linking coaches to clients."""

    __tablename__ = "coach_client_associations"
    __table_args__ = (
        UniqueConstraint("coach_id", "client_id", "domain", name="uq_coach_client_domain"),
        {"schema": "users"},
    )

    id_: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4, name="id")
    coach_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.users.id"), nullable=False)
    client_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.users.id"), nullable=False)
    requester_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.users.id"), nullable=False)
    domain: Mapped[DomainModel] = mapped_column(Enum(DomainModel, name="domain_enum", schema="users"), nullable=False)
    status: Mapped[AssociationStatusModel] = mapped_column(
        Enum(AssociationStatusModel, name="association_status_enum", schema="users"),
        nullable=False,
        default=AssociationStatusModel.pending,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))

    coach: Mapped["UserModel"] = relationship("UserModel", foreign_keys=[coach_id], back_populates="coaching_clients")
    client: Mapped["UserModel"] = relationship("UserModel", foreign_keys=[client_id], back_populates="coaches")
    requester: Mapped["UserModel"] = relationship("UserModel", foreign_keys=[requester_id])

    def to_dict(self) -> dict:
        return {
            "id_": str(self.id_),
            "coach_id": str(self.coach_id),
            "client_id": str(self.client_id),
            "requester_id": str(self.requester_id),
            "domain": self.domain.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
        }


class UserModel(Base):
    """Model representing a user in the system."""

    __tablename__ = "users"
    __table_args__ = {"schema": "users"}

    id_: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4, name="id")
    supabase_id: Mapped[str] = mapped_column(String(256), nullable=False, unique=True, index=True)
    keycloak_id: Mapped[Optional[str]] = mapped_column(String(256), nullable=True, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))

    # Relationship to user_services linking table
    service_links: Mapped[List["UserServicesModel"]] = relationship(
        "UserServicesModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Relationship to user roles
    roles: Mapped[List["UserRoleModel"]] = relationship(
        "UserRoleModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Relationships for coach-client associations
    coaching_clients: Mapped[List["CoachClientAssociationModel"]] = relationship(
        "CoachClientAssociationModel",
        foreign_keys="CoachClientAssociationModel.coach_id",
        back_populates="coach",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    coaches: Mapped[List["CoachClientAssociationModel"]] = relationship(
        "CoachClientAssociationModel",
        foreign_keys="CoachClientAssociationModel.client_id",
        back_populates="client",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Relationship to schedulables
    schedulables: Mapped[List["SchedulableModel"]] = relationship(
        "SchedulableModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    def id(self) -> UUID:
        return self.id_

    def __str__(self) -> str:
        return f"<UserModel(id_={self.id_}, supabase_id='{self.supabase_id}')>"

    def __repr__(self) -> str:
        return f"<UserModel(id_={self.id_!r}, supabase_id='{self.supabase_id!r}', keycloak_id='{self.keycloak_id!r}')>"

    def to_dict(self) -> dict:
        """Convert model to dictionary for FE consumption."""
        return {
            "id_": str(self.id_),
            "supabase_id": self.supabase_id,
            "keycloak_id": self.keycloak_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "service_links": [link.to_dict() for link in self.service_links] if self.service_links else [],
            "schedulables": [s.to_dict() for s in self.schedulables] if self.schedulables else [],
            "roles": [role.to_dict() for role in self.roles] if self.roles else [],
            "coaching_clients": [c.to_dict() for c in self.coaching_clients] if self.coaching_clients else [],
            "coaches": [c.to_dict() for c in self.coaches] if self.coaches else [],
        }
