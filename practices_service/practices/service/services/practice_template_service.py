from typing import Any, Dict, List, Optional
from uuid import UUID

from practices.domain.models import DomainPracticeTemplate
from practices.repository.repositories import PracticeTemplateRepository


class PracticeTemplateService:
    def __init__(self, repository: PracticeTemplateRepository):
        self.repository = repository

    async def create_template(self, template_data: Dict[str, Any]) -> DomainPracticeTemplate:
        return await self.repository.create_template_with_nested_data(template_data)

    async def get_template_by_id(self, template_id: UUID) -> Optional[DomainPracticeTemplate]:
        return await self.repository.get_template_by_id(template_id)

    async def list_templates(self) -> List[DomainPracticeTemplate]:
        return await self.repository.list_templates()

    async def update_template(self, template_id: UUID, update_data: Dict[str, Any]) -> Optional[DomainPracticeTemplate]:
        return await self.repository.update_template(template_id, update_data)

    async def delete_template(self, template_id: UUID) -> bool:
        return await self.repository.delete_template(template_id)
