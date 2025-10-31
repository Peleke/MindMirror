import uuid
from datetime import date, timedelta
from typing import Optional

from sqlalchemy.orm import selectinload

from practices.domain.models.enrollment import DomainProgramEnrollment
from practices.repository.models.enrollment import (
    EnrollmentStatus,
    ProgramEnrollmentModel,
)
from practices.repository.models.program import ProgramModel
from practices.repository.models.progress import ScheduledPracticeModel
from practices.repository.repositories import (
    EnrollmentRepository,
    ScheduledPracticeRepository,
)


class ProgressServiceError(Exception):
    pass


def _to_domain_enrollment(repo_enrollment: ProgramEnrollmentModel) -> DomainProgramEnrollment:
    """Converts a repository-layer enrollment model to a domain model."""
    return DomainProgramEnrollment.model_validate(repo_enrollment)


class ProgressService:
    def __init__(self, enrollment_repo: EnrollmentRepository, scheduled_practice_repo: ScheduledPracticeRepository):
        self._enrollment_repo = enrollment_repo
        self._scheduled_practice_repo = scheduled_practice_repo

    async def complete_and_advance_progress(
        self, enrollment_id: uuid.UUID, user_id: uuid.UUID
    ) -> DomainProgramEnrollment:
        enrollment = await self._enrollment_repo.get_enrollment_by_id(
            enrollment_id,
            options=[selectinload(ProgramEnrollmentModel.program).selectinload(ProgramModel.practice_links)],
        )

        if not enrollment:
            raise ProgressServiceError("Enrollment not found.")

        if enrollment.user_id != user_id:
            raise ProgressServiceError("User is not authorized to update this enrollment.")

        if not enrollment.current_practice_link_id:
            raise ProgressServiceError("Enrollment has no current practice to complete.")

        program = enrollment.program
        if not program:
            raise ProgressServiceError("Program not found for this enrollment.")

        practice_links = sorted(program.practice_links, key=lambda link: link.sequence_order)

        current_link_index = -1
        for i, link in enumerate(practice_links):
            if link.id_ == enrollment.current_practice_link_id:
                current_link_index = i
                break

        if current_link_index == -1:
            raise ProgressServiceError("Current practice link not found in program.")

        if current_link_index + 1 < len(practice_links):
            next_practice_link = practice_links[current_link_index + 1]
            enrollment.current_practice_link_id = next_practice_link.id_

            new_scheduled_practice = ScheduledPracticeModel(
                enrollment_id=enrollment.id_,
                practice_template_id=next_practice_link.practice_template_id,
                scheduled_date=date.today() + timedelta(days=1),
            )
            await self._scheduled_practice_repo.add(new_scheduled_practice)
        else:
            enrollment.status = EnrollmentStatus.COMPLETED
            enrollment.current_practice_link_id = None

        return _to_domain_enrollment(enrollment)

    async def defer_practice(self, enrollment_id: uuid.UUID, user_id: uuid.UUID, mode: str = "push") -> None:
        enrollment = await self._enrollment_repo.get_enrollment_by_id(enrollment_id)
        if not enrollment or enrollment.user_id != user_id:
            raise ProgressServiceError("User is not authorized to update this enrollment.")

        today = date.today()
        if mode == "push":
            todays_practices = await self._scheduled_practice_repo.list(
                enrollment_ids=[enrollment.id_], from_date=today
            )

            if todays_practices:
                practice_to_defer = todays_practices[0]
                practice_to_defer.scheduled_date += timedelta(days=1)

        elif mode == "shift":
            all_practices = await self._scheduled_practice_repo.list(enrollment_ids=[enrollment.id_])
            practices_to_shift = [p for p in all_practices if p.scheduled_date >= today]

            for practice in practices_to_shift:
                practice.scheduled_date += timedelta(days=1)
