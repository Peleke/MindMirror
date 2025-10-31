import pytest

from practices.repository.models import EnrollmentStatus
from practices.repository.repositories import EnrollmentRepository, ProgramRepository
from practices.service.services import EnrollmentService


@pytest.mark.asyncio
class TestEnrollmentService:
    async def test_enroll_user(
        self,
        uow,
        seed_db,
    ):
        program_repo = ProgramRepository(uow.session)
        enrollment_repo = EnrollmentRepository(uow.session)
        service = EnrollmentService(enrollment_repo)

        coach_id = seed_db["coach_user"].id
        new_program_data = {
            "name": "Enrollment Service Test Program",
            "description": "A fresh program for testing enrollment.",
            "level": "BEGINNER",
            "user_id": coach_id,
        }
        created_program = await program_repo.create_program_with_links_and_tags(new_program_data)

        client_to_enroll_id = seed_db["client_user_one"].id
        enrolling_user_id = coach_id

        enrollment = await service.enroll_user(
            program_id=created_program.id_,
            user_to_enroll_id=client_to_enroll_id,
            enrolling_user_id=enrolling_user_id,
        )

        assert enrollment is not None
        assert enrollment.program_id == created_program.id_
        assert enrollment.user_id == client_to_enroll_id
        assert enrollment.status.value == EnrollmentStatus.ACTIVE.value

    async def test_update_enrollment_status(
        self,
        uow,
        seed_db,
    ):
        enrollment_repo = EnrollmentRepository(uow.session)
        service = EnrollmentService(enrollment_repo)

        enrollment_to_update = seed_db["enrollments"][0]

        updated_enrollment = await service.update_enrollment_status(
            enrollment_id=enrollment_to_update.id_, status="completed"
        )

        assert updated_enrollment is not None
        assert updated_enrollment.id_ == enrollment_to_update.id_
        assert updated_enrollment.status.value == EnrollmentStatus.COMPLETED.value

        # Verify the change was persisted
        persisted_enrollment = await enrollment_repo.get_by_id(enrollment_to_update.id_)
        assert persisted_enrollment is not None
        assert persisted_enrollment.status == EnrollmentStatus.COMPLETED
