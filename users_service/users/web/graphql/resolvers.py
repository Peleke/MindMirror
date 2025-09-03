import uuid
from datetime import date, datetime, timezone  # Added timezone
from typing import List, Optional, cast

import httpx  # Added for making HTTP requests
import strawberry
from strawberry.types import Info

from users.domain.models import (
    DomainAssociationStatus,
    DomainCoachClientAssociation,
    DomainCoachClientRelationship,
    DomainCoachingRequest,
    DomainUserSummary,
)
from users.domain.models import DomainDomain as DomainModelDomain
from users.domain.models import DomainRole as DomainModelRole  # Pydantic domain models
from users.domain.models import (
    DomainSchedulable,
    DomainService,
    DomainUser,
    DomainUserRole,
    DomainUserServiceLink,
)
from users.repository.models import (
    AssociationStatusModel,
    CoachClientAssociationModel,
    CoachClientRelationshipModel,
    DomainModel,
    RoleModel,
    SchedulableModel,
)
from users.repository.models import ServiceEnum as SQLAlchemyServiceEnum
from users.repository.models import (
    ServiceModel,
    UserModel,
    UserRoleModel,
    UserServicesModel,
)

# Import actual repository classes
from users.repository.repositories import (
    SchedulableRepository,
    ServiceRepository,
    UserRepository,
)
from users.repository.uow import UnitOfWork

from .scalars import UUID
from .types import (  # GraphQL Types
    AssociationStatusGQL,
    CoachClientAssociationGQL,
    CoachingRequestGQL,
    DomainGQL,
    RoleGQL,
    SchedulableTypeGQL,
    ServiceTypeGQL,
    ServiceTypeGQL_Type,
    UserRoleTypeGQL,
    UserServiceLinkTypeGQL,
    UserSummaryGQL,
    UserTypeGQL,
)

# Helper to convert SQLAlchemy model to Pydantic domain model (basic example)
# In a real app, you might have more sophisticated mappers or use Pydantic's from_orm


def to_domain_user(user_model: UserModel) -> DomainUser:
    return DomainUser.model_validate(user_model)  # Uses Pydantic v2 model_validate (from_orm equivalent)


def to_domain_user_summary(user_model: UserModel) -> DomainUserSummary:
    return DomainUserSummary.model_validate(user_model)


def to_domain_coaching_request(relationship_model: CoachClientRelationshipModel) -> DomainCoachingRequest:
    return DomainCoachingRequest.model_validate(relationship_model)


def to_domain_coach_client_relationship(relationship_model: CoachClientRelationshipModel) -> DomainCoachClientRelationship:
    return DomainCoachClientRelationship.model_validate(relationship_model)


def to_domain_coach_client_association(association_model: CoachClientAssociationModel) -> DomainCoachClientAssociation:
    return DomainCoachClientAssociation.model_validate(association_model)


def to_domain_service(service_model: ServiceModel) -> DomainService:
    # Ensure the name field gets the string value of the enum
    validated_data = service_model.__dict__  # Start with all attributes
    if hasattr(service_model, "name") and service_model.name is not None:
        validated_data["name"] = service_model.name.value
    return DomainService.model_validate(validated_data)


def to_domain_schedulable(schedulable_model: SchedulableModel) -> DomainSchedulable:
    # Handle the service_id and user_id for GQL type mapping carefully
    domain_model = DomainSchedulable.model_validate(schedulable_model)
    return domain_model


def to_domain_user_service_link(link_model: UserServicesModel) -> DomainUserServiceLink:
    return DomainUserServiceLink.model_validate(link_model)


def to_domain_user_role(role_model: UserRoleModel) -> DomainUserRole:
    """Converts a UserRoleModel (SQLAlchemy) to a DomainUserRole (Pydantic)."""
    return DomainUserRole.model_validate(role_model)


def to_domain_coach_client_association(association_model: CoachClientAssociationModel) -> DomainCoachClientAssociation:
    """Converts a CoachClientAssociationModel (SQLAlchemy) to a DomainCoachClientAssociation (Pydantic)."""
    return DomainCoachClientAssociation.model_validate(association_model)


async def get_uow_from_info(info: Info) -> UnitOfWork:
    """
    Get UnitOfWork from GraphQL info context.
    The UoW is already managed by the GraphQL router dependencies via get_request_uow,
    so it's already in an active context and should NOT be wrapped in another async with.
    """
    uow = cast(UnitOfWork, info.context["uow"])
    return uow


async def get_current_user_from_info(info: Info) -> DomainUser:
    """Retrieves the current user from the GraphQL context."""
    current_user = info.context.get("current_user")
    if not current_user:
        # Check if this is due to missing authentication headers
        request = info.context.get("request")
        auth_header = request.headers.get("authorization") if request else None
        internal_id_header = request.headers.get("x-internal-id") if request else None
        
        if not auth_header and not internal_id_header:
            raise Exception("Unauthorized: Missing authentication headers (Authorization or X-Internal-Id)")
        else:
            raise Exception("Unauthorized: User not found or invalid authentication")
    return current_user


@strawberry.type
class Query:
    @strawberry.field
    async def users(self, info: Info) -> List[UserTypeGQL]:
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            user_models = await repo.list_users()
            return [to_domain_user(user) for user in user_models]

    @strawberry.field
    async def user_by_id(self, info: Info, id: UUID) -> Optional[UserTypeGQL]:
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            user_model = await repo.get_user_by_id(id)
            return to_domain_user(user_model) if user_model else None

    @strawberry.field
    async def userById(self, info: Info, id: strawberry.ID) -> Optional[UserTypeGQL]:
        """Alias for user_by_id to match mobile app expectations."""
        # Convert strawberry.ID to UUID and implement the same logic
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            user_model = await repo.get_user_by_id(uuid.UUID(str(id)))
            return to_domain_user(user_model) if user_model else None

    @strawberry.field
    async def user_by_supabase_id(self, info: Info, supabase_id: str) -> Optional[UserTypeGQL]:
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            user_model = await repo.get_user_by_supabase_id(supabase_id)
            return to_domain_user(user_model) if user_model else None

    @strawberry.field
    async def services(self, info: Info) -> List[ServiceTypeGQL_Type]:
        uow = await get_uow_from_info(info)
        async with uow:
            repo = ServiceRepository(session=uow.session)
            service_models = await repo.list_services()
            return [to_domain_service(service) for service in service_models]

    @strawberry.field
    async def service_by_id(self, info: Info, id: UUID) -> Optional[ServiceTypeGQL_Type]:
        uow = await get_uow_from_info(info)
        async with uow:
            repo = ServiceRepository(session=uow.session)
            service_model = await repo.get_service_by_id(id)
            return to_domain_service(service_model) if service_model else None

    @strawberry.field
    async def service_by_name(
        self, info: Info, name: ServiceTypeGQL
    ) -> Optional[ServiceTypeGQL_Type]:  # Uses GQL Enum for input
        uow = await get_uow_from_info(info)
        async with uow:
            # Convert GQL enum to SQLAlchemy enum if necessary, or ensure repository handles GQL enum value
            # Assuming repository method get_service_by_name expects SQLAlchemyServiceEnum or its value
            repo = ServiceRepository(session=uow.session)
            service_model = await repo.get_service_by_name(SQLAlchemyServiceEnum(name.value))
            return to_domain_service(service_model) if service_model else None

    @strawberry.field
    async def schedulables_by_user_id(self, info: Info, user_id: UUID) -> List[SchedulableTypeGQL]:
        uow = await get_uow_from_info(info)
        async with uow:
            repo = SchedulableRepository(session=uow.session)
            schedulable_models = await repo.get_schedulables_by_user_id(user_id)
            return [to_domain_schedulable(s) for s in schedulable_models]

    @strawberry.field
    async def schedulable_by_id(self, info: Info, id: UUID) -> Optional[SchedulableTypeGQL]:
        uow = await get_uow_from_info(info)
        async with uow:
            repo = SchedulableRepository(session=uow.session)
            schedulable_model = await repo.get_schedulable_by_id(id)
            return to_domain_schedulable(schedulable_model) if schedulable_model else None

    @strawberry.field
    async def schedulables_for_user_on_date(
        self, info: Info, user_id: UUID, service_name: Optional[str] = None, event_date: Optional[date] = None
    ) -> List[SchedulableTypeGQL]:
        uow = await get_uow_from_info(info)
        # TODO: Handle timezone properly. For now, assuming UTC or naive comparison.
        target_date = event_date if event_date else datetime.now(timezone.utc).date()

        results: List[SchedulableTypeGQL] = []

        if service_name and service_name.lower() != "practices":
            raise NotImplementedError(f"Fetching schedulables for service '{service_name}' is not yet implemented.")

        # For now, only "practices" is implemented or if service_name is None
        if not service_name or service_name.lower() == "practices":
            async with uow:
                service_repo = ServiceRepository(session=uow.session)
                user_repo = UserRepository(session=uow.session)

                practices_service_model = await service_repo.get_service_by_name(SQLAlchemyServiceEnum.PRACTICE)
                if not practices_service_model or not practices_service_model.url:
                    # Log this issue
                    print(f"Practices service URL not configured or service not found.")
                    return []  # Or raise an error

                target_user = await user_repo.get_user_by_id(uuid.UUID(str(user_id)))
                if not target_user:
                    print(f"User with ID {user_id} not found.")
                    return []  # Or raise error

                # The practices service query doesn't filter by user_id or date, so we do it client-side.
                # This is NOT ideal for performance. The practices API should be enhanced.
                practices_query = """
                    query GetAllPractices {
                        practices {
                            id_
                            title
                            description
                            complete
                            date
                            userId
                        }
                    }
                """
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(practices_service_model.url, json={"query": practices_query})
                        response.raise_for_status()  # Raise an exception for bad status codes
                        practices_data = response.json()

                    print(f"Practices data: {practices_data}")
                    if practices_data.get("errors"):
                        print(f"Error from practices service: {practices_data['errors']}")
                        return []

                    all_practices = practices_data.get("data", {}).get("practices", [])

                    for p_data in all_practices:
                        practice_date_str = p_data.get("date")
                        practice_user_id = p_data.get("userId")  # Assuming practices returns user_id

                        if not practice_date_str or not practice_user_id:
                            # Log missing data if necessary
                            continue

                        try:
                            practice_date = datetime.strptime(practice_date_str, "%Y-%m-%d").date()
                        except ValueError:
                            print(
                                f"Could not parse date '{practice_date_str}' from practices service for practice ID {p_data.get('id_')}"
                            )
                            continue

                        # Perform client-side filtering
                        # This assumes target_user.supabase_id is what practice_user_id would match.
                        if practice_date == target_date and practice_user_id == str(target_user.id_):
                            results.append(
                                SchedulableTypeGQL(
                                    id_=UUID(str(p_data.get("id_"))),  # This is practice_id, acting as entity_id
                                    created_at=datetime.now(timezone.utc),  # Placeholder, not from practice data
                                    modified_at=datetime.now(timezone.utc),  # Placeholder
                                    name=p_data.get("title", "Practice"),
                                    description=p_data.get("description"),
                                    entity_id=UUID(str(p_data.get("id_"))),  # The ID of the practice itself
                                    completed=p_data.get("complete", False),
                                    service_id_str=UUID(str(practices_service_model.id_)),
                                    user_id_str=UUID(str(user_id)),
                                    date=practice_date,
                                    service=to_domain_service(
                                        practices_service_model
                                    ),  # Pass the ServiceModel for conversion to GQL type
                                    # user field is not populated here as it would be recursive or require another fetch
                                )
                            )
                except httpx.RequestError as e:
                    print(f"HTTP request to practices service failed: {e}")
                    return []  # Or handle more gracefully
                except Exception as e:
                    print(f"An error occurred processing practices: {e}")
                    import traceback

                    traceback.print_exc()
                    return []
        return results

    @strawberry.field
    async def user_roles(self, info: Info, user_id: UUID) -> List[UserRoleTypeGQL]:
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            user_model = await repo.get_user_by_id(uuid.UUID(str(user_id)))
            if not user_model:
                return []
            return [
                UserRoleTypeGQL(
                    id_=str(r.id_),
                    role=RoleGQL(r.role.value),
                    domain=DomainGQL(r.domain.value),
                    created_at=r.created_at,
                )
                for r in user_model.roles
            ]

    @strawberry.field
    async def user_service_links_by_user_id(self, info: Info, user_id: UUID) -> List[UserServiceLinkTypeGQL]:
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)  # Use UserRepository for user-service links
            link_models = await repo.list_user_services(uuid.UUID(str(user_id)))
            return [to_domain_user_service_link(link) for link in link_models]

    @strawberry.field
    async def list_coaches(self, info: Info, domain: Optional[DomainGQL] = None) -> List[UserTypeGQL]:
        """Lists all users with the 'COACH' role, optionally filtered by domain."""
        uow = await get_uow_from_info(info)
        domain_filter = DomainModel(domain.value) if domain else None
        async with uow:
            repo = UserRepository(session=uow.session)
            coaches = await repo.list_users_by_role(RoleModel.coach, domain=domain_filter)
            return [to_domain_user(coach) for coach in coaches]

    @strawberry.field
    async def list_clients(self, info: Info, domain: Optional[DomainGQL] = None) -> List[UserTypeGQL]:
        """
        Lists all clients who have an ACCEPTED association with the current user (who must be a coach).
        """
        current_user = await get_current_user_from_info(info)
        uow = await get_uow_from_info(info)
        domain_filter = DomainModel(domain.value) if domain else None

        async with uow:
            repo = UserRepository(uow.session)
            associations = await repo.list_associations_for_user(
                user_id=current_user.id_,
                as_role="coach",
                status=AssociationStatusModel.accepted,
                domain=domain_filter,
            )
            return [to_domain_user(assoc.client) for assoc in associations]

    @strawberry.field
    async def incoming_coaching_requests(self, info: Info) -> List[CoachClientAssociationGQL]:
        """Returns all pending association requests for the current user where they are the client."""
        uow = await get_uow_from_info(info)
        current_user = await get_current_user_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            # The repository method should handle filtering by status.
            associations = await repo.list_associations_for_user(
                current_user.id_, as_role="client", status=AssociationStatusModel.pending
            )
            return [to_domain_coach_client_association(assoc) for assoc in associations]

    @strawberry.field
    async def outgoing_coaching_requests(self, info: Info) -> List[CoachClientAssociationGQL]:
        """Returns all pending association requests for the current user where they are the coach."""
        uow = await get_uow_from_info(info)
        current_user = await get_current_user_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            # The repository method should handle filtering by status.
            associations = await repo.list_associations_for_user(
                current_user.id_, as_role="coach", status=AssociationStatusModel.pending
            )
            # This is a bit inefficient if the user has many associations,
            # as it filters in Python after fetching from DB.
            # A dedicated repository method would be better.
            # For now, this is a client-side filter:
            # outgoing = [
            #     to_domain_coach_client_association(assoc)
            #     for assoc in associations
            #     if assoc.requester_id == current_user.id_ and assoc.status == AssociationStatusModel.pending
            # ]
            return [to_domain_coach_client_association(assoc) for assoc in associations]

    @strawberry.field
    async def verify_coach_client_relationship(
        self, info: Info, coach_id: UUID, client_id: UUID, domain: DomainGQL
    ) -> bool:
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            is_verified = await repo.check_existing_association(
                coach_id=coach_id,
                client_id=client_id,
                domain=DomainModel(domain.value),
                status=AssociationStatusModel.accepted,
            )
            return is_verified

    # --- New Coaching Queries ---

    @strawberry.field
    async def myPendingCoachingRequests(self, info: Info) -> List[CoachingRequestGQL]:
        """Gets pending coaching requests where current user is the client."""
        current_user = await get_current_user_from_info(info)
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            relationships = await repo.get_pending_coaching_requests_for_client(current_user.id_)
            return [to_domain_coaching_request(rel) for rel in relationships]

    @strawberry.field
    async def myClients(self, info: Info) -> List[UserSummaryGQL]:
        """Gets accepted clients for current coach."""
        current_user = await get_current_user_from_info(info)
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            relationships = await repo.get_my_clients(current_user.id_)
            return [to_domain_user_summary(rel.client) for rel in relationships if rel.client]

    @strawberry.field
    async def myCoaches(self, info: Info) -> List[UserSummaryGQL]:
        """Gets accepted coaches for current client."""
        current_user = await get_current_user_from_info(info)
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            relationships = await repo.get_my_coaches(current_user.id_)
            return [to_domain_user_summary(rel.coach) for rel in relationships if rel.coach]

    @strawberry.field
    async def isCoachForClient(self, info: Info, clientId: UUID) -> bool:
        """Checks if current user is coach for the specified client."""
        current_user = await get_current_user_from_info(info)
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            return await repo.is_coach_for_client(
                coach_user_id=current_user.id_,
                client_user_id=uuid.UUID(str(clientId))
            )

    @strawberry.field
    async def searchUsers(self, info: Info, query: str) -> List[UserSummaryGQL]:
        """Search users by email or name."""
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            users = await repo.search_users(query, limit=10)
            return [to_domain_user_summary(user) for user in users]

    @strawberry.field
    async def searchUsers(self, info: Info, query: str) -> List[UserSummaryGQL]:
        """Search users by email or name."""
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            users = await repo.search_users(query, limit=10)
            return [to_domain_user_summary(user) for user in users]


# --- Input Types for Mutations ---
@strawberry.input
class UserCreateInput:
    supabase_id: str
    keycloak_id: Optional[str] = None


@strawberry.input
class UserUpdateInput:
    keycloak_id: Optional[str] = None
    # Add other updatable fields as necessary


@strawberry.input
class ServiceCreateInput:
    name: ServiceTypeGQL  # Use the GraphQL Enum for input
    description: Optional[str] = None
    url: Optional[str] = None  # New URL field


@strawberry.input
class ServiceUpdateInput:
    description: Optional[str] = None
    url: Optional[str] = None  # New URL field
    # Name update might be complex due to enum and uniqueness, handle with care if needed


@strawberry.input
class SchedulableCreateInput:
    name: str
    user_id: UUID
    service_id: UUID
    entity_id: UUID  # This is the foreign key to an entity in another service
    description: Optional[str] = None
    completed: Optional[bool] = False


@strawberry.input
class SchedulableUpdateInput:
    name: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    # entity_id, user_id, service_id are usually not updated on an existing schedulable.


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_user(self, info: Info, user_data: UserCreateInput) -> UserTypeGQL:
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            created_user_model = await repo.create_user(user_data.__dict__)
            await uow.commit()
            return to_domain_user(created_user_model)

    @strawberry.mutation
    async def update_user(self, info: Info, user_id: UUID, update_data: UserUpdateInput) -> Optional[UserTypeGQL]:
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            data_to_update = {k: v for k, v in update_data.__dict__.items() if v is not None}
            if not data_to_update:
                # Or raise an error if no fields to update are provided
                user_model = await repo.get_user_by_id(uuid.UUID(str(user_id)))
                return to_domain_user(user_model) if user_model else None

            updated_user_model = await repo.update_user(uuid.UUID(str(user_id)), data_to_update)
            if updated_user_model:
                await uow.commit()
                return to_domain_user(updated_user_model)
            return None

    @strawberry.mutation
    async def delete_user(self, info: Info, id: UUID) -> bool:
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            success = await repo.delete_user(uuid.UUID(str(id)))
            if success:
                await uow.commit()
            return success

    @strawberry.mutation
    async def create_service(self, info: Info, service_data: ServiceCreateInput) -> ServiceTypeGQL_Type:
        uow = await get_uow_from_info(info)
        async with uow:
            repo = ServiceRepository(session=uow.session)
            repo_data = {
                "name": SQLAlchemyServiceEnum(service_data.name.value),
                "description": service_data.description,
                "url": service_data.url,  # Add URL to repo_data
            }
            created_service_model = await repo.create_service(repo_data)
            await uow.commit()
            return to_domain_service(created_service_model)

    @strawberry.mutation
    async def update_service(
        self, info: Info, id: UUID, update_data: ServiceUpdateInput
    ) -> Optional[ServiceTypeGQL_Type]:
        uow = await get_uow_from_info(info)
        async with uow:
            repo = ServiceRepository(session=uow.session)
            # Filter out None values from input to only update provided fields
            data_to_update = {k: v for k, v in update_data.__dict__.items() if v is not None}
            if not data_to_update:
                # If no actual data is provided for update, just fetch and return the current state
                service_model = await repo.get_service_by_id(uuid.UUID(str(id)))
                return to_domain_service(service_model) if service_model else None

            updated_service_model = await repo.update_service(uuid.UUID(str(id)), data_to_update)
            if updated_service_model:
                await uow.commit()
                return to_domain_service(updated_service_model)
            return None

    @strawberry.mutation
    async def delete_service(self, info: Info, id: UUID) -> bool:
        uow = await get_uow_from_info(info)
        async with uow:
            repo = ServiceRepository(session=uow.session)
            success = await repo.delete_service(uuid.UUID(str(id)))
            if success:
                await uow.commit()
            return success

    @strawberry.mutation
    async def create_schedulable(self, info: Info, schedulable_data: SchedulableCreateInput) -> SchedulableTypeGQL:
        uow = await get_uow_from_info(info)
        async with uow:
            repo = SchedulableRepository(session=uow.session)
            repo_data = {
                "name": schedulable_data.name,
                "user_id": uuid.UUID(str(schedulable_data.user_id)),
                "service_id": uuid.UUID(str(schedulable_data.service_id)),
                "entity_id": uuid.UUID(str(schedulable_data.entity_id)),
                "description": schedulable_data.description,
                "completed": schedulable_data.completed if schedulable_data.completed is not None else False,
            }
            created_schedulable_model = await repo.create_schedulable(repo_data)
            await uow.commit()
            return to_domain_schedulable(created_schedulable_model)

    @strawberry.mutation
    async def update_schedulable(
        self, info: Info, id: UUID, update_data: SchedulableUpdateInput
    ) -> Optional[SchedulableTypeGQL]:
        uow = await get_uow_from_info(info)
        async with uow:
            repo = SchedulableRepository(session=uow.session)
            data_to_update = {k: v for k, v in update_data.__dict__.items() if v is not None}
            if not data_to_update:
                schedulable_model = await repo.get_schedulable_by_id(uuid.UUID(str(id)))
                return to_domain_schedulable(schedulable_model) if schedulable_model else None

            updated_schedulable_model = await repo.update_schedulable(uuid.UUID(str(id)), data_to_update)
            if updated_schedulable_model:
                await uow.commit()
                return to_domain_schedulable(updated_schedulable_model)
            return None

    @strawberry.mutation
    async def delete_schedulable(self, info: Info, id: UUID) -> bool:
        uow = await get_uow_from_info(info)
        async with uow:
            repo = SchedulableRepository(session=uow.session)
            success = await repo.delete_schedulable(uuid.UUID(str(id)))
            if success:
                await uow.commit()
            return success

    @strawberry.mutation
    async def link_user_to_service(
        self, info: Info, user_id: UUID, service_id: UUID
    ) -> Optional[UserServiceLinkTypeGQL]:
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)  # UserRepository handles linking
            link_model = await repo.link_user_to_service(uuid.UUID(str(user_id)), uuid.UUID(str(service_id)))
            if link_model:
                await uow.commit()
                return to_domain_user_service_link(link_model)
            return None

    @strawberry.mutation
    async def unlink_user_from_service(self, info: Info, user_id: UUID, service_id: UUID) -> bool:
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)  # UserRepository handles unlinking
            success = await repo.unlink_user_from_service(uuid.UUID(str(user_id)), uuid.UUID(str(service_id)))
            if success:
                await uow.commit()
            return success

    @strawberry.mutation
    async def get_or_create_user(self, info: Info, supabase_id: str, email: Optional[str] = None, first_name: Optional[str] = None, last_name: Optional[str] = None) -> UserTypeGQL:
        """Get an existing user by Supabase ID or create a new one if not found."""
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            profile_data = {}
            if email:
                profile_data['email'] = email
            if first_name:
                profile_data['first_name'] = first_name
            if last_name:
                profile_data['last_name'] = last_name
            user_model = await repo.get_or_create_user(supabase_id, profile_data if profile_data else None)
            await uow.commit()
            return to_domain_user(user_model)

    @strawberry.mutation
    async def assign_role_to_user(
        self, info: Info, user_id: UUID, role: RoleGQL, domain: DomainGQL
    ) -> Optional[UserRoleTypeGQL]:
        """Assigns a role to a user within a specific domain."""
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            # Convert GraphQL enums to SQLAlchemy enums before passing to repository
            role_model = await repo.assign_role_to_user(
                user_id=uuid.UUID(str(user_id)),
                role=RoleModel(role.value),
                domain=DomainModel(domain.value),
            )
            if role_model:
                await uow.commit()
                # Convert the resulting model back to a domain model for the GraphQL type
                return to_domain_user_role(role_model)
            return None

    @strawberry.mutation
    async def remove_role_from_user(self, info: Info, user_id: UUID, role: RoleGQL, domain: DomainGQL) -> bool:
        """Removes a role from a user within a specific domain."""
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            success = await repo.remove_role_from_user(
                user_id=uuid.UUID(str(user_id)),
                role=RoleModel(role.value),
                domain=DomainModel(domain.value),
            )
            if success:
                await uow.commit()
            return success

    # --- Coach-Client Association Mutations ---
    @strawberry.mutation
    async def send_coaching_request(self, info: Info, client_id: UUID, domain: DomainGQL) -> CoachClientAssociationGQL:
        """Sends a coaching request from the current user (as coach) to a client."""
        current_user = await get_current_user_from_info(info)  # This user is the coach
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            # Optional: Verify the current user has a 'COACH' role in this domain.
            if not any(r.role == DomainModelRole.COACH and r.domain.value == domain.value for r in current_user.roles):
                raise Exception(f"You do not have a COACH role in the {domain.value} domain.")

            association = await repo.create_association_request(
                coach_id=current_user.id_,
                client_id=uuid.UUID(str(client_id)),
                requester_id=current_user.id_,
                domain=DomainModel(domain.value),
            )
            await uow.commit()
            return to_domain_coach_client_association(association)

    @strawberry.mutation
    async def request_coaching(self, info: Info, coach_id: UUID, domain: DomainGQL) -> CoachClientAssociationGQL:
        """Sends a request for coaching from the current user (as client) to a coach."""
        current_user = await get_current_user_from_info(info)  # This user is the client
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            association = await repo.create_association_request(
                coach_id=uuid.UUID(str(coach_id)),
                client_id=current_user.id_,
                requester_id=current_user.id_,
                domain=DomainModel(domain.value),
            )
            await uow.commit()
            return to_domain_coach_client_association(association)

    @strawberry.mutation
    async def respond_to_coaching_request(
        self, info: Info, association_id: UUID, accept: bool
    ) -> Optional[CoachClientAssociationGQL]:
        """Accepts or rejects a pending coaching request."""
        current_user = await get_current_user_from_info(info)
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            association = await repo.get_association_by_id(uuid.UUID(str(association_id)))

            if not association:
                raise Exception("Association request not found.")
            if association.status != AssociationStatusModel.pending:
                raise Exception("This request is no longer pending.")
            # The user responding must NOT be the one who sent the request.
            if association.requester_id == current_user.id_:
                raise Exception("You cannot respond to your own request.")

            # The user responding MUST be either the coach or the client in the association.
            # This implicitly means they are the recipient.
            if not (association.coach_id == current_user.id_ or association.client_id == current_user.id_):
                raise Exception("You are not a party to this coaching request.")

            new_status = AssociationStatusModel.accepted if accept else AssociationStatusModel.rejected
            updated_association = await repo.update_association_status(
                association_id=uuid.UUID(str(association_id)), status=new_status
            )
            await uow.commit()
            return to_domain_coach_client_association(updated_association) if updated_association else None

    @strawberry.mutation
    async def terminate_coaching_relationship(self, info: Info, association_id: UUID) -> bool:
        """Terminates an active coaching relationship. Can be initiated by coach or client."""
        current_user = await get_current_user_from_info(info)
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            association = await repo.get_association_by_id(uuid.UUID(str(association_id)))

            if not association:
                raise Exception("Association not found.")
            if association.status != AssociationStatusModel.accepted:
                raise Exception("Only accepted relationships can be terminated.")
            # Ensure the current user is part of this relationship
            if association.coach_id != current_user.id_ and association.client_id != current_user.id_:
                raise Exception("You are not part of this coaching relationship.")

            await repo.update_association_status(
                association_id=uuid.UUID(str(association_id)), status=AssociationStatusModel.terminated
            )
            await uow.commit()
            return True

    @strawberry.mutation
    async def terminateCoachingForClient(self, info: Info, clientId: UUID) -> bool:
        """Coach convenience mutation: terminate the accepted relationship with a given client."""
        current_user = await get_current_user_from_info(info)
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            # Find the accepted association between current coach and the client
            associations = await repo.list_associations_for_user(
                user_id=current_user.id_, as_role="coach", status=AssociationStatusModel.accepted
            )
            target = next((a for a in associations if str(a.client_id) == str(clientId)), None)
            if not target:
                raise Exception("No accepted coaching relationship found for this client.")
            await repo.update_association_status(
                association_id=uuid.UUID(str(target.id_)), status=AssociationStatusModel.terminated
            )
            await uow.commit()
            return True

    # --- New Simplified Coaching Mutations (per plan) ---

    @strawberry.mutation
    async def requestCoaching(self, info: Info, clientEmail: str) -> bool:
        """Coach requests to coach a client by email. Creates user if not exists."""
        current_user = await get_current_user_from_info(info)
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            
            # Check if user has coach role
            if not any(r.role == DomainModelRole.COACH and r.domain == DomainModelDomain.PRACTICES for r in current_user.roles):
                raise Exception("You do not have a COACH role in the practices domain.")
            
            try:
                await repo.create_coaching_request(current_user.id_, clientEmail)
                await uow.commit()
                return True
            except ValueError as e:
                raise Exception(str(e))
            except Exception as e:
                raise Exception(f"Failed to create coaching request: {str(e)}")

    @strawberry.mutation
    async def requestCoachingByUserId(self, info: Info, clientUserId: UUID) -> bool:
        """Coach requests to coach a client by user ID (for testing)."""
        current_user = await get_current_user_from_info(info)
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            
            # Check if current user has coach role in practices domain
            if not any(r.role == DomainModelRole.COACH and r.domain == DomainModelDomain.PRACTICES for r in current_user.roles):
                raise Exception("You do not have a COACH role in the practices domain.")
            
            try:
                await repo.request_coaching_by_user_id(
                    coach_user_id=current_user.id_,
                    client_user_id=uuid.UUID(str(clientUserId))
                )
                await uow.commit()
                return True
            except ValueError as e:
                raise Exception(str(e))

    @strawberry.mutation
    async def acceptCoaching(self, info: Info, coachUserId: strawberry.ID) -> bool:
        """Client accepts a coaching request from a coach."""
        current_user = await get_current_user_from_info(info)
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            
            relationship = await repo.accept_coaching_request(
                client_user_id=current_user.id_,
                coach_user_id=uuid.UUID(str(coachUserId))
            )
            
            if not relationship:
                raise Exception("No pending coaching request found from this coach.")
            
            await uow.commit()
            return True

    @strawberry.mutation
    async def rejectCoaching(self, info: Info, coachUserId: strawberry.ID) -> bool:
        """Client rejects a coaching request from a coach."""
        current_user = await get_current_user_from_info(info)
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            
            success = await repo.reject_coaching_request(
                client_user_id=current_user.id_,
                coach_user_id=uuid.UUID(str(coachUserId))
            )
            
            if not success:
                raise Exception("No pending coaching request found from this coach.")
            
            await uow.commit()
            return True

    @strawberry.mutation
    async def assignRoleToUser(self, info: Info, userId: strawberry.ID, role: str, domain: str) -> bool:
        """Assigns a role to a user in a specific domain."""
        uow = await get_uow_from_info(info)
        async with uow:
            repo = UserRepository(session=uow.session)
            
            try:
                # Convert string inputs to enum values
                role_enum = RoleModel(role)
                domain_enum = DomainModel(domain)
                
                await repo.assign_role_to_user(
                    user_id=uuid.UUID(str(userId)),
                    role=role_enum,
                    domain=domain_enum
                )
                await uow.commit()
                return True
            except ValueError as e:
                raise Exception(f"Invalid role or domain: {str(e)}")
            except Exception as e:
                raise Exception(f"Failed to assign role: {str(e)}")




__all__ = ["Query", "Mutation"]
