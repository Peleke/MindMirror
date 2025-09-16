from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..repository.movements_repo import MovementsRepoPg


class ExerciseDBLocalClient:
    def __init__(self, repo: MovementsRepoPg):
        self.repo = repo

    async def search(self, term: Optional[str], body_region: Optional[str], equipment: Optional[str], limit: int, offset: int = 0) -> List[Dict[str, Any]]:
        rows = await self.repo.search(searchTerm=term, bodyRegion=body_region, equipment=equipment, limit=limit, offset=offset)
        # Normalize minimal shape
        out: List[Dict[str, Any]] = []
        for r in rows:
            out.append({
                "id_": r.get("id_"),
                "name": r.get("name", ""),
                "imageUrl": r.get("gifUrl") or r.get("shortVideoUrl"),
                "source": "local",
            })
        return out

    async def get_by_id(self, id_: str) -> Optional[Dict[str, Any]]:
        return await self.repo.get(id_)

    async def create(self, user_id: Optional[str], data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.repo.create(user_id, data) 