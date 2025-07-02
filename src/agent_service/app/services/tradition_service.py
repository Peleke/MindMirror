from typing import List

from agent_service.app.repositories.tradition_repository import TraditionRepository


class TraditionService:
    """
    A service layer for handling business logic related to traditions.
    """

    def __init__(self, repository: TraditionRepository):
        self._repository = repository

    def list_traditions(self) -> List[str]:
        """
        Retrieves a list of all available traditions.
        """
        return self._repository.list_traditions()
