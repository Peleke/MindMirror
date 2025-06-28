"""
REST Router for Hooks and Webhooks

Clean REST router setup for hooks and webhook endpoints.
"""

from fastapi import APIRouter

# Import the existing hooks router
# Note: This will need to be updated when we refactor the hooks module
from agent_service.app.api.hooks import router as hooks_router

# Create main REST router
router = APIRouter()

# Include hooks router
router.include_router(hooks_router, prefix="/hooks", tags=["hooks"])


@router.get("/")
async def root():
    """Root endpoint."""
    return {"message": "MindMirror Agent Service API"}


@router.get("/ping")
async def ping():
    """Health check endpoint."""
    return {"status": "pong"}
