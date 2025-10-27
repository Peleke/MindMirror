import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from journal.app.config import get_settings
from journal.app.db.database import init_db, close_db
from journal.app.graphql.schemas.journal_schema import schema
from journal.app.graphql.context import get_context

# Import GraphQL schema (will be created next)
# from journal_service.app.graphql.schemas import create_schema

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info("Starting Journal Service...")
    try:
        await init_db()
        logger.info("Journal Service started successfully")
    except Exception as e:
        logger.warning(f"Database initialization failed (this is OK in development): {e}")
        logger.info("Journal Service started without database connection")
    
    yield
    
    logger.info("Shutting down Journal Service...")
    try:
        await close_db()
        logger.info("Journal Service shutdown complete")
    except Exception as e:
        logger.warning(f"Database cleanup failed: {e}")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="Journal Service",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add direct health endpoint
    @app.get("/health")
    async def health_check():
        """Basic health check endpoint."""
        return {
            "status": "healthy",
            "service": "journal-service",
            "version": "0.1.0"
        }
    
    # Register GraphQL
    graphql_app = GraphQLRouter(
        schema,
        graphql_ide="graphiql",
        context_getter=get_context
    )
    app.include_router(graphql_app, prefix="/graphql", tags=["graphql"])
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 
