from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class MealFoodModel(Base):
    __tablename__ = "meal_foods"
    __table_args__ = {"schema": "meals"}

    id_: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4, name="id")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))

    # Foreign keys
    meal_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("meals.meals.id", ondelete="CASCADE"), nullable=False)
    food_item_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("meals.food_items.id"), nullable=False)

    # Quantity information
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    serving_unit: Mapped[str] = mapped_column(String(64), nullable=False)

    # Relationships
    meal: Mapped["MealModel"] = relationship("MealModel", back_populates="meal_foods")
    food_item: Mapped["FoodItemModel"] = relationship("FoodItemModel", lazy="selectin")

    @property
    def id(self) -> UUID:
        return self.id_

    def to_dict(self) -> dict:
        """Convert model to dictionary for API consumption."""
        return {
            "id_": str(self.id_),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "meal_id": str(self.meal_id),
            "food_item_id": str(self.food_item_id),
            "quantity": self.quantity,
            "serving_unit": self.serving_unit,
            "food_item": self.food_item.to_dict() if self.food_item else None,
        }
