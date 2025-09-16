from __future__ import annotations

from typing import Any, Dict, List, Optional
import os
import httpx


class ExerciseDBApiClient:
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, timeout_s: float = 8.0):
        self.base_url = base_url or os.getenv("EXERCISE_DB_BASE_URL", "https://v2.exercisedb.dev/api/v1")
        self.api_key = api_key or os.getenv("EXERCISE_DB_API_KEY")
        self.timeout_s = timeout_s

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {"Accept": "application/json"}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    async def search(self, search: Optional[str], limit: int = 25) -> List[Dict[str, Any]]:
        if not search:
            return []
        url = f"{self.base_url}/exercises/search"
        params = {"search": search}
        async with httpx.AsyncClient(timeout=self.timeout_s, headers=self._headers()) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json() or {}
            items = data.get("data") or []
            out: List[Dict[str, Any]] = []
            for it in items[:limit]:
                out.append({
                    "externalId": it.get("exerciseId"),
                    "name": it.get("name") or "",
                    "imageUrl": it.get("imageUrl"),
                    "source": "exercise_db",
                })
            return out

    async def get_by_id(self, external_id: str) -> Optional[Dict[str, Any]]:
        if not external_id:
            return None
        url = f"{self.base_url}/exercises/{external_id}"
        async with httpx.AsyncClient(timeout=self.timeout_s, headers=self._headers()) as client:
            resp = await client.get(url)
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            data = (resp.json() or {}).get("data") or {}
            # Normalize to a richer dict to map into local
            return {
                "externalId": data.get("exerciseId"),
                "name": data.get("name") or "",
                "imageUrl": data.get("imageUrl"),
                "videoUrl": data.get("videoUrl"),
                "exerciseType": data.get("exerciseType"),
                "bodyParts": data.get("bodyParts") or [],
                "equipments": data.get("equipments") or [],
                "targetMuscles": data.get("targetMuscles") or [],
                "secondaryMuscles": data.get("secondaryMuscles") or [],
                "keywords": data.get("keywords") or [],
                "overview": data.get("overview"),
                "instructions": data.get("instructions") or [],
                "exerciseTips": data.get("exerciseTips") or [],
                "variations": data.get("variations") or [],
                "relatedExternalIds": data.get("relatedExerciseIds") or [],
                "source": "exercise_db",
            } 