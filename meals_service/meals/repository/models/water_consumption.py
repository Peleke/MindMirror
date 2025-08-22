from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, String, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class WaterConsumptionModel(Base):
    __tablename__ = "water_consumption"
    __table_args__ = {"schema": "meals"}

    id_: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4, name="id")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))

    user_id: Mapped[str] = mapped_column(String, nullable=False)  # Supabase user ID
    quantity: Mapped[float] = mapped_column(Float, nullable=False)  # mL of water consumed
    consumed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @property
    def id(self) -> UUID:
        return self.id_

    def to_dict(self) -> dict:
        """Convert model to dictionary for API consumption."""
        return {
            "id_": str(self.id_),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "user_id": self.user_id,
            "quantity": self.quantity,
            "consumed_at": self.consumed_at.isoformat() if self.consumed_at else None,
        }
