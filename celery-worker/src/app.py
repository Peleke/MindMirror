from fastapi import FastAPI, HTTPException, Header
from src.models.task_models import IndexJournalEntryRequest, ReindexTraditionRequest
from src.tasks.journal_tasks import queue_journal_entry_indexing
from src.tasks.tradition_tasks import queue_tradition_reindex
import os

app = FastAPI()

@app.post("/tasks/index-journal-entry")
async def submit_index_task(request: IndexJournalEntryRequest):
    try:
        task = queue_journal_entry_indexing(
            request.entry_id, 
            request.user_id, 
            request.tradition
        )
        return {"task_id": task.id, "status": "queued"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tasks/reindex-tradition")
async def submit_reindex_task(
    request: ReindexTraditionRequest,
    x_reindex_secret: str = Header(...)
):
    secret = os.getenv("REINDEX_SECRET_KEY")
    if not secret or x_reindex_secret != secret:
        raise HTTPException(status_code=401, detail="Invalid secret")
    
    try:
        task = queue_tradition_reindex(request.tradition)
        return {"task_id": task.id, "status": "queued"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "celery-worker"} 