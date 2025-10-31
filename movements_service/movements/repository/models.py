from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import String, DateTime, Boolean, text, Integer, UniqueConstraint, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class MovementModel(Base):
    __tablename__ = "movements"

    id_: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()), name="id")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))

    slug: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)

    difficulty: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    body_region: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    target_muscle_group: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    prime_mover_muscle: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    posture: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    arm_mode: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    arm_pattern: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    grip: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    load_position: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    leg_pattern: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    foot_elevation: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    combo_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    mechanics: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    laterality: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    primary_classification: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    force_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    archetype: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Freeform description/notes for the movement
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    short_video_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    long_video_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    gif_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    source: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    external_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Flexible metadata storage for coach videos, import details, etc.
    metadata_: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True, name="metadata")

    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    user_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)


class MovementAliasModel(Base):
    __tablename__ = "movement_aliases"

    id_: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()), name="id")
    movement_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), index=True)
    alias: Mapped[str] = mapped_column(String, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))


class MovementMuscleLink(Base):
    __tablename__ = "movement_muscle_links"
    movement_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True)
    muscle_name: Mapped[str] = mapped_column(String, primary_key=True)
    role: Mapped[str] = mapped_column(String, primary_key=True)  # primary|secondary|tertiary


class MovementEquipmentLink(Base):
    __tablename__ = "movement_equipment_links"
    movement_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True)
    equipment_name: Mapped[str] = mapped_column(String, primary_key=True)
    role: Mapped[str] = mapped_column(String, primary_key=True)  # primary|secondary
    item_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


class MovementPatternLink(Base):
    __tablename__ = "movement_pattern_links"
    movement_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True)
    pattern_name: Mapped[str] = mapped_column(String, primary_key=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class MovementPlaneLink(Base):
    __tablename__ = "movement_plane_links"
    movement_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True)
    plane_name: Mapped[str] = mapped_column(String, primary_key=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class MovementTagLink(Base):
    __tablename__ = "movement_tag_links"
    movement_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True)
    tag_name: Mapped[str] = mapped_column(String, primary_key=True)


class MovementInstruction(Base):
    __tablename__ = "movement_instructions"
    movement_id: Mapped[str] = mapped_column(PGUUID(as_uuid=False), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String)


class MovementRelationship(Base):
    """
    Exercise relationship graph edges for progressions, regressions, and variations.

    Represents directed edges in the exercise difficulty graph:
    - regression: easier variation (e.g., Plank → easier → Hands-Elevated Plank)
    - progression: harder variation (e.g., Plank → harder → Ab Wheel Iso)
    - travel_modification: minimal equipment alternative (e.g., Barbell Squat → Band Squat)
    - variation: same difficulty, different style (e.g., Barbell Row → Dumbbell Row)

    Examples:
        # Create a progression edge
        MovementRelationship(
            from_movement_id="plank_id",
            to_movement_id="ab_wheel_id",
            relationship_type="progression",
            difficulty_delta=1
        )

        # Create a regression edge (inverse of above)
        MovementRelationship(
            from_movement_id="ab_wheel_id",
            to_movement_id="plank_id",
            relationship_type="regression",
            difficulty_delta=-1
        )

    Future Neo4j Migration:
        This schema maps directly to Neo4j property graph:
        (:Movement)-[:PROGRESSION {difficulty_delta: 1}]->(:Movement)
    """
    __tablename__ = "movement_relationships"

    id_: Mapped[str] = mapped_column(
        PGUUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
        name="id"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("clock_timestamp()")
    )

    # Directed edge: from_movement --[relationship_type]--> to_movement
    from_movement_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=False),
        ForeignKey("movements.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    to_movement_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=False),
        ForeignKey("movements.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Relationship type: regression, progression, travel_modification, variation
    relationship_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True
    )

    # Optional: difficulty delta (negative for easier, positive for harder)
    difficulty_delta: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Optional: notes about this specific relationship
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    __table_args__ = (
        # Prevent duplicate relationships
        UniqueConstraint(
            'from_movement_id',
            'to_movement_id',
            'relationship_type',
            name='uq_movement_relationship'
        ),
        # Enforce valid relationship types
        CheckConstraint(
            "relationship_type IN ('regression', 'progression', 'travel_modification', 'variation')",
            name='ck_relationship_type'
        ),
        # Prevent self-referential relationships
        CheckConstraint(
            "from_movement_id != to_movement_id",
            name='ck_no_self_reference'
        ),
        {'schema': 'movements'}
    ) 