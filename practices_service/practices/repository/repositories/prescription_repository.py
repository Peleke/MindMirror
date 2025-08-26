import uuid
from typing import Any, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from practices.domain.models import DomainPrescription
from practices.repository.models import (
    PrescribedMovementModel,
    PrescriptionModel,
    SetModel,
)


class PrescriptionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_prescription_with_movements(self, prescription_data: dict) -> DomainPrescription:
        movements_data = prescription_data.pop("movements_data", [])
        # practice_id must be provided in prescription_data
        new_prescription = PrescriptionModel(**prescription_data)
        self.session.add(new_prescription)
        await self.session.flush()
        await self.session.refresh(new_prescription)

        created_movements = []
        for mov_data in movements_data:
            sets_data = mov_data.pop("sets_data", [])
            new_movement = PrescribedMovementModel(**mov_data, prescription_id=new_prescription.id_)
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
            created_movements.append(new_movement)
        new_prescription.movements = created_movements

        await self.session.commit()
        # Re-fetch with relationships loaded for Pydantic model validation
        stmt = (
            select(PrescriptionModel)
            .where(PrescriptionModel.id_ == new_prescription.id_)
            .options(selectinload(PrescriptionModel.movements).selectinload(PrescribedMovementModel.sets))
        )
        result = await self.session.execute(stmt)
        refetched_prescription = result.scalar_one_or_none()
        if not refetched_prescription:
            raise Exception("Failed to re-fetch prescription after creation")

        return DomainPrescription.model_validate(refetched_prescription)

    async def get_prescription_by_id(self, prescription_id: uuid.UUID) -> Optional[DomainPrescription]:
        stmt = (
            select(PrescriptionModel)
            .where(PrescriptionModel.id_ == prescription_id)
            .options(selectinload(PrescriptionModel.movements).selectinload(PrescribedMovementModel.sets))
        )
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()
        return DomainPrescription.model_validate(record) if record else None

    async def list_prescriptions_by_practice_id(
        self, practice_id: uuid.UUID, limit: Optional[int] = None
    ) -> List[DomainPrescription]:
        stmt = (
            select(PrescriptionModel)
            .where(PrescriptionModel.practice_id == practice_id)
            .options(selectinload(PrescriptionModel.movements).selectinload(PrescribedMovementModel.sets))
            .order_by(PrescriptionModel.position)
        )
        if limit:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        records = result.scalars().all()
        return [DomainPrescription.model_validate(record) for record in records]

    async def list_all_prescriptions(self) -> List[DomainPrescription]:
        stmt = (
            select(PrescriptionModel)
            .options(selectinload(PrescriptionModel.movements).selectinload(PrescribedMovementModel.sets))
            .order_by(PrescriptionModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        records = result.scalars().all()
        return [DomainPrescription.model_validate(record) for record in records]

    async def update_prescription(self, prescription_id: uuid.UUID, update_data: dict) -> Optional[DomainPrescription]:
        stmt = select(PrescriptionModel).where(PrescriptionModel.id_ == prescription_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            return None

        # Exclude 'movements' from direct setattr; handle separately if needed
        movements_update = update_data.pop("movements", None)

        for key, value in update_data.items():
            if hasattr(record, key):
                setattr(record, key, value)

        # Logic for updating movements would be more complex:
        # - Identify new, modified, deleted movements
        # - Process them accordingly (similar to create_prescription_with_movements or separate methods)
        # For now, this update focuses on PrescriptionModel's direct attributes.
        if movements_update is not None:
            # This is a placeholder for more complex logic.
            # A full update of nested movements is non-trivial.
            # One might delete all existing movements and recreate, or diff and apply.
            # For simplicity, this basic repo update won't handle deep movement updates.
            pass

        await self.session.commit()
        # Re-fetch to get a consistent DomainPrescription object with loaded movements
        return await self.get_prescription_by_id(prescription_id)

    async def delete_prescription(self, prescription_id: uuid.UUID) -> bool:
        stmt = select(PrescriptionModel).where(PrescriptionModel.id_ == prescription_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if record:
            await self.session.delete(record)
            await self.session.commit()
            return True
        return False
