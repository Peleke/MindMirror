import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .practice_instance import PracticeInstanceModel


class ScheduledPracticeModel(Base):
    """
    Represents a specific practice from a program that is scheduled for a user.
    """

    __tablename__ = "scheduled_practices"
    __table_args__ = {"schema": "practices"}

    id_: Mapped[uuid.UUID] = mapped_column(PGUUID, primary_key=True, default=uuid.uuid4, name="id")

    # Link to the enrollment this scheduled practice belongs to
    enrollment_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID, ForeignKey("practices.program_enrollments.id"), nullable=False, index=True
    )

    # Link to the practice template that this scheduled practice is based on
    practice_template_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID, ForeignKey("practices.practice_templates.id"), nullable=False, index=True
    )

    # Link to the specific practice instance (when the practice is completed)
    practice_instance_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PGUUID, ForeignKey("practices.practice_instances.id"), nullable=True
    )

    # The date the user is scheduled to complete this practice
    scheduled_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    modified_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    enrollment: Mapped["ProgramEnrollmentModel"] = relationship(
        "ProgramEnrollmentModel", back_populates="scheduled_practices"
    )
    practice_template: Mapped["PracticeTemplateModel"] = relationship("PracticeTemplateModel")
    practice_instance: Mapped[Optional["PracticeInstanceModel"]] = relationship(
        back_populates="scheduled_practice", uselist=False
    )

    def __repr__(self) -> str:
        return (
            f"<ScheduledPracticeModel(id={self.id_}, "
            f"enrollment_id={self.enrollment_id}, "
            f"practice_instance_id={self.practice_instance_id}, "
            f"scheduled_date='{self.scheduled_date}')>"
        )
