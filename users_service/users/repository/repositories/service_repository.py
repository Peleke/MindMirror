import uuid
from typing import Any, Dict, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from users.repository.models import ServiceEnum, ServiceModel


class ServiceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_service_by_id(self, service_uuid: uuid.UUID) -> Optional[ServiceModel]:
        stmt = select(ServiceModel).where(ServiceModel.id_ == service_uuid)
        result = await self.session.execute(stmt)
        service = result.scalars().first()
        if service:
            await self.session.refresh(service)
        return service

    async def get_service_by_name(self, service_name: ServiceEnum) -> Optional[ServiceModel]:
        stmt = select(ServiceModel).where(ServiceModel.name == service_name)
        result = await self.session.execute(stmt)
        service = result.scalars().first()
        if service:
            await self.session.refresh(service)
        return service

    async def list_services(self) -> Sequence[ServiceModel]:
        stmt = select(ServiceModel).order_by(ServiceModel.name)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_service(self, service_data: Dict[str, Any]) -> ServiceModel:
        if "name" not in service_data or not isinstance(service_data["name"], ServiceEnum):
            name_val = service_data.get("name")
            if isinstance(name_val, str):
                try:
                    service_data["name"] = ServiceEnum(name_val)
                except ValueError:
                    raise ValueError(f"Invalid service name string for ServiceEnum: {name_val}")
            else:
                raise ValueError(
                    "service_data must contain 'name' of type ServiceEnum or a valid string for ServiceEnum."
                )

        service = ServiceModel(**service_data)
        self.session.add(service)
        await self.session.flush()
        await self.session.refresh(service)
        return service

    async def update_service(self, service_id: uuid.UUID, update_data: Dict[str, Any]) -> Optional[ServiceModel]:
        service = await self.get_service_by_id(service_id)
        if service:
            if "name" in update_data:  # Ensure name is ServiceEnum if provided
                name_val = update_data["name"]
                if isinstance(name_val, str):
                    try:
                        update_data["name"] = ServiceEnum(name_val)
                    except ValueError:
                        raise ValueError(f"Invalid service name string for ServiceEnum in update: {name_val}")
                elif not isinstance(name_val, ServiceEnum):
                    raise ValueError(
                        "Service 'name' in update_data must be ServiceEnum or a valid string for ServiceEnum."
                    )

            for key, value in update_data.items():
                if hasattr(service, key):
                    setattr(service, key, value)
                else:
                    # Potentially log a warning or raise an error for unexpected keys
                    print(f"Warning: Attribute {key} not found on ServiceModel during update.")
            await self.session.flush()
            await self.session.refresh(service)
        return service

    async def delete_service(self, service_id: uuid.UUID) -> bool:
        # Note: Deleting a service might fail if UserServicesModel or SchedulableModel
        # have foreign key constraints that are not set to ON DELETE CASCADE for services.id_
        # The SQL schema migration seems to have ON DELETE CASCADE for user_services.service_id
        # and schedulables.service_id.
        service = await self.session.get(ServiceModel, service_id)
        if service:
            await self.session.delete(service)
            await self.session.flush()
            return True
        return False
