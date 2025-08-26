import enum
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class EnrollmentStatus(enum.Enum):
    """Defines the status of a user's enrollment in a program."""

    ACTIVE = "active"
    INACTIVE = "inactive"  # Paused or temporarily suspended
    CANCELLED = "cancelled"  # User or coach cancelled enrollment
    COMPLETED = "completed"  # User finished the program
    PENDING = "pending"  # User has not yet started the program


class ProgramEnrollmentModel(Base):
    __tablename__ = "program_enrollments"
    __table_args__ = {"schema": "practices"}

    id_: Mapped[uuid.UUID] = mapped_column(PGUUID, primary_key=True, default=uuid.uuid4, name="id")
    program_id: Mapped[uuid.UUID] = mapped_column(PGUUID, ForeignKey("practices.programs.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(PGUUID, nullable=False, index=True)
    enrolled_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(PGUUID, nullable=True, index=True)
    status: Mapped[EnrollmentStatus] = mapped_column(
        Enum(EnrollmentStatus, name="enrollment_status_enum", schema="practices"),
        nullable=False,
        default=EnrollmentStatus.ACTIVE,
    )

    current_practice_link_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PGUUID,
        ForeignKey("practices.program_practice_links.id"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    program: Mapped["ProgramModel"] = relationship("ProgramModel", back_populates="enrollments")

    current_practice_link: Mapped[Optional["ProgramPracticeLinkModel"]] = relationship(
        "ProgramPracticeLinkModel", foreign_keys=[current_practice_link_id]
    )

    scheduled_practices: Mapped[List["ScheduledPracticeModel"]] = relationship(
        "ScheduledPracticeModel",
        back_populates="enrollment",
        cascade="all, delete-orphan",
        order_by="ScheduledPracticeModel.scheduled_date",
    )

    def __repr__(self):
        return f"<ProgramEnrollmentModel(program_id='{self.program_id}', user_id='{self.user_id}', status='{self.status.value}')>"

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id_": str(self.id_),
            "program_id": str(self.program_id),
            "user_id": str(self.user_id),
            "enrolled_by_user_id": str(self.enrolled_by_user_id) if self.enrolled_by_user_id else None,
            "status": self.status.value,
            "current_practice_link_id": str(self.current_practice_link_id) if self.current_practice_link_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
        }
