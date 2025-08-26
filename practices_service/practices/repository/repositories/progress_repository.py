from practices.repository.models.progress import ScheduledPracticeModel
from practices.repository.repositories.base_repository import SQLAlchemyRepository


class ProgressRepository(SQLAlchemyRepository):
    _model = ScheduledPracticeModel
