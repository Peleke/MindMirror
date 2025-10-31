from __future__ import annotations

from typing import Any, Dict, List, Optional

from .local_db_client import ExerciseDBLocalClient
from .exercisedb_api_client import ExerciseDBApiClient


class CompositeExerciseClient:
    def __init__(self, local: ExerciseDBLocalClient, external: ExerciseDBApiClient):
        self.local = local
        self.external = external

    async def search(self, term: Optional[str], body_region: Optional[str], equipment: Optional[str], limit: int, offset: int = 0) -> List[Dict[str, Any]]:
        # fan-out
        local_res, ext_res = await _gather(self.local.search(term, body_region, equipment, limit, offset), self.external.search(term, limit))
        # simply concatenate for now
        return local_res + ext_res


async def _gather(*aws):
    # lightweight gather to avoid importing asyncio here; keep coupling minimal
    import asyncio
    return await asyncio.gather(*aws) 