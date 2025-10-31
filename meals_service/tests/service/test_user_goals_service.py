from uuid import uuid4

import pytest

from meals.domain.models import DomainUserGoals
from meals.repository.repositories import UserGoalsRepository
from meals.service.services import UserGoalsService


@pytest.mark.asyncio
class TestUserGoalsService:
    async def test_create_user_goals(self, session, seed_db):
        """Test creating user goals through the service."""
        goals_repo = UserGoalsRepository(session)
        service = UserGoalsService(goals_repo)

        goals_data = {
            "user_id": "service-test-user",
            "daily_calorie_goal": 2200.0,
            "daily_protein_goal": 150.0,
            "daily_carbs_goal": 220.0,
            "daily_fat_goal": 80.0,
            "daily_water_goal": 2500.0,
        }

        created_goals = await service.create_user_goals(goals_data)
        await session.commit()

        assert isinstance(created_goals, DomainUserGoals)
        assert created_goals.user_id == goals_data["user_id"]
        assert created_goals.daily_calorie_goal == goals_data["daily_calorie_goal"]
        assert created_goals.daily_protein_goal == goals_data["daily_protein_goal"]

        # Verify in database
        fetched_goals = await service.get_user_goals_by_id(created_goals.id_)
        assert fetched_goals is not None
        assert fetched_goals.user_id == goals_data["user_id"]

    async def test_get_user_goals_by_id(self, session, seed_db):
        """Test getting user goals by ID."""
        goals_repo = UserGoalsRepository(session)
        service = UserGoalsService(goals_repo)
        test_goals = seed_db["user_goals"]

        fetched_goals = await service.get_user_goals_by_id(test_goals.id_)
        assert fetched_goals is not None
        assert fetched_goals.id_ == test_goals.id_
        assert fetched_goals.user_id == test_goals.user_id

    async def test_get_user_goals_by_id_not_found(self, session, seed_db):
        """Test getting non-existent user goals."""
        goals_repo = UserGoalsRepository(session)
        service = UserGoalsService(goals_repo)

        fake_id = uuid4()
        fetched_goals = await service.get_user_goals_by_id(fake_id)
        assert fetched_goals is None

    async def test_get_user_goals_by_user_id(self, session, seed_db):
        """Test getting user goals by user ID."""
        goals_repo = UserGoalsRepository(session)
        service = UserGoalsService(goals_repo)
        test_goals = seed_db["user_goals"]

        fetched_goals = await service.get_user_goals_by_user_id(test_goals.user_id)
        assert fetched_goals is not None
        assert fetched_goals.user_id == test_goals.user_id
        assert fetched_goals.id_ == test_goals.id_

    async def test_get_user_goals_by_user_id_not_found(self, session, seed_db):
        """Test getting non-existent user goals by user ID."""
        goals_repo = UserGoalsRepository(session)
        service = UserGoalsService(goals_repo)

        fetched_goals = await service.get_user_goals_by_user_id("non-existent-user")
        assert fetched_goals is None

    async def test_update_user_goals(self, session, seed_db):
        """Test updating user goals by ID."""
        goals_repo = UserGoalsRepository(session)
        service = UserGoalsService(goals_repo)
        test_goals = seed_db["user_goals"]

        update_data = {
            "daily_calorie_goal": 2500.0,
            "daily_protein_goal": 180.0,
        }

        updated_goals = await service.update_user_goals(test_goals.id_, update_data)
        await session.commit()

        assert updated_goals is not None
        assert updated_goals.daily_calorie_goal == 2500.0
        assert updated_goals.daily_protein_goal == 180.0

    async def test_update_user_goals_not_found(self, session, seed_db):
        """Test updating non-existent user goals."""
        goals_repo = UserGoalsRepository(session)
        service = UserGoalsService(goals_repo)

        fake_id = uuid4()
        update_data = {"daily_calorie_goal": 2500.0}

        updated_goals = await service.update_user_goals(fake_id, update_data)
        assert updated_goals is None

    async def test_update_user_goals_by_user_id(self, session, seed_db):
        """Test updating user goals by user ID."""
        goals_repo = UserGoalsRepository(session)
        service = UserGoalsService(goals_repo)
        test_goals = seed_db["user_goals"]

        update_data = {
            "daily_water_goal": 3000.0,
            "daily_fat_goal": 100.0,
        }

        updated_goals = await service.update_user_goals_by_user_id(test_goals.user_id, update_data)
        await session.commit()

        assert updated_goals is not None
        assert updated_goals.daily_water_goal == 3000.0
        assert updated_goals.daily_fat_goal == 100.0

    async def test_update_user_goals_by_user_id_not_found(self, session, seed_db):
        """Test updating non-existent user goals by user ID."""
        goals_repo = UserGoalsRepository(session)
        service = UserGoalsService(goals_repo)

        update_data = {"daily_calorie_goal": 2500.0}
        updated_goals = await service.update_user_goals_by_user_id("non-existent-user", update_data)
        assert updated_goals is None

    async def test_upsert_user_goals_create(self, session, seed_db):
        """Test upsert creating new user goals."""
        goals_repo = UserGoalsRepository(session)
        service = UserGoalsService(goals_repo)

        user_id = "new-upsert-user"
        goals_data = {
            "daily_calorie_goal": 1800.0,
            "daily_protein_goal": 120.0,
            "daily_carbs_goal": 180.0,
            "daily_fat_goal": 60.0,
            "daily_water_goal": 2000.0,
        }

        upserted_goals = await service.upsert_user_goals(user_id, goals_data)
        await session.commit()

        assert upserted_goals is not None
        assert upserted_goals.user_id == user_id
        assert upserted_goals.daily_calorie_goal == 1800.0
        assert upserted_goals.daily_protein_goal == 120.0

        # Verify it was created (not updated)
        assert upserted_goals.daily_carbs_goal == 180.0

    async def test_upsert_user_goals_update(self, session, seed_db):
        """Test upsert updating existing user goals."""
        goals_repo = UserGoalsRepository(session)
        service = UserGoalsService(goals_repo)
        test_goals = seed_db["user_goals"]

        goals_data = {
            "daily_calorie_goal": 2800.0,
            "daily_protein_goal": 200.0,
            "daily_carbs_goal": 300.0,
            "daily_fat_goal": 120.0,
            "daily_water_goal": 3500.0,
        }

        upserted_goals = await service.upsert_user_goals(test_goals.user_id, goals_data)
        await session.commit()

        assert upserted_goals is not None
        assert upserted_goals.id_ == test_goals.id_  # Same record updated
        assert upserted_goals.daily_calorie_goal == 2800.0
        assert upserted_goals.daily_protein_goal == 200.0

    async def test_delete_user_goals(self, session, seed_db):
        """Test deleting user goals."""
        goals_repo = UserGoalsRepository(session)
        service = UserGoalsService(goals_repo)

        # Create goals to delete
        goals_data = {
            "user_id": "delete-test-user",
            "daily_calorie_goal": 2000.0,
            "daily_protein_goal": 100.0,
            "daily_carbs_goal": 250.0,
            "daily_fat_goal": 70.0,
            "daily_water_goal": 2000.0,
        }
        created_goals = await service.create_user_goals(goals_data)
        await session.commit()

        # Delete the goals
        deleted = await service.delete_user_goals(created_goals.id_)
        await session.commit()

        assert deleted is True

        # Verify deletion
        fetched_goals = await service.get_user_goals_by_id(created_goals.id_)
        assert fetched_goals is None

    async def test_delete_user_goals_not_found(self, session, seed_db):
        """Test deleting non-existent user goals."""
        goals_repo = UserGoalsRepository(session)
        service = UserGoalsService(goals_repo)

        fake_id = uuid4()
        deleted = await service.delete_user_goals(fake_id)
        assert deleted is False

    async def test_user_isolation(self, session, seed_db):
        """Test that user goals are properly isolated by user_id."""
        goals_repo = UserGoalsRepository(session)
        service = UserGoalsService(goals_repo)

        # Create goals for user A
        goals_data_a = {
            "user_id": "isolation-user-a",
            "daily_calorie_goal": 2000.0,
            "daily_protein_goal": 100.0,
        }
        goals_a = await service.create_user_goals(goals_data_a)

        # Create goals for user B
        goals_data_b = {
            "user_id": "isolation-user-b",
            "daily_calorie_goal": 2500.0,
            "daily_protein_goal": 150.0,
        }
        goals_b = await service.create_user_goals(goals_data_b)
        await session.commit()

        # Verify each user can only see their own goals
        fetched_goals_a = await service.get_user_goals_by_user_id("isolation-user-a")
        fetched_goals_b = await service.get_user_goals_by_user_id("isolation-user-b")

        assert fetched_goals_a is not None
        assert fetched_goals_b is not None
        assert fetched_goals_a.id_ == goals_a.id_
        assert fetched_goals_b.id_ == goals_b.id_
        assert fetched_goals_a.daily_calorie_goal == 2000.0
        assert fetched_goals_b.daily_calorie_goal == 2500.0
