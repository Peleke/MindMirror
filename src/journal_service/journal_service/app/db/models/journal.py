import uuid
from sqlalchemy import Column, String, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from journal_service.journal_service.app.db.models.base import TimestampedModel


class JournalEntry(TimestampedModel):
    """Journal entry model."""
    
    __tablename__ = "journal_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    entry_type = Column(String(50), nullable=False)  # GRATITUDE, REFLECTION, FREEFORM
    payload = Column(JSON, nullable=False)
    
    def __repr__(self):
        return f"<JournalEntry(id={self.id}, user_id={self.user_id}, type={self.entry_type})>" 