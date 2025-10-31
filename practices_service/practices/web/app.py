from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware

# Import official Strawberry extensions
from strawberry.extensions.tracing import ApolloTracingExtension, OpenTelemetryExtension
from strawberry.fastapi import GraphQLRouter

from practices.monitoring.instrumentation import setup_opentelemetry, setup_prometheus
from practices.monitoring.logging_config import setup_logging
from practices.monitoring.middleware import log_requests_middleware
from practices.monitoring.opentelemetry_config import setup_opentelemetry_sdk
from practices.monitoring.strawberry_logging import LoguruStrawberryExtension
from practices.repository.database import close_db, init_db
from practices.repository.uow import UnitOfWork, get_uow
from practices.web.config import Config
from practices.web.graphql.dependencies import get_context
from practices.web.graphql.schema import get_schema

# For ApolloTracingExtension, Strawberry typically provides one that works for async.
# If there were a specific ApolloTracingExtensionAsync, we'd use that.


def create_app() -> FastAPI:
    """
    Creates and configures a new FastAPI application instance.
    This factory pattern is used to create a fresh app for both production runs and testing.
    """
    API_VERSION = Config.API_VERSION

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        print("Initializing database...")
        await init_db()
        yield
        print("Closing database connection...")
        await close_db()

    app = FastAPI(
        title="Practices API",
        description="API for managing practices",
        version=API_VERSION,
        lifespan=lifespan,
    )

    app.add_middleware(BaseHTTPMiddleware, dispatch=log_requests_middleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if not Config.DEBUG_GRAPHQL_SERVER:
        setup_logging()
        setup_opentelemetry_sdk()
        setup_prometheus(app)
        setup_opentelemetry(app)

    # Define extensions
    graphql_extensions = [
        LoguruStrawberryExtension(),
        OpenTelemetryExtension(),
    ]

    # Create schema with extensions
    schema_with_extensions = get_schema(extensions=graphql_extensions)

    graphql_app = GraphQLRouter(
        schema_with_extensions,  # Use the schema instance that has extensions
        graphiql=Config.DEBUG_GRAPHQL_SERVER,
        context_getter=get_context,
    )
    app.include_router(graphql_app, prefix="/graphql")

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    @app.get("/sdl", include_in_schema=False, tags=["internal"])
    async def get_schema_sdl():
        """
        Public SDL endpoint for schema composition.
        Returns GraphQL schema in SDL format.
        Used by mesh-compose to build supergraph.

        Note: Exposes schema structure only, not data.
        Data queries still require JWT authentication.
        """
        from fastapi.responses import Response
        return Response(
            content=str(schema_with_extensions),
            media_type="text/plain"
        )

    @app.get("/")
    async def root():
        return {"message": "Practices backend is running. Visit /graphql for the GraphQL API."}

    return app


app = create_app()
