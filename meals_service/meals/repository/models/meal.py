from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, String, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import MealType


class MealModel(Base):
    __tablename__ = "meals"
    __table_args__ = {"schema": "meals"}

    id_: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4, name="id")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))

    # Meal information
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    type: Mapped[MealType] = mapped_column(Enum(MealType), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)  # Supabase user ID

    # Relationships
    meal_foods: Mapped[List["MealFoodModel"]] = relationship(
        "MealFoodModel",
        back_populates="meal",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    def id(self) -> UUID:
        return self.id_

    def to_dict(self) -> dict:
        """Convert model to dictionary for API consumption."""
        return {
            "id_": str(self.id_),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "name": self.name,
            "type": self.type.value,
            "date": self.date.isoformat() if self.date else None,
            "notes": self.notes,
            "user_id": self.user_id,
            "meal_foods": [mf.to_dict() for mf in self.meal_foods] if self.meal_foods else [],
        }
