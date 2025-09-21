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


def get_context(request: Request):
    user_id = request.headers.get("x-internal-id") or None
    # Prefer a request-scoped session if available
    session: AsyncSession
    try:
        session = request.state.db_session  # type: ignore[attr-defined]
    except Exception:
        session_factory = get_session_factory()
        session = session_factory()
    repo = MovementsRepoPg(session)
    client = ExerciseDBClient(Config.EXERCISEDB_BASE_URL, Config.EXERCISEDB_API_KEY)
    return {"movements_repo": repo, "exercise_client": client, "user_id": user_id}


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Create schema and tables if they don't exist (dev convenience)
        session_factory = get_session_factory()
        async with session_factory() as s:
            await s.execute(text('CREATE SCHEMA IF NOT EXISTS "movements"'))
            await s.commit()
        # Create tables
        async with session_factory().bind.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
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
    @app.middleware("http")
    async def db_session_middleware(request, call_next):
        session = None
        try:
            session_factory = get_session_factory()
            session = session_factory()
            request.state.db_session = session
            response = await call_next(request)
            return response
        finally:
            try:
                if session is not None:
                    await session.close()
            except Exception:
                pass

    schema = get_schema()
    graphql_app = GraphQLRouter(schema, graphiql=Config.DEBUG_GRAPHQL_SERVER, context_getter=get_context)
    app.include_router(graphql_app, prefix="/graphql")

    @app.get("/")
    async def root():
        return {"message": "Movements backend running", "graphql": "/graphql"}

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app() 