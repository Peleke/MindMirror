import uuid
from typing import Any, Dict, List, Optional, Sequence

from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from users.repository.models import (
    AssociationStatusModel,
    CoachClientAssociationModel,
    DomainModel,
    RoleModel,
    SchedulableModel,
    ServiceModel,
    UserModel,
    UserRoleModel,
    UserServicesModel,
)


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user_data: Dict[str, Any]) -> UserModel:
        if "supabase_id" not in user_data:
            raise ValueError("supabase_id is required to create a user.")
        user = UserModel(**user_data)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[UserModel]:
        stmt = (
            select(UserModel)
            .where(UserModel.id_ == user_id)
            .options(
                selectinload(UserModel.service_links).options(selectinload(UserServicesModel.service)),
                selectinload(UserModel.schedulables).options(selectinload(SchedulableModel.service)),
                selectinload(UserModel.roles),
                selectinload(UserModel.coaching_clients).options(
                    selectinload(CoachClientAssociationModel.coach),
                    selectinload(CoachClientAssociationModel.client),
                    selectinload(CoachClientAssociationModel.requester),
                ),
                selectinload(UserModel.coaches).options(
                    selectinload(CoachClientAssociationModel.coach),
                    selectinload(CoachClientAssociationModel.client),
                    selectinload(CoachClientAssociationModel.requester),
                ),
            )
        )
        result = await self.session.execute(stmt)
        user = result.scalars().first()
        if user:
            await self.session.refresh(
                user,
                attribute_names=[
                    "service_links",
                    "schedulables",
                    "roles",
                    "coaching_clients",
                    "coaches",
                ],
            )
        return user

    async def get_user_by_supabase_id(self, supabase_id: str) -> Optional[UserModel]:
        stmt = (
            select(UserModel)
            .where(UserModel.supabase_id == supabase_id)
            .options(
                selectinload(UserModel.service_links).options(selectinload(UserServicesModel.service)),
                selectinload(UserModel.schedulables).options(selectinload(SchedulableModel.service)),
                selectinload(UserModel.roles),
                selectinload(UserModel.coaching_clients).options(
                    selectinload(CoachClientAssociationModel.coach),
                    selectinload(CoachClientAssociationModel.client),
                    selectinload(CoachClientAssociationModel.requester),
                ),
                selectinload(UserModel.coaches).options(
                    selectinload(CoachClientAssociationModel.coach),
                    selectinload(CoachClientAssociationModel.client),
                    selectinload(CoachClientAssociationModel.requester),
                ),
            )
        )
        result = await self.session.execute(stmt)
        user = result.scalars().first()
        if user:
            await self.session.refresh(
                user,
                attribute_names=[
                    "service_links",
                    "schedulables",
                    "roles",
                    "coaching_clients",
                    "coaches",
                ],
            )
        return user

    async def list_users(self) -> Sequence[UserModel]:
        stmt = (
            select(UserModel)
            .order_by(UserModel.created_at)
            .options(
                selectinload(UserModel.service_links).options(selectinload(UserServicesModel.service)),
                selectinload(UserModel.schedulables).options(selectinload(SchedulableModel.service)),
                selectinload(UserModel.roles),
                selectinload(UserModel.coaching_clients),
                selectinload(UserModel.coaches),
            )
        )
        result = await self.session.execute(stmt)
        users = result.scalars().all()
        # The refresh here might be excessive if all necessary data is eagerly loaded.
        # However, if there are other attributes that might be lazy-loaded by Pydantic,
        # it could be a safeguard. For now, let's try without individual refreshes in a loop.
        # for user in users:
        #     await self.session.refresh(user) # Consider if truly needed after eager loading
        return users

    async def update_user(self, user_id: uuid.UUID, update_data: Dict[str, Any]) -> Optional[UserModel]:
        user = await self.get_user_by_id(user_id)
        if user:
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
                else:
                    print(f"Warning: Attribute {key} not found on UserModel during update.")
            await self.session.flush()
            await self.session.refresh(user)
        return user

    async def delete_user(self, user_id: uuid.UUID) -> bool:
        user = await self.session.get(UserModel, user_id)
        if user:
            await self.session.delete(user)
            await self.session.flush()
            return True
        return False

    async def link_user_to_service(self, user_id: uuid.UUID, service_id: uuid.UUID) -> Optional[UserServicesModel]:
        existing_link = await self.session.get(UserServicesModel, (user_id, service_id))
        if existing_link:
            if not existing_link.active:
                existing_link.active = True
                await self.session.flush()
                await self.session.refresh(existing_link, attribute_names=["user", "service"])
            stmt_select = (
                select(UserServicesModel)
                .where(UserServicesModel.user_id == user_id, UserServicesModel.service_id == service_id)
                .options(selectinload(UserServicesModel.user), selectinload(UserServicesModel.service))
            )
            result_select = await self.session.execute(stmt_select)
            return result_select.scalars().first()

        new_link = UserServicesModel(user_id=user_id, service_id=service_id, active=True)
        self.session.add(new_link)
        await self.session.flush()
        await self.session.refresh(new_link, attribute_names=["user", "service"])
        return new_link

    async def unlink_user_from_service(self, user_id: uuid.UUID, service_id: uuid.UUID) -> bool:
        stmt = delete(UserServicesModel).where(
            UserServicesModel.user_id == user_id, UserServicesModel.service_id == service_id
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0

    async def get_user_service_link(self, user_id: uuid.UUID, service_id: uuid.UUID) -> Optional[UserServicesModel]:
        stmt = (
            select(UserServicesModel)
            .where(UserServicesModel.user_id == user_id, UserServicesModel.service_id == service_id)
            .options(selectinload(UserServicesModel.user), selectinload(UserServicesModel.service))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_user_services(self, user_id: uuid.UUID) -> Sequence[UserServicesModel]:
        stmt = (
            select(UserServicesModel)
            .where(UserServicesModel.user_id == user_id)
            .options(selectinload(UserServicesModel.service))
            .order_by(UserServicesModel.created_at)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_or_create_user(self, supabase_id: str) -> UserModel:
        """Get an existing user by Supabase ID or create a new one if not found."""
        user = await self.get_user_by_supabase_id(supabase_id)
        if user:
            return user

        # Create new user
        user_data = {"supabase_id": supabase_id}
        return await self.create_user(user_data)

    async def assign_role_to_user(
        self, user_id: uuid.UUID, role: RoleModel, domain: DomainModel
    ) -> Optional[UserRoleModel]:
        """
        Assigns a role to a user within a specific domain. This operation is idempotent.
        If the role assignment already exists, it returns the existing one.
        If the user doesn't exist, it returns None.
        """
        # First, check if the role assignment already exists to ensure idempotency.
        existing_role_stmt = select(UserRoleModel).where(
            UserRoleModel.user_id == user_id,
            UserRoleModel.role == role,
            UserRoleModel.domain == domain,
        )
        existing_role_result = await self.session.execute(existing_role_stmt)
        existing_role = existing_role_result.scalars().first()
        if existing_role:
            return existing_role

        # Proceed to create the new role if the user exists.
        user = await self.session.get(UserModel, user_id)
        if not user:
            raise ValueError(f"User not found for user_id: {user_id}")

        new_role = UserRoleModel(user_id=user_id, role=role, domain=domain)
        self.session.add(new_role)
        await self.session.flush()
        await self.session.refresh(new_role)
        return new_role

    async def remove_role_from_user(self, user_id: uuid.UUID, role: RoleModel, domain: DomainModel) -> bool:
        """Removes a role from a user within a specific domain."""
        stmt = delete(UserRoleModel).where(
            UserRoleModel.user_id == user_id,
            UserRoleModel.role == role,
            UserRoleModel.domain == domain,
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0

    async def get_user_roles(self, user_id: uuid.UUID) -> Sequence[UserRoleModel]:
        """Gets all roles for a given user."""
        stmt = select(UserRoleModel).where(UserRoleModel.user_id == user_id).options(selectinload(UserRoleModel.user))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    # --- Coach-Client Association Methods ---

    async def create_association_request(
        self, coach_id: uuid.UUID, client_id: uuid.UUID, requester_id: uuid.UUID, domain: DomainModel
    ) -> CoachClientAssociationModel:
        """Creates a new coach-client association request."""
        # Check for existing pending/accepted/rejected(recently) requests to avoid spam.
        # For now, we just check for any existing non-terminated one.
        existing_stmt = select(CoachClientAssociationModel).where(
            CoachClientAssociationModel.coach_id == coach_id,
            CoachClientAssociationModel.client_id == client_id,
            CoachClientAssociationModel.domain == domain,
            CoachClientAssociationModel.status != AssociationStatusModel.terminated,
        )
        existing_result = await self.session.execute(existing_stmt)
        if existing_result.scalars().first():
            raise ValueError("An active or pending association request already exists for this domain.")

        # Ensure both users exist
        coach = await self.session.get(UserModel, coach_id)
        client = await self.session.get(UserModel, client_id)
        if not coach or not client:
            raise ValueError("Coach or Client not found.")

        new_association = CoachClientAssociationModel(
            coach_id=coach_id,
            client_id=client_id,
            requester_id=requester_id,
            domain=domain,
            status=AssociationStatusModel.pending,
        )
        self.session.add(new_association)
        await self.session.flush()
        # Eagerly load the relationships on the new instance before returning
        await self.session.refresh(new_association, attribute_names=["coach", "client", "requester"])
        return new_association

    async def update_association_status(
        self, association_id: uuid.UUID, status: AssociationStatusModel
    ) -> Optional[CoachClientAssociationModel]:
        """Updates the status of an association (e.g., to accepted, rejected, terminated)."""
        association = await self.get_association_by_id(association_id)
        if association:
            association.status = status
            await self.session.flush()
            await self.session.refresh(association)
        return association

    async def get_association_by_id(self, association_id: uuid.UUID) -> Optional[CoachClientAssociationModel]:
        """Fetches a single association by its ID, with related users."""
        stmt = (
            select(CoachClientAssociationModel)
            .where(CoachClientAssociationModel.id_ == association_id)
            .options(
                selectinload(CoachClientAssociationModel.coach),
                selectinload(CoachClientAssociationModel.client),
                selectinload(CoachClientAssociationModel.requester),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_associations_for_user(
        self,
        user_id: uuid.UUID,
        as_role: str,  # "coach" or "client"
        status: Optional[AssociationStatusModel] = None,
        domain: Optional[DomainModel] = None,
    ) -> Sequence[CoachClientAssociationModel]:
        """
        Lists associations for a user, optionally filtering by their role in the association,
        the association's status, and the domain.
        """
        if as_role not in ["coach", "client"]:
            raise ValueError("as_role must be either 'coach' or 'client'")

        if as_role == "coach":
            stmt = select(CoachClientAssociationModel).where(CoachClientAssociationModel.coach_id == user_id)
        else:  # as_role == "client"
            stmt = select(CoachClientAssociationModel).where(CoachClientAssociationModel.client_id == user_id)

        if status:
            stmt = stmt.where(CoachClientAssociationModel.status == status)

        if domain:
            stmt = stmt.where(CoachClientAssociationModel.domain == domain)

        stmt = stmt.options(
            selectinload(CoachClientAssociationModel.coach).options(
                selectinload(UserModel.roles),
                selectinload(UserModel.coaching_clients),
                selectinload(UserModel.coaches),
            ),
            selectinload(CoachClientAssociationModel.client).options(
                selectinload(UserModel.roles),
                selectinload(UserModel.coaching_clients),
                selectinload(UserModel.coaches),
            ),
            selectinload(CoachClientAssociationModel.requester),
        ).order_by(CoachClientAssociationModel.created_at.desc())

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def check_existing_association(
        self,
        coach_id: uuid.UUID,
        client_id: uuid.UUID,
        domain: DomainModel,
        status: Optional[AssociationStatusModel] = None,
    ) -> bool:
        """
        Checks if an association exists between a coach and a client in a specific domain,
        optionally filtering by status. Returns True if such an association exists.
        """
        stmt = select(CoachClientAssociationModel.id_).where(
            CoachClientAssociationModel.coach_id == coach_id,
            CoachClientAssociationModel.client_id == client_id,
            CoachClientAssociationModel.domain == domain,
        )

        if status:
            stmt = stmt.where(CoachClientAssociationModel.status == status)

        result = await self.session.execute(stmt)
        return result.scalars().first() is not None

    async def list_users_by_role(self, role: RoleModel, domain: Optional[DomainModel] = None) -> List[UserModel]:
        """Lists all users who have a specific role, optionally filtered by domain."""
        stmt = (
            select(UserModel)
            .join(UserRoleModel)
            .where(UserRoleModel.role == role)
            .options(
                selectinload(UserModel.roles),
                selectinload(UserModel.service_links).options(selectinload(UserServicesModel.service)),
                selectinload(UserModel.coaching_clients).options(
                    selectinload(CoachClientAssociationModel.coach),
                    selectinload(CoachClientAssociationModel.client),
                    selectinload(CoachClientAssociationModel.requester),
                ),
                selectinload(UserModel.coaches).options(
                    selectinload(CoachClientAssociationModel.coach),
                    selectinload(CoachClientAssociationModel.client),
                    selectinload(CoachClientAssociationModel.requester),
                ),
            )
            .distinct()
        )
        if domain:
            stmt = stmt.where(UserRoleModel.domain == domain)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
