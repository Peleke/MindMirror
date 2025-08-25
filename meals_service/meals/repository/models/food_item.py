from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, String, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class FoodItemModel(Base):
    __tablename__ = "food_items"
    __table_args__ = {"schema": "meals"}

    id_: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4, name="id")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))

    # Basic information
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    serving_size: Mapped[float] = mapped_column(Float, nullable=False)
    serving_unit: Mapped[str] = mapped_column(String(64), nullable=False)

    # Macronutrients (required)
    calories: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    protein: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    carbohydrates: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    fat: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Fat breakdown (optional)
    saturated_fat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    monounsaturated_fat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    polyunsaturated_fat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    trans_fat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Other nutrients (optional)
    cholesterol: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # mg
    fiber: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # g
    sugar: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # g
    sodium: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # mg

    # Vitamins and minerals (optional)
    vitamin_d: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # μg
    calcium: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # mg
    iron: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # mg
    potassium: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # mg
    zinc: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # mg

    # User association and notes
    user_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # For user-specific food items
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # OFF provenance and display fields
    brand: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    source: Mapped[str] = mapped_column(String(16), nullable=False, default="local")
    external_source: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    external_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

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
            "serving_size": self.serving_size,
            "serving_unit": self.serving_unit,
            "calories": self.calories,
            "protein": self.protein,
            "carbohydrates": self.carbohydrates,
            "fat": self.fat,
            "saturated_fat": self.saturated_fat,
            "monounsaturated_fat": self.monounsaturated_fat,
            "polyunsaturated_fat": self.polyunsaturated_fat,
            "trans_fat": self.trans_fat,
            "cholesterol": self.cholesterol,
            "fiber": self.fiber,
            "sugar": self.sugar,
            "sodium": self.sodium,
            "vitamin_d": self.vitamin_d,
            "calcium": self.calcium,
            "iron": self.iron,
            "potassium": self.potassium,
            "zinc": self.zinc,
            "user_id": self.user_id,
            "notes": self.notes,
            "brand": self.brand,
            "thumbnail_url": self.thumbnail_url,
            "source": self.source,
            "external_source": self.external_source,
            "external_id": self.external_id,
            "external_metadata": self.external_metadata,
        }
