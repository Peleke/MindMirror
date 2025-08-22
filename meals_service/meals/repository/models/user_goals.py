from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, String, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class UserGoalsModel(Base):
    __tablename__ = "user_goals"
    __table_args__ = {"schema": "meals"}

    id_: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4, name="id")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("clock_timestamp()"))

    user_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)  # Supabase user ID

    # Daily goals
    daily_calorie_goal: Mapped[float] = mapped_column(Float, nullable=False, default=2000.0)
    daily_water_goal: Mapped[float] = mapped_column(Float, nullable=False, default=2000.0)  # mL

    # Optional macro goals
    daily_protein_goal: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # g
    daily_carbs_goal: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # g
    daily_fat_goal: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # g

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
            "daily_calorie_goal": self.daily_calorie_goal,
            "daily_water_goal": self.daily_water_goal,
            "daily_protein_goal": self.daily_protein_goal,
            "daily_carbs_goal": self.daily_carbs_goal,
            "daily_fat_goal": self.daily_fat_goal,
        }
