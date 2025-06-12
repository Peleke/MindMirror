import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.journal import JournalEntry as PydanticJournalEntry
from src.models.sql.base import Base


class JournalEntryModel(Base):
    __tablename__ = "journal_entries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[str] = mapped_column(String, index=True, nullable=False)

    entry_type: Mapped[str] = mapped_column(
        Enum("GRATITUDE", "REFLECTION", "FREEFORM", name="journal_entry_type_enum"),
        nullable=False,
    )

    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=True,
    )

    def to_pydantic(self) -> PydanticJournalEntry:
        """Converts the SQLAlchemy model to a Pydantic model."""
        return PydanticJournalEntry(
            id=str(self.id),
            user_id=self.user_id,
            entry_type=self.entry_type,
            payload=self.payload,
            created_at=self.created_at,
            modified_at=self.modified_at,
        )
