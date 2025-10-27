import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class UserServicesModel(Base):
    """Linking table for many-to-many relationship between users and services.

    This represents a user's subscription/connection to a particular service.
    """

    __tablename__ = "user_services"
    __table_args__ = {"schema": "users"}

    # Composite primary key
    user_id: Mapped[uuid.UUID] = mapped_column(PGUUID, ForeignKey("users.users.id"), primary_key=True, index=True)
    service_id: Mapped[uuid.UUID] = mapped_column(PGUUID, ForeignKey("users.services.id"), primary_key=True, index=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))

    # Optional metadata about the subscription
    active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="service_links")
    service: Mapped["ServiceModel"] = relationship("ServiceModel", back_populates="user_links")

    def __str__(self) -> str:
        return f"<UserServicesModel(user_id={self.user_id}, service_id={self.service_id})>"

    def __repr__(self) -> str:
        return f"<UserServicesModel(user_id={self.user_id!r}, service_id={self.service_id!r}, active={self.active!r})>"

    def to_dict(self) -> dict:
        """Convert model to dictionary for FE consumption."""
        return {
            "user_id": str(self.user_id),
            "service_id": str(self.service_id),
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "service": self.service.to_dict() if self.service else None,
        }
