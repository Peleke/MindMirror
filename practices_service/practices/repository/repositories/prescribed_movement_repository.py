import uuid
from typing import Any, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from practices.domain.models import DomainPrescribedMovement
from practices.repository.models import PrescribedMovementModel, SetModel


class PrescribedMovementRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_movement_with_sets(self, movement_data: dict) -> DomainPrescribedMovement:
        sets_data = movement_data.pop("sets_data", [])
        # prescription_id must be provided in movement_data
        new_movement = PrescribedMovementModel(**movement_data)
        self.session.add(new_movement)
        await self.session.flush()
        await self.session.refresh(new_movement)

        created_sets = []
        for set_data in sets_data:
            new_set = SetModel(**set_data, prescribed_movement_id=new_movement.id_)
            self.session.add(new_set)
            await self.session.flush()
            await self.session.refresh(new_set)
            created_sets.append(new_set)
        new_movement.sets = created_sets

        await self.session.commit()
        # Re-fetch with sets loaded
        stmt = (
            select(PrescribedMovementModel)
            .where(PrescribedMovementModel.id_ == new_movement.id_)
            .options(selectinload(PrescribedMovementModel.sets))
        )
        result = await self.session.execute(stmt)
        refetched_movement = result.scalar_one_or_none()
        if not refetched_movement:
            raise Exception("Failed to re-fetch prescribed movement after creation")

        return DomainPrescribedMovement.model_validate(refetched_movement)

    async def get_movement_by_id(self, movement_id: uuid.UUID) -> Optional[DomainPrescribedMovement]:
        stmt = (
            select(PrescribedMovementModel)
            .where(PrescribedMovementModel.id_ == movement_id)
            .options(selectinload(PrescribedMovementModel.sets))
        )
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()
        return DomainPrescribedMovement.model_validate(record) if record else None

    async def list_movements_by_prescription_id(
        self, prescription_id: uuid.UUID, limit: Optional[int] = None
    ) -> List[DomainPrescribedMovement]:
        stmt = (
            select(PrescribedMovementModel)
            .where(PrescribedMovementModel.prescription_id == prescription_id)
            .options(selectinload(PrescribedMovementModel.sets))
            .order_by(PrescribedMovementModel.position)  # Assuming 'order' field exists
        )
        if limit:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        records = result.scalars().all()
        return [DomainPrescribedMovement.model_validate(record) for record in records]

    async def list_all_prescribed_movements(self) -> List[DomainPrescribedMovement]:
        stmt = (
            select(PrescribedMovementModel)
            .options(selectinload(PrescribedMovementModel.sets))
            .order_by(PrescribedMovementModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        records = result.scalars().all()
        return [DomainPrescribedMovement.model_validate(record) for record in records]

    async def update_movement(self, movement_id: uuid.UUID, update_data: dict) -> Optional[DomainPrescribedMovement]:
        stmt = select(PrescribedMovementModel).where(PrescribedMovementModel.id_ == movement_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            return None

        # Exclude 'sets' from direct setattr; handle separately if needed
        sets_update = update_data.pop("sets", None)

        for key, value in update_data.items():
            if hasattr(record, key):
                setattr(record, key, value)

        # Complex logic for updating sets (diffing, deleting old, adding new) would go here.
        # For simplicity, this basic repo update won't handle deep set updates.
        if sets_update is not None:
            # Placeholder for complex logic. For example, delete existing and create new:
            # existing_sets = await self.session.execute(select(SetModel).where(SetModel.prescribed_movement_id == record.id_))
            # for s_to_del in existing_sets.scalars().all():
            #     await self.session.delete(s_to_del)
            # for set_data_new in sets_update:
            #     new_s = SetModel(**set_data_new, prescribed_movement_id=record.id_)
            #     self.session.add(new_s)
            pass

        await self.session.commit()
        # Re-fetch to get a consistent DomainPrescribedMovement object
        return await self.get_movement_by_id(movement_id)

    async def delete_movement(self, movement_id: uuid.UUID) -> bool:
        stmt = select(PrescribedMovementModel).where(PrescribedMovementModel.id_ == movement_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if record:
            await self.session.delete(record)
            await self.session.commit()
            return True
        return False
