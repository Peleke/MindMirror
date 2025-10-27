from uuid import UUID, uuid4

import pytest

# Attempt to import the repository, will fail until implemented
from practices.repository.repositories.practice_template_repository import (
    PracticeTemplateRepository,
)


@pytest.mark.asyncio
class TestPracticeTemplateRepository:
    async def test_create_and_get_template(self, seed_db, session):
        user_id = seed_db["coach_user"].id
        new_template_data = {
            "title": "Yoga Flow Template",
            "description": "A reusable morning yoga session",
            "duration": 45.0,
            "user_id": user_id,
            "prescriptions": [
                {
                    "name": "Sun Salutations",
                    "block": "warmup",
                    "movements": [
                        {
                            "name": "Surya Namaskar A",
                            "metric_unit": "iterative",
                            "metric_value": 5,
                        }
                    ],
                }
            ],
        }
        template_repo = PracticeTemplateRepository(session)
        created_template = await template_repo.create_template_with_nested_data(new_template_data)
        assert created_template is not None
        assert created_template.title == "Yoga Flow Template"

        fetched_template = await template_repo.get_template_by_id(created_template.id_)
        assert fetched_template is not None
        assert fetched_template.title == "Yoga Flow Template"
        assert len(fetched_template.prescriptions) == 1
        assert fetched_template.prescriptions[0].name == "Sun Salutations"
        assert len(fetched_template.prescriptions[0].movements) == 1

    async def test_list_templates(self, seed_db, session):
        template_repo = PracticeTemplateRepository(session)
        templates = await template_repo.list_templates()
        # This will fail until we update seed_db to create templates
        assert len(templates) >= 1

    async def test_update_template(self, seed_db, session):
        template_repo = PracticeTemplateRepository(session)
        template_to_update = seed_db["practice_templates"][0]
        updated_data = {
            "title": "Evening Meditation Template",
            "description": "A reusable guided meditation",
        }
        updated_template = await template_repo.update_template(template_to_update.id_, updated_data)
        assert updated_template is not None
        assert updated_template.title == "Evening Meditation Template"

    async def test_delete_template(self, seed_db, session):
        template_repo = PracticeTemplateRepository(session)
        template_to_delete = seed_db["practice_templates"][0]
        result = await template_repo.delete_template(template_to_delete.id_)
        assert result is True
        fetched_template = await template_repo.get_template_by_id(template_to_delete.id_)
        assert fetched_template is None
