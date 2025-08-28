import uuid
from typing import Any, Dict, List, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from users.repository.models import (  # Import ServiceModel for type hint if needed
    SchedulableModel,
    ServiceModel,
)


class SchedulableRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_schedulable(self, schedulable_data: Dict[str, Any]) -> SchedulableModel:
        # Ensure service_id is a UUID and present
        service_id_input = schedulable_data.get("service_id")
        if not isinstance(service_id_input, uuid.UUID):
            if isinstance(service_id_input, str):
                try:
                    service_id_input = uuid.UUID(service_id_input)
                except ValueError:
                    raise ValueError("Invalid service_id string format for schedulable. Must be UUID string.")
            else:
                raise ValueError("Schedulable data must contain 'service_id' of type UUID or UUID string.")
        schedulable_data["service_id"] = service_id_input  # Ensure it's UUID type

        # Ensure user_id is a UUID
        user_id_input = schedulable_data.get("user_id")
        if not isinstance(user_id_input, uuid.UUID):
            if isinstance(user_id_input, str):
                try:
                    user_id_input = uuid.UUID(user_id_input)
                except ValueError:
                    raise ValueError("Invalid user_id string format for schedulable. Must be UUID string.")
            else:
                raise ValueError("Schedulable data must contain 'user_id' of type UUID or UUID string.")
        schedulable_data["user_id"] = user_id_input

        # Ensure entity_id is a UUID
        entity_id_input = schedulable_data.get("entity_id")
        if not isinstance(entity_id_input, uuid.UUID):
            if isinstance(entity_id_input, str):
                try:
                    entity_id_input = uuid.UUID(entity_id_input)
                except ValueError:
                    raise ValueError("Invalid entity_id string format for schedulable. Must be UUID string.")
            else:  # could be None if not provided, or other type. Defaulting if not UUID or string.
                schedulable_data["entity_id"] = uuid.uuid4()  # Or handle as error if strict
        else:  # Is already a UUID
            schedulable_data["entity_id"] = entity_id_input

        # Prepare data for model creation, ensuring only valid fields are passed
        model_data = {
            "name": schedulable_data["name"],
            "description": schedulable_data.get("description"),
            "entity_id": schedulable_data["entity_id"],
            "completed": schedulable_data.get("completed", False),
            "user_id": schedulable_data["user_id"],
            "service_id": schedulable_data["service_id"],
        }

        schedulable = SchedulableModel(**model_data)
        self.session.add(schedulable)
        await self.session.flush()
        await self.session.refresh(schedulable)
        return schedulable

    async def get_schedulables_by_user_id(self, user_id: uuid.UUID) -> Sequence[SchedulableModel]:
        stmt = (
            select(SchedulableModel)
            .where(SchedulableModel.user_id == user_id)
            .options(selectinload(SchedulableModel.service))
            .order_by(SchedulableModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_schedulables_for_user_by_service(
        self, user_id: uuid.UUID, service_id: Optional[uuid.UUID] = None, completed: Optional[bool] = None
    ) -> List[SchedulableModel]:
        stmt = (
            select(SchedulableModel)
            .where(SchedulableModel.user_id == user_id)
            .options(joinedload(SchedulableModel.service))
            .order_by(SchedulableModel.created_at.desc())
        )
        if service_id:
            stmt = stmt.where(SchedulableModel.service_id == service_id)
        if completed is not None:
            stmt = stmt.where(SchedulableModel.completed == completed)

        result = await self.session.execute(stmt)
        schedulables = result.scalars().all()
        return list(schedulables)

    async def get_schedulable_by_id(self, schedulable_id: uuid.UUID) -> Optional[SchedulableModel]:
        stmt = (
            select(SchedulableModel)
            .where(SchedulableModel.id_ == schedulable_id)
            .options(selectinload(SchedulableModel.service), selectinload(SchedulableModel.user))
        )
        result = await self.session.execute(stmt)
        schedulable = result.scalars().first()
        if schedulable:
            await self.session.refresh(schedulable)
        return schedulable

    async def update_schedulable(
        self, schedulable_id: uuid.UUID, update_data: Dict[str, Any]
    ) -> Optional[SchedulableModel]:
        schedulable = await self.get_schedulable_by_id(schedulable_id)
        if schedulable:
            # Ensure service_id is UUID if provided
            if "service_id" in update_data:
                service_id_input = update_data["service_id"]
                if not isinstance(service_id_input, uuid.UUID):
                    if isinstance(service_id_input, str):
                        try:
                            update_data["service_id"] = uuid.UUID(service_id_input)
                        except ValueError:
                            raise ValueError("Invalid service_id string for update.")
                    else:
                        raise ValueError("service_id for update must be UUID or UUID string.")

            # Ensure entity_id is UUID if provided
            if "entity_id" in update_data:
                entity_id_input = update_data["entity_id"]
                if not isinstance(entity_id_input, uuid.UUID):
                    if isinstance(entity_id_input, str):
                        try:
                            update_data["entity_id"] = uuid.UUID(entity_id_input)
                        except ValueError:
                            raise ValueError("Invalid entity_id string for update.")
                    # If not UUID or string, it might be an issue, or allow None to clear it if model allows
                    # For now, assuming valid UUID string or UUID if provided.

            for key, value in update_data.items():
                if hasattr(schedulable, key):
                    setattr(schedulable, key, value)
                else:
                    print(f"Warning: Attribute {key} not found on SchedulableModel during update.")
            await self.session.flush()
            await self.session.refresh(schedulable)
        return schedulable

    async def delete_schedulable(self, schedulable_id: uuid.UUID) -> bool:
        schedulable = await self.session.get(SchedulableModel, schedulable_id)
        if schedulable:
            await self.session.delete(schedulable)
            await self.session.flush()
            return True
        return False
