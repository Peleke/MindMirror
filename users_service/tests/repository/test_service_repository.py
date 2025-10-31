import uuid
from typing import Any, Dict, Optional, Sequence

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from users.repository.models import ServiceEnum, ServiceModel
from users.repository.repositories import ServiceRepository
from users.repository.uow import UnitOfWork


@pytest.mark.asyncio
class TestServiceRepository:
    async def test_create_and_get_service(self, session: AsyncSession):
        """Test creating a service and retrieving it by ID and name using a direct session."""
        repo = ServiceRepository(session)
        service_name = ServiceEnum.fitness_db
        service_desc = "Fitness Database Service - Direct Session Test"
        service_data = {"name": service_name, "description": service_desc}

        created_service = await repo.create_service(service_data)
        await session.commit()

        assert created_service.id_ is not None
        assert created_service.name == service_name
        assert created_service.description == service_desc

        fetched_by_id = await repo.get_service_by_id(created_service.id_)
        fetched_by_name = await repo.get_service_by_name(service_name)

        assert fetched_by_id is not None
        assert fetched_by_id.id_ == created_service.id_
        assert fetched_by_name is not None
        assert fetched_by_name.name == service_name

    async def test_explicit_create_and_get_service_uow(self, uow: UnitOfWork):
        """Test creating a service and retrieving it using UoW."""
        service_name = ServiceEnum.programs
        service_desc = "Test Programs Service - UoW"
        service_data = {"name": service_name, "description": service_desc}
        created_service_id: Optional[uuid.UUID] = None

        async with uow:
            repo = ServiceRepository(uow.session)
            created_service = await repo.create_service(service_data)
            created_service_id = created_service.id_
            # UoW commits here

        assert created_service_id is not None

        async with UnitOfWork(session_factory=uow.session_factory) as read_uow:
            repo_read = ServiceRepository(read_uow.session)
            fetched_by_id = await repo_read.get_service_by_id(created_service_id)
            fetched_by_name = await repo_read.get_service_by_name(service_name)

        assert fetched_by_id is not None
        assert fetched_by_id.id_ == created_service_id
        assert fetched_by_id.name == service_name
        assert fetched_by_id.description == service_desc
        assert fetched_by_name is not None
        assert fetched_by_name.name == service_name

    async def test_list_services(self, seed_data: Dict[str, Any], uow: UnitOfWork):
        """Test listing all services, ensuring seeded services are present."""
        # seed_data ensures MEALS and PRACTICE services are created
        service_meals_from_seed: Optional[ServiceModel] = seed_data.get("service_meals")
        service_practice_from_seed: Optional[ServiceModel] = seed_data.get("service_practice")
        assert service_meals_from_seed is not None
        assert service_practice_from_seed is not None

        async with uow:
            repo = ServiceRepository(uow.session)
            services = await repo.list_services()

        assert services is not None
        assert len(services) >= 2

        service_names = [s.name for s in services]
        assert ServiceEnum.meals in service_names
        assert ServiceEnum.practice in service_names

    async def test_update_service(self, uow: UnitOfWork):
        """Test updating a service's description."""
        original_name = ServiceEnum.shadow_boxing
        original_desc = "Original Shadow Boxing Description"
        updated_desc = "Updated Shadow Boxing Description - More Intense!"
        service_id: Optional[uuid.UUID] = None

        async with uow:
            repo = ServiceRepository(uow.session)
            # Create a service to update
            service_to_update = await repo.create_service({"name": original_name, "description": original_desc})
            service_id = service_to_update.id_
            # UoW commits creation

        assert service_id is not None

        async with UnitOfWork(session_factory=uow.session_factory) as update_uow:
            repo_update = ServiceRepository(update_uow.session)
            updated_service = await repo_update.update_service(service_id, {"description": updated_desc})
            assert updated_service is not None
            assert updated_service.description == updated_desc
            assert updated_service.name == original_name  # Name should not change
            # UoW commits update

        async with UnitOfWork(session_factory=uow.session_factory) as read_uow:
            repo_read = ServiceRepository(read_uow.session)
            refetched_service = await repo_read.get_service_by_id(service_id)
            assert refetched_service is not None
            assert refetched_service.description == updated_desc

    async def test_delete_service(self, uow: UnitOfWork):
        """Test deleting a service."""
        service_to_delete_name = ServiceEnum.fitness_db  # Choose one not used by other tests if possible
        service_id: Optional[uuid.UUID] = None

        async with uow:
            repo = ServiceRepository(uow.session)
            service = await repo.create_service({"name": service_to_delete_name, "description": "To be deleted"})
            service_id = service.id_
            # UoW commits creation

        assert service_id is not None

        async with UnitOfWork(session_factory=uow.session_factory) as delete_uow:
            repo_delete = ServiceRepository(delete_uow.session)
            delete_result = await repo_delete.delete_service(service_id)
            assert delete_result is True
            # UoW commits deletion

        async with UnitOfWork(session_factory=uow.session_factory) as read_uow:
            repo_read = ServiceRepository(read_uow.session)
            fetched_service = await repo_read.get_service_by_id(service_id)
            assert fetched_service is None
