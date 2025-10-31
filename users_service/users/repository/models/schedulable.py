import uuid  # Import uuid for Mapped[uuid.UUID] and default
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class SchedulableModel(Base):
    """Model representing a schedulable task/item from any service.

    This acts as a virtual entity that aggregates data from different services
    to present a unified view of user tasks.
    """

    __tablename__ = "schedulables"
    __table_args__ = {"schema": "users"}

    id_: Mapped[uuid.UUID] = mapped_column(PGUUID, primary_key=True, default=uuid.uuid4, name="id")
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(PGUUID, nullable=False, index=True)  # Federated foreign key
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))

    # Foreign key relationships
    user_id: Mapped[uuid.UUID] = mapped_column(PGUUID, ForeignKey("users.users.id"), nullable=False, index=True)
    service_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID, ForeignKey("users.services.id"), nullable=False, index=True
    )  # Changed FK to point to services.id

    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="schedulables")
    service: Mapped["ServiceModel"] = relationship(
        "ServiceModel", back_populates="schedulables", lazy="selectin"
    )  # Added back_populates here

    @property
    def id(self) -> uuid.UUID:
        return self.id_

    def __str__(self) -> str:
        return f"<SchedulableModel(id_={self.id_}, name='{self.name}', user_id={self.user_id}, service_id={self.service_id})>"

    def __repr__(self) -> str:
        return (
            f"<SchedulableModel(id_={self.id_!r}, name='{self.name!r}', "
            f"user_id={self.user_id!r}, service_id={self.service_id!r}, "
            f"entity_id={self.entity_id!r}, completed={self.completed!r})>"
        )

    def to_dict(self) -> dict:
        """Convert model to dictionary for FE consumption."""
        return {
            "id_": str(self.id_),
            "name": self.name,
            "description": self.description,
            "entity_id": str(self.entity_id),
            "completed": self.completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "user_id": str(self.user_id),
            "service_id": str(self.service_id),  # Will be UUID string
            "service": self.service.to_dict() if self.service else None,
        }
