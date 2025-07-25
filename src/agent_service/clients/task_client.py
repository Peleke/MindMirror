from typing import Optional

import httpx


import os

class TaskClient:
    def __init__(self, base_url: str = None):
        if base_url:
            self.base_url = base_url
        else:
            # Use environment variable or fallback to local development
            self.base_url = os.getenv("CELERY_WORKER_URL", "http://celery-worker-web:8000")
        self.client = httpx.AsyncClient()

    async def queue_journal_indexing(
        self, entry_id: str, user_id: str, tradition: str = "canon-default"
    ) -> dict:
        response = await self.client.post(
            f"{self.base_url}/tasks/index-journal-entry",
            json={"entry_id": entry_id, "user_id": user_id, "tradition": tradition},
        )
        response.raise_for_status()
        return response.json()

    async def queue_tradition_reindex(self, tradition: str, secret: str) -> dict:
        response = await self.client.post(
            f"{self.base_url}/tasks/reindex-tradition",
            json={"tradition": tradition},
            headers={"X-Reindex-Secret": secret},
        )
        response.raise_for_status()
        return response.json()
