import uuid
from sqlalchemy import Column, String, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from journal.app.db.models.base import TimestampedModel


class JournalEntry(TimestampedModel):
    """Journal entry model."""
    
    __tablename__ = "journal_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    entry_type = Column(String(50), nullable=False)  # GRATITUDE, REFLECTION, FREEFORM
    payload = Column(JSON, nullable=False)
    # Optional link to a habit template (in habits service) that this entry relates to
    habit_template_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    def __repr__(self):
        return f"<JournalEntry(id={self.id}, user_id={self.user_id}, type={self.entry_type})>" 