from fastapi import FastAPI
import logging

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Factory function to create FastAPI app instance."""
    app = FastAPI()
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "celery-worker"}

    return app


# Create the FastAPI app
app = create_app()
