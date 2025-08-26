from datetime import date
from uuid import UUID

import pytest

from practices.repository.repositories.practice_instance_repository import (
    PracticeInstanceRepository,
)
from practices.repository.repositories.practice_template_repository import (
    PracticeTemplateRepository,
)


@pytest.mark.asyncio
class TestPracticeInstanceRepository:
    async def test_create_instance_from_template(self, session, seed_db):
        """
        Verify that a practice instance can be created as a deep copy of a template.
        """
        instance_repo = PracticeInstanceRepository(session)
        practice_template = seed_db["practice_templates"][0]
        user_id = seed_db["client_user_one"].id
        instance_date = date.today()

        created_instance = await instance_repo.create_instance_from_template(
            template_id=practice_template.id_,
            user_id=user_id,
            date=instance_date,
        )

        assert created_instance is not None
        assert created_instance.user_id == user_id
        assert created_instance.date == instance_date
        assert created_instance.template_id == practice_template.id_
        assert created_instance.title == practice_template.title
        assert len(created_instance.prescriptions) == len(practice_template.prescriptions)
        assert created_instance.prescriptions[0].id_ != practice_template.prescriptions[0].id_
        assert created_instance.prescriptions[0].name == practice_template.prescriptions[0].name

    async def test_create_standalone_instance(self, session, seed_db):
        """
        Verify creating a one-off practice instance not tied to a template.
        """
        instance_repo = PracticeInstanceRepository(session)
        user_id = seed_db["client_user_one"].id
        instance_data = {
            "user_id": user_id,
            "title": "Standalone Run",
            "date": date.today(),
            "prescriptions": [{"name": "5k Run", "block": "workout", "movements": []}],
        }

        created_instance = await instance_repo.create_standalone_instance(instance_data)
        assert created_instance is not None
        assert created_instance.user_id == user_id
        assert created_instance.title == "Standalone Run"
        assert created_instance.template_id is None
        assert len(created_instance.prescriptions) == 1

    async def test_get_instance_by_id(self, session, seed_db):
        instance_repo = PracticeInstanceRepository(session)
        instance_id = seed_db["practice_instances"][0].id_
        fetched_instance = await instance_repo.get_instance_by_id(instance_id)

        assert fetched_instance is not None
        assert fetched_instance.id_ == instance_id

    async def test_list_instances_for_user(self, session, seed_db):
        instance_repo = PracticeInstanceRepository(session)
        user_id = seed_db["client_user_one"].id
        instances = await instance_repo.list_instances_for_user(user_id)

        assert instances is not None
        assert len(instances) >= 1
        assert all(instance.user_id == user_id for instance in instances)

    async def test_update_instance(self, session, seed_db):
        instance_repo = PracticeInstanceRepository(session)
        instance_to_update = seed_db["practice_instances"][0]
        updated_data = {"title": "Evening Walk", "notes": "Felt relaxing."}

        updated_instance = await instance_repo.update_instance(instance_to_update.id_, updated_data)

        assert updated_instance is not None
        assert updated_instance.title == "Evening Walk"
        assert updated_instance.notes == "Felt relaxing."

    async def test_delete_instance(self, session, seed_db):
        instance_repo = PracticeInstanceRepository(session)
        instance_to_delete = seed_db["practice_instances"][0]

        result = await instance_repo.delete_instance(instance_to_delete.id_)
        assert result is True

        fetched_instance = await instance_repo.get_instance_by_id(instance_to_delete.id_)
        assert fetched_instance is None
