from datetime import date
from typing import Any, Dict, List, Optional
from uuid import UUID

from practices.domain.models import DomainPracticeInstance
from practices.repository.repositories import PracticeInstanceRepository


class PracticeInstanceService:
    def __init__(self, repository: PracticeInstanceRepository):
        self.repository = repository

    async def create_instance_from_template(
        self, template_id: UUID, user_id: UUID, date: date, enrollment_id: Optional[UUID] = None
    ) -> DomainPracticeInstance:
        return await self.repository.create_instance_from_template(template_id, user_id, date, enrollment_id)

    async def create_standalone_instance(self, instance_data: Dict[str, Any]) -> DomainPracticeInstance:
        return await self.repository.create_standalone_instance(instance_data)

    async def get_instance_by_id(self, instance_id: UUID) -> Optional[DomainPracticeInstance]:
        return await self.repository.get_instance_by_id(instance_id)

    async def list_instances_for_user(self, user_id: UUID) -> List[DomainPracticeInstance]:
        return await self.repository.list_instances_for_user(user_id)

    async def update_instance(self, instance_id: UUID, update_data: Dict[str, Any]) -> Optional[DomainPracticeInstance]:
        return await self.repository.update_instance(instance_id, update_data)

    async def delete_instance(self, instance_id: UUID) -> bool:
        return await self.repository.delete_instance(instance_id)

    async def complete_instance(self, instance_id: UUID) -> Optional[DomainPracticeInstance]:
        return await self.repository.update_instance(instance_id, {"completed_at": date.today()})
