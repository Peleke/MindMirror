import uuid

import pytest

from practices.repository.models import EnrollmentStatus
from practices.repository.repositories import EnrollmentRepository


@pytest.mark.asyncio
class TestEnrollmentRepository:
    async def test_create_enrollment(self, enrollment_repository: EnrollmentRepository, seed_db: dict):
        """Verify successful creation of a new enrollment."""
        program = seed_db["programs"][0]
        client_two_id = seed_db["client_user_two"].id
        coach_id = seed_db["coach_user"].id

        # To avoid conflicts with existing seeded enrollment,
        # let's create a new, distinct enrollment.
        new_enrollment = await enrollment_repository.create_enrollment(
            program_id=program.id_,
            user_id=client_two_id,
            enrolled_by_user_id=coach_id,
        )

        assert new_enrollment is not None
        assert new_enrollment.program_id == program.id_
        assert new_enrollment.user_id == client_two_id
        assert new_enrollment.enrolled_by_user_id == coach_id
        assert new_enrollment.status == EnrollmentStatus.ACTIVE

    async def test_create_enrollment_handles_existing_inactive(
        self, enrollment_repository: EnrollmentRepository, seed_db: dict, session
    ):
        """Verify that creating an enrollment for an inactive one reactivates it."""
        existing_enrollment = seed_db["enrollments"][0]
        program_id = existing_enrollment.program_id
        user_id = existing_enrollment.user_id

        # First, make the existing enrollment inactive
        existing_enrollment.status = EnrollmentStatus.INACTIVE
        session.add(existing_enrollment)
        await session.commit()
        await session.refresh(existing_enrollment)
        assert existing_enrollment.status == EnrollmentStatus.INACTIVE

        # Attempt to "re-create" the enrollment
        reactivated_enrollment = await enrollment_repository.create_enrollment(
            program_id=program_id,
            user_id=user_id,
        )

        assert reactivated_enrollment is not None
        assert reactivated_enrollment.id_ == existing_enrollment.id_
        assert reactivated_enrollment.status == EnrollmentStatus.ACTIVE

    async def test_get_enrollment_by_id(self, enrollment_repository: EnrollmentRepository, seed_db: dict):
        """Verify fetching an enrollment by its ID."""
        enrollment_id = seed_db["enrollments"][0].id_
        fetched_enrollment = await enrollment_repository.get_enrollment_by_id(enrollment_id)

        assert fetched_enrollment is not None
        assert fetched_enrollment.id_ == enrollment_id
        assert fetched_enrollment.program_id == seed_db["programs"][0].id_

    async def test_get_enrollments_for_user(self, enrollment_repository: EnrollmentRepository, seed_db: dict):
        """Verify fetching all enrollments for a specific user."""
        client_one_id = seed_db["client_user_one"].id
        enrollments = await enrollment_repository.get_enrollments_for_user(client_one_id)

        assert enrollments is not None
        assert len(enrollments) >= 1
        assert enrollments[0].user_id == client_one_id
        assert enrollments[0].id_ == seed_db["enrollments"][0].id_

    async def test_get_enrollments_for_program(self, enrollment_repository: EnrollmentRepository, seed_db: dict):
        """Verify fetching all enrollments for a specific program."""
        program_id = seed_db["programs"][0].id_
        enrollments = await enrollment_repository.get_enrollments_for_program(program_id)

        assert enrollments is not None
        assert len(enrollments) >= 2  # Both users are enrolled
        assert enrollments[0].program_id == program_id

    async def test_update_enrollment_status(self, enrollment_repository: EnrollmentRepository, seed_db: dict):
        """Verify updating the status of an enrollment."""
        enrollment_id = seed_db["enrollments"][0].id_
        updated_enrollment = await enrollment_repository.update_enrollment_status(
            enrollment_id, EnrollmentStatus.COMPLETED
        )

        assert updated_enrollment is not None
        assert updated_enrollment.id_ == enrollment_id
        assert updated_enrollment.status == EnrollmentStatus.COMPLETED

        # Verify it's persisted
        fetched_enrollment = await enrollment_repository.get_enrollment_by_id(enrollment_id)
        assert fetched_enrollment.status == EnrollmentStatus.COMPLETED

    async def test_get_enrollment_by_id_not_found(self, enrollment_repository: EnrollmentRepository, create_tables):
        """Verify getting a non-existent enrollment returns None."""
        non_existent_id = uuid.uuid4()
        fetched_enrollment = await enrollment_repository.get_enrollment_by_id(non_existent_id)
        assert fetched_enrollment is None
