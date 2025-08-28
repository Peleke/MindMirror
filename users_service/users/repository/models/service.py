import enum
import uuid
from datetime import datetime
from typing import List, Optional

import sqlalchemy
from sqlalchemy import DateTime, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from users.repository.database import SCHEMA_NAME

from .base import Base


class ServiceEnum(str, enum.Enum):
    """Enumeration of available services."""

    meals = "meals"
    practice = "practice"
    sleep = "sleep"
    shadow_boxing = "shadow_boxing"
    fitness_db = "fitness_db"
    programs = "programs"


class ServiceModel(Base):
    """Model representing a service that users can subscribe to."""

    __tablename__ = "services"
    __table_args__ = (UniqueConstraint("name", name="uq_services_name"), {"schema": SCHEMA_NAME})

    id_: Mapped[uuid.UUID] = mapped_column(PGUUID, primary_key=True, default=uuid.uuid4, name="id")
    name: Mapped[ServiceEnum] = mapped_column(
        sqlalchemy.Enum(
            ServiceEnum,
            name="service_type",
            schema=SCHEMA_NAME,
            create_type=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        unique=True,
        index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))

    # Relationship to user_services linking table
    user_links: Mapped[List["UserServicesModel"]] = relationship(
        "UserServicesModel",
        back_populates="service",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Relationship to schedulables (if a service can have many schedulables directly, usually schedulables belong to a user FOR a service)
    # This might not be needed if schedulables always link through user_services or directly to user and service by ID.
    # SchedulableModel already has a service_id FK and a relationship to ServiceModel.
    # So, a back-populating relationship from ServiceModel to SchedulableModel can be added.
    schedulables: Mapped[List["SchedulableModel"]] = relationship("SchedulableModel", back_populates="service")

    @property
    def service_id(self) -> uuid.UUID:
        return self.id_

    def __str__(self) -> str:
        return f"<ServiceModel(id_={self.id_}, name='{self.name.value if self.name else None}')>"

    def __repr__(self) -> str:
        return f"<ServiceModel(id_={self.id_!r}, name={self.name!r}, url='{self.url!r}')>"

    def to_dict(self) -> dict:
        """Convert model to dictionary for FE consumption."""
        return {
            "id": str(self.id_),
            "name": self.name.value if self.name else None,
            "description": self.description,
            "url": self.url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
        }
