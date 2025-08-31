# practice_template.py
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import Block, LoadUnit, MetricUnit, MovementClass


class PracticeTemplateModel(Base):
    __tablename__ = "practice_templates"
    __table_args__ = {"schema": "practices"}

    id_: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4, name="id")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))

    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    duration: Mapped[float] = mapped_column(Float, nullable=False, server_default="0.0")
    user_id: Mapped[UUID] = mapped_column("user_id", PGUUID(as_uuid=True))

    prescriptions: Mapped[List["PrescriptionTemplateModel"]] = relationship(
        "PrescriptionTemplateModel",
        back_populates="practice_template",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    program_links: Mapped[List["ProgramPracticeLinkModel"]] = relationship(
        "ProgramPracticeLinkModel",
        back_populates="practice_template",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    instances: Mapped[List["PracticeInstanceModel"]] = relationship(
        "PracticeInstanceModel",
        back_populates="template",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class PrescriptionTemplateModel(Base):
    __tablename__ = "prescription_templates"
    __table_args__ = (
        CheckConstraint("block IN ('warmup', 'workout', 'cooldown', 'other')", name="block_check"),
        {"schema": "practices"},
    )

    id_: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4, name="id")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False, server_default="")
    block: Mapped[Block] = mapped_column(String(64), nullable=False, server_default=Block.OTHER.value)
    practice_template_id: Mapped[UUID] = mapped_column(
        PGUUID,
        ForeignKey("practices.practice_templates.id", ondelete="CASCADE"),
    )
    prescribed_rounds: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    position: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    movements: Mapped[List["MovementTemplateModel"]] = relationship(
        "MovementTemplateModel",
        back_populates="prescription_template",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    practice_template: Mapped["PracticeTemplateModel"] = relationship(back_populates="prescriptions")


class MovementTemplateModel(Base):
    __tablename__ = "movement_templates"
    __table_args__ = (
        CheckConstraint(
            "metric_unit IN ('iterative', 'temporal', 'breath', 'other')",
            name="metric_unit_check",
        ),
        CheckConstraint(
            "movement_class IN ('conditioning', 'power', 'strength', 'mobility', 'other')",
            name="movement_class_check",
        ),
        {"schema": "practices"},
    )

    id_: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4, name="id")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))

    name: Mapped[str] = mapped_column(String(256), nullable=False)
    metric_unit: Mapped[MetricUnit] = mapped_column(
        String(64), nullable=False, server_default=MetricUnit.ITERATIVE.value
    )
    metric_value: Mapped[float] = mapped_column(Float, nullable=False, server_default="0.0")
    description: Mapped[str] = mapped_column(String, nullable=False, server_default="")
    prescribed_sets: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    video_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    movement_class: Mapped[MovementClass] = mapped_column(
        String(64), nullable=False, server_default=MovementClass.OTHER.value
    )
    rest_duration: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    position: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    exercise_id: Mapped[Optional[UUID]] = mapped_column(PGUUID, nullable=True)
    movement_id: Mapped[Optional[UUID]] = mapped_column(PGUUID, nullable=True)
    prescription_template_id: Mapped[UUID] = mapped_column(
        PGUUID,
        ForeignKey("practices.prescription_templates.id", ondelete="CASCADE"),
    )

    prescription_template: Mapped["PrescriptionTemplateModel"] = relationship(back_populates="movements")
    sets: Mapped[List["SetTemplateModel"]] = relationship(
        "SetTemplateModel",
        back_populates="movement_template",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class SetTemplateModel(Base):
    __tablename__ = "set_templates"
    __table_args__ = (
        CheckConstraint(
            "load_unit IN ('pounds', 'kilograms', 'bodyweight', 'other')",
            name="load_unit_check",
        ),
        CheckConstraint(
            "reps >= 0",
            name="reps_check",
        ),
        {"schema": "practices"},
    )

    id_: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4, name="id")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))

    reps: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    load_value: Mapped[float] = mapped_column(Float, nullable=False, server_default="0.0")
    load_unit: Mapped[LoadUnit] = mapped_column(String(64), nullable=False, server_default=LoadUnit.POUNDS.value)
    duration: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    rest_duration: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    position: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    movement_template_id: Mapped[UUID] = mapped_column(
        PGUUID,
        ForeignKey("practices.movement_templates.id", ondelete="CASCADE"),
    )

    movement_template: Mapped["MovementTemplateModel"] = relationship(back_populates="sets")
