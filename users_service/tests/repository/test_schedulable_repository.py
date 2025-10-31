import uuid
from typing import Any, Dict, Optional, Sequence

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from users.repository.models import (
    SchedulableModel,
    ServiceEnum,
    ServiceModel,
    UserModel,
)
from users.repository.repositories import (
    SchedulableRepository,
    ServiceRepository,
    UserRepository,
)
from users.repository.uow import UnitOfWork


@pytest.mark.asyncio
class TestSchedulableRepository:
    async def test_create_and_get_schedulable(self, session: AsyncSession):
        """Test creating a schedulable and retrieving it using a direct session."""
        user_repo = UserRepository(session)
        service_repo = ServiceRepository(session)
        sched_repo = SchedulableRepository(session)

        # 1. Create User
        test_user = await user_repo.create_user({"supabase_id": f"sched_user_{uuid.uuid4()}"})
        # 2. Create Service
        test_service = await service_repo.create_service(
            {"name": ServiceEnum.shadow_boxing, "description": "Shadow Boxing routines"}
        )
        await session.commit()  # Commit user and service

        assert test_user and test_user.id_ is not None
        assert test_service and test_service.id_ is not None

        entity_uuid = uuid.uuid4()
        schedulable_data = {
            "name": "Morning Shadow Boxing",
            "description": "15 minutes focus on footwork.",
            "entity_id": entity_uuid,
            "completed": False,
            "user_id": test_user.id_,
            "service_id": test_service.id_,  # Pass UUID directly
        }

        created_schedulable = await sched_repo.create_schedulable(schedulable_data)
        await session.commit()  # Commit schedulable

        assert created_schedulable is not None
        assert created_schedulable.id_ is not None
        assert created_schedulable.name == "Morning Shadow Boxing"
        assert created_schedulable.user_id == test_user.id_
        assert created_schedulable.service_id == test_service.id_

        fetched_schedulable = await sched_repo.get_schedulable_by_id(created_schedulable.id_)
        assert fetched_schedulable is not None
        assert fetched_schedulable.id_ == created_schedulable.id_
        assert fetched_schedulable.name == "Morning Shadow Boxing"
        assert fetched_schedulable.service is not None
        assert fetched_schedulable.service.name == ServiceEnum.shadow_boxing
        assert fetched_schedulable.user is not None
        assert fetched_schedulable.user.id_ == test_user.id_

    async def test_list_schedulables_by_user(self, seed_data: Dict[str, Any], uow: UnitOfWork):
        """Test listing schedulables for a user, ensuring seeded schedulable is present."""
        user1: Optional[UserModel] = seed_data.get("user1_coach")
        schedulable1_seeded: Optional[SchedulableModel] = seed_data.get("schedulable1")

        assert user1 is not None, "user1_coach not found in seed_data"
        assert user1.id_ is not None
        assert schedulable1_seeded is not None, "Schedulable1 not found in seed_data"
        assert schedulable1_seeded.user_id == user1.id_, "Seeded schedulable does not belong to user1_coach"

        async with uow:
            repo = SchedulableRepository(uow.session)
            user_schedulables = await repo.get_schedulables_by_user_id(user1.id_)

        assert user_schedulables is not None
        assert len(user_schedulables) >= 1

        found_seeded_schedulable = False
        for sched in user_schedulables:
            if sched.id_ == schedulable1_seeded.id_:
                assert sched.name == schedulable1_seeded.name
                found_seeded_schedulable = True
                break
        assert (
            found_seeded_schedulable
        ), f"Seeded schedulable (ID: {schedulable1_seeded.id_}) for user1_coach not found in list."

    async def test_update_schedulable_completion(self, seed_data: Dict[str, Any], uow: UnitOfWork):
        """Test updating a schedulable's completion status."""
        schedulable_to_update: Optional[SchedulableModel] = seed_data.get("schedulable1")
        assert schedulable_to_update is not None, "Schedulable1 not found in seed_data for update test"
        assert schedulable_to_update.id_ is not None
        assert schedulable_to_update.completed is False, "Seeded schedulable should initially be incomplete."

        schedulable_id = schedulable_to_update.id_

        async with uow:
            repo = SchedulableRepository(uow.session)
            updated_sched = await repo.update_schedulable(schedulable_id, {"completed": True})
            # UoW commits here

        assert updated_sched is not None
        assert updated_sched.completed is True

        async with UnitOfWork(session_factory=uow.session_factory) as read_uow:
            repo_read = SchedulableRepository(read_uow.session)
            refetched_sched = await repo_read.get_schedulable_by_id(schedulable_id)
            assert refetched_sched is not None
            assert refetched_sched.completed is True

    async def test_delete_schedulable(self, session: AsyncSession, uow: UnitOfWork):
        """Test deleting a schedulable."""
        user_repo = UserRepository(session)
        service_repo = ServiceRepository(session)
        sched_repo_setup = SchedulableRepository(session)

        test_user = await user_repo.create_user({"supabase_id": f"del_sched_user_{uuid.uuid4()}"})
        test_service = await service_repo.create_service(
            {"name": ServiceEnum.programs, "description": "Programs for deletion test"}
        )
        await session.commit()
        assert test_user and test_user.id_
        assert test_service and test_service.id_

        sched_data = {
            "name": "Schedulable to delete",
            "user_id": test_user.id_,
            "service_id": test_service.id_,
            "entity_id": uuid.uuid4(),
        }
        sched_to_delete = await sched_repo_setup.create_schedulable(sched_data)
        await session.commit()
        assert sched_to_delete and sched_to_delete.id_
        schedulable_id_to_delete = sched_to_delete.id_

        async with uow:
            sched_repo_delete = SchedulableRepository(uow.session)
            delete_result = await sched_repo_delete.delete_schedulable(schedulable_id_to_delete)
            assert delete_result is True
            # UoW commits deletion

        async with UnitOfWork(session_factory=uow.session_factory) as verify_uow:
            sched_repo_verify = SchedulableRepository(verify_uow.session)
            fetched_sched = await sched_repo_verify.get_schedulable_by_id(schedulable_id_to_delete)
            assert fetched_sched is None
