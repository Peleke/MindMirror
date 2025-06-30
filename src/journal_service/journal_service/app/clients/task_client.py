import httpx
from typing import Optional
from datetime import datetime

class TaskClient:
    def __init__(self, base_url: str = "http://celery-worker:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def queue_journal_indexing(
        self, 
        entry_id: str, 
        user_id: str, 
        content: str,
        created_at: Optional[datetime] = None,
        metadata: Optional[dict] = None
    ) -> dict:
        # Use current time if not provided
        if created_at is None:
            created_at = datetime.utcnow()
            
        response = await self.client.post(
            f"{self.base_url}/tasks/index-journal-entry",
            json={
                "entry_id": entry_id,
                "user_id": user_id,
                "content": content,
                "created_at": created_at.isoformat(),
                "metadata": metadata or {}
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def queue_tradition_reindex(
        self, 
        tradition: str,
        secret: str
    ) -> dict:
        response = await self.client.post(
            f"{self.base_url}/tasks/reindex-tradition",
            json={"tradition": tradition},
            headers={"X-Reindex-Secret": secret}
        )
        response.raise_for_status()
        return response.json() 