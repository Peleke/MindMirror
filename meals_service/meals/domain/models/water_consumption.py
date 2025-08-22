from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DomainWaterConsumption(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_: UUID
    created_at: datetime
    modified_at: datetime

    user_id: str  # Internal user ID (not Supabase ID)
    quantity: float  # mL of water consumed
    consumed_at: datetime
