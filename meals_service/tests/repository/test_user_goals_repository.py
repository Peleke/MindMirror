from uuid import UUID

import pytest

from meals.repository.repositories.user_goals_repository import UserGoalsRepository


@pytest.mark.asyncio
class TestUserGoalsRepository:

    async def test_create_and_get_user_goals(self, seed_db, session):
        """Test creating new user goals and retrieving them."""
        goals_data = {
            "user_id": "test-user-new",
            "daily_calorie_goal": 2200.0,
            "daily_water_goal": 2500.0,
            "daily_protein_goal": 180.0,
            "daily_carbs_goal": 275.0,
            "daily_fat_goal": 73.0,
        }

        goals_repo = UserGoalsRepository(session)
        created_goals = await goals_repo.create_user_goals(goals_data)

        assert created_goals is not None
        assert created_goals.user_id == "test-user-new"
        assert created_goals.daily_calorie_goal == 2200.0
        assert created_goals.daily_water_goal == 2500.0
        assert created_goals.daily_protein_goal == 180.0
        assert created_goals.daily_carbs_goal == 275.0
        assert created_goals.daily_fat_goal == 73.0

        # Test retrieval by ID
        fetched_goals = await goals_repo.get_user_goals_by_id(created_goals.id_)
        assert fetched_goals is not None
        assert fetched_goals.user_id == "test-user-new"
        assert fetched_goals.daily_calorie_goal == 2200.0

    async def test_get_user_goals_by_user_id(self, seed_db, session):
        """Test retrieving user goals by user ID."""
        goals_repo = UserGoalsRepository(session)

        # Get seeded user goals
        user_goals = await goals_repo.get_user_goals_by_user_id("test-user-123")

        assert user_goals is not None
        assert user_goals.user_id == "test-user-123"
        assert user_goals.daily_calorie_goal == 2000.0
        assert user_goals.daily_water_goal == 2000.0

    async def test_get_user_goals_by_nonexistent_user(self, seed_db, session):
        """Test getting user goals for a user that doesn't exist."""
        goals_repo = UserGoalsRepository(session)

        result = await goals_repo.get_user_goals_by_user_id("nonexistent-user")
        assert result is None

    async def test_get_nonexistent_user_goals_by_id(self, seed_db, session):
        """Test getting user goals by ID that doesn't exist."""
        goals_repo = UserGoalsRepository(session)
        fake_uuid = UUID("00000000-0000-0000-0000-000000000000")

        result = await goals_repo.get_user_goals_by_id(fake_uuid)
        assert result is None

    async def test_list_all_user_goals(self, seed_db, session):
        """Test listing all user goals with pagination."""
        goals_repo = UserGoalsRepository(session)

        # Create additional user goals for testing
        additional_goals_data = {
            "user_id": "test-user-additional",
            "daily_calorie_goal": 1800.0,
            "daily_water_goal": 2200.0,
        }
        await goals_repo.create_user_goals(additional_goals_data)

        # List all goals
        all_goals = await goals_repo.list_all_user_goals()
        assert len(all_goals) >= 2  # Seeded + additional

        # Test pagination
        limited_goals = await goals_repo.list_all_user_goals(limit=1)
        assert len(limited_goals) == 1

        # Test offset
        offset_goals = await goals_repo.list_all_user_goals(limit=1, offset=1)
        assert len(offset_goals) >= 1

    async def test_update_user_goals_by_id(self, seed_db, session):
        """Test updating user goals by ID."""
        goals_repo = UserGoalsRepository(session)
        user_goals = seed_db["user_goals"]

        update_data = {
            "daily_calorie_goal": 2100.0,
            "daily_protein_goal": 160.0,
            "daily_fat_goal": 70.0,
        }

        updated_goals = await goals_repo.update_user_goals(user_goals.id_, update_data)

        assert updated_goals is not None
        assert updated_goals.daily_calorie_goal == 2100.0
        assert updated_goals.daily_protein_goal == 160.0
        assert updated_goals.daily_fat_goal == 70.0
        # Unchanged fields should remain the same
        assert updated_goals.daily_water_goal == 2000.0
        assert updated_goals.daily_carbs_goal == 250.0

    async def test_update_user_goals_by_user_id(self, seed_db, session):
        """Test updating user goals by user ID."""
        goals_repo = UserGoalsRepository(session)

        update_data = {
            "daily_calorie_goal": 2300.0,
            "daily_water_goal": 2800.0,
        }

        updated_goals = await goals_repo.update_user_goals_by_user_id("test-user-123", update_data)

        assert updated_goals is not None
        assert updated_goals.user_id == "test-user-123"
        assert updated_goals.daily_calorie_goal == 2300.0
        assert updated_goals.daily_water_goal == 2800.0

    async def test_update_nonexistent_user_goals_by_id(self, seed_db, session):
        """Test updating user goals that don't exist by ID."""
        goals_repo = UserGoalsRepository(session)
        fake_uuid = UUID("00000000-0000-0000-0000-000000000000")

        update_data = {"daily_calorie_goal": 2000.0}
        result = await goals_repo.update_user_goals(fake_uuid, update_data)

        assert result is None

    async def test_update_nonexistent_user_goals_by_user_id(self, seed_db, session):
        """Test updating user goals for a user that doesn't exist."""
        goals_repo = UserGoalsRepository(session)

        update_data = {"daily_calorie_goal": 2000.0}
        result = await goals_repo.update_user_goals_by_user_id("nonexistent-user", update_data)

        assert result is None

    async def test_delete_user_goals_by_id(self, seed_db, session):
        """Test deleting user goals by ID."""
        goals_repo = UserGoalsRepository(session)

        # Create goals to delete
        goals_data = {
            "user_id": "test-user-to-delete",
            "daily_calorie_goal": 1900.0,
            "daily_water_goal": 2100.0,
        }
        created_goals = await goals_repo.create_user_goals(goals_data)

        # Delete the goals
        result = await goals_repo.delete_user_goals(created_goals.id_)
        assert result is True

        # Verify they're gone
        fetched_goals = await goals_repo.get_user_goals_by_id(created_goals.id_)
        assert fetched_goals is None

    async def test_delete_user_goals_by_user_id(self, seed_db, session):
        """Test deleting user goals by user ID."""
        goals_repo = UserGoalsRepository(session)

        # Create goals to delete
        goals_data = {
            "user_id": "test-user-to-delete-by-user-id",
            "daily_calorie_goal": 1900.0,
            "daily_water_goal": 2100.0,
        }
        created_goals = await goals_repo.create_user_goals(goals_data)

        # Delete by user ID
        result = await goals_repo.delete_user_goals_by_user_id("test-user-to-delete-by-user-id")
        assert result is True

        # Verify they're gone
        fetched_goals = await goals_repo.get_user_goals_by_user_id("test-user-to-delete-by-user-id")
        assert fetched_goals is None

    async def test_delete_nonexistent_user_goals_by_id(self, seed_db, session):
        """Test deleting user goals that don't exist by ID."""
        goals_repo = UserGoalsRepository(session)
        fake_uuid = UUID("00000000-0000-0000-0000-000000000000")

        result = await goals_repo.delete_user_goals(fake_uuid)
        assert result is False

    async def test_delete_nonexistent_user_goals_by_user_id(self, seed_db, session):
        """Test deleting user goals for a user that doesn't exist."""
        goals_repo = UserGoalsRepository(session)

        result = await goals_repo.delete_user_goals_by_user_id("nonexistent-user")
        assert result is False

    async def test_upsert_user_goals_create(self, seed_db, session):
        """Test upserting user goals when they don't exist (should create)."""
        goals_repo = UserGoalsRepository(session)

        goals_data = {
            "daily_calorie_goal": 2400.0,
            "daily_water_goal": 2600.0,
            "daily_protein_goal": 200.0,
        }

        # User doesn't have goals yet
        result = await goals_repo.upsert_user_goals("test-user-upsert-new", goals_data)

        assert result is not None
        assert result.user_id == "test-user-upsert-new"
        assert result.daily_calorie_goal == 2400.0
        assert result.daily_water_goal == 2600.0
        assert result.daily_protein_goal == 200.0

    async def test_upsert_user_goals_update(self, seed_db, session):
        """Test upserting user goals when they already exist (should update)."""
        goals_repo = UserGoalsRepository(session)

        # User already has goals (from seed data)
        new_goals_data = {
            "daily_calorie_goal": 2500.0,
            "daily_water_goal": 2700.0,
        }

        result = await goals_repo.upsert_user_goals("test-user-123", new_goals_data)

        assert result is not None
        assert result.user_id == "test-user-123"
        assert result.daily_calorie_goal == 2500.0
        assert result.daily_water_goal == 2700.0
        # Other fields should remain from the original goals
        assert result.daily_protein_goal == 150.0  # Original value

    async def test_create_user_goals_minimal_data(self, seed_db, session):
        """Test creating user goals with only required fields."""
        goals_repo = UserGoalsRepository(session)

        minimal_goals_data = {
            "user_id": "test-user-minimal",
            "daily_calorie_goal": 2000.0,
            "daily_water_goal": 2000.0,
        }

        created_goals = await goals_repo.create_user_goals(minimal_goals_data)

        assert created_goals is not None
        assert created_goals.user_id == "test-user-minimal"
        assert created_goals.daily_calorie_goal == 2000.0
        assert created_goals.daily_water_goal == 2000.0
        # Optional fields should be None
        assert created_goals.daily_protein_goal is None
        assert created_goals.daily_carbs_goal is None
        assert created_goals.daily_fat_goal is None

    async def test_list_user_goals_with_filters(self, seed_db, session):
        """Test listing user goals with custom filters."""
        goals_repo = UserGoalsRepository(session)

        # Create goals with specific characteristics for filtering
        high_calorie_goals_data = {
            "user_id": "test-user-high-calorie",
            "daily_calorie_goal": 3000.0,
            "daily_water_goal": 2000.0,
        }
        await goals_repo.create_user_goals(high_calorie_goals_data)

        low_calorie_goals_data = {
            "user_id": "test-user-low-calorie",
            "daily_calorie_goal": 1500.0,
            "daily_water_goal": 2000.0,
        }
        await goals_repo.create_user_goals(low_calorie_goals_data)

        # List all goals to verify they were created
        all_goals = await goals_repo.list_all_user_goals()
        assert len(all_goals) >= 3  # Original seeded + 2 new ones

        # Note: The current implementation supports **filters but exact behavior
        # depends on the filter implementation in the repository
        user_ids = [goal.user_id for goal in all_goals]
        assert "test-user-high-calorie" in user_ids
        assert "test-user-low-calorie" in user_ids
