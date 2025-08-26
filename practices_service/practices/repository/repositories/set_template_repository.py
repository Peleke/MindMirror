import uuid
from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from practices.domain.models import DomainSetTemplate
from practices.repository.models import SetTemplateModel


class SetTemplateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_set_template(self, set_data: dict) -> DomainSetTemplate:
        """Create a new set template"""
        new_set = SetTemplateModel(**set_data)
        self.session.add(new_set)
        await self.session.commit()
        await self.session.refresh(new_set)
        return DomainSetTemplate.model_validate(new_set)

    async def get_set_template_by_id(self, set_id: uuid.UUID) -> Optional[DomainSetTemplate]:
        """Get set template by ID"""
        stmt = select(SetTemplateModel).where(SetTemplateModel.id_ == set_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()
        return DomainSetTemplate.model_validate(record) if record else None

    async def get_set_templates_by_movement_template_id(
        self, movement_template_id: uuid.UUID
    ) -> List[DomainSetTemplate]:
        """Get all set templates for a movement template"""
        stmt = (
            select(SetTemplateModel)
            .where(SetTemplateModel.movement_template_id == movement_template_id)
            .order_by(SetTemplateModel.position)
        )
        result = await self.session.execute(stmt)
        records = result.scalars().all()
        return [DomainSetTemplate.model_validate(record) for record in records]

    async def update_set_template(self, set_id: uuid.UUID, update_data: dict) -> Optional[DomainSetTemplate]:
        """Update set template"""
        stmt = select(SetTemplateModel).where(SetTemplateModel.id_ == set_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            return None

        for key, value in update_data.items():
            if hasattr(record, key):
                setattr(record, key, value)

        await self.session.commit()
        await self.session.refresh(record)
        return DomainSetTemplate.model_validate(record)

    async def delete_set_template(self, set_id: uuid.UUID) -> bool:
        """Delete set template"""
        stmt = select(SetTemplateModel).where(SetTemplateModel.id_ == set_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if record:
            await self.session.delete(record)
            await self.session.commit()
            return True
        return False

    async def reorder_sets_in_movement_template(
        self, movement_template_id: uuid.UUID, set_orders: List[dict]
    ) -> List[DomainSetTemplate]:
        """Reorder sets within a movement template

        Args:
            movement_template_id: The movement template ID
            set_orders: List of dicts with 'set_id' and 'position' keys
        """
        for order_data in set_orders:
            stmt = (
                update(SetTemplateModel)
                .where(SetTemplateModel.id_ == order_data["set_id"])
                .where(SetTemplateModel.movement_template_id == movement_template_id)
                .values(position=order_data["position"])
            )
            await self.session.execute(stmt)

        await self.session.commit()
        return await self.get_set_templates_by_movement_template_id(movement_template_id)

    async def get_template_usage_count(self, template_id: uuid.UUID) -> int:
        """Get number of times this template has been used to create instances"""
        from practices.repository.models.practice_instance import SetInstanceModel

        stmt = select(SetInstanceModel).where(SetInstanceModel.template_id == template_id)
        result = await self.session.execute(stmt)
        instances = result.scalars().all()
        return len(instances)
