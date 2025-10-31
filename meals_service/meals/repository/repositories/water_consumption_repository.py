from datetime import date, datetime
from typing import Any, List, Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from meals.domain.models import DomainWaterConsumption
from meals.repository.models import WaterConsumptionModel


class WaterConsumptionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_water_consumption(self, consumption_data: dict) -> DomainWaterConsumption:
        """Create a new water consumption record."""
        new_consumption = WaterConsumptionModel(**consumption_data)
        self.session.add(new_consumption)
        await self.session.flush()
        await self.session.refresh(new_consumption)
        return DomainWaterConsumption.model_validate(new_consumption)

    async def get_water_consumption_by_id(self, consumption_id: UUID) -> Optional[DomainWaterConsumption]:
        """Get water consumption record by ID."""
        stmt = select(WaterConsumptionModel).where(WaterConsumptionModel.id_ == consumption_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()
        return DomainWaterConsumption.model_validate(record) if record else None

    async def list_water_consumption_by_user(
        self,
        user_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[DomainWaterConsumption]:
        """List water consumption records for a user."""
        stmt = (
            select(WaterConsumptionModel)
            .where(WaterConsumptionModel.user_id == user_id)
            .order_by(WaterConsumptionModel.consumed_at.desc())
        )

        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        records = result.scalars().all()
        return [DomainWaterConsumption.model_validate(record) for record in records]

    async def list_water_consumption_by_user_and_date_range(
        self,
        user_id: str,
        start_date: date,
        end_date: date,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[DomainWaterConsumption]:
        """List water consumption for a user within a date range."""
        # Convert dates to datetime range for the day
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())

        stmt = (
            select(WaterConsumptionModel)
            .where(WaterConsumptionModel.user_id == user_id)
            .where(WaterConsumptionModel.consumed_at >= start_datetime)
            .where(WaterConsumptionModel.consumed_at <= end_datetime)
            .order_by(WaterConsumptionModel.consumed_at.desc())
        )

        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        records = result.scalars().all()
        return [DomainWaterConsumption.model_validate(record) for record in records]

    async def list_water_consumption_by_user_and_date(
        self,
        user_id: str,
        target_date: date,
    ) -> List[DomainWaterConsumption]:
        """List water consumption for a user on a specific date."""
        # Convert date to datetime range for the day
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())

        stmt = (
            select(WaterConsumptionModel)
            .where(WaterConsumptionModel.user_id == user_id)
            .where(WaterConsumptionModel.consumed_at >= start_datetime)
            .where(WaterConsumptionModel.consumed_at <= end_datetime)
            .order_by(WaterConsumptionModel.consumed_at)
        )

        result = await self.session.execute(stmt)
        records = result.scalars().all()
        return [DomainWaterConsumption.model_validate(record) for record in records]

    async def get_total_water_consumption_by_user_and_date(
        self,
        user_id: str,
        target_date: date,
    ) -> float:
        """Get total water consumption for a user on a specific date."""
        # Convert date to datetime range for the day
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())

        stmt = (
            select(func.sum(WaterConsumptionModel.quantity))
            .where(WaterConsumptionModel.user_id == user_id)
            .where(WaterConsumptionModel.consumed_at >= start_datetime)
            .where(WaterConsumptionModel.consumed_at <= end_datetime)
        )

        result = await self.session.execute(stmt)
        total = result.scalar() or 0.0
        return float(total)

    async def update_water_consumption(
        self, consumption_id: UUID, update_data: dict
    ) -> Optional[DomainWaterConsumption]:
        """Update water consumption record."""
        stmt = select(WaterConsumptionModel).where(WaterConsumptionModel.id_ == consumption_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            return None

        for key, value in update_data.items():
            if hasattr(record, key):
                setattr(record, key, value)

        await self.session.flush()
        await self.session.refresh(record)
        return DomainWaterConsumption.model_validate(record)

    async def delete_water_consumption(self, consumption_id: UUID) -> bool:
        """Delete water consumption record."""
        stmt = select(WaterConsumptionModel).where(WaterConsumptionModel.id_ == consumption_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if record:
            await self.session.delete(record)
            await self.session.flush()
            return True
        return False

    async def delete_water_consumption_by_user_and_date(self, user_id: str, target_date: date) -> int:
        """Delete all water consumption records for a user on a specific date. Returns count of deleted records."""
        # Convert date to datetime range for the day
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())

        # First get the records to count them
        stmt = (
            select(WaterConsumptionModel)
            .where(WaterConsumptionModel.user_id == user_id)
            .where(WaterConsumptionModel.consumed_at >= start_datetime)
            .where(WaterConsumptionModel.consumed_at <= end_datetime)
        )
        result = await self.session.execute(stmt)
        records = result.scalars().all()

        # Delete the records
        for record in records:
            await self.session.delete(record)

        await self.session.flush()
        return len(records)
