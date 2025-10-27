import uuid
from typing import Any, Dict, Optional, Sequence

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from users.repository.models import (
    AssociationStatusModel,
    CoachClientAssociationModel,
    DomainModel,
    RoleModel,
    SchedulableModel,
    ServiceEnum,
    ServiceModel,
    UserModel,
    UserServicesModel,
)
from users.repository.repositories import (
    SchedulableRepository,
    ServiceRepository,
    UserRepository,
)
from users.repository.uow import UnitOfWork


@pytest.mark.asyncio
class TestUserRepository:
    # USER ENTITY TESTS (using UserRepository)
    async def test_create_and_get_user(self, session: AsyncSession):
        repo = UserRepository(session)
        supabase_id = f"test_supabase_id_{uuid.uuid4()}"
        user_data = {"supabase_id": supabase_id, "keycloak_id": None}

        created_user = await repo.create_user(user_data)
        await session.commit()

        assert created_user is not None
        assert created_user.id_ is not None
        assert created_user.supabase_id == supabase_id

        fetched_user = await repo.get_user_by_id(created_user.id_)
        assert fetched_user is not None
        assert fetched_user.id_ == created_user.id_

    async def test_get_user_by_supabase_id(self, seed_data: Dict[str, Any], uow: UnitOfWork):
        user1_from_seed: Optional[UserModel] = seed_data.get("user1_coach")
        assert user1_from_seed is not None, "User1 not found in seed_data"

        async with uow:
            user_repo = UserRepository(uow.session)
            fetched_user = await user_repo.get_user_by_supabase_id(user1_from_seed.supabase_id)

        assert fetched_user is not None
        assert fetched_user.id_ == user1_from_seed.id_

    async def test_list_users(self, seed_data: Dict[str, Any], uow: UnitOfWork):
        assert seed_data.get("user1_coach") is not None, "user1_coach missing from seed_data"
        assert seed_data.get("user2_client") is not None, "user2_client missing from seed_data"

        async with uow:
            user_repo = UserRepository(uow.session)
            users = await user_repo.list_users()

        assert users is not None
        assert len(users) >= 2
        supabase_ids = [u.supabase_id for u in users]
        assert seed_data["user1_coach"].supabase_id in supabase_ids
        assert seed_data["user2_client"].supabase_id in supabase_ids

    async def test_update_user(self, seed_data: Dict[str, Any], uow: UnitOfWork):
        user_to_update: Optional[UserModel] = seed_data.get("user1_coach")
        assert user_to_update is not None, "user1_coach not found in seed_data for update"

        new_keycloak_id = f"test_keycloak_id_{uuid.uuid4()}"
        update_data = {"keycloak_id": new_keycloak_id}

        async with uow:
            user_repo = UserRepository(uow.session)
            updated_user = await user_repo.update_user(user_to_update.id_, update_data)

        assert updated_user is not None
        assert updated_user.id_ == user_to_update.id_
        assert updated_user.keycloak_id == new_keycloak_id

        async with UnitOfWork(session_factory=uow.session_factory) as read_uow:
            user_repo_read = UserRepository(read_uow.session)
            refetched_user = await user_repo_read.get_user_by_id(user_to_update.id_)
        assert refetched_user is not None
        assert refetched_user.keycloak_id == new_keycloak_id

    async def test_delete_user(self, uow: UnitOfWork, session: AsyncSession):
        supabase_id_to_delete = f"delete_me_{uuid.uuid4()}"
        user_id_to_delete: Optional[uuid.UUID] = None

        user_repo_create = UserRepository(session)
        user_to_delete = await user_repo_create.create_user({"supabase_id": supabase_id_to_delete})
        await session.commit()
        user_id_to_delete = user_to_delete.id_
        assert user_id_to_delete is not None

        async with uow:
            user_repo_del = UserRepository(uow.session)
            delete_result = await user_repo_del.delete_user(user_id_to_delete)
            assert delete_result is True

        async with UnitOfWork(session_factory=uow.session_factory) as verify_uow:
            user_repo_verify = UserRepository(verify_uow.session)
            fetched_user = await user_repo_verify.get_user_by_id(user_id_to_delete)
            assert fetched_user is None

    # USER-SERVICE LINKING TESTS (using UserRepository and ServiceRepository for setup)
    async def test_link_and_get_user_services(self, seed_data: Dict[str, Any], uow: UnitOfWork, session: AsyncSession):
        user3: Optional[UserModel] = seed_data.get("user3_client")
        # Get practice_service_id using ServiceRepository for setup, as it's not linked by default in seed_data for user2
        service_repo_setup = ServiceRepository(session)  # Use direct session for setup before UoW block
        sleep_service = await service_repo_setup.get_service_by_name(ServiceEnum.sleep)
        if not sleep_service:
            sleep_service = await service_repo_setup.create_service({"name": ServiceEnum.sleep})
        await session.commit()  # Commit the read, though not strictly necessary for get

        assert user3 is not None, "User3 not found in seed_data"
        assert sleep_service is not None, "Sleep service not found"
        assert sleep_service.id_ is not None

        link: Optional[UserServicesModel] = None
        async with uow:  # UoW for the main test operations
            user_repo = UserRepository(uow.session)

            # Verify user3 is not initially linked to sleep service
            existing_link = await user_repo.get_user_service_link(user3.id_, sleep_service.id_)
            assert existing_link is None, "User3 should not be pre-linked to sleep service"

            link = await user_repo.link_user_to_service(user3.id_, sleep_service.id_)

        assert link is not None
        assert link.user_id == user3.id_
        assert link.service_id == sleep_service.id_
        assert link.active is True

        async with UnitOfWork(session_factory=uow.session_factory) as read_uow:
            user_repo_read = UserRepository(read_uow.session)
            user_services = await user_repo_read.list_user_services(user3.id_)
            found_link = any(us.service_id == sleep_service.id_ and us.active for us in user_services)
            assert found_link, "Newly created link for user3 and sleep service not found or inactive"

    async def test_unlink_user_from_service(self, seed_data: Dict[str, Any], uow: UnitOfWork):
        user1_linked: Optional[UserModel] = seed_data.get("user1_coach")
        meals_service: Optional[ServiceModel] = seed_data.get("service_meals")
        assert user1_linked is not None, "user1_coach not found in seed_data"
        assert meals_service is not None, "Meals service not found in seed_data"
        assert meals_service.id_ is not None

        async with UnitOfWork(session_factory=uow.session_factory) as verify_uow:
            user_repo_verify = UserRepository(verify_uow.session)
            initial_link = await user_repo_verify.get_user_service_link(user1_linked.id_, meals_service.id_)
        assert initial_link is not None, "Link between user1 and meals should exist from seed_data"
        assert initial_link.active is True, "Link should be active initially"

        async with uow:
            user_repo = UserRepository(uow.session)
            unlink_result = await user_repo.unlink_user_from_service(user1_linked.id_, meals_service.id_)
            assert unlink_result is True

        async with UnitOfWork(session_factory=uow.session_factory) as read_uow:
            user_repo_read = UserRepository(read_uow.session)
            final_link = await user_repo_read.get_user_service_link(user1_linked.id_, meals_service.id_)
            assert final_link is None, "Link should be deleted after unlink operation"

    async def test_list_user_services(self, seed_data: Dict[str, Any], uow: UnitOfWork):
        user1: Optional[UserModel] = seed_data.get("user1_coach")
        meals_service: Optional[ServiceModel] = seed_data.get("service_meals")
        assert user1 is not None, "user1_coach not found in seed_data"
        assert meals_service is not None, "Meals service (from seed_data) not found"

        async with uow:
            user_repo = UserRepository(uow.session)
            user_services = await user_repo.list_user_services(user1.id_)

        assert user_services is not None
        assert len(user_services) >= 1

        found_meals_link = False
        for link_item in user_services:
            assert link_item.service is not None
            if link_item.service.id_ == meals_service.id_:
                found_meals_link = True
                break
        assert (
            found_meals_link
        ), f"user1_coach should be linked to the MEALS service (ID: {meals_service.id_}) as per seed_data"

    # Placeholder for tests that would go into test_service_repository.py
    # async def test_create_and_get_service(self, session: AsyncSession):
    # async def test_get_all_services(self, seed_data: Dict[str, Any], uow: UnitOfWork, service_repository: ServiceRepository):
    # async def test_explicit_create_and_get_service(self, uow: UnitOfWork, service_repository: ServiceRepository):

    # Placeholder for tests that would go into test_schedulable_repository.py
    # async def test_create_and_get_schedulables(self, seed_data: Dict[str, Any], uow: UnitOfWork, service_repository: ServiceRepository, schedulable_repository: SchedulableRepository):
    # async def test_list_schedulables_by_user(self, seed_data: Dict[str, Any], uow: UnitOfWork, schedulable_repository: SchedulableRepository):

    # Add more tests as needed for update, delete, edge cases, etc.


@pytest.mark.asyncio
class TestUserAssociationRepository:
    """Tests for Role and Coach-Client Association logic in UserRepository."""

    async def test_assign_and_get_user_roles(self, seed_data, uow: UnitOfWork):
        coach: UserModel = seed_data["user1_coach"]
        async with uow:
            repo = UserRepository(uow.session)
            roles = await repo.get_user_roles(coach.id_)

        assert roles is not None
        assert len(roles) >= 2  # Has roles in PRACTICES and MEALS
        assert any(r.role == RoleModel.coach and r.domain == DomainModel.practices for r in roles)

    async def test_create_association_request(self, seed_data, uow: UnitOfWork):
        coach: UserModel = seed_data["user1_coach"]
        client: UserModel = seed_data["user2_client"]
        # This association is already accepted in the seed data for a different domain
        # Let's try to create a new one in a new domain
        async with uow:
            repo = UserRepository(uow.session)
            new_association = await repo.create_association_request(
                coach_id=coach.id_,
                client_id=client.id_,
                requester_id=coach.id_,
                domain=DomainModel.sleep,
            )
            await uow.commit()

            assert new_association is not None
            assert new_association.status == AssociationStatusModel.pending
            assert new_association.coach_id == coach.id_
            assert new_association.client_id == client.id_

    async def test_create_duplicate_association_request_fails(self, seed_data, uow: UnitOfWork):
        coach: UserModel = seed_data["user1_coach"]
        client: UserModel = seed_data["user2_client"]  # assoc_accepted is between these two in PRACTICES domain

        with pytest.raises(ValueError, match="An active or pending association request already exists"):
            async with uow:
                repo = UserRepository(uow.session)
                # Attempt to create another request where one already exists (it's ACCEPTED in seed)
                await repo.create_association_request(
                    coach_id=coach.id_,
                    client_id=client.id_,
                    requester_id=client.id_,
                    domain=DomainModel.practices,
                )

    async def test_update_association_status(self, seed_data, uow: UnitOfWork):
        pending_assoc: CoachClientAssociationModel = seed_data["assoc_pending"]
        async with uow:
            repo = UserRepository(uow.session)
            updated = await repo.update_association_status(pending_assoc.id_, AssociationStatusModel.accepted)
            await uow.commit()

            assert updated is not None
            assert updated.status == AssociationStatusModel.accepted

            refetched = await repo.get_association_by_id(pending_assoc.id_)
            assert refetched.status == AssociationStatusModel.accepted

    async def test_get_association_by_id(self, seed_data, uow: UnitOfWork):
        accepted_assoc: CoachClientAssociationModel = seed_data["assoc_accepted"]
        async with uow:
            repo = UserRepository(uow.session)
            fetched = await repo.get_association_by_id(accepted_assoc.id_)

            assert fetched is not None
            assert fetched.id_ == accepted_assoc.id_
            assert fetched.status == AssociationStatusModel.accepted
            assert fetched.coach is not None
            assert fetched.client is not None
            assert fetched.coach.supabase_id == "coach_user_1"
            assert fetched.client.supabase_id == "client_user_1"

    async def test_list_associations_for_user(self, seed_data, uow: UnitOfWork):
        coach: UserModel = seed_data["user1_coach"]
        client: UserModel = seed_data["user2_client"]

        async with uow:
            repo = UserRepository(uow.session)
            # Associations where user1 is the coach
            coach_assocs = await repo.list_associations_for_user(coach.id_, as_role="coach")
            assert len(coach_assocs) == 3  # accepted, pending, rejected
            # Associations where user2 is the client
            client_assocs = await repo.list_associations_for_user(client.id_, as_role="client")
            assert len(client_assocs) == 2  # accepted, rejected
            # Filter by status
            pending_coach_assocs = await repo.list_associations_for_user(
                coach.id_, as_role="coach", status=AssociationStatusModel.pending
            )
            assert len(pending_coach_assocs) == 1
            assert pending_coach_assocs[0].client.supabase_id == "client_user_2"

    async def test_check_existing_association(self, seed_data, uow: UnitOfWork):
        coach: UserModel = seed_data["user1_coach"]
        client1: UserModel = seed_data["user2_client"]
        client2: UserModel = seed_data["user3_client"]
        accepted_assoc: CoachClientAssociationModel = seed_data["assoc_accepted"]
        rejected_assoc: CoachClientAssociationModel = seed_data["assoc_rejected"]

        async with uow:
            repo = UserRepository(uow.session)
            # Should be true for the accepted relationship
            assert (
                await repo.check_existing_association(
                    coach.id_, client1.id_, DomainModel.practices, status=AssociationStatusModel.accepted
                )
                is True
            )
            # Should be false for a pending relationship when checking for accepted
            assert (
                await repo.check_existing_association(
                    coach.id_, client2.id_, DomainModel.practices, status=AssociationStatusModel.accepted
                )
                is False
            )
            # Should be true for a pending relationship if not filtering by status
            assert await repo.check_existing_association(coach.id_, client2.id_, DomainModel.practices) is True
            # Should be true for a rejected relationship if not filtering by status
            assert await repo.check_existing_association(coach.id_, client1.id_, rejected_assoc.domain) is True
            # Should be false for a rejected relationship when checking for accepted
            assert (
                await repo.check_existing_association(
                    coach.id_, client1.id_, rejected_assoc.domain, status=AssociationStatusModel.accepted
                )
                is False
            )
