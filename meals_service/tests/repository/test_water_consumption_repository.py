from datetime import date, datetime, timedelta
from uuid import UUID

import pytest

from meals.repository.repositories.water_consumption_repository import (
    WaterConsumptionRepository,
)


@pytest.mark.asyncio
class TestWaterConsumptionRepository:

    async def test_create_and_get_water_consumption(self, seed_db, session):
        """Test creating new water consumption record and retrieving it."""
        consumption_data = {
            "user_id": "test-user-new",
            "quantity": 250.0,
            "consumed_at": datetime.now(),
        }

        water_repo = WaterConsumptionRepository(session)
        created_record = await water_repo.create_water_consumption(consumption_data)

        assert created_record is not None
        assert created_record.user_id == "test-user-new"
        assert created_record.quantity == 250.0
        assert created_record.consumed_at is not None

        # Test retrieval by ID
        fetched_record = await water_repo.get_water_consumption_by_id(created_record.id_)
        assert fetched_record is not None
        assert fetched_record.user_id == "test-user-new"
        assert fetched_record.quantity == 250.0

    async def test_get_nonexistent_water_consumption(self, seed_db, session):
        """Test getting water consumption record that doesn't exist."""
        water_repo = WaterConsumptionRepository(session)
        fake_uuid = UUID("00000000-0000-0000-0000-000000000000")

        result = await water_repo.get_water_consumption_by_id(fake_uuid)
        assert result is None

    async def test_list_water_consumption_by_user(self, seed_db, session):
        """Test listing water consumption records for a user."""
        water_repo = WaterConsumptionRepository(session)

        # Create additional water records for testing
        for i in range(3):
            consumption_data = {
                "user_id": "test-user-123",
                "quantity": 200.0 + (i * 50),
                "consumed_at": datetime.now() + timedelta(minutes=i * 30),
            }
            await water_repo.create_water_consumption(consumption_data)

        # List all records for user
        user_records = await water_repo.list_water_consumption_by_user("test-user-123")
        assert len(user_records) >= 5  # 2 seeded + 3 new

        # Test pagination
        limited_records = await water_repo.list_water_consumption_by_user("test-user-123", limit=3)
        assert len(limited_records) == 3

        # Test offset
        offset_records = await water_repo.list_water_consumption_by_user("test-user-123", limit=2, offset=2)
        assert len(offset_records) >= 2

    async def test_list_water_consumption_by_user_and_date_range(self, seed_db, session):
        """Test listing water consumption for a user within a date range."""
        water_repo = WaterConsumptionRepository(session)

        # Create records across different dates
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        # Yesterday's records
        yesterday_data = {
            "user_id": "test-user-date-range",
            "quantity": 300.0,
            "consumed_at": datetime.combine(yesterday, datetime.min.time()) + timedelta(hours=10),
        }
        await water_repo.create_water_consumption(yesterday_data)

        # Today's records
        today_data1 = {
            "user_id": "test-user-date-range",
            "quantity": 400.0,
            "consumed_at": datetime.combine(today, datetime.min.time()) + timedelta(hours=8),
        }
        await water_repo.create_water_consumption(today_data1)

        today_data2 = {
            "user_id": "test-user-date-range",
            "quantity": 350.0,
            "consumed_at": datetime.combine(today, datetime.min.time()) + timedelta(hours=14),
        }
        await water_repo.create_water_consumption(today_data2)

        # Tomorrow's records
        tomorrow_data = {
            "user_id": "test-user-date-range",
            "quantity": 250.0,
            "consumed_at": datetime.combine(tomorrow, datetime.min.time()) + timedelta(hours=9),
        }
        await water_repo.create_water_consumption(tomorrow_data)

        # Test date range query
        records_in_range = await water_repo.list_water_consumption_by_user_and_date_range(
            user_id="test-user-date-range",
            start_date=yesterday,
            end_date=today,
        )

        # Should include yesterday's and today's records
        assert len(records_in_range) == 3
        quantities = [record.quantity for record in records_in_range]
        assert 300.0 in quantities  # Yesterday
        assert 400.0 in quantities  # Today morning
        assert 350.0 in quantities  # Today afternoon

    async def test_list_water_consumption_by_user_and_specific_date(self, seed_db, session):
        """Test listing water consumption for a user on a specific date."""
        water_repo = WaterConsumptionRepository(session)

        target_date = date.today()

        # Create multiple records for the same date
        morning_data = {
            "user_id": "test-user-specific-date",
            "quantity": 500.0,
            "consumed_at": datetime.combine(target_date, datetime.min.time()) + timedelta(hours=8),
        }
        await water_repo.create_water_consumption(morning_data)

        noon_data = {
            "user_id": "test-user-specific-date",
            "quantity": 300.0,
            "consumed_at": datetime.combine(target_date, datetime.min.time()) + timedelta(hours=12),
        }
        await water_repo.create_water_consumption(noon_data)

        evening_data = {
            "user_id": "test-user-specific-date",
            "quantity": 200.0,
            "consumed_at": datetime.combine(target_date, datetime.min.time()) + timedelta(hours=19),
        }
        await water_repo.create_water_consumption(evening_data)

        # Get records for specific date
        daily_records = await water_repo.list_water_consumption_by_user_and_date(
            user_id="test-user-specific-date",
            target_date=target_date,
        )

        assert len(daily_records) == 3
        # Should be ordered by consumed_at (ascending)
        assert daily_records[0].quantity == 500.0  # Morning
        assert daily_records[1].quantity == 300.0  # Noon
        assert daily_records[2].quantity == 200.0  # Evening

    async def test_get_total_water_consumption_by_user_and_date(self, seed_db, session):
        """Test aggregating total water consumption for a user on a specific date."""
        water_repo = WaterConsumptionRepository(session)

        target_date = date.today()

        # Create records for the target date
        consumption_amounts = [250.0, 300.0, 200.0, 150.0]
        for amount in consumption_amounts:
            consumption_data = {
                "user_id": "test-user-total",
                "quantity": amount,
                "consumed_at": datetime.combine(target_date, datetime.min.time()) + timedelta(hours=8),
            }
            await water_repo.create_water_consumption(consumption_data)

        # Also create a record for a different date (should not be included)
        different_date_data = {
            "user_id": "test-user-total",
            "quantity": 500.0,
            "consumed_at": datetime.combine(target_date - timedelta(days=1), datetime.min.time()),
        }
        await water_repo.create_water_consumption(different_date_data)

        # Get total for target date
        total = await water_repo.get_total_water_consumption_by_user_and_date(
            user_id="test-user-total",
            target_date=target_date,
        )

        expected_total = sum(consumption_amounts)
        assert total == expected_total

    async def test_get_total_water_consumption_no_records(self, seed_db, session):
        """Test getting total water consumption when no records exist."""
        water_repo = WaterConsumptionRepository(session)

        total = await water_repo.get_total_water_consumption_by_user_and_date(
            user_id="nonexistent-user",
            target_date=date.today(),
        )

        assert total == 0.0

    async def test_update_water_consumption(self, seed_db, session):
        """Test updating water consumption record."""
        water_repo = WaterConsumptionRepository(session)
        water_record = seed_db["water1"]

        update_data = {
            "quantity": 600.0,
            "consumed_at": datetime.now() + timedelta(hours=1),
        }

        updated_record = await water_repo.update_water_consumption(water_record.id_, update_data)

        assert updated_record is not None
        assert updated_record.quantity == 600.0
        assert updated_record.user_id == "test-user-123"  # Should remain unchanged

    async def test_update_nonexistent_water_consumption(self, seed_db, session):
        """Test updating water consumption record that doesn't exist."""
        water_repo = WaterConsumptionRepository(session)
        fake_uuid = UUID("00000000-0000-0000-0000-000000000000")

        update_data = {"quantity": 500.0}
        result = await water_repo.update_water_consumption(fake_uuid, update_data)

        assert result is None

    async def test_delete_water_consumption(self, seed_db, session):
        """Test deleting water consumption record."""
        water_repo = WaterConsumptionRepository(session)

        # Create a record to delete
        consumption_data = {
            "user_id": "test-user-delete",
            "quantity": 400.0,
            "consumed_at": datetime.now(),
        }
        created_record = await water_repo.create_water_consumption(consumption_data)

        # Delete the record
        result = await water_repo.delete_water_consumption(created_record.id_)
        assert result is True

        # Verify it's gone
        fetched_record = await water_repo.get_water_consumption_by_id(created_record.id_)
        assert fetched_record is None

    async def test_delete_nonexistent_water_consumption(self, seed_db, session):
        """Test deleting water consumption record that doesn't exist."""
        water_repo = WaterConsumptionRepository(session)
        fake_uuid = UUID("00000000-0000-0000-0000-000000000000")

        result = await water_repo.delete_water_consumption(fake_uuid)
        assert result is False

    async def test_delete_water_consumption_by_user_and_date(self, seed_db, session):
        """Test deleting all water consumption records for a user on a specific date."""
        water_repo = WaterConsumptionRepository(session)

        target_date = date.today()

        # Create multiple records for the target date
        records_to_create = 4
        for i in range(records_to_create):
            consumption_data = {
                "user_id": "test-user-bulk-delete",
                "quantity": 200.0 + (i * 50),
                "consumed_at": datetime.combine(target_date, datetime.min.time()) + timedelta(hours=8 + i),
            }
            await water_repo.create_water_consumption(consumption_data)

        # Also create a record for a different date (should not be deleted)
        different_date_data = {
            "user_id": "test-user-bulk-delete",
            "quantity": 500.0,
            "consumed_at": datetime.combine(target_date - timedelta(days=1), datetime.min.time()),
        }
        await water_repo.create_water_consumption(different_date_data)

        # Delete records for target date
        deleted_count = await water_repo.delete_water_consumption_by_user_and_date(
            user_id="test-user-bulk-delete",
            target_date=target_date,
        )

        assert deleted_count == records_to_create

        # Verify records for target date are gone
        remaining_records = await water_repo.list_water_consumption_by_user_and_date(
            user_id="test-user-bulk-delete",
            target_date=target_date,
        )
        assert len(remaining_records) == 0

        # Verify record for different date still exists
        different_date_records = await water_repo.list_water_consumption_by_user_and_date(
            user_id="test-user-bulk-delete",
            target_date=target_date - timedelta(days=1),
        )
        assert len(different_date_records) == 1

    async def test_delete_water_consumption_by_user_and_date_no_records(self, seed_db, session):
        """Test deleting water consumption when no records exist for the date."""
        water_repo = WaterConsumptionRepository(session)

        deleted_count = await water_repo.delete_water_consumption_by_user_and_date(
            user_id="nonexistent-user",
            target_date=date.today(),
        )

        assert deleted_count == 0

    async def test_water_consumption_ordering(self, seed_db, session):
        """Test that water consumption records are properly ordered."""
        water_repo = WaterConsumptionRepository(session)

        # Create records with specific times to test ordering
        times = [
            datetime.now() - timedelta(hours=3),
            datetime.now() - timedelta(hours=1),
            datetime.now() - timedelta(hours=2),
        ]

        for i, time in enumerate(times):
            consumption_data = {
                "user_id": "test-user-ordering",
                "quantity": 100.0 + (i * 50),
                "consumed_at": time,
            }
            await water_repo.create_water_consumption(consumption_data)

        # Get records (should be ordered by consumed_at DESC)
        records = await water_repo.list_water_consumption_by_user("test-user-ordering")

        assert len(records) == 3
        # Should be in descending order (most recent first)
        assert records[0].consumed_at > records[1].consumed_at
        assert records[1].consumed_at > records[2].consumed_at

    async def test_water_consumption_different_users(self, seed_db, session):
        """Test that water consumption records are properly isolated by user."""
        water_repo = WaterConsumptionRepository(session)

        # Create records for different users
        users = ["user-a", "user-b", "user-c"]
        for user in users:
            for i in range(2):
                consumption_data = {
                    "user_id": user,
                    "quantity": 200.0,
                    "consumed_at": datetime.now(),
                }
                await water_repo.create_water_consumption(consumption_data)

        # Verify each user only sees their own records
        for user in users:
            user_records = await water_repo.list_water_consumption_by_user(user)
            assert len(user_records) == 2
            for record in user_records:
                assert record.user_id == user
