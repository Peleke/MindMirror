from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from strawberry.fastapi import GraphQLRouter
from sqlalchemy import text

from .config import Config
from ..web.schema import get_schema
from ..repository.database import get_session_factory, Base
from sqlalchemy.ext.asyncio import AsyncSession
from ..repository.movements_repo import MovementsRepoPg
from ..service.exercisedb_client import ExerciseDBClient
from shared.secrets import should_auto_create_schema


def get_context(request: Request):
    user_id = request.headers.get("x-internal-id") or None
    session_factory = get_session_factory()

    def repo_factory() -> MovementsRepoPg:
        # Create a fresh AsyncSession per resolver usage to avoid concurrent access on a single session
        session: AsyncSession = session_factory()
        return MovementsRepoPg(session)

    client = ExerciseDBClient(Config.EXERCISEDB_BASE_URL, Config.EXERCISEDB_API_KEY)
    return {"movements_repo_factory": repo_factory, "exercise_client": client, "user_id": user_id}


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Create schema and tables if they don't exist (dev convenience)
        session_factory = get_session_factory()
        async with session_factory() as s:
            await s.execute(text('CREATE SCHEMA IF NOT EXISTS "movements"'))
            await s.commit()

        # Only auto-create schema in local/test environments
        # In production/staging, we use Alembic migrations
        if should_auto_create_schema():
            print("Auto-creating schema for movements (local/test environment)")
            async with session_factory().bind.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        else:
            print("Skipping auto-create schema for movements (production/staging - use Alembic)")
    except Exception:
        pass
    yield
    try:
        pass
    except Exception:
        pass


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan, title="Movements Service")

    # Request-scoped DB session middleware to avoid pool leaks
    # Note: We avoid a single request-scoped session to prevent concurrent use across parallel resolvers.
    # Each resolver acquires its own AsyncSession via repo_factory instead.

    schema = get_schema()
    graphql_app = GraphQLRouter(schema, graphiql=Config.DEBUG_GRAPHQL_SERVER, context_getter=get_context)
    app.include_router(graphql_app, prefix="/graphql")

    @app.get("/")
    async def root():
        return {"message": "Movements backend running", "graphql": "/graphql"}

    @app.get("/health")
    async def health():
        return {"status": "ok"}

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
            content=str(schema),
            media_type="text/plain"
        )

    return app


app = create_app() 