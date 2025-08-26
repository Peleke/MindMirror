from datetime import date
from uuid import uuid4

import pytest

from practices.repository.repositories import PracticeTemplateRepository
from practices.service.services import PracticeTemplateService


@pytest.mark.asyncio
class TestPracticeTemplateService:
    async def test_create_template(self, uow, seed_db):
        template_repo = PracticeTemplateRepository(uow.session)
        service = PracticeTemplateService(template_repo)
        coach_id = seed_db["coach_user"].id
        template_data = {
            "user_id": coach_id,
            "title": "Morning Mobility Template",
            "description": "A reusable morning mobility session",
            "prescriptions": [
                {
                    "name": "Warm-up",
                    "block": "warmup",
                    "movements": [
                        {
                            "name": "Cat-Cow",
                            "metric_unit": "iterative",
                            "metric_value": 10,
                        }
                    ],
                }
            ],
        }

        created_template = await service.create_template(template_data)

        assert created_template is not None
        assert created_template.title == "Morning Mobility Template"
        assert len(created_template.prescriptions) == 1
        assert created_template.prescriptions[0].movements[0].name == "Cat-Cow"

    async def test_get_template(self, uow, seed_db):
        template_repo = PracticeTemplateRepository(uow.session)
        service = PracticeTemplateService(template_repo)
        seeded_template_model = seed_db["practice_templates"][0]
        template = await service.get_template_by_id(seeded_template_model.id_)

        assert template is not None
        assert template.id_ == seeded_template_model.id_

    async def test_list_templates(self, uow, seed_db):
        template_repo = PracticeTemplateRepository(uow.session)
        service = PracticeTemplateService(template_repo)
        templates = await service.list_templates()

        assert len(templates) >= 1
        assert any(t.id_ == seed_db["practice_templates"][0].id_ for t in templates)

    async def test_update_template(self, uow, seed_db):
        template_repo = PracticeTemplateRepository(uow.session)
        service = PracticeTemplateService(template_repo)
        template_to_update_id = seed_db["practice_templates"][0].id_
        update_data = {"title": "Updated Yoga Flow"}

        updated_template = await service.update_template(template_to_update_id, update_data)

        assert updated_template is not None
        assert updated_template.id_ == template_to_update_id
        assert updated_template.title == "Updated Yoga Flow"

    async def test_delete_template(self, uow, seed_db):
        template_repo = PracticeTemplateRepository(uow.session)
        service = PracticeTemplateService(template_repo)
        template_to_delete_id = seed_db["practice_templates"][0].id_
        result = await service.delete_template(template_to_delete_id)

        assert result is True
        deleted_template = await service.get_template_by_id(template_to_delete_id)
        assert deleted_template is None
