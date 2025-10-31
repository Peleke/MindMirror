import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID  # Use PGUUID for consistency
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enrollment import ProgramEnrollmentModel  # Import the new model
from .practice_template import (  # Renamed import
    PracticeTemplateModel,
)


class ProgramTagModel(Base):
    __tablename__ = "program_tags"
    __table_args__ = (UniqueConstraint("program_id", "name", name="_program_tag_name_uc"), {"schema": "practices"})

    id_ = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="id")
    program_id = Column(PGUUID(as_uuid=True), ForeignKey("practices.programs.id"), nullable=False)
    name = Column(String(100), nullable=False)  # The tag text, e.g., "Strength", "Hypertrophy"

    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    program = relationship("ProgramModel", back_populates="tags")

    def __repr__(self):
        return f"<ProgramTagModel(id={self.id_}, name='{self.name}', program_id='{self.program_id}')>"

    def to_dict(self) -> dict:
        """Convert model to dictionary for FE consumption."""
        return {
            "id_": str(self.id_),
            "program_id": str(self.program_id),
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
        }


class ProgramModel(Base):
    __tablename__ = "programs"
    __table_args__ = {"schema": "practices"}

    id_ = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="id")
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    level = Column(String(50), nullable=True)  # e.g., "BEGINNER", "INTERMEDIATE", "ADVANCED"
    user_id: Mapped[uuid.UUID] = mapped_column("user_id", PGUUID(as_uuid=True))
    habits_program_template_id = Column(PGUUID(as_uuid=True), nullable=True)  # Link to habits service program template
    # owner_id = Column(PGUUID(as_uuid=True), ForeignKey('practices.users.id'), nullable=True) # Future: when users exist in 'practices' schema

    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    practice_links = relationship(
        "ProgramPracticeLinkModel",
        back_populates="program",
        cascade="all, delete-orphan",
        order_by="ProgramPracticeLinkModel.sequence_order",
    )
    tags = relationship("ProgramTagModel", back_populates="program", cascade="all, delete-orphan")
    # user_progress = relationship("ProgramProgress", back_populates="program") # Future
    enrollments = relationship("ProgramEnrollmentModel", back_populates="program", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ProgramModel(id={self.id_}, name='{self.name}')>"

    def to_dict(self) -> dict:
        """Convert model to dictionary for FE consumption."""
        return {
            "id_": str(self.id_),
            "name": self.name,
            "description": self.description,
            "level": self.level,
            "user_id": str(self.user_id),
            "habits_program_template_id": str(self.habits_program_template_id) if self.habits_program_template_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "tags": [tag.to_dict() for tag in self.tags] if self.tags else [],
            "practice_links": [link.to_dict() for link in self.practice_links] if self.practice_links else [],
            "enrollments": [e.to_dict() for e in self.enrollments] if self.enrollments else [],
        }


class ProgramPracticeLinkModel(Base):
    __tablename__ = "program_practice_links"
    __table_args__ = (
        UniqueConstraint("program_id", "sequence_order", name="_program_sequence_uc"),
        {"schema": "practices"},
    )

    id_: Mapped[uuid.UUID] = mapped_column(PGUUID, primary_key=True, default=uuid.uuid4, name="id")
    program_id: Mapped[uuid.UUID] = mapped_column(PGUUID, ForeignKey("practices.programs.id"), nullable=False)
    practice_template_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID, ForeignKey("practices.practice_templates.id"), nullable=False
    )

    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)
    interval_days_after: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    modified_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    program: Mapped["ProgramModel"] = relationship("ProgramModel", back_populates="practice_links")
    practice_template: Mapped["PracticeTemplateModel"] = relationship(
        "PracticeTemplateModel", back_populates="program_links"
    )

    def __repr__(self):
        return f"<ProgramPracticeLinkModel(program_id={self.program_id}, practice_template_id={self.practice_template_id}, order={self.sequence_order})>"

    def to_dict(self) -> dict:
        """Convert model to dictionary for FE consumption."""
        return {
            "id_": str(self.id_),
            "program_id": str(self.program_id),
            "practice_template_id": str(self.practice_template_id),
            "sequence_order": self.sequence_order,
            "interval_days_after": self.interval_days_after,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
        }


# Future ProgramProgress model placeholder:
# class ProgramProgress(Base):
#     __tablename__ = "program_progress"
#     __table_args__ = {"schema": "practices"}
#     # ... fields as discussed ...
#     pass
