import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .models import Base


class HabitTemplate(Base):
    __tablename__ = "habit_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = Column(String, nullable=False, unique=True, index=True)
    title = Column(String, nullable=False)
    short_description = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    level = Column(Integer, nullable=True)
    default_duration_days = Column(Integer, nullable=False, default=7)
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class LessonTemplate(Base):
    __tablename__ = "lesson_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = Column(String, nullable=False, unique=True, index=True)
    title = Column(String, nullable=False)
    markdown_content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)
    est_read_minutes = Column(Integer, nullable=True)
    # Versioning and metadata
    version = Column(Integer, nullable=False, server_default="1")
    content_hash = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default="true")
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class ProgramTemplate(Base):
    __tablename__ = "program_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = Column(String, nullable=False, unique=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    # Versioning
    version = Column(Integer, nullable=False, server_default="1")
    content_hash = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class ProgramStepTemplate(Base):
    __tablename__ = "program_step_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    program_template_id = Column(
        UUID(as_uuid=True), ForeignKey("program_templates.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    sequence_index = Column(Integer, nullable=False)
    habit_template_id = Column(
        UUID(as_uuid=True), ForeignKey("habit_templates.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    duration_days = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("program_template_id", "sequence_index", name="uq_program_step_sequence"),
    )


class StepLessonTemplate(Base):
    __tablename__ = "step_lesson_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    program_step_template_id = Column(
        UUID(as_uuid=True), ForeignKey("program_step_templates.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    day_index = Column(Integer, nullable=False)
    lesson_template_id = Column(
        UUID(as_uuid=True), ForeignKey("lesson_templates.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    __table_args__ = (
        Index("ix_step_day", "program_step_template_id", "day_index"),
    )


class UserProgramAssignment(Base):
    __tablename__ = "user_program_assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)
    program_template_id = Column(
        UUID(as_uuid=True), ForeignKey("program_templates.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    start_date = Column(Date, nullable=False)
    status = Column(String, nullable=False, default="active")  # active|paused|completed|cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class HabitEvent(Base):
    __tablename__ = "habit_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)
    habit_template_id = Column(
        UUID(as_uuid=True), ForeignKey("habit_templates.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    program_assignment_id = Column(
        UUID(as_uuid=True), ForeignKey("user_program_assignments.id", ondelete="SET NULL"), nullable=True, index=True
    )
    date = Column(Date, nullable=False)
    response = Column(String, nullable=False)  # yes|no
    source = Column(String, nullable=True)  # tap|swipeLeft|swipeRight
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "user_id", "habit_template_id", "date", "program_assignment_id", name="uq_habit_event_uniqueness"
        ),
    )


class LessonEvent(Base):
    __tablename__ = "lesson_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)
    lesson_template_id = Column(
        UUID(as_uuid=True), ForeignKey("lesson_templates.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    program_assignment_id = Column(
        UUID(as_uuid=True), ForeignKey("user_program_assignments.id", ondelete="SET NULL"), nullable=True, index=True
    )
    date = Column(Date, nullable=False)
    event_type = Column(String, nullable=False)  # opened|completed
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class JournalTaskEvent(Base):
    __tablename__ = "journal_task_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)
    date = Column(Date, nullable=False)
    action = Column(String, nullable=False)  # opened|dismissed|completed
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


# --- ACL & Provenance ---

class TemplateAccess(Base):
    """
    Generic ACL for templates. Keeps templates user-agnostic while supporting:
    - Private templates (owner only)
    - Shared templates (view/edit to specific users)
    - Public templates (user_id NULL + permission 'view')

    Conventions:
    - kind: 'habit' | 'lesson' | 'program'
    - permission: 'owner' | 'edit' | 'view'
    - Public: (user_id IS NULL, permission='view')
    - Ownership: exactly one (kind, template_id, user_id, 'owner') for user-authored templates
    """

    __tablename__ = "template_access"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kind = Column(String, nullable=False)  # habit|lesson|program
    template_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(String, nullable=True, index=True)  # NULL => public
    permission = Column(String, nullable=False)  # owner|edit|view
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("kind", "template_id", "user_id", "permission", name="uq_template_access"),
        Index("ix_template_access_user_kind", "user_id", "kind"),
        Index("ix_template_access_template", "kind", "template_id"),
        CheckConstraint("permission in ('owner','edit','view')", name="ck_template_access_permission"),
        CheckConstraint("kind in ('habit','lesson','program')", name="ck_template_access_kind"),
    )


class TemplateProvenance(Base):
    """
    Provenance metadata for templates, decoupled from templates themselves.
    - origin: 'system' | 'user' | 'import'
    - origin_user_id: set when origin='user' (creator) or import attribution
    - unique per (kind, template_id)
    """

    __tablename__ = "template_provenance"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kind = Column(String, nullable=False)  # habit|lesson|program
    template_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    origin = Column(String, nullable=False)  # system|user|import
    origin_user_id = Column(String, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("kind", "template_id", name="uq_template_provenance_template"),
        CheckConstraint("origin in ('system','user','import')", name="ck_template_provenance_origin"),
        CheckConstraint("kind in ('habit','lesson','program')", name="ck_template_provenance_kind"),
    )


