from datetime import datetime
from sqlalchemy import Column, DateTime, func
from journal_service.journal_service.app.db.database import Base


class TimestampedModel(Base):
    """Base model with timestamp fields."""
    
    __abstract__ = True
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False) 