import uuid
from typing import Optional

from practices.domain.models import DomainProgramEnrollment
from practices.repository.models import EnrollmentStatus
from practices.repository.repositories import EnrollmentRepository


class EnrollmentService:
    """
    Provides business logic for managing program enrollments.
    This service layer sits between the GraphQL resolvers and the data repository.
    """

    def __init__(self, repository: EnrollmentRepository):
        self.repository = repository

    async def enroll_user(
        self,
        program_id: uuid.UUID,
        user_to_enroll_id: uuid.UUID,
        enrolling_user_id: uuid.UUID,
    ) -> DomainProgramEnrollment:
        """
        Enrolls a user into a program, handling the creation of the enrollment record.

        Args:
            program_id: The ID of the program to enroll in.
            user_to_enroll_id: The ID of the user being enrolled.
            enrolling_user_id: The ID of the user performing the enrollment.
                               For self-enrollment, this is the same as user_to_enroll_id.

        Returns:
            The domain model for the newly created (or existing) enrollment.
        """
        enrollment_model = await self.repository.create_enrollment(
            program_id=program_id,
            user_id=user_to_enroll_id,
            enrolled_by_user_id=enrolling_user_id,
        )
        return DomainProgramEnrollment.model_validate(enrollment_model)

    async def update_enrollment_status(
        self, enrollment_id: uuid.UUID, status: str
    ) -> Optional[DomainProgramEnrollment]:
        """
        Updates the status of a specific enrollment.
        If the status is set to COMPLETED, it also clears the current practice link.
        """
        status_enum = EnrollmentStatus(status)
        update_data = {"status": status_enum}

        if status_enum == EnrollmentStatus.COMPLETED:
            update_data["current_practice_link_id"] = None

        enrollment_model = await self.repository.update(enrollment_id, update_data)
        if enrollment_model:
            return DomainProgramEnrollment.model_validate(enrollment_model)
        return None
