from datetime import date, datetime, timedelta
from uuid import uuid4

import pytest

from meals.domain.models import DomainWaterConsumption
from meals.repository.repositories import WaterConsumptionRepository
from meals.service.services import WaterConsumptionService


@pytest.mark.asyncio
class TestWaterConsumptionService:
    async def test_create_water_consumption_with_datetime_string(self, session, seed_db):
        """Test creating water consumption with datetime string conversion."""
        water_repo = WaterConsumptionRepository(session)
        service = WaterConsumptionService(water_repo)

        consumption_data = {
            "user_id": "service-test-user",
            "consumed_at": "2024-08-15T10:30:00",  # ISO datetime string
            "quantity": 250.0,
        }

        created_consumption = await service.create_water_consumption(consumption_data)
        await session.commit()

        assert isinstance(created_consumption, DomainWaterConsumption)
        assert created_consumption.user_id == consumption_data["user_id"]
        # Check date and time components (timezone handling may vary)
        assert created_consumption.consumed_at.date() == date(2024, 8, 15)
        assert created_consumption.consumed_at.hour >= 10  # Should be around 10 AM, allowing for timezone conversion
        assert created_consumption.quantity == consumption_data["quantity"]

        # Verify in database
        fetched_consumption = await service.get_water_consumption_by_id(created_consumption.id_)
        assert fetched_consumption is not None
        assert fetched_consumption.user_id == consumption_data["user_id"]

    async def test_create_water_consumption_with_datetime_object(self, session, seed_db):
        """Test creating water consumption with datetime object (no conversion needed)."""
        water_repo = WaterConsumptionRepository(session)
        service = WaterConsumptionService(water_repo)

        test_datetime = datetime(2024, 8, 20, 14, 30, 0)
        consumption_data = {
            "user_id": "service-test-user",
            "consumed_at": test_datetime,  # Already a datetime object
            "quantity": 500.0,
        }

        created_consumption = await service.create_water_consumption(consumption_data)
        await session.commit()

        # Check date and time components (timezone handling may vary)
        assert created_consumption.consumed_at.date() == test_datetime.date()
        assert created_consumption.consumed_at.hour >= 14  # Should be around 2 PM, allowing for timezone conversion

    async def test_create_water_consumption_invalid_datetime_string(self, session, seed_db):
        """Test creating water consumption with invalid datetime string."""
        water_repo = WaterConsumptionRepository(session)
        service = WaterConsumptionService(water_repo)

        consumption_data = {
            "user_id": "service-test-user",
            "consumed_at": "invalid-datetime-format",  # Invalid datetime
            "quantity": 250.0,
        }

        with pytest.raises(ValueError, match="Invalid datetime format"):
            await service.create_water_consumption(consumption_data)

    async def test_get_water_consumption_by_id(self, session, seed_db):
        """Test getting water consumption by ID."""
        water_repo = WaterConsumptionRepository(session)
        service = WaterConsumptionService(water_repo)

        # Create a test consumption first
        consumption_data = {
            "user_id": "test-get-user",
            "consumed_at": datetime.now(),
            "quantity": 300.0,
        }
        test_consumption = await service.create_water_consumption(consumption_data)
        await session.commit()

        fetched_consumption = await service.get_water_consumption_by_id(test_consumption.id_)
        assert fetched_consumption is not None
        assert fetched_consumption.id_ == test_consumption.id_
        assert fetched_consumption.user_id == test_consumption.user_id

    async def test_get_water_consumption_by_id_not_found(self, session, seed_db):
        """Test getting non-existent water consumption."""
        water_repo = WaterConsumptionRepository(session)
        service = WaterConsumptionService(water_repo)

        fake_id = uuid4()
        fetched_consumption = await service.get_water_consumption_by_id(fake_id)
        assert fetched_consumption is None

    async def test_list_water_consumption_by_user(self, session, seed_db):
        """Test listing water consumption for a user with pagination."""
        water_repo = WaterConsumptionRepository(session)
        service = WaterConsumptionService(water_repo)

        # Create a test consumption first
        consumption_data = {
            "user_id": "test-list-user",
            "consumed_at": datetime.now(),
            "quantity": 250.0,
        }
        test_consumption = await service.create_water_consumption(consumption_data)
        await session.commit()

        consumptions = await service.list_water_consumption_by_user(user_id=test_consumption.user_id, limit=10)

        assert len(consumptions) >= 1
        assert any(c.id_ == test_consumption.id_ for c in consumptions)

    async def test_list_water_consumption_by_user_and_date_range(self, session, seed_db):
        """Test listing water consumption by user and date range."""
        water_repo = WaterConsumptionRepository(session)
        service = WaterConsumptionService(water_repo)

        # Create test consumption for date range testing
        today = date.today()
        yesterday = today - timedelta(days=1)

        consumption_data = {
            "user_id": "range-test-user",
            "consumed_at": datetime.combine(yesterday, datetime.min.time()) + timedelta(hours=10),
            "quantity": 300.0,
        }
        await service.create_water_consumption(consumption_data)
        await session.commit()

        # List consumption in range
        consumptions = await service.list_water_consumption_by_user_and_date_range(
            user_id="range-test-user",
            start_date=yesterday,
            end_date=today,
        )

        assert len(consumptions) >= 1
        assert any(c.quantity == 300.0 for c in consumptions)

    async def test_get_total_water_consumption_by_user_and_date(self, session, seed_db):
        """Test getting total water consumption for a user on a specific date."""
        water_repo = WaterConsumptionRepository(session)
        service = WaterConsumptionService(water_repo)

        test_date = date.today()
        user_id = "total-test-user"

        # Create multiple consumption entries for the same date
        consumption_data_1 = {
            "user_id": user_id,
            "consumed_at": datetime.combine(test_date, datetime.min.time()) + timedelta(hours=8),
            "quantity": 250.0,
        }
        consumption_data_2 = {
            "user_id": user_id,
            "consumed_at": datetime.combine(test_date, datetime.min.time()) + timedelta(hours=14),
            "quantity": 350.0,
        }

        await service.create_water_consumption(consumption_data_1)
        await service.create_water_consumption(consumption_data_2)
        await session.commit()

        total = await service.get_total_water_consumption_by_user_and_date(user_id, test_date)
        assert total == 600.0  # 250 + 350

    async def test_update_water_consumption_with_datetime_string(self, session, seed_db):
        """Test updating water consumption with datetime string conversion."""
        water_repo = WaterConsumptionRepository(session)
        service = WaterConsumptionService(water_repo)

        # Create a test consumption first
        consumption_data = {
            "user_id": "test-update-user",
            "consumed_at": datetime.now(),
            "quantity": 200.0,
        }
        test_consumption = await service.create_water_consumption(consumption_data)
        await session.commit()

        update_data = {
            "quantity": 400.0,
            "consumed_at": "2024-09-01T15:30:00",  # ISO datetime string
        }

        updated_consumption = await service.update_water_consumption(test_consumption.id_, update_data)
        await session.commit()

        assert updated_consumption is not None
        assert updated_consumption.quantity == 400.0
        assert updated_consumption.consumed_at.date() == date(2024, 9, 1)

    async def test_update_water_consumption_invalid_datetime_string(self, session, seed_db):
        """Test updating water consumption with invalid datetime string."""
        water_repo = WaterConsumptionRepository(session)
        service = WaterConsumptionService(water_repo)

        # Create a test consumption first
        consumption_data = {
            "user_id": "test-invalid-user",
            "consumed_at": datetime.now(),
            "quantity": 200.0,
        }
        test_consumption = await service.create_water_consumption(consumption_data)
        await session.commit()

        update_data = {
            "consumed_at": "invalid-datetime-format",
        }

        with pytest.raises(ValueError, match="Invalid datetime format"):
            await service.update_water_consumption(test_consumption.id_, update_data)

    async def test_update_water_consumption_not_found(self, session, seed_db):
        """Test updating non-existent water consumption."""
        water_repo = WaterConsumptionRepository(session)
        service = WaterConsumptionService(water_repo)

        fake_id = uuid4()
        update_data = {"quantity": 500.0}

        updated_consumption = await service.update_water_consumption(fake_id, update_data)
        assert updated_consumption is None

    async def test_delete_water_consumption(self, session, seed_db):
        """Test deleting water consumption."""
        water_repo = WaterConsumptionRepository(session)
        service = WaterConsumptionService(water_repo)

        # Create consumption to delete
        consumption_data = {
            "user_id": "delete-test-user",
            "consumed_at": datetime.now(),
            "quantity": 200.0,
        }
        created_consumption = await service.create_water_consumption(consumption_data)
        await session.commit()

        # Delete the consumption
        deleted = await service.delete_water_consumption(created_consumption.id_)
        await session.commit()

        assert deleted is True

        # Verify deletion
        fetched_consumption = await service.get_water_consumption_by_id(created_consumption.id_)
        assert fetched_consumption is None

    async def test_delete_water_consumption_not_found(self, session, seed_db):
        """Test deleting non-existent water consumption."""
        water_repo = WaterConsumptionRepository(session)
        service = WaterConsumptionService(water_repo)

        fake_id = uuid4()
        deleted = await service.delete_water_consumption(fake_id)
        assert deleted is False
