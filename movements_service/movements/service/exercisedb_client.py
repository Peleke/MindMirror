from __future__ import annotations

from typing import List, Optional, Dict, Any
import httpx


class ExerciseDBClient:
    def __init__(self, base_url: str, api_key: str | None = None, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or ""
        self.timeout = timeout
        self._headers = {}
        # Common patterns: some providers expect X-Api-Key, others use rapidapi headers
        if self.api_key:
            self._headers["X-Api-Key"] = self.api_key

    async def search(self, term: Optional[str], body_region: Optional[str], equipment: Optional[str], limit: int) -> List[Dict[str, Any]]:
        # Fallback if no key configured
        if not self.base_url:
            return []
        params: Dict[str, Any] = {}
        if term:
            params["name"] = term
        if body_region:
            params["bodyPart"] = body_region
        if equipment:
            params["equipment"] = equipment
        params["limit"] = limit

        url = f"{self.base_url}/exercises"
        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=self._headers) as client:
                resp = await client.get(url, params=params)
                if resp.status_code != 200:
                    return []
                data = resp.json()
        except Exception:
            return []

        results: List[Dict[str, Any]] = []
        if isinstance(data, list):
            for item in data[:limit]:
                results.append(self._map_search_result(item))
        elif isinstance(data, dict) and "data" in data:
            for item in data.get("data", [])[:limit]:
                results.append(self._map_search_result(item))
        return results

    async def fetch(self, external_id: str) -> Optional[Dict[str, Any]]:
        if not self.base_url:
            return None
        url = f"{self.base_url}/exercises/{external_id}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=self._headers) as client:
                resp = await client.get(url)
                if resp.status_code != 200:
                    return None
                item = resp.json()
        except Exception:
            return None
        return self._map_full_item(item)

    def _map_search_result(self, item: Dict[str, Any]) -> Dict[str, Any]:
        # ExerciseDB v2 fields
        return {
            "externalId": item.get("id"),
            "name": item.get("name", ""),
            "bodyRegion": item.get("bodyPart"),
            "equipment": [item.get("equipment")] if item.get("equipment") else [],
            "difficulty": item.get("difficulty"),
            "shortVideoUrl": None,
        }

    def _map_full_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        # Map to our repo.create() input
        return {
            "name": item.get("name", ""),
            "slug": (item.get("name") or "").lower().replace(" ", "-"),
            "bodyRegion": item.get("bodyPart"),
            "difficulty": item.get("difficulty"),
            "primaryClassification": item.get("category"),
            "primeMoverMuscle": item.get("target"),
            "secondaryMuscles": item.get("secondaryMuscles") or [],
            "primaryEquipment": [item.get("equipment")] if item.get("equipment") else [],
            "gifUrl": item.get("gifUrl"),
            "instructions": item.get("instructions") or [],
        } 