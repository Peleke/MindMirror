from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from practices.domain.models import DomainSetInstance
from practices.repository.models.practice_instance import SetInstanceModel


class SetInstanceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, set_instance_data: dict) -> DomainSetInstance:
        """Creates a new set instance."""
        model = SetInstanceModel(**set_instance_data)
        self.session.add(model)
        await self.session.flush()

        # Convert the refreshed model directly to avoid a redundant DB call
        return DomainSetInstance(
            id_=model.id_,
            movement_instance_id=model.movement_instance_id,
            set_template_id=getattr(model, "template_id", None),
            position=model.position,
            reps=model.reps,
            duration=model.duration,
            rest_duration=model.rest_duration,
            load_value=model.load_value,
            load_unit=model.load_unit,
            perceived_exertion=model.perceived_exertion,
            complete=model.complete,
            completed_at=model.completed_at,
            notes=model.notes,
            created_at=model.created_at,
            modified_at=model.modified_at,
        )

    async def get_by_id(self, id_: UUID) -> Optional[DomainSetInstance]:
        """Retrieves a set instance by ID."""
        result = await self.session.execute(select(SetInstanceModel).where(SetInstanceModel.id_ == id_))
        record = result.scalars().first()
        if not record:
            return None

        set_dict = {
            "id_": record.id_,
            "movement_instance_id": record.movement_instance_id,
            "set_template_id": getattr(record, "template_id", None),
            "position": record.position,
            "reps": record.reps,
            "duration": record.duration,
            "rest_duration": record.rest_duration,
            "load_value": record.load_value,
            "load_unit": record.load_unit,
            "perceived_exertion": record.perceived_exertion,
            "complete": record.complete,
            "completed_at": record.completed_at,
            "notes": record.notes,
            "created_at": record.created_at,
            "modified_at": record.modified_at,
        }
        return DomainSetInstance(**set_dict)

    async def update(self, id_: UUID, update_data: dict) -> Optional[DomainSetInstance]:
        """Updates a set instance."""
        stmt = select(SetInstanceModel).where(SetInstanceModel.id_ == id_)
        result = await self.session.execute(stmt)
        model = result.scalars().first()
        if not model:
            return None

        # Apply updates from the input dictionary
        for key, value in update_data.items():
            setattr(model, key, value)

        # If the set is being marked as complete, always set the timestamp
        # (regardless of whether it was already set)
        if update_data.get("complete") is True:
            model.completed_at = datetime.now(timezone.utc)

        # Create the domain object from the model's current state BEFORE flushing.
        # This captures the `completed_at` timestamp we just set.
        domain_instance = DomainSetInstance(
            id_=model.id_,
            movement_instance_id=model.movement_instance_id,
            set_template_id=getattr(model, "template_id", None),
            position=model.position,
            reps=model.reps,
            duration=model.duration,
            rest_duration=model.rest_duration,
            load_value=model.load_value,
            load_unit=model.load_unit,
            perceived_exertion=model.perceived_exertion,
            complete=model.complete,
            completed_at=model.completed_at,
            notes=model.notes,
            created_at=model.created_at,
            modified_at=model.modified_at,
        )

        await self.session.flush()

        # Return the domain object we created before the flush.
        return domain_instance

    async def delete(self, id_: UUID) -> bool:
        """Deletes a set instance."""
        stmt = select(SetInstanceModel).where(SetInstanceModel.id_ == id_)
        result = await self.session.execute(stmt)
        model = result.scalars().first()
        if not model:
            return False

        await self.session.delete(model)
        return True

    async def get_set_instances_by_template_id(self, template_id: UUID) -> List[DomainSetInstance]:
        """Gets all set instances created from a specific template."""
        stmt = select(SetInstanceModel).where(SetInstanceModel.template_id == template_id)
        result = await self.session.execute(stmt)
        records = result.scalars().all()

        return [
            DomainSetInstance(
                id_=record.id_,
                movement_instance_id=record.movement_instance_id,
                set_template_id=record.template_id,
                position=record.position,
                reps=record.reps,
                duration=record.duration,
                rest_duration=record.rest_duration,
                load_value=record.load_value,
                load_unit=record.load_unit,
                perceived_exertion=record.perceived_exertion,
                complete=record.complete,
                completed_at=record.completed_at,
                notes=record.notes,
                created_at=record.created_at,
                modified_at=record.modified_at,
            )
            for record in records
        ]

    async def get_sets_by_movement_instance_id(self, movement_instance_id: UUID) -> List[DomainSetInstance]:
        """Get all sets for a movement instance"""
        stmt = (
            select(SetInstanceModel)
            .where(SetInstanceModel.movement_instance_id == movement_instance_id)
            .order_by(SetInstanceModel.position)
        )
        result = await self.session.execute(stmt)
        records = result.scalars().all()
        return [DomainSetInstance.model_validate(record) for record in records]

    async def mark_set_complete(self, set_id: UUID) -> Optional[DomainSetInstance]:
        """Mark a set as complete"""
        return await self.update(set_id, {"complete": True, "completed_at": datetime.now(timezone.utc)})

    # async def reorder_sets_in_movement(self, movement_instance_id: UUID, set_orders: List[dict]) -> List[DomainSetInstance]:
    #     """Reorder sets within a movement instance

    #     Args:
    #         movement_instance_id: The movement instance ID
    #         set_orders: List of dicts with 'set_id' and 'position' keys
    #     """
    #     for order_data in set_orders:
    #         stmt = (
    #             select(SetInstanceModel)
    #             .where(SetInstanceModel.id_ == order_data["set_id"])
    #             .where(SetInstanceModel.movement_instance_id == movement_instance_id)
    #             .values(position=order_data["position"])
    #         )
    #         await self.session.execute(stmt)

    #     await self.session.flush()
    #     return await self.get_sets_by_movement_instance_id(movement_instance_id)
