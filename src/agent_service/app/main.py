"""
FastAPI Application Factory

Clean architecture main application entry point with proper lifespan management,
logging, and router organization.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent_service.app.api.graphql_router import graphql_app
from agent_service.app.api.rest_router import router as rest_router
from agent_service.app.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    
    Handles startup and shutdown logic for the agent service.
    """
    logger.info("Starting agent service...")
    
    # Mock users service client for development
    mock_users_service_client = AsyncMock()
    
    try:
        with patch("shared.auth.users_service_client", new=mock_users_service_client):
            logger.info("Agent service started successfully")
            yield
    except Exception as e:
        logger.error(f"Error during application startup: {e}")
        raise
    finally:
        logger.info("Shutting down agent service...")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    settings = get_settings()
    
    app = FastAPI(
        title="MindMirror Agent Service",
        description="AI-powered journaling and coaching agent service",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(graphql_app, prefix="/graphql", tags=["graphql"])
    app.include_router(rest_router, tags=["rest"])
    
    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check() -> dict:
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "agent-service",
            "version": "1.0.0"
        }
    
    logger.info("FastAPI application configured successfully")
    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 