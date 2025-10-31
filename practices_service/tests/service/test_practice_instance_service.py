from datetime import date
from uuid import uuid4

import pytest

from practices.repository.repositories import (
    PracticeInstanceRepository,
)
from practices.service.services import PracticeInstanceService


@pytest.mark.asyncio
class TestPracticeInstanceService:
    async def test_create_instance_from_template(self, uow, seed_db):
        instance_repo = PracticeInstanceRepository(uow.session)
        service = PracticeInstanceService(instance_repo)
        template = seed_db["practice_templates"][0]
        user_id = seed_db["client_user_one"].id
        instance_date = date.today()

        instance = await service.create_instance_from_template(
            template_id=template.id_, user_id=user_id, date=instance_date
        )

        assert instance is not None
        assert instance.user_id == user_id
        assert instance.template_id == template.id_
        assert instance.title == template.title

    async def test_create_standalone_instance(self, uow, seed_db):
        instance_repo = PracticeInstanceRepository(uow.session)
        service = PracticeInstanceService(instance_repo)
        user_id = seed_db["client_user_one"].id
        instance_data = {
            "user_id": user_id,
            "title": "Standalone Kayaking",
            "date": date.today(),
            "prescriptions": [{"name": "Endurance", "block": "workout"}],
        }

        instance = await service.create_standalone_instance(instance_data)

        assert instance is not None
        assert instance.title == "Standalone Kayaking"
        assert instance.user_id == user_id
        assert instance.template_id is None

    async def test_get_instance(self, uow, seed_db):
        instance_repo = PracticeInstanceRepository(uow.session)
        service = PracticeInstanceService(instance_repo)
        instance_id = seed_db["practice_instances"][0].id_
        instance = await service.get_instance_by_id(instance_id)
        assert instance is not None
        assert instance.id_ == instance_id

    async def test_list_instances_for_user(self, uow, seed_db):
        instance_repo = PracticeInstanceRepository(uow.session)
        service = PracticeInstanceService(instance_repo)
        user_id = seed_db["client_user_one"].id
        instances = await service.list_instances_for_user(user_id)
        assert len(instances) >= 2

    async def test_update_instance(self, uow, seed_db):
        instance_repo = PracticeInstanceRepository(uow.session)
        service = PracticeInstanceService(instance_repo)
        instance_id = seed_db["practice_instances"][0].id_
        update_data = {"title": "Updated Title"}
        instance = await service.update_instance(instance_id, update_data)
        assert instance is not None
        assert instance.title == "Updated Title"

    async def test_delete_instance(self, uow, seed_db):
        instance_repo = PracticeInstanceRepository(uow.session)
        service = PracticeInstanceService(instance_repo)
        instance_id = seed_db["practice_instances"][0].id_
        result = await service.delete_instance(instance_id)
        assert result is True
        instance = await service.get_instance_by_id(instance_id)
        assert instance is None

    async def test_complete_instance(self, uow, seed_db):
        instance_repo = PracticeInstanceRepository(uow.session)
        service = PracticeInstanceService(instance_repo)
        instance_id = seed_db["practice_instances"][0].id_
        instance = await service.complete_instance(instance_id)
        assert instance is not None
        assert instance.completed_at is not None
