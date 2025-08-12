from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
import strawberry
from habits_service.habits_service.app.db.session import engine
from habits_service.habits_service.app.db.models import Base
from habits_service.habits_service.app.graphql.schemas.query import Query as RootQuery
from habits_service.habits_service.app.graphql.schemas.mutation import Mutation as RootMutation
from habits_service.habits_service.app.config import get_settings
from sqlalchemy import text


schema = strawberry.Schema(query=RootQuery, mutation=RootMutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(graphql_app, prefix="/graphql")


@app.on_event("startup")
async def ensure_schema_exists():
    # Create schema if not present (optional, works on Postgres when user has perms)
    # This is best-effort; Alembic will manage tables later.
    try:
        async with engine.begin() as conn:
            schema = get_settings().database_schema
            # Ensure schema exists first (dev convenience)
            await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
            await conn.run_sync(Base.metadata.create_all)
    except Exception:
        # Do not crash service on startup if perms are insufficient
        pass


