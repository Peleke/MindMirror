# practice_instance.py
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
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


class PracticeInstanceModel(Base):
    __tablename__ = "practice_instances"
    __table_args__ = {"schema": "practices"}

    id_: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4, name="id")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))

    date: Mapped[date] = mapped_column(Date, nullable=False, server_default=text("CURRENT_DATE"))
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    duration: Mapped[float] = mapped_column(Float, nullable=False, server_default="0.0")
    completed_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    user_id: Mapped[UUID] = mapped_column("user_id", PGUUID(as_uuid=True))
    template_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID,
        ForeignKey("practices.practice_templates.id", ondelete="SET NULL"),
        nullable=True,
    )

    template: Mapped[Optional["PracticeTemplateModel"]] = relationship(
        "PracticeTemplateModel", back_populates="instances"
    )
    prescriptions: Mapped[List["PrescriptionInstanceModel"]] = relationship(
        "PrescriptionInstanceModel",
        back_populates="practice_instance",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    scheduled_practice: Mapped[Optional["ScheduledPracticeModel"]] = relationship(back_populates="practice_instance")


class PrescriptionInstanceModel(Base):
    __tablename__ = "prescription_instances"
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
    practice_instance_id: Mapped[UUID] = mapped_column(
        PGUUID,
        ForeignKey("practices.practice_instances.id", ondelete="CASCADE"),
    )
    prescribed_rounds: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    complete: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    position: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    template_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID,
        ForeignKey("practices.prescription_templates.id", ondelete="SET NULL"),
        nullable=True,
    )

    movements: Mapped[List["MovementInstanceModel"]] = relationship(
        "MovementInstanceModel",
        back_populates="prescription_instance",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    practice_instance: Mapped["PracticeInstanceModel"] = relationship(back_populates="prescriptions")


class MovementInstanceModel(Base):
    __tablename__ = "movement_instances"
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
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    exercise_id: Mapped[Optional[UUID]] = mapped_column(PGUUID, nullable=True)
    complete: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    prescription_instance_id: Mapped[UUID] = mapped_column(
        PGUUID,
        ForeignKey("practices.prescription_instances.id", ondelete="CASCADE"),
    )
    template_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID,
        ForeignKey("practices.movement_templates.id", ondelete="SET NULL"),
        nullable=True,
    )

    prescription_instance: Mapped["PrescriptionInstanceModel"] = relationship(back_populates="movements")
    sets: Mapped[List["SetInstanceModel"]] = relationship(
        "SetInstanceModel",
        back_populates="movement_instance",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class SetInstanceModel(Base):
    __tablename__ = "set_instances"
    __table_args__ = (
        CheckConstraint(
            "perceived_exertion >= 1 AND perceived_exertion <= 4",
            name="perceived_exertion_check",
        ),
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
    complete: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    perceived_exertion: Mapped[int] = mapped_column(Integer, nullable=False, server_default="2")
    video_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    movement_instance_id: Mapped[UUID] = mapped_column(
        PGUUID,
        ForeignKey("practices.movement_instances.id", ondelete="CASCADE"),
    )
    template_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID,
        ForeignKey("practices.set_templates.id", ondelete="SET NULL"),
        nullable=True,
    )

    movement_instance: Mapped["MovementInstanceModel"] = relationship(back_populates="sets")
