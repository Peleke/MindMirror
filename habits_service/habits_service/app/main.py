from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
import strawberry
from habits_service.habits_service.app.db.session import engine
from habits_service.habits_service.app.db.models import Base


@strawberry.type
class Query:
    @strawberry.field
    def health(self) -> str:
        return "ok"

    @strawberry.field
    def version(self) -> str:
        return "0.1.0"


schema = strawberry.Schema(query=Query)
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
            await conn.run_sync(Base.metadata.create_all)
    except Exception:
        # Do not crash service on startup if perms are insufficient
        pass


